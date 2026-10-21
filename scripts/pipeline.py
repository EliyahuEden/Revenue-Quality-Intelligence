"""Run from any directory: python scripts/pipeline.py [--raw-dir PATH]."""
from pathlib import Path
import argparse,json,time,platform,sys,subprocess
import duckdb
from ingest import ingest
ROOT=Path(__file__).resolve().parents[1]

def configure(con):
    cfg=json.loads((ROOT/'config.json').read_text())
    if cfg['return_horizon_days']!=90:raise ValueError('This KPI contract and measure kit explicitly require a 90-day horizon')
    for key,val in [('cutoff',cfg['last_complete_month_exclusive']),('warmup',cfg['cohort_warmup_end']),('horizon',cfg['return_horizon_days'])]:
        con.execute(f'SET VARIABLE {key} = ?',[val])
    con.execute("SET threads=4")
    con.execute("SET memory_limit='2GB'")

def connect():
    con=duckdb.connect(str(ROOT/'data/warehouse/retail.duckdb'))
    configure(con)
    return con

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--raw-dir',type=Path,default=ROOT/'data/raw');parser.add_argument('--refresh',action='store_true')
    args=parser.parse_args()
    for folder in ['data/warehouse','data/exports','reports/query_results','assets','powerbi/screenshots']:(ROOT/folder).mkdir(parents=True,exist_ok=True)
    con=connect()
    # Atomic transformation transaction: consumers never see half a model. Roll back failures.
    # Drop schemas together because DuckDB enforces FK dependencies during rebuild.
    for schema in ['raw','staging']:con.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
    started=time.perf_counter(); manifest=ingest(con,ROOT,args.raw_dir,args.refresh)
    con.execute('BEGIN')
    try:
        con.execute('DROP SCHEMA IF EXISTS mart CASCADE');con.execute('CREATE SCHEMA mart')
        for f in sorted((ROOT/'sql/transformations').glob('*.sql'))+sorted((ROOT/'sql/analytical_marts').glob('*.sql')):
            print('Executing',f.name,flush=True)
            for statement in con.extract_statements(f.read_text(encoding='utf-8')):
                con.execute(statement)
        con.execute('COMMIT')
    except Exception:
        try: con.execute('ROLLBACK')
        except duckdb.Error: pass
        raise
    from validate import validate
    quality=validate(con,ROOT)
    if not quality['passed']:raise RuntimeError('Data contract failed: inspect reports/data_quality.json')
    performance=[]
    for f in sorted((ROOT/'sql/advanced_analysis').glob('*.sql')):
        t=time.perf_counter();df=con.execute(f.read_text(encoding='utf-8')).df()
        df.to_csv(ROOT/'reports/query_results'/f.with_suffix('.csv').name,index=False)
        performance.append({'query':f.name,'rows':len(df),'seconds':round(time.perf_counter()-t,4)})
    # Store independent plan evidence, not an invented optimization speedup.
    q=(ROOT/'sql/advanced_analysis/19_basket_affinity.sql').read_text()
    (ROOT/'reports/query_plan.txt').write_text(con.execute('EXPLAIN ANALYZE '+q).fetchone()[1],encoding='utf-8')
    tables=['dim_date','dim_customer','dim_product','dim_country','fact_invoice_line','fact_order','customer_lifecycle','cohort_retention','customer_segments','monthly_performance','daily_country']
    for name in tables:con.execute(f'COPY mart.{name} TO ? (HEADER, DELIMITER \',\')',[str(ROOT/f'data/exports/{name}.csv')])
    from report import build_report
    build_report(con,ROOT)
    status={'source_rows':manifest['rows'],'sql_transformations':5,'sql_analyses':len(performance),
            'source_cache_used':manifest['cache_used'],
            'elapsed_seconds':round(time.perf_counter()-started,2),'python':platform.python_version(),
            'duckdb':duckdb.__version__,'checks':quality['checks'],'query_execution':performance,
            'powerbi_status':'Native project in powerbi; see powerbi/validation.md for Desktop verification status'}
    (ROOT/'reports/run_manifest.json').write_text(json.dumps(status,indent=2))
    con.close();print(json.dumps({k:v for k,v in status.items() if k not in ['checks','query_execution']},indent=2),flush=True)

if __name__=='__main__':main()
