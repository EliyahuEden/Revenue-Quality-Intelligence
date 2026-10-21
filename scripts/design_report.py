"""Native PBIR report design. All KPI and analytical visuals remain native Power BI visuals."""
from pathlib import Path
import json,uuid,shutil,tempfile

SCHEMA='https://developer.microsoft.com/json-schemas/fabric/'
NAVY='#14243C';TEAL='#008C82';CORAL='#D86B4D';BLUE='#526AD4';INK='#23344D';MUTED='#64748B';BG='#F3F5FA';LINE='#DEE5EF'
PAGES=['5b9cef77342b526099d0','d2de67539b5e5bc794d0','cad6cde6010858449260','0190a4d82893586eb525','d9623a00b21653628513']
def lit(v):
 val=str(v).lower() if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+str(v).replace("'","''")+"'"
 return {'expr':{'Literal':{'Value':val}}}
def color(v):return {'solid':{'color':lit(v)}}
def props(p,selector=None):
 d={'properties':p}
 if selector is not None:d['selector']=selector
 return [d]
def expr(table,name,measure=False,source=False):
 return {'Measure' if measure else 'Column':{'Expression':{'SourceRef':{'Source' if source else 'Entity':table}},'Property':name}}
def projection(table,name,measure=False,label=None):
 return {'field':expr(table,name,measure),'queryRef':table+'.'+name,'nativeQueryRef':name,'displayName':label or name.replace('_',' ').title()}
def m(name,label=None):return projection('fact_invoice_line',name,True,label or name)
def col(t,n,label=None):return projection(t,n,False,label)
def stable(name):return uuid.uuid5(uuid.NAMESPACE_URL,'revenue-quality-v2:'+name).hex[:20]

