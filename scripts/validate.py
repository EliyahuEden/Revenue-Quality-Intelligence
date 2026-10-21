"""Failing contracts block outputs. Descriptive anomalies remain reported, not deleted."""
import json
def validate(con,root):
    checks=[]
    def check(name,sql,expected=0):
        value=con.execute(sql).fetchone()[0]
        checks.append({'name':name,'value':float(value) if value is not None else None,'expected':expected,'passed':value==expected})
    check('source_row_count','SELECT count(*) FROM raw.lines',1067371)
    check('classification_conserves_rows','SELECT (SELECT count(*) FROM raw.lines)-(SELECT count(*) FROM staging.lines)')
    check('line_key_unique','SELECT count(*)-count(DISTINCT line_id) FROM staging.lines')
    check('overlap_rows_verified_by_multiset',"""SELECT count(*) FROM (
    SELECT invoice_no,stock_code,description,quantity,invoice_ts,unit_price,source_customer_id,country,
    count(*) FILTER(WHERE source_sheet='Year 2009-2010') old_n,
    count(*) FILTER(WHERE source_sheet='Year 2010-2011') new_n
    FROM staging.lines WHERE invoice_ts>=TIMESTAMP '2010-12-01' AND invoice_ts<TIMESTAMP '2010-12-10'
    GROUP BY 1,2,3,4,5,6,7,8 HAVING old_n<>new_n)""")
    check('no_invalid_source_timestamps','SELECT count(*) FROM staging.lines WHERE invoice_ts IS NULL')
    check('source_quantity_cast_loss','SELECT count(*) FROM staging.lines WHERE quantity IS NULL')
    check('source_price_cast_loss','SELECT count(*) FROM staging.lines WHERE unit_price IS NULL')
    check('fact_reconciles_core','SELECT (SELECT sum(amount_pence) FROM mart.fact_invoice_line)-(SELECT sum(amount_pence) FROM staging.lines WHERE line_status IN (\'sale\',\'cancellation\'))')
    check('fact_grain_unique','SELECT count(*)-count(DISTINCT line_id) FROM mart.fact_invoice_line')
    for dim,key in [('dim_customer','customer_key'),('dim_product','product_key'),('dim_country','country_key'),('dim_date','date_key')]:
        check(f'{dim}_referential_integrity',f'SELECT count(*) FROM mart.fact_invoice_line f LEFT JOIN mart.{dim} d USING({key}) WHERE d.{key} IS NULL')
    check('sale_sign_valid',"SELECT count(*) FROM mart.fact_invoice_line WHERE line_status='sale' AND (quantity<=0 OR unit_price<=0 OR amount_pence<=0)")
    check('cancellation_sign_valid',"SELECT count(*) FROM mart.fact_invoice_line WHERE line_status='cancellation' AND (quantity>=0 OR unit_price<=0 OR amount_pence>=0)")
    check('order_amount_reconciles',"SELECT (SELECT sum(gross_pence) FROM mart.fact_order)-(SELECT sum(amount_pence) FROM mart.fact_invoice_line WHERE line_status='sale')")
    check('invoice_has_single_customer_country_date',"SELECT count(*) FROM (SELECT invoice_no FROM mart.fact_invoice_line WHERE line_status='sale' GROUP BY 1 HAVING count(DISTINCT customer_key)>1 OR count(DISTINCT country_key)>1 OR count(DISTINCT date_key)>1)")
    check('cohort_rates_valid','SELECT count(*) FROM mart.cohort_retention WHERE retention_rate<0 OR retention_rate>1')
    check('cohort_age_zero_equals_size','SELECT count(*) FROM mart.cohort_retention WHERE month_age=0 AND active_customers<>cohort_size')
    check('future_cohort_cells_absent',"SELECT count(*) FROM mart.cohort_retention WHERE activity_month>=cast(getvariable('cutoff') AS DATE)")
    check('no_unknown_lifecycle',"SELECT count(*) FROM mart.customer_lifecycle WHERE customer_key='UNKNOWN'")
    check('dense_calendar_country_grain','SELECT count(*)-count(DISTINCT (date_key,country_key)) FROM mart.daily_country')
    check('monthly_bridge_agrees','SELECT (SELECT sum(net_pence) FROM mart.monthly_performance)-(SELECT sum(amount_pence) FROM mart.v_complete_lines)')
    check('raw_financial_bridge',"SELECT (SELECT sum(amount_pence) FROM staging.lines)-(SELECT sum(amount_pence) FROM mart.fact_invoice_line)-(SELECT sum(amount_pence) FROM staging.lines WHERE line_status NOT IN ('sale','cancellation'))")
    # Independent arithmetic from source, separate from model classifications.
    check('source_vs_typed_pence',"SELECT sum(cast(round(quantity*cast(unit_price AS DECIMAL(18,4))*100,0) AS BIGINT))-(SELECT sum(amount_pence) FROM staging.lines) FROM raw.lines")
    audit=con.execute('SELECT line_status,count(*) row_count,sum(amount_pence)/100.0 signed_gbp FROM staging.lines GROUP BY 1 ORDER BY row_count DESC').df()
    anomalies={
       'invoice_timestamp_variants':con.execute("SELECT count(*) FROM (SELECT invoice_no FROM mart.fact_invoice_line WHERE line_status='sale' GROUP BY 1 HAVING count(DISTINCT invoice_ts)>1)").fetchone()[0],
       'superseded_overlap_rows':con.execute("SELECT count(*) FROM staging.lines WHERE is_superseded_partition").fetchone()[0],
       'max_invoice_timestamp_span_minutes':con.execute("SELECT max(span) FROM (SELECT datediff('minute',min(invoice_ts),max(invoice_ts)) span FROM mart.fact_invoice_line WHERE line_status='sale' GROUP BY invoice_no)").fetchone()[0],
       'missing_customers':con.execute('SELECT count(*) FROM staging.lines WHERE source_customer_id IS NULL').fetchone()[0],
       'missing_descriptions':con.execute('SELECT count(*) FROM staging.lines WHERE description IS NULL').fetchone()[0],
       'repeated_extra_rows':con.execute('SELECT count(*) FROM staging.lines WHERE duplicate_ordinal>1').fetchone()[0],
       'unknown_countries':con.execute("SELECT count(*) FROM staging.lines WHERE country='Unknown'").fetchone()[0],
       'customer_country_changes':con.execute('SELECT count(*) FROM mart.dim_customer WHERE observed_country_count>1').fetchone()[0],
       'source_date_range':[str(x) for x in con.execute('SELECT min(invoice_ts),max(invoice_ts) FROM staging.lines').fetchone()],
       'price_range':[str(x) for x in con.execute('SELECT min(unit_price),max(unit_price) FROM staging.lines').fetchone()],
       'quantity_range':list(con.execute('SELECT min(quantity),max(quantity) FROM staging.lines').fetchone()),
       'stock_codes':con.execute('SELECT count(DISTINCT stock_code) FROM staging.lines').fetchone()[0]
    }
    result={'passed':all(c['passed'] for c in checks),'checks':checks,'anomalies':anomalies,'classification':audit.to_dict('records')}
    (root/'reports/data_quality.json').write_text(json.dumps(result,indent=2))
    md='# Data quality and reconciliation\n\n'+f"Contracts: {sum(c['passed'] for c in checks)}/{len(checks)} passed. Full-window diagnostics (core reporting stops before December 2011).\n\n"
    md+='|Contract|Value|Expected|Pass|\n|---|---:|---:|---|\n'+''.join(f"|{c['name']}|{c['value']}|{c['expected']}|{c['passed']}|\n" for c in checks)
    md+='\n## Observed anomalies\n\n```json\n'+json.dumps(anomalies,indent=2)+'\n```\n\n'
    md+='|Classification|Rows|Signed GBP|\n|---|---:|---:|\n'+''.join(f"|{r.line_status}|{r.row_count:,}|{r.signed_gbp:,.2f}|\n" for r in audit.itertuples())
    md+='\nPolicies: all physical rows retained in raw/staging. Missing identity maps to UNKNOWN and stays in financial totals, excluded from customer analyses. Verified overlapping partition copies are superseded after multiset validation. Within-partition exact repeats are retained because source has no reliable line key; deduplication is a labeled sensitivity. Zero/negative prices, non-merchandise codes, zero quantities and sign exceptions are excluded from core, visible in this bridge. Large valid wholesale lines remain. C-prefixed negative merchandise lines are cancellation postings, not proven returned goods. No country imputation; customer location stays on each transaction.\n'
    (root/'reports/data_quality.md').write_text(md,encoding='utf-8')
    return result
