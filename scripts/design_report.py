"""Native management report: comparison first, detail on demand."""
from pathlib import Path
import json,uuid,shutil,tempfile
SCHEMA='https://developer.microsoft.com/json-schemas/fabric/'
FOREST='#173F35';GREEN='#26745B';ORANGE='#C46635';INK='#243D35';MUTED='#65756B';BG='#F3F1E9';WHITE='#FFFFFF';SOFT='#E3EADF'
PAGES=['5b9cef77342b526099d0','d9623a00b21653628513','d2de67539b5e5bc794d0','b6e49a703d2b5c198a61','cad6cde6010858449260','0190a4d82893586eb525']
def stable(v):return uuid.uuid5(uuid.NAMESPACE_URL,'retail-manager-v3:'+v).hex[:20]
def lit(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+v.replace("'","''")+"'"}}}
def color(v):return {'solid':{'color':lit(v)}}
def props(p,selector=None):return [{'properties':p,**({'selector':selector} if selector else {})}]
def expr(t,n,measure=False,source=False):return {'Measure' if measure else 'Column':{'Expression':{'SourceRef':{'Source' if source else 'Entity':t}},'Property':n}}
def field(t,n,measure=False,label=None):return {'field':expr(t,n,measure),'queryRef':t+'.'+n,'nativeQueryRef':n,'displayName':label or n}
def m(n,label=None):return field('fact_invoice_line',n,True,label)
def col(t,n,label=None):return field(t,n,False,label)
def basic(t,n,values):
 return {'name':stable(t+n+str(values)),'field':expr(t,n),'type':'Categorical','howCreated':'User','filter':{'Version':2,'From':[{'Name':'d','Entity':t,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[expr('d',n,source=True)],'Values':[[{'Literal':{'Value':str(v)+'L' if isinstance(v,int) else "'"+v.replace("'","''")+"'"}}] for v in values]}}}]}}
def rank(n=10):return {'name':stable('rank'+str(n)),'field':expr('fact_invoice_line','Product Net 2011 Rank',True),'type':'Advanced','howCreated':'User','filter':{'Version':2,'From':[{'Name':'f','Entity':'fact_invoice_line','Type':0}],'Where':[{'Condition':{'Comparison':{'ComparisonKind':4,'Left':expr('f','Product Net 2011 Rank',True,True),'Right':{'Literal':{'Value':str(n)+'L'}}}}}]}}
def measure_filter(name,n):
 return {'name':stable('measure-filter'+name+str(n)),'field':expr('fact_invoice_line',name,True),'type':'Advanced','howCreated':'User','filter':{'Version':2,'From':[{'Name':'f','Entity':'fact_invoice_line','Type':0}],'Where':[{'Condition':{'Comparison':{'ComparisonKind':4,'Left':expr('f',name,True,True),'Right':{'Literal':{'Value':str(n)+'L'}}}}}]}}
def chart(ink=GREEN,labels=False,legend=False,units=1000):
 return {'dataPoint':props({'defaultColor':color(ink)}),'legend':props({'show':lit(legend),'position':lit('Top'),'fontSize':lit(12),'labelColor':color(MUTED)}),'labels':props({'show':lit(labels),'color':color(INK),'labelDisplayUnits':lit(units),'labelPrecision':lit(0),'fontSize':lit(12),'labelPosition':lit('OutsideEnd')}),'categoryAxis':props({'show':lit(True),'showAxisTitle':lit(False),'labelColor':color(MUTED),'fontSize':lit(12),'maxSize':lit(55)}),'valueAxis':props({'show':lit(True),'showAxisTitle':lit(False),'labelColor':color(MUTED),'fontSize':lit(11),'gridlineColor':color('#E9EDE5')})}
def build_report(root):
 root=Path(root);report=root/'powerbi/RevenueQuality.Report';definition=report/'definition'
 assert definition.resolve()==(root/'powerbi/RevenueQuality.Report/definition').resolve()
 if definition.exists():shutil.move(str(definition),str(Path(tempfile.mkdtemp(prefix='retail-pbir-'))/'definition'))
 definition.mkdir(parents=True);count=0
 def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=True),encoding='utf-8')
 def visual(p,key,typ,x,y,w,h,roles=None,title=None,objects=None,bg=WHITE,sort=None,filters=None):
  nonlocal count
  name=stable(p+key);v={'visualType':typ,'drillFilterOtherVisuals':True}
  if roles and 'Category' in roles and 'Tooltips' not in roles:
   table=roles['Category'][0]['field'].get('Column',{}).get('Expression',{}).get('SourceRef',{}).get('Entity')
   if table=='dim_country':roles['Tooltips']=[m('Net Change GBP','Net change | GBP'),m('Net 2010 GBP','2010 net | GBP'),m('Net 2011 GBP','2011 net | GBP'),m('Invoice Comparison Growth','Invoice change vs 2010'),m('Cancellation 2011 Ratio','Cancelled / gross')]
   if table=='dim_product':roles['Tooltips']=[m('Product SKU Title','SKU'),m('Product Description Title','Original description'),m('Net 2010 GBP','2010 net | GBP'),m('Net 2011 GBP','2011 net | GBP'),m('Cancellation 2011 Ratio','Cancelled / gross'),m('Product Comparison Title','Sales history')]
   if table=='customer_segments':roles['Tooltips']=[m('Snapshot Customers','Identified buyers'),m('Snapshot Gross GBP','Historical gross | GBP'),m('Segment Gross Share','Share of known-buyer gross')]
  if roles and 'Tooltips' in roles:
   used={f['queryRef'] for role,fields in roles.items() if role!='Tooltips' for f in fields}
   roles['Tooltips']=[f for f in roles['Tooltips'] if f['queryRef'] not in used]
   if not roles['Tooltips']:roles.pop('Tooltips')
  if roles:v['query']={'queryState':{k:{'projections':val} for k,val in roles.items()}}
  if sort:v['query']['sortDefinition']={'sort':[{'field':sort[0]['field'],'direction':sort[1]}],'isDefaultSort':False}
  v['visualContainerObjects']={'background':props({'show':lit(True),'color':color(bg),'transparency':lit(0)}),'border':props({'show':lit(False),'radius':lit(12)}),'visualHeader':props({'show':lit(False)})}
  if title:v['visualContainerObjects']['title']=props({'show':lit(True),'text':{'expr':title['field']} if isinstance(title,dict) else lit(title),'fontColor':color(INK),'fontSize':lit(15),'fontFamily':lit('Segoe UI Semibold')})
  if objects:v['objects']=objects
  if roles and len(roles.get('Y',[]))==2:
   v['objects']['dataPoint']=[{'properties':{'fill':color(ORANGE if 'cancel' in key else GREEN)},'selector':{'metadata':roles['Y'][0]['queryRef']}},{'properties':{'fill':color(ORANGE if roles['Y'][1]['nativeQueryRef'] in ['Driver Decline GBP','Net Decline GBP'] else '#A2B3A0')},'selector':{'metadata':roles['Y'][1]['queryRef']}}]
  if roles and len(roles.get('Y',[]))==1 and key in ['growth_bridge','market_change','market_variance']:
   ref=roles['Y'][0]['queryRef']
   stops={'min':{'color':{'Literal':{'Value':"'"+ORANGE+"'"}},'value':{'Literal':{'Value':'0D'}}},'max':{'color':{'Literal':{'Value':"'"+GREEN+"'"}},'value':{'Literal':{'Value':'1D'}}}}
   rule={'Input':{'SelectRef':{'ExpressionName':ref}},'FillRule':{'linearGradient2':stops}}
   v.setdefault('objects',{})['dataPoint']=[{'properties':{'defaultColor':color(MUTED)}},{'properties':{'fill':{'solid':{'color':{'expr':{'FillRule':rule}}}}},'selector':{'data':[{'dataViewWildcard':{'matchingOption':1}}]}}]
  d={'$schema':SCHEMA+'item/report/definition/visualContainer/2.4.0/schema.json','name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':count,'tabOrder':count},'visual':v}
  if filters:d['filterConfig']={'filters':filters}
  write(definition/f'pages/{p}/visuals/{name}/visual.json',d);count+=1
 def text(p,key,s,x,y,w,h,size=14,ink=INK,bg=BG,bold=False):
  paras=[{'textRuns':[{'value':line,'textStyle':{'fontFamily':'Segoe UI Semibold' if bold else 'Segoe UI','fontSize':str(size)+'pt','color':ink}}]} for line in s.split('\n')]
  visual(p,key,'textbox',x,y,w,max(h,size*1.5+22),objects={'general':props({'paragraphs':paras})},bg=bg)
 def card(p,key,n,label,x,y,w=366,h=110,units=1,precision=0,accent=FOREST):
  visual(p,key,'card',x,y,w,h,{'Values':[m(n)]},label,{'labels':props({'color':color(accent),'fontSize':lit(38),'labelDisplayUnits':lit(units),'labelPrecision':lit(precision)}),'categoryLabels':props({'show':lit(False)})})
 def small(p,key,n,label,x,y,w,accent=GREEN):
  # A compact dynamic comparison beneath the headline, with an explicit benchmark.
  visual(p,key,'card',x,y,w,53,{'Values':[m(n)]},None,{'labels':props({'color':color(accent),'fontSize':lit(18),'labelDisplayUnits':lit(1),'labelPrecision':lit(1)}),'categoryLabels':props({'show':lit(False)})})
  text(p,key+'label',label,x+w,y+7,200,38,12,MUTED,WHITE)
 def page(p,name,title,scope,market=False):
  write(definition/f'pages/{p}/page.json',{'$schema':SCHEMA+'item/report/definition/page/2.0.0/schema.json','name':p,'displayName':name,'displayOption':'FitToPage','height':900,'width':1600,'objects':{'background':props({'color':color(BG),'transparency':lit(0)})}})
  text(p,'header','',0,0,1600,108,1,bg=FOREST)
  text(p,'brand','RETAIL  /  PERFORMANCE',32,0,1000,33,11,'#B9CCB5',FOREST,True)
  text(p,'title',title,32,30,1100,67,28,WHITE,FOREST,True)
  if market:
   visual(p,'country','slicer',1230,23,338,67,{'Values':[col('dim_country','country_key','Market')]},objects={'data':props({'mode':lit('Dropdown')}),'header':props({'text':lit('Market'),'fontColor':color(FOREST),'fontSize':lit(12)})})
  text(p,'scope',scope,32,111,1536,39,12,MUTED)
  text(p,'footer','UCI Online Retail II  /  Independent portfolio study',32,858,1040,36,11,MUTED)
  text(p,'page',name[:2]+' / 06',1460,858,110,36,12,MUTED)
 # 01 / Executive: direction, arithmetic drivers, location and cancellation pressure.
 p=PAGES[0];page(p,'01 | Executive','Sales growth and its drivers','JAN-NOV 2011 vs JAN-NOV 2010  /  GBP  /  select a market to investigate',True)
 for i,(key,n,label,units,prec,change,accent) in enumerate([
  ('net','Net 2011 GBP','Net merchandise value',1000000,2,'Net Comparison Growth',GREEN),
  ('orders','Invoices 2011','Sales invoices',1000,1,'Invoice Comparison Growth',ORANGE),
  ('basket','Basket 2011 GBP','Gross value per invoice',1,0,'Basket Comparison Growth',GREEN),
  ('cancel','Cancellation 2011 Ratio','Cancellation value / gross',1,1,'Cancellation Change Points',ORANGE)]):
  x=32+i*392;text(p,key+'panel','',x,158,368,134,1,bg=WHITE)
  card(p,key,n,label,x+8,161,352,82,units,prec,ORANGE if key=='cancel' else FOREST)
  small(p,key+'change',change,'vs 2010',x+12,235,120,accent)
 visual(p,'sales_trend','lineChart',32,309,914,270,{'Category':[col('dim_date','Month')],'Y':[m('Net 2011 GBP','2011'),m('Net 2010 GBP','2010')]},m('Sales Trend Title'),chart(legend=True),sort=(col('dim_date','month_number'),'Ascending'),filters=[basic('dim_date','month_number',list(range(1,12)))])
 visual(p,'growth_bridge','clusteredBarChart',968,309,600,270,{'Category':[col('growth_driver','driver','Driver')],'Y':[m('Driver Contribution GBP','Change contribution')]},'What changed net value? | GBP contribution',chart(GREEN,True),sort=(col('growth_driver','sort'),'Ascending'))
 visual(p,'market_change','clusteredBarChart',32,603,914,224,{'Category':[col('dim_country','country_key','Market')],'Y':[m('Net Change GBP','Change vs 2010')]},'Markets driving the change | largest 6 movements',chart(GREEN,True),sort=(m('Net Change GBP'),'Descending'),filters=[measure_filter('Absolute Market Change Rank',6)])
 visual(p,'cancel_trend','clusteredColumnChart',968,603,600,224,{'Category':[col('dim_date','Month')],'Y':[m('Cancellation 2011 Ratio','2011'),m('Cancellation 2010 Ratio','2010')]},'Is cancellation value taking a larger sales share?',chart(ORANGE,legend=True),sort=(col('dim_date','month_number'),'Ascending'),filters=[basic('dim_date','month_number',list(range(1,12)))])
 text(p,'key','Net = gross minus cancellation postings. Driver bars reconcile the change; they do not establish causes.',32,830,1536,37,11,MUTED)
 # 02 / Market: all countries are eligible; rank on movement, not a hand-picked list.
 p=PAGES[1];page(p,'02 | Markets','Which markets explain the change?','JAN-NOV 2011 vs JAN-NOV 2010  /  all markets  /  eight largest absolute changes shown')
 card(p,'current','Net 2011 GBP','Net merchandise value | 2011',32,158,496,118,1000000,2)
 card(p,'change','Net Change GBP','Change vs 2010',552,158,496,118,1000,1)
 card(p,'ukshare','UK Gross 2011 Share','UK share of gross sales | 2011',1072,158,496,118,precision=1)
 visual(p,'market_variance','clusteredBarChart',32,305,850,514,{'Category':[col('dim_country','country_key','Market')],'Y':[m('Net Change GBP','Change vs 2010')]},'Net-value change by market | GBP',chart(GREEN,True),sort=(m('Net Change GBP'),'Descending'),filters=[measure_filter('Absolute Market Change Rank',8)])
 visual(p,'market_table','tableEx',904,305,664,514,{'Values':[col('dim_country','country_key','Market'),m('Net 2011 GBP','2011 net | GBP'),m('Net Change GBP','Change | GBP'),m('Net Comparison Growth','Change %')]},'Scale and growth | same eight markets',{'grid':props({'gridHorizontal':lit(False),'rowPadding':lit(12)}),'columnHeaders':props({'fontSize':lit(12),'fontColor':color(MUTED)}),'values':props({'fontSize':lit(12)})},sort=(m('Net Change GBP'),'Descending'),filters=[measure_filter('Absolute Market Change Rank',8)])
 text(p,'key','Hover a market for both years and invoice growth. Percentage growth is blank when the 2010 net baseline is zero.',32,830,1536,37,11,MUTED)
 # 03 / Customer value: show dependence and review priorities, not only buyer counts.
 p=PAGES[2];page(p,'03 | Customer value','How concentrated is customer value?','FIXED SNAPSHOT: 1 DEC 2011  /  Dec 2009-Nov 2011 history  /  identified buyers only')
 card(p,'topdecile','Top Decile Gross Share','Gross from top 10% of buyers',32,158,496,118,precision=1)
 card(p,'dormantvalue','Established Dormant Gross GBP','Dormant established buyers | past gross',552,158,496,118,1000000,2,ORANGE)
 card(p,'dormantbuyers','Established Dormant Buyers','Established buyers inactive >90 days',1072,158,496,118,accent=ORANGE)
 pareto=chart(legend=True);pareto['valueAxis'][0]['properties'].update({'start':lit(0),'end':lit(1)})
 visual(p,'pareto','lineChart',32,305,750,475,{'Category':[col('customer_percentile','buyer_share','Share of buyers | largest first')],'Y':[m('Cumulative Customer Gross Share','Observed gross share'),m('Equal Customer Share Reference','Equal-share reference')]},'Biggest buyers: buyer share vs gross-value share',pareto,sort=(col('customer_percentile','buyer_share'),'Ascending'))
 visual(p,'segmentvalue','clusteredBarChart',804,305,764,475,{'Category':[col('customer_segments','segment','Customer group')],'Y':[m('Snapshot Gross GBP','Historical gross value')]},'Which customer groups generated the gross value?',chart(GREEN,True),sort=(m('Snapshot Gross GBP'),'Descending'))
 text(p,'axes','CURVE  /  x: share of buyers, highest spend first   /   y: share of identified-customer gross',32,790,1536,39,12,FOREST,SOFT)
 text(p,'key','Established = at least 5 invoices. Dormant = last purchase >90 days ago. Past purchases are not forecast recoverable revenue.',32,830,1536,37,11,MUTED)
 # 04 / Repeat buying: separate monthly purchasing from the fully observed 90-day KPI.
 p=PAGES[3];page(p,'04 | Repeat buying','How consistently do buyers return?','FIXED SNAPSHOT: 1 DEC 2011  /  identified buyers  /  90-day KPI uses all eligible historical cohorts')
 card(p,'rate','Repeat 90d Rate','Bought again within 90 days',32,158,496,118,precision=1)
 card(p,'eligible','Mature 90d Customers','Buyers with fair 90-day follow-up',552,158,496,118)
 card(p,'repeat','Mature 90d Repeat Customers','Eligible buyers who bought again',1072,158,496,118)
 stops={'min':{'color':{'Literal':{'Value':"'#F2F5ED'"}},'value':{'Literal':{'Value':'0D'}}},'max':{'color':{'Literal':{'Value':"'#79B79D'"}},'value':{'Literal':{'Value':'0.5D'}}},'nullColoringStrategy':{'strategy':{'Literal':{'Value':"'noColor'"}}}}
 gradient={'solid':{'color':{'expr':{'FillRule':{'Input':{'SelectRef':{'ExpressionName':'fact_invoice_line.Purchase Retention Rate'}},'FillRule':{'linearGradient2':stops}}}}}}
 matrix={'rowHeaders':props({'fontSize':lit(13),'fontColor':color(INK)}),'columnHeaders':props({'fontSize':lit(13),'fontColor':color(MUTED)}),'values':[{'properties':{'fontSize':lit(13),'fontColorPrimary':color(INK),'fontColorSecondary':color(INK),'backColorPrimary':color(WHITE),'backColorSecondary':color(WHITE)}},{'properties':{'backColor':gradient},'selector':{'data':[{'dataViewWildcard':{'matchingOption':1}}],'metadata':'fact_invoice_line.Purchase Retention Rate'}}],'subTotals':props({'rowSubtotals':lit(False),'columnSubtotals':lit(False)}),'rowTotal':props({'show':lit(False)}),'columnTotal':props({'show':lit(False)}),'grid':props({'rowPadding':lit(6)}),'general':props({'autoSizeColumnWidth':lit(False)}),'columnWidth':[{'properties':{'value':lit(105)},'selector':{'metadata':'fact_invoice_line.Purchase Retention Rate'}}]}
 visual(p,'cohort','pivotTable',32,305,850,475,{'Rows':[col('cohort_retention','cohort_month','First purchase')],'Columns':[col('cohort_retention','month_age','Months after first purchase')],'Values':[m('Purchase Retention Rate','% bought in that month')]},'2011 cohorts | % buying 1-6 months after first purchase',matrix,filters=[basic('cohort_retention','Cohort Year',[2011]),basic('cohort_retention','month_age',list(range(1,7)))])
 retention=chart(GREEN,True,units=1);retention['labels'][0]['properties']['labelPrecision']=lit(1);retention['valueAxis'][0]['properties'].update({'start':lit(0),'end':lit(1)})
 visual(p,'cohort90','clusteredBarChart',904,305,664,475,{'Category':[col('customer_lifecycle','cohort_month','First-purchase cohort')],'Y':[m('Repeat 90d Rate','Bought again within 90 days')],'Tooltips':[m('Mature 90d Customers','Eligible buyers'),m('Mature 90d Repeat Customers','Repeat buyers')]},'90-day repeat rate | fully observed Jan-Aug 2011 cohorts',retention,sort=(col('customer_lifecycle','cohort_month'),'Ascending'),filters=[basic('customer_lifecycle','Review cohort',[1])])
 text(p,'key','GRID  /  M+1 = next calendar month. Darker = more buyers returning. Blank = not yet observable. Do not add the percentages.',32,798,1536,49,12,FOREST,SOFT)
 # 05 / Products: monetary movers are useful for assortment review; sales ranking alone misses declines.
 p=PAGES[4];page(p,'05 | Products','Which products gained or lost sales?','JAN-NOV 2011 vs JAN-NOV 2010  /  GBP change  /  select or hover a product for detail',True)
 card(p,'net','Net 2011 GBP','Net merchandise value | 2011',32,158,496,118,1000000,2)
 card(p,'change','Net Change GBP','Change vs 2010',552,158,496,118,1000,1)
 card(p,'cancel','Cancellations 2011 GBP','Cancellation postings | 2011',1072,158,496,118,1000,1,ORANGE)
 visual(p,'gains','clusteredBarChart',32,305,756,514,{'Category':[col('dim_product','Product label','Product')],'Y':[m('Net Change GBP','Net-value gain')]},'Six biggest gains | change in net value',chart(GREEN,True),sort=(m('Net Change GBP'),'Descending'),filters=[measure_filter('Product Gain Rank',6)])
 visual(p,'declines','clusteredBarChart',810,305,758,514,{'Category':[col('dim_product','Product label','Product')],'Y':[m('Net Change GBP','Net-value decline')]},'Six biggest declines | change in net value',chart(ORANGE,True),sort=(m('Net Change GBP'),'Ascending'),filters=[measure_filter('Product Decline Rank',6)])
 text(p,'key','Hover for both years, SKU and cancellation ratio. No 2010/2011 sales can reflect assortment changes; sales value is not margin.',32,830,1536,37,11,MUTED)
 # 06 / Cancellation: show value and exposure across all products, not only top sellers.
 p=PAGES[5];page(p,'06 | Cancellations','Where is cancellation value concentrated?','JAN-NOV 2011 vs JAN-NOV 2010  /  postings by their recorded date  /  GBP',True)
 card(p,'posted','Cancellations 2011 GBP','Cancellation postings | 2011',32,158,496,118,1000,1,ORANGE)
 card(p,'ratio','Cancellation 2011 Ratio','Cancellation value / gross',552,158,496,118,precision=1,accent=ORANGE)
 card(p,'change','Cancellation Change Points','Change vs 2010 | percentage points',1072,158,496,118,precision=1,accent=ORANGE)
 visual(p,'cancel_month','clusteredColumnChart',32,305,850,514,{'Category':[col('dim_date','Month')],'Y':[m('Cancellations 2011 GBP','2011'),m('Cancellations 2010 GBP','2010')]},'When was cancellation value posted? | GBP',chart(ORANGE,legend=True),sort=(col('dim_date','month_number'),'Ascending'),filters=[basic('dim_date','month_number',list(range(1,12)))])
 visual(p,'cancel_products','clusteredBarChart',904,305,664,514,{'Category':[col('dim_product','Product label','Product')],'Y':[m('Cancellations 2011 GBP','Cancellation value')]},'Products with the most cancellation value | top 6',chart(ORANGE,True,units=1),sort=(m('Cancellations 2011 GBP'),'Descending'),filters=[measure_filter('Product Cancellation Rank',6)])
 text(p,'key','Posting value / current sales is an exposure ratio, not a matched return rate. Original invoice links and reasons need investigation.',32,830,1536,37,11,MUTED)

 write(definition/'pages/pages.json',{'$schema':SCHEMA+'item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':PAGES,'activePageName':PAGES[0]})
 write(definition/'version.json',{'$schema':SCHEMA+'item/report/definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
 theme={'name':'Retail | Forest and Linen','dataColors':[GREEN,'#A2B3A0',ORANGE,'#D7AE83','#668D7D'],'background':BG,'foreground':INK,'tableAccent':GREEN,'textClasses':{'title':{'fontFace':'Segoe UI Semibold','fontSize':15,'color':INK},'label':{'fontFace':'Segoe UI','fontSize':12,'color':MUTED},'callout':{'fontFace':'Segoe UI Semibold','fontSize':38,'color':FOREST}}}
 write(root/'powerbi/theme.json',theme);write(report/'StaticResources/RegisteredResources/RevenueQualityTheme.json',theme)
 write(definition/'report.json',{'$schema':SCHEMA+'item/report/definition/report/3.1.0/schema.json','themeCollection':{'customTheme':{'name':'RevenueQualityTheme','type':'RegisteredResources','reportVersionAtImport':{'visual':'2.4.0','page':'2.0.0','report':'3.1.0'}}},'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'RevenueQualityTheme','path':'RevenueQualityTheme.json','type':'CustomTheme'}]}],'settings':{'defaultFilterActionIsDataFilter':True,'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized'}})
 return {'pages':6,'visuals':count,'native_project':str(root/'powerbi/RevenueQuality.pbip')}
if __name__=='__main__':print(json.dumps(build_report(Path(__file__).resolve().parents[1]),indent=2))
