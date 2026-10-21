"""Meaningful contract/regression tests: independent arithmetic, keys and censoring boundaries."""
from pathlib import Path
import sys,json
from decimal import Decimal,ROUND_HALF_UP
import pytest
import pandas as pd
import duckdb
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pipeline import configure

@pytest.fixture(scope='module')
def con():
    db=ROOT/'data/warehouse/retail.duckdb'
    if not db.exists():pytest.fail('Run pipeline first; warehouse missing')
    c=duckdb.connect(str(db),read_only=True);configure(c);yield c;c.close()

def test_independent_source_arithmetic(con):
    # Independent pandas filtering over unclassified source; excludes partial final month.
    raw=con.sql('SELECT * FROM raw.lines').df()
    raw=raw.loc[~((raw.source_sheet=='Year 2009-2010')&(raw.invoice_ts>=pd.Timestamp('2010-12-01')))]
    code=raw.stock_code.str.strip().str.upper().str.fullmatch(r'[0-9]{5}[A-Z]*')
    price=raw.unit_price>0;before=raw.invoice_ts<pd.Timestamp('2011-12-01')
    cancel=raw.invoice_no.str.upper().str.startswith('C')
    sale=code&price&before&(~cancel)&(raw.quantity>0)
    credit=code&price&before&cancel&(raw.quantity<0)
    def pence(mask):
        return sum(int((Decimal(str(q))*Decimal(str(p))*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP)) for q,p in zip(raw.loc[mask,'quantity'],raw.loc[mask,'unit_price']))
    metrics=json.loads((ROOT/'reports/metrics.json').read_text())
    assert pence(sale)==round(metrics['gross_gbp']*100)
    assert -pence(credit)==round(metrics['cancellation_gbp']*100)
    assert raw.loc[sale,'invoice_no'].nunique()==metrics['orders']

def test_censoring_boundaries(con):
    bad=con.sql("SELECT count(*) FROM mart.customer_lifecycle WHERE fully_observed_90d AND first_purchase_date+90>DATE '2011-11-30'").fetchone()[0]
    assert bad==0
    assert con.sql("SELECT count(*) FROM mart.cohort_retention WHERE activity_month>=DATE '2011-12-01'").fetchone()[0]==0
    assert con.sql('SELECT count(*) FROM mart.cohort_retention WHERE month_age=0 AND retention_rate<>1').fetchone()[0]==0

def test_dense_calendar(con):
    days=con.sql('SELECT count(*) FROM mart.dim_date WHERE is_complete_period').fetchone()[0]
    countries=con.sql('SELECT count(*) FROM mart.dim_country').fetchone()[0]
    assert con.sql('SELECT count(*) FROM mart.daily_country').fetchone()[0]==days*countries

def test_physical_foreign_keys_and_invoice_grain(con):
    constraints=con.sql("SELECT count(*) FROM duckdb_constraints() WHERE schema_name='mart' AND table_name='fact_invoice_line' AND constraint_type='FOREIGN KEY'").fetchone()[0]
    assert constraints==4
    assert con.sql('SELECT count(*)-count(DISTINCT invoice_no) FROM mart.fact_order').fetchone()[0]==0
    assert con.sql("SELECT count(*) FROM mart.fact_order o LEFT JOIN mart.dim_customer d USING(customer_key) WHERE d.customer_key IS NULL").fetchone()[0]==0

def test_financial_join_does_not_fanout(con):
    baseline=con.sql('SELECT sum(amount_pence) FROM mart.fact_invoice_line').fetchone()[0]
    joined=con.sql('SELECT sum(f.amount_pence) FROM mart.fact_invoice_line f JOIN mart.dim_customer c USING(customer_key) JOIN mart.dim_product p USING(product_key) JOIN mart.dim_country k USING(country_key) JOIN mart.dim_date d USING(date_key)').fetchone()[0]
    assert baseline==joined

def test_reopened_view_has_persisted_cutoff(con):
    assert con.sql('SELECT max(date_key) FROM mart.v_complete_lines').fetchone()[0].isoformat()=='2011-11-30'

def test_reporting_mart_sql_parity(con):
    m=json.loads((ROOT/'reports/metrics.json').read_text())
    totals=con.sql('SELECT sum(net_pence),sum(orders) FROM mart.daily_country').fetchone()
    assert totals[0]==round(m['net_gbp']*100)
    assert totals[1]==m['orders']
    assert json.loads((ROOT/'reports/data_quality.json').read_text())['passed']

def test_repeat_statistics_denominators(con):
    counts=con.sql("SELECT count(*), count(*) FILTER(WHERE days_to_second_order<=90) FROM mart.customer_lifecycle WHERE after_warmup AND fully_observed_90d").fetchone()
    m=json.loads((ROOT/'reports/metrics.json').read_text());assert counts==(m['repeat_eligible'],m['repeat_n'])
    results=pd.read_csv(ROOT/'reports/repeat_purchase_statistics.csv')
    assert results.eligible_customers.sum()==counts[0]
    assert results.repeat_customers.sum()==counts[1]
    assert ((results.ci95_lower<=results.repeat_90d_rate)&(results.ci95_upper>=results.repeat_90d_rate)).all()

def test_source_edge_case_classification():
    c=duckdb.connect();c.execute('CREATE SCHEMA raw');c.execute('CREATE SCHEMA staging')
    c.execute('''CREATE TABLE raw.lines(line_id BIGINT,source_sheet VARCHAR,source_row BIGINT,invoice_no VARCHAR,stock_code VARCHAR,description VARCHAR,quantity BIGINT,invoice_ts TIMESTAMP,unit_price DOUBLE,source_customer_id VARCHAR,country VARCHAR)''')
    data=[(1,'x',2,'1','12345','A',2,'2011-01-01',2.5,'7','UK'),
          (2,'x',3,'1','12345','A',2,'2011-01-01',2.5,'7','UK'),
          (3,'x',4,'C2','12345','A',-1,'2011-01-02',2.5,'7','UK'),
          (4,'x',5,'3','POST','Postage',1,'2011-01-02',5,None,'UK'),
          (5,'x',6,'4','12345','A',1,'2011-01-02',0,None,'UK'),
          (6,'x',7,'C5','12345','A',1,'2011-01-02',2.5,'7','UK'),
          (7,'x',8,'6','12345','A',1,'2011-01-02',-2.5,'7','UK'),
          (8,'x',9,'7','12345',None,1,'2011-01-02',2.5,None,'UK')]
    c.executemany('INSERT INTO raw.lines VALUES (?,?,?,?,?,?,?,?,?,?,?)',data)
    c.execute((ROOT/'sql/transformations/01_classify.sql').read_text())
    assert c.sql('SELECT line_status FROM staging.lines ORDER BY line_id').fetchall()==[(s,) for s in ['sale','sale','cancellation','non_merchandise','zero_price','sign_exception','negative_price','sale']]
    assert c.sql('SELECT count(*) FROM staging.lines WHERE duplicate_ordinal>1').fetchone()[0]==1
    assert c.sql("SELECT customer_key FROM staging.lines WHERE line_id=8").fetchone()[0]=='UNKNOWN'
    assert c.sql("SELECT sum(amount_pence) FROM staging.lines WHERE line_status IN ('sale','cancellation')").fetchone()[0]==1000
    c.close()

def test_source_provenance():
    source=json.loads((ROOT/'reports/source_manifest.json').read_text())
    config=json.loads((ROOT/'config.json').read_text())
    assert source['sha256']==config['expected_workbook_sha256']
    assert source['rows']==1067371
    assert source['license']=='CC BY 4.0'
