"""Acquire official source atomically, record provenance, load exact source rows."""
from pathlib import Path
import hashlib, json, zipfile
import requests
import pandas as pd

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def ingest(con, root, raw_dir, refresh=False):
    raw_dir.mkdir(parents=True,exist_ok=True)
    config=json.loads((root/'config.json').read_text())
    target=raw_dir/'online_retail_II.xlsx'
    if not target.exists() or refresh:
        z=raw_dir/'source.zip.part'
        session=requests.Session()
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        session.mount('https://',HTTPAdapter(max_retries=Retry(total=3,backoff_factor=1)))
        with session.get(config['source_url'],stream=True,timeout=(30,180)) as r:
            r.raise_for_status()
            with z.open('wb') as f:
                for chunk in r.iter_content(1024*1024): f.write(chunk)
        with zipfile.ZipFile(z) as archive:
            members=[m for m in archive.namelist() if m.endswith('.xlsx')]
            if len(members)!=1: raise ValueError('Expected exactly one workbook')
            temp=target.with_suffix('.xlsx.part')
            with archive.open(members[0]) as src,temp.open('wb') as dst:
                import shutil
                shutil.copyfileobj(src,dst)
            temp.replace(target)
        z.unlink()
    book=pd.ExcelFile(target)
    actual_sha=sha256(target)
    expected_sha=config.get('expected_workbook_sha256')
    if expected_sha and actual_sha!=expected_sha:
        raise ValueError('Source checksum changed; inspect publisher version before updating config')
    manifest={'source_url':config['source_url'],'source_doi':'10.24432/C5CG6D',
              'research_date':config['research_date'],'sha256':actual_sha,
              'bytes':target.stat().st_size,'license':'CC BY 4.0','sheets':{}}
    # Excel parsing is the slow step; cache losslessly as DuckDB-native Parquet.
    cache=raw_dir/'raw_lines.parquet'
    cache_meta=raw_dir/'cache.json'
    cached=cache.exists() and cache_meta.exists() and json.loads(cache_meta.read_text()).get('sha256')==manifest['sha256']
    if cached and not refresh:
        con.execute('CREATE OR REPLACE TABLE raw.lines AS SELECT * FROM read_parquet(?)',[str(cache)])
        manifest['sheets']=json.loads(cache_meta.read_text())['sheets']
    else:
        con.execute('DROP TABLE IF EXISTS raw.lines')
        for i,sheet in enumerate(book.sheet_names):
            print('Reading workbook sheet',sheet,flush=True)
            df=pd.read_excel(book,sheet_name=sheet,dtype={'Invoice':str,'StockCode':str,'Customer ID':str})
            expected=['Invoice','StockCode','Description','Quantity','InvoiceDate','Price','Customer ID','Country']
            if list(df.columns)!=expected: raise ValueError(f'Source schema changed: {list(df.columns)}')
            df.columns=['invoice_no','stock_code','description','quantity','invoice_ts','unit_price','source_customer_id','country']
            df['source_sheet']=sheet
            df['source_row']=range(2,len(df)+2)
            df['line_id']=i*1000000+df['source_row']
            con.register('sheet_frame',df)
            if i==0:con.execute('CREATE TABLE raw.lines AS SELECT * FROM sheet_frame')
            else:con.execute('INSERT INTO raw.lines SELECT * FROM sheet_frame')
            manifest['sheets'][sheet]=len(df)
        con.execute('COPY raw.lines TO ? (FORMAT PARQUET)',[str(cache)])
        cache_meta.write_text(json.dumps(manifest,indent=2))
    manifest['rows']=con.execute('SELECT count(*) FROM raw.lines').fetchone()[0]
    manifest['cache_used']=cached and not refresh
    (root/'reports/source_manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest
