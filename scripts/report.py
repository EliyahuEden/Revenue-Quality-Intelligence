"""Derive every published number from executed SQL, with traceable denominators."""
import json,math
import numpy as np
import pandas as pd
from scipy.stats import norm

def wilson(k,n):
    if n==0:return [None,None]
    z=norm.ppf(.975);p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [center-half,center+half]

def build_report(con,root):
    def q(name):return pd.read_csv(root/f'reports/query_results/{name}.csv')
    executive=q('01_executive_bridge').iloc[0];years=q('16_comparable_year_bridge');countries=q('04_country_mix')
    anon=q('13_anonymous_coverage');duplicates=q('14_duplicate_sensitivity').iloc[0];cohort=q('07_repeat_90d')
    products=q('10_product_concentration');pareto=q('05_customer_pareto');segments=q('06_segments')
    stats=q('17_first_basket_repeat');interval=q('09_reorder_intervals').iloc[0]
    for i,row in stats.iterrows():
        lo,hi=wilson(int(row.repeat_customers),int(row.eligible_customers))
        stats.loc[i,'ci95_lower']=lo;stats.loc[i,'ci95_upper']=hi
    stats.to_csv(root/'reports/repeat_purchase_statistics.csv',index=False)
    # Descriptive month-standardized contrast, using only strata where both groups appear.
    strata=con.execute("""SELECT cohort_month,first_order_breadth>=6 broad,count(*) n,
    count(*) FILTER(WHERE days_to_second_order<=90) k FROM mart.customer_lifecycle
    WHERE after_warmup AND fully_observed_90d GROUP BY 1,2""").df()
    pivot=strata.pivot(index='cohort_month',columns='broad',values=['n','k']).dropna()
    weights=(pivot['n'][False]+pivot['n'][True]);weights=weights/weights.sum()
    p0=pivot['k'][False]/pivot['n'][False];p1=pivot['k'][True]/pivot['n'][True]
    diff=float((weights*(p1-p0)).sum());variance=float((weights**2*(p0*(1-p0)/pivot['n'][False]+p1*(1-p1)/pivot['n'][True])).sum())
    standardized={'comparison':'6+ first-order SKUs versus 1–5; common calendar cohorts',
                  'risk_difference':diff,'ci95_normal':[diff-1.96*math.sqrt(variance),diff+1.96*math.sqrt(variance)],
                  'common_cohorts':len(pivot),'method':'Pooled cohort-size standardization; independent Bernoulli plug-in variance; fixed strata weights',
                  'limitations':'Observational convenience data; adjusts month only. No causal effect, randomized allocation or population representativeness.'}
    (root/'reports/statistical_method.json').write_text(json.dumps(standardized,indent=2))
    total_gross=float(executive.gross_gbp);cancel=float(executive.cancellation_gbp);net=float(executive.net_gbp)
    known_gross=float(anon.loc[~anon.anonymous,'gross_gbp'].sum());anonymous=float(anon.loc[anon.anonymous,'gross_gbp'].sum())
    top_share=float(pareto.loc[pareto.in_top_decile,'gross_pence'].sum()/pareto.gross_pence.sum())
    repeat_n=int(cohort.eligible_customers.sum());repeat_k=int(cohort.repeat_customers.sum());repeat_rate=repeat_k/repeat_n
    old,new=years.iloc[0],years.iloc[1];growth=float(new.net_gbp/old.net_gbp-1)
    uk=countries.loc[countries.country_key=='United Kingdom'].iloc[0]
    single=segments.loc[segments.segment=='Single purchase dormant'].iloc[0]
    established=segments.loc[segments.segment=='Established dormant'].iloc[0]
    history=q('12_cancellation_history_coverage');unmatched=history.loc[~history.prior_sale_exists]
    findings=[]
    def finding(title,observed,source,decision,hypothesis,limitation,success):
        findings.append(dict(id=len(findings)+1,title=title,observed=observed,source=source,decision=decision,
                             hypothesis=hypothesis,limitation=limitation,success=success))
    finding('Gross sales need a cancellation bridge',f'Complete-month merchandise gross is £{total_gross:,.2f}; cancellation postings total £{cancel:,.2f} ({cancel/total_gross:.2%} of gross), leaving £{net:,.2f} net merchandise value.',
            '01_executive_bridge; 21_quality_reconciliation','Finance should review the gross-to-net bridge monthly and reconcile exclusions against the ledger.',
            'Wholesale order corrections or reversals may explain part of the cancellation value.','Cancellation posting dates do not establish the original sale or physical returns. Net merchandise value is not accounting-recognized revenue or profit.',
            'Reconciliation difference in pence; cancellation-value ratio and documented exceptions.')
    finding('Comparable periods change the growth discussion',f'January–November net merchandise value changes from £{old.net_gbp:,.2f} in 2010 to £{new.net_gbp:,.2f} in 2011 ({growth:+.2%}). Orders change from {int(old.orders):,} to {int(new.orders):,}.',
            '16_comparable_year_bridge; 02_monthly_growth','Use equal January–November windows for the management growth comparison.',
            'Order mix, volume and cancellation timing may contribute.','Only two historical annual cycles; no inflation adjustment, causal attribution or full December 2011.',
            'Comparable-window net value, orders and AOV, reviewed together.')
    finding('Unidentified transactions limit CRM coverage',f'Anonymous merchandise sales contribute £{anonymous:,.2f}, or {anonymous/total_gross:.2%} of gross sales, while remaining included in finance KPIs.',
            '13_anonymous_coverage','Audit checkout/customer capture and keep an explicit unknown bucket in financial reports.',
            'Guest orders or operational data capture practices may explain missing IDs.','Missingness may be non-random. Known-customer retention cannot describe anonymous buyers.',
            'Share of gross sales linked to a stable customer ID; no retrospective fabricated IDs.')
    finding('Known-customer revenue is concentrated',f'The top 10% of {len(pareto):,} known buyers by observed gross sales generate {top_share:.2%} of known-customer gross sales.',
            '05_customer_pareto','Prioritize a review of high-value account continuity and service needs.',
            'The publisher notes many wholesale customers, which may create a long value tail.','Ranked over the full observed period; this is a retrospective concentration measure and not a future targeting score.',
            'Revenue concentration and repeat-order continuity among approved account segments.')
    finding('Repeat purchase has an explicit observation window',f'{repeat_k:,} of {repeat_n:,} eligible known buyers place a second order within 90 days ({repeat_rate:.2%}); eligibility begins March 2010 and requires 90 fully observed days before December 2011.',
            '07_repeat_90d; 22_cohort_maturity','Use the mature 90-day rate as a CRM baseline; design a randomized outreach test only after obtaining consent and treatment data.',
            'Ordering cadence, customer type and assortment needs may explain non-repeat purchases.','First observed purchase may not be first-ever purchase. Warmup reduces but cannot remove left censoring. Non-repeat is not contractual churn.',
            'Pre-registered 90-day repeat rate, revenue/customer and cancellation guardrail in a future randomized test.')
    finding('First-basket breadth is a useful research hypothesis',f'Month-standardized 90-day repeat-rate difference for 6+ first-order SKUs versus 1–5 SKUs is {diff*100:+.2f} percentage points ({standardized["common_cohorts"]} common cohorts). Descriptive 95% interval: {standardized["ci95_normal"][0]*100:+.2f} to {standardized["ci95_normal"][1]*100:+.2f} points.',
            '17_first_basket_repeat; repeat_purchase_statistics.csv; statistical_method.json','Research whether basket breadth identifies different customer needs before testing recommendations or bundles.',
            'Wholesale intent or existing familiarity may influence both breadth and repeat buying.','Observational association, adjusted only for calendar cohort; not evidence that increasing basket breadth causes retention.',
            'Future randomized bundle experiment: repeat purchase, basket value and cancellation guardrails.')
    finding('Dormancy contains distinct commercial cases',f'{int(single.customers):,} buyers are single-purchase dormant; {int(established.customers):,} are established dormant (at least five orders, last purchase over 90 days before cutoff), with £{established.gross_gbp:,.2f} historical gross purchases.',
            '06_segments','Separate first-purchase onboarding research from established-account reactivation review.',
            'Established buyers may pause seasonally; single purchasers may have one-time needs.','Segments are an as-of snapshot at 1 December 2011. Historical purchases are not recoverable revenue or forecast exposure.',
            'Subsequent repeat rate by preassigned segment in newly collected data.')
    finding('Geography has a dominant base market',f'The United Kingdom contributes £{uk.gross_gbp:,.2f}, or {uk.gross_gbp/total_gross:.2%} of gross merchandise sales, across {int(uk.orders):,} sale invoices.',
            '04_country_mix','Protect service quality in the base market; evaluate expansion with market-specific commercial costs.',
            'Retailer location and historical distribution relationships may drive this mix.','No acquisition, delivery costs or market-size denominator; this cannot establish geographic profitability or addressable market.',
            'Market gross/net value and cancellation ratio, with delivery and margin data added before investment.')
    overlap=int(con.execute("SELECT count(*) FROM staging.lines WHERE is_superseded_partition").fetchone()[0])
    finding('Separate proven partition overlap from ambiguous line repeats',f'The two sheets repeat {overlap:,} rows over 1–9 December 2010; an eight-field multiset check verifies equal records and multiplicities, so the later partition is authoritative. Separately, removing {int(duplicates.repeated_rows):,} repeated core lines within authoritative partitions changes net merchandise value by £{duplicates.retained_net_gbp-duplicates.deduplicated_net_gbp:,.2f} as a sensitivity.',
            '14_duplicate_sensitivity','Request source-system line identifiers and retain the current auditable baseline until duplication is confirmed.',
            'Repeated identical lines could be duplicate ingestion or valid repeated invoice lines.','Partition overlap is verified and excluded from core. Remaining within-partition repeats lack a trustworthy line key; removing those is a scenario, not a verified correction.',
            'Duplicate key failures on future loads; finance reconciliation under an approved policy.')
    finding('Cancellation history is incomplete evidence',f'{int(unmatched.cancellation_lines.sum()):,} identified cancellation lines have no earlier sale with the same customer, SKU and price in the observed history, totaling £{unmatched.cancellation_gbp.sum():,.2f}.',
            '12_cancellation_history_coverage','Investigate unmatched cancellations and obtain original-invoice references before calculating matched return rates.',
            'Pre-history sales, corrections, price changes or identifier errors may explain gaps.','An earlier matching-price sale also does not prove a match; quantities and original documents are not allocated.',
            'Share of cancellation value linked to a verified original invoice and approved reason.')
    (root/'reports/findings.json').write_text(json.dumps(findings,indent=2,ensure_ascii=False),encoding='utf-8')
    md='# Executive analytical findings\n\nHistorical case study; observational results, not achieved employer impact. Reporting window: 1 December 2009–30 November 2011. Source through 9 December 2011 is retained for audit; incomplete December is excluded from headline analyses. Monetary figures are nominal GBP.\n\n'
    for f in findings:
        md+=f"## {f['id']}. {f['title']}\n\n**Observed:** {f['observed']}\n\n**Evidence:** `{f['source']}` in `reports/query_results/` unless stated otherwise.\n\n**Decision:** {f['decision']}\n\n**Possible explanation:** {f['hypothesis']}\n\n**Limits:** {f['limitation']}\n\n**Success measure:** {f['success']}\n\n"
    (root/'docs/insights.md').write_text(md,encoding='utf-8')
    metrics={'gross_gbp':total_gross,'cancellation_gbp':cancel,'net_gbp':net,'orders':int(executive.orders),
             'known_buyers':int(executive.known_buyers),'anonymous_gross_share':anonymous/total_gross,
             'top_decile_gross_share':top_share,'repeat_90d_rate':repeat_rate,'repeat_eligible':repeat_n,
             'repeat_n':repeat_k,'jan_nov_net_growth':growth,'core_lines_complete':int(executive.lines)}
    (root/'reports/metrics.json').write_text(json.dumps(metrics,indent=2))
    schema=con.execute("SELECT table_name,column_name,data_type,is_nullable FROM information_schema.columns WHERE table_schema='mart' ORDER BY table_name,ordinal_position").df()
    schema.to_csv(root/'docs/schema_columns.csv',index=False)
    from plot_statistics import plot
    plot(root)