def build_report(root):
 root=Path(root);report=root/'powerbi/RevenueQuality.Report';definition=report/'definition'
 # Only this generated definition tree is replaced. The imported model is untouched.
 assert definition.resolve()==(root/'powerbi/RevenueQuality.Report/definition').resolve()
 if definition.exists():
  backup=Path(tempfile.mkdtemp(prefix='revenue-quality-pbir-'))/'definition'
  shutil.move(str(definition),str(backup))
 definition.mkdir(parents=True,exist_ok=True)
 count=0
 def write(path,value):
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,ensure_ascii=True),encoding='utf-8')
 def visual(page,key,typ,x,y,w,h,roles=None,title=None,objects=None,bg='#FFFFFF',sort=None,filters=None):
  nonlocal count
  ident=stable(page+'.'+key)
  v={'visualType':typ,'drillFilterOtherVisuals':True}
  if roles:v['query']={'queryState':{k:{'projections':val} for k,val in roles.items()}}
  if sort:v['query']['sortDefinition']={'sort':[{'field':sort[0]['field'],'direction':sort[1]}],'isDefaultSort':False}
  v['visualContainerObjects']={'background':props({'show':lit(True),'color':color(bg),'transparency':lit(0)}),'border':props({'show':lit(False),'radius':lit(10)})}
  if title:v['visualContainerObjects']['title']=props({'show':lit(True),'text':lit(title),'fontColor':color(INK),'fontSize':lit(13),'fontFamily':lit('Segoe UI Semibold')})
  if objects:v['objects']=objects
  d={'$schema':SCHEMA+'item/report/definition/visualContainer/2.4.0/schema.json','name':ident,'position':{'x':x,'y':y,'z':count,'width':w,'height':h,'tabOrder':count},'visual':v}
  if filters:d['filterConfig']={'filters':filters}
  write(definition/f'pages/{page}/visuals/{ident}/visual.json',d);count+=1
  return d
 def text(page,key,value,x,y,w,h,size=11,ink=MUTED,bg=BG,bold=False):
  h=max(h,size*1.5+22)
  paragraphs=[{'textRuns':[{'value':line,'textStyle':{'fontFamily':'Segoe UI Semibold' if bold else 'Segoe UI','fontSize':str(size)+'pt','color':ink}}]} for line in value.split('\n')]
  return visual(page,key,'textbox',x,y,w,h,objects={'general':props({'paragraphs':paragraphs})},bg=bg)
 def card(page,key,name,label,x,y,w=365,h=118,hero=False,units=1,precision=0,note=None,accent=TEAL):
  bg=NAVY if hero else '#FFFFFF';ink='#FFFFFF' if hero else INK
  d=visual(page,key,'card',x,y,w,h-28 if note else h,{'Values':[m(name)]},label,
   {'labels':props({'color':color(ink if hero else accent),'fontSize':lit(38 if hero else 32),'labelDisplayUnits':lit(units),'labelPrecision':lit(precision)}),'categoryLabels':props({'show':lit(False)})},bg)
  d['visual']['visualContainerObjects']['title'][0]['properties']['fontColor']=color('#D7E4F5' if hero else MUTED)
  write(definition/f"pages/{page}/visuals/{d['name']}/visual.json",d)
  if note:text(page,key+'_note',note,x,y+h-32,w,43,9,'#BACDDE' if hero else MUTED,bg)
 def basic(t,n,values):
  return {'name':stable(t+n+str(values)),'field':expr(t,n),'type':'Categorical','howCreated':'User','filter':{'Version':2,'From':[{'Name':'d','Entity':t,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[expr('d',n,source=True)],'Values':[[{'Literal':{'Value':str(v)+'L' if isinstance(v,int) else "'"+v.replace("'","''")+"'"}}] for v in values]}}}]}}
 def rank_filter():
  return {'name':stable('top-products'),'field':expr('fact_invoice_line','Product Revenue Rank',True),'type':'Advanced','howCreated':'User','filter':{'Version':2,'From':[{'Name':'f','Entity':'fact_invoice_line','Type':0}],'Where':[{'Condition':{'Comparison':{'ComparisonKind':4,'Left':expr('f','Product Revenue Rank',True,True),'Right':{'Literal':{'Value':'10L'}}}}}]}}
 def chart_objects(ink=TEAL,labels=False):
  return {'dataPoint':props({'defaultColor':color(ink)}),'legend':props({'show':lit(False)}),'labels':props({'show':lit(labels),'color':color(INK),'labelDisplayUnits':lit(1000),'labelPrecision':lit(0),'fontSize':lit(10)}),'categoryAxis':props({'show':lit(True),'showAxisTitle':lit(False),'labelColor':color(MUTED),'fontSize':lit(10),'maxSize':lit(48)}),'valueAxis':props({'show':lit(True),'showAxisTitle':lit(False),'labelColor':color(MUTED),'fontSize':lit(10),'gridlineColor':color('#E7EDF4')})}
 def filters(page,product=False):
  visual(page,'country','slicer',36,133,340,57,{'Values':[col('dim_country','country_key','Country')]},objects={'data':props({'mode':lit('Dropdown')}),'header':props({'text':lit('Country'),'fontColor':color(INK),'fontSize':lit(10)})})
  if product:visual(page,'product','slicer',396,133,340,57,{'Values':[col('dim_product','product_key','Product code')]},objects={'data':props({'mode':lit('Dropdown')}),'header':props({'text':lit('Product code'),'fontColor':color(INK),'fontSize':lit(10)})})
  else:visual(page,'year','slicer',396,133,205,57,{'Values':[col('dim_date','calendar_year','Year')]},objects={'data':props({'mode':lit('Dropdown')}),'header':props({'text':lit('Year'),'fontColor':color(INK),'fontSize':lit(10)})})
  text(page,'filter_help','EXPLORE  /  Use the filters or select a chart bar. Clear a selection to return to all data.',760 if product else 630,145,790 if not product else 790,36,10)
 def page(page_id,display,question,subtitle,snapshot=False):
  write(definition/f'pages/{page_id}/page.json',{'$schema':SCHEMA+'item/report/definition/page/2.0.0/schema.json','name':page_id,'displayName':display,'displayOption':'FitToPage','height':900,'width':1600,'objects':{'background':props({'color':color(BG),'transparency':lit(0)})}})
  text(page_id,'header_bg','',0,0,1600,116,1,bg=NAVY)
  text(page_id,'brand','REVENUE QUALITY  /  INTELLIGENCE',32,0,1000,35,9,'#72D7CB',NAVY,True)
  text(page_id,'question',question,32,30,1515,61,25,'#FFFFFF',NAVY,True)
  text(page_id,'scope',subtitle,34,80,1518,36,10,'#C4D2E4',NAVY)
  text(page_id,'page_number',display[:2]+' / 05',1480,0,92,35,10,'#C4D2E4',NAVY)
  text(page_id,'footer','UCI Online Retail II  |  Independent historical case study  |  GBP  |  '+('Fixed customer snapshot: 1 Dec 2011' if snapshot else 'Complete months: Dec 2009-Nov 2011'),34,852,1530,36,9)
 def takeaway(page_id,heading,body,y=758,h=89):
  text(page_id,'takeaway_title',heading,36,y,1528,29,10,'#006A64','#E0F1ED',True)
  text(page_id,'takeaway_body',body,36,y+29,1528,h-29,12,INK,'#E0F1ED')

 p=PAGES[0];page(p,'01 | Sales overview','How much sales value remains after cancellations?','Sales value, timing and market dependence. Read the headline first, then explore the drivers.')
 filters(p)
 card(p,'net','Net Merchandise GBP','Net merchandise value',36,215,490,124,True,1000000,2,'Gross sales minus cancellation postings')
 card(p,'gross','Gross Sales GBP','Gross merchandise sales',546,215,315,124,units=1000000,precision=2,note='Before cancellation postings',accent=BLUE)
 card(p,'cancel_ratio','Cancellation Value Ratio','Cancellation value / gross',881,215,315,124,precision=1,note='A value ratio, not a return rate',accent=CORAL)
 card(p,'orders','Sale Invoices','Sale invoices',1216,215,348,124,units=1000,precision=1,note='Distinct invoices, not product lines')
 visual(p,'trend','areaChart',36,367,940,359,{'Category':[col('dim_date','month_start','Month')],'Y':[m('Net Merchandise GBP','Net merchandise value')]},'When did net merchandise value rise or fall?',chart_objects(),sort=(col('dim_date','month_start'),'Ascending'))
 visual(p,'markets','clusteredBarChart',998,367,566,359,{'Category':[col('dim_country','country_key','Country')],'Y':[m('Gross Sales GBP','Gross sales')]},'Five major markets | gross sales',chart_objects(BLUE,True),sort=(m('Gross Sales GBP'),'Descending'),filters=[basic('dim_country','country_key',['United Kingdom','EIRE','Netherlands','Germany','France'])])
 takeaway(p,'READ THE PATTERN, THEN ASK WHY','Peaks reveal sales timing; the market chart shows dependence on a few countries. Compare equal periods before calling a change growth. The five-market list is fixed from the full-history ranking.')

 p=PAGES[1];page(p,'02 | Customer return','Do customers come back to buy again?','Identified buyers only. Repeat purchase requires a full 90-day follow-up; this page is a fixed historical snapshot.',True)
 text(p,'snapshot_tag','FIXED SNAPSHOT  /  1 DEC 2011     |     Transaction-date and country filters from other pages do not change these figures.',36,139,1528,43,11,INK,'#E5EAF7')
 card(p,'repeat_rate','Repeat 90d Rate','Bought again within 90 days',36,215,490,124,True,precision=1,note='1,458 repeat buyers / 3,533 eligible buyers')
 card(p,'known','Snapshot Customers','Identified buyers',546,215,315,124,note='Anonymous purchases excluded',accent=BLUE)
 card(p,'eligible','Mature 90d Customers','Eligible for fair comparison',881,215,315,124,note='Warmup + full 90-day follow-up')
 card(p,'repeat_n','Mature 90d Repeat Customers','Observed repeat buyers',1216,215,348,124,note='Second invoice within 90 days')
 # Color is driven by the native retention measure, not by a rendered picture.
 stops={'min':{'color':{'Literal':{'Value':"'#F0F6F6'"}},'value':{'Literal':{'Value':'0D'}}},'max':{'color':{'Literal':{'Value':"'#88CFC5'"}},'value':{'Literal':{'Value':'0.5D'}}}}
 stops['nullColoringStrategy']={'strategy':{'Literal':{'Value':"'noColor'"}}}
 rule={'Input':{'SelectRef':{'ExpressionName':'fact_invoice_line.Purchase Retention Rate'}},'FillRule':{'linearGradient2':stops}}
 gradient={'solid':{'color':{'expr':{'FillRule':rule}}}}
 matrix={'rowHeaders':props({'fontSize':lit(10),'fontColor':color(INK)}),'columnHeaders':props({'fontSize':lit(10),'fontColor':color(MUTED)}),'values':[{'properties':{'fontSize':lit(10),'fontColorPrimary':color(INK),'fontColorSecondary':color(INK),'backColorPrimary':color('#FFFFFF'),'backColorSecondary':color('#FFFFFF')}},{'properties':{'backColor':gradient},'selector':{'data':[{'dataViewWildcard':{'matchingOption':1}}],'metadata':'fact_invoice_line.Purchase Retention Rate'}}],'subTotals':props({'rowSubtotals':lit(False),'columnSubtotals':lit(False)}),'rowTotal':props({'show':lit(False)}),'columnTotal':props({'show':lit(False)})}
 visual(p,'cohort','pivotTable',36,367,1000,359,{'Rows':[col('cohort_retention','cohort_month','First observed month')],'Columns':[col('cohort_retention','month_age','Months later')],'Values':[m('Purchase Retention Rate','Bought in this month')]},'Who purchased again in later calendar months?',matrix,filters=[basic('cohort_retention','month_age',list(range(1,13)))])
 segment_style=chart_objects(BLUE,True)
 segment_style['labels'][0]['properties'].update({'labelDisplayUnits':lit(1),'labelPrecision':lit(0)})
 segment_style['categoryAxis'][0]['properties'].update({'fontSize':lit(9),'maxSize':lit(60)})
 visual(p,'segments','clusteredBarChart',1058,367,506,359,{'Category':[col('customer_segments','segment','Customer group')],'Y':[m('Snapshot Customers','Buyers')]},'Customer groups | fixed snapshot',segment_style,sort=(m('Snapshot Customers'),'Descending'))
 takeaway(p,'HOW TO READ THE COHORT GRID','Each row groups buyers by their first observed purchase month. Column 1 is the next calendar month. Darker cells mean more bought again; blanks are not yet observable. Monthly activity is not the same metric as the 90-day repeat rate.')

 p=PAGES[2];page(p,'03 | Product drivers','Which products deserve a closer look?','Explore sales contribution and cancellation exposure. Product value is not product profit.')
 filters(p,True)
 card(p,'net','Net Merchandise GBP','Net value in your selection',36,215,490,124,True,1000000,2,note='Sales less cancellation postings')
 card(p,'share','Product Gross Share','Share of all-product gross',546,215,315,124,precision=1,note='Same country/date context',accent=BLUE)
 card(p,'cancel','Cancellation Postings GBP','Cancellation postings',881,215,315,124,units=1000,precision=1,note='Posted against selected products',accent=CORAL)
 card(p,'aov','Gross AOV GBP','Selected-product value / invoice',1216,215,348,124,precision=2,note='Not the value of the entire basket')
 visual(p,'products','clusteredBarChart',36,367,700,359,{'Category':[col('dim_product','product_key','Product code')],'Y':[m('Gross Sales GBP','Gross sales')]},'Leading product codes | gross sales',chart_objects(TEAL,True),sort=(m('Gross Sales GBP'),'Descending'),filters=[rank_filter()])
 visual(p,'detail','tableEx',758,367,806,359,{'Values':[col('dim_product','product_key','Code'),col('dim_product','product_name','Product'),m('Gross Sales GBP','Gross'),m('Cancellation Postings GBP','Cancelled'),m('Net Merchandise GBP','Net')]},'Product detail | select a bar to investigate',{'grid':props({'gridHorizontal':lit(False),'rowPadding':lit(5)}),'columnHeaders':props({'fontSize':lit(10),'fontColor':color(MUTED)}),'values':props({'fontSize':lit(10)})},sort=(m('Gross Sales GBP'),'Descending'))
 takeaway(p,'INVESTIGATE BEFORE CHANGING THE ASSORTMENT','Use the ranking to find important products, then inspect their cancellation postings. A large sales figure does not establish a good margin; cost and original-invoice links are needed before making that judgment.')

 p=PAGES[3];page(p,'04 | Trust the numbers','Can we trust the sales figures?','Follow the gross-to-net calculation, then inspect missing customer identity and duplicate-policy sensitivity.')
 filters(p)
 card(p,'gross','Gross Sales GBP','Gross merchandise sales',36,215,466,124,units=1000000,precision=2,note='Positive merchandise sale lines',accent=BLUE)
 text(p,'minus','-',512,250,45,65,32,CORAL)
 card(p,'cancel','Cancellation Postings GBP','Less cancellation postings',567,215,466,124,units=1000,precision=1,note='Cancellation value as a positive reduction',accent=CORAL)
 text(p,'equals','=',1040,250,45,65,28,INK)
 card(p,'net','Net Merchandise GBP','Net merchandise value',1098,215,466,124,True,1000000,2,note='Posting-based sales value, not profit')
 visual(p,'cancel_month','clusteredColumnChart',36,367,940,359,{'Category':[col('dim_date','month_start','Month')],'Y':[m('Cancellation Postings GBP','Cancellation postings')]},'When were cancellation values posted?',chart_objects(CORAL),sort=(col('dim_date','month_start'),'Ascending'))
 card(p,'anonymous','Anonymous Gross Share','Gross sales without a customer ID',998,367,566,137,precision=1,note='Kept in financial totals; excluded from cohorts',accent=BLUE)
 card(p,'duplicate','Duplicate Sensitivity GBP','Change under a deduplication scenario',998,526,566,137,units=1000,precision=1,note='A policy sensitivity, not a confirmed correction',accent=CORAL)
 text(p,'quality_note','No original-invoice link: cancellation postings cannot establish a matched return rate.',1006,678,550,49,10)
 takeaway(p,'FULL-SOURCE AUDIT  /  TWO DIFFERENT DUPLICATE QUESTIONS','22,523 overlapping export rows were verified and superseded. Another 11,511 repeated complete-period lines remain ambiguous; they stay in the baseline, with a separate what-if calculation. These source-audit counts do not follow page filters.')

 p=PAGES[4];page(p,'05 | Next decisions','Turn the evidence into the next decision','Three priorities grounded in the full historical dataset. These are proposals, with no claimed realized uplift.')
 text(p,'priority_intro','THE DECISION ORDER  /  Establish reliable numbers, understand the customers, then test an intervention.',36,139,1528,43,11,INK,'#E5EAF7')
 items=[('finance','01  /  RECONCILE','Cancellation Postings GBP','Cancellation postings',CORAL,'FINANCE','Understand the adjustment','Review cancellation documents, reason codes and original-invoice links. Reconcile excluded postings with the finance ledger.','Measure next: verified links and reconciliation exceptions.'),('identity','02  /  IDENTIFY','Anonymous Gross Share','Gross sales without identity',BLUE,'DATA + CRM','Understand who is buying','Audit customer capture at checkout. Keep unknown buyers visible in financial totals instead of inventing customer identities.','Measure next: share of gross linked to stable customer IDs.'),('crm','03  /  TEST','Repeat 90d Rate','Mature 90-day repeat rate',TEAL,'COMMERCIAL + CRM','Test a useful follow-up','Research account needs, then design a randomized outreach test with a control group and cancellation guardrails.','Measure next: repeat-purchase difference under random assignment.')]
 for i,(key,tag,metric,label,accent,owner,headline,action,success) in enumerate(items):
  x=36+i*516
  text(p,key+'_panel','',x,215,496,496,1,bg='#FFFFFF')
  text(p,key+'_tag',tag,x+16,234,464,27,11,accent,'#FFFFFF',True)
  card(p,key+'_value',metric,label,x+10,281,476,126,units=1000 if 'GBP' in metric else 1,precision=1,note='Full-history evidence',accent=accent)
  text(p,key+'_owner',owner,x+17,425,460,23,9,MUTED,'#FFFFFF',True)
  text(p,key+'_headline',headline,x+16,455,464,42,16,INK,'#FFFFFF',True)
  text(p,key+'_action',action,x+16,506,464,116,12,INK,'#FFFFFF')
  text(p,key+'_success',success,x+16,636,464,62,10,accent,'#FFFFFF')
 takeaway(p,'KEEP THE COMMERCIAL CLAIM HONEST','The data identifies patterns and priorities. It does not establish profit, a matched product-return rate, or the financial effect of a campaign that was never run.')

 write(definition/'pages/pages.json',{'$schema':SCHEMA+'item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':PAGES,'activePageName':PAGES[0]})
 write(definition/'version.json',{'$schema':SCHEMA+'item/report/definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
 theme={'name':'Revenue Quality | Editorial','dataColors':[TEAL,BLUE,CORAL,'#91C9C3','#B4BDEA','#E9BEA9'],'background':BG,'foreground':INK,'tableAccent':TEAL,'textClasses':{'title':{'fontFace':'Segoe UI Semibold','fontSize':14,'color':INK},'label':{'fontFace':'Segoe UI','fontSize':10,'color':MUTED},'callout':{'fontFace':'Segoe UI Semibold','fontSize':36,'color':INK}}}
 write(root/'powerbi/theme.json',theme);write(report/'StaticResources/RegisteredResources/RevenueQualityTheme.json',theme)
 write(definition/'report.json',{'$schema':SCHEMA+'item/report/definition/report/3.1.0/schema.json','themeCollection':{'customTheme':{'name':'RevenueQualityTheme','type':'RegisteredResources','reportVersionAtImport':{'visual':'2.4.0','page':'2.0.0','report':'3.1.0'}}},'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'RevenueQualityTheme','path':'RevenueQualityTheme.json','type':'CustomTheme'}]}],'settings':{'defaultFilterActionIsDataFilter':True,'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized'}})
 return {'pages':5,'visuals':count,'native_project':str(root/'powerbi/RevenueQuality.pbip')}

if __name__=='__main__':
 print(json.dumps(build_report(Path(__file__).resolve().parents[1]),indent=2))
