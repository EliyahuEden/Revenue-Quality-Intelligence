"""Native management report: comparison first, detail on demand."""
from pathlib import Path
import json,uuid,shutil,tempfile
SCHEMA='https://developer.microsoft.com/json-schemas/fabric/'
FOREST='#173F35';GREEN='#26745B';ORANGE='#C46635';INK='#243D35';MUTED='#65756B';BG='#F3F1E9';WHITE='#FFFFFF';SOFT='#E3EADF'
PAGES=['5b9cef77342b526099d0','d2de67539b5e5bc794d0','cad6cde6010858449260','0190a4d82893586eb525','d9623a00b21653628513']
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
def chart(ink=GREEN,labels=False,legend=False,units=1000):
 return {'dataPoint':props({'defaultColor':color(ink)}),'legend':props({'show':lit(legend),'position':lit('Top'),'fontSize':lit(12),'labelColor':color(MUTED)}),'labels':props({'show':lit(labels),'color':color(INK),'labelDisplayUnits':lit(units),'labelPrecision':lit(0),'fontSize':lit(12)}),'categoryAxis':props({'show':lit(True),'showAxisTitle':lit(False),'labelColor':color(MUTED),'fontSize':lit(12),'maxSize':lit(55)}),'valueAxis':props({'show':lit(True),'showAxisTitle':lit(False),'labelColor':color(MUTED),'fontSize':lit(11),'gridlineColor':color('#E9EDE5')})}
def build_report(root):
 root=Path(root);report=root/'powerbi/RevenueQuality.Report';definition=report/'definition'
 assert definition.resolve()==(root/'powerbi/RevenueQuality.Report/definition').resolve()
 if definition.exists():shutil.move(str(definition),str(Path(tempfile.mkdtemp(prefix='retail-pbir-'))/'definition'))
 definition.mkdir(parents=True);count=0
 def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=True),encoding='utf-8')
 def visual(p,key,typ,x,y,w,h,roles=None,title=None,objects=None,bg=WHITE,sort=None,filters=None):
  nonlocal count
  name=stable(p+key);v={'visualType':typ,'drillFilterOtherVisuals':True}
  if roles:v['query']={'queryState':{k:{'projections':val} for k,val in roles.items()}}
  if sort:v['query']['sortDefinition']={'sort':[{'field':sort[0]['field'],'direction':sort[1]}],'isDefaultSort':False}
  v['visualContainerObjects']={'background':props({'show':lit(True),'color':color(bg),'transparency':lit(0)}),'border':props({'show':lit(False),'radius':lit(12)}),'visualHeader':props({'show':lit(False)})}
  if title:v['visualContainerObjects']['title']=props({'show':lit(True),'text':lit(title),'fontColor':color(INK),'fontSize':lit(15),'fontFamily':lit('Segoe UI Semibold')})
  if objects:v['objects']=objects
  if objects and 'legend' in objects and objects['legend'][0]['properties'].get('show')==lit(True) and roles and 'Y' in roles:
   v['objects']['dataPoint']=[{'properties':{'fill':color(ORANGE if 'cancel' in key else GREEN)},'selector':{'metadata':roles['Y'][0]['queryRef']}},{'properties':{'fill':color('#A2B3A0')},'selector':{'metadata':roles['Y'][1]['queryRef']}}]
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
  text(p,'page',name[:2]+' / 05',1460,858,110,36,12,MUTED)
 # 01: Four comparative KPIs and four charts. No explanatory paragraphs.
 p=PAGES[0];page(p,'01 | Overview','Business performance','JAN-NOV 2011  /  compared with Jan-Nov 2010  /  GBP',True)
 for i,(key,n,label,units,prec,change,bench,accent) in enumerate([
  ('net','Net 2011 GBP','Net merchandise value',1000000,2,'Net Comparison Growth','vs 2010',GREEN),
  ('orders','Invoices 2011','Sales invoices',1000,1,'Invoice Comparison Growth','vs 2010',ORANGE),
  ('basket','Basket 2011 GBP','Average gross / invoice',1,0,'Basket Comparison Growth','vs 2010',GREEN),
  ('cancel','Cancellation 2011 Ratio','Cancellation value / gross',1,1,'Cancellation Change Points','vs 2010',ORANGE)]):
  x=32+i*392
  text(p,key+'panel','',x,158,368,134,1,bg=WHITE)
  card(p,key,n,label,x+8,161,352,82,units,prec,ORANGE if key=='cancel' else FOREST)
  small(p,key+'change',change,bench,x+12,235,120,accent)
 visual(p,'sales_trend','lineChart',32,304,970,265,{'Category':[col('dim_date','Month')],'Y':[m('Net 2011 GBP','2011'),m('Net 2010 GBP','2010')]},'Net sales | monthly comparison',chart(legend=True),sort=(col('dim_date','month_number'),'Ascending'),filters=[basic('dim_date','month_number',list(range(1,12)))])
 visual(p,'cancel_trend','clusteredColumnChart',1024,304,544,265,{'Category':[col('dim_date','Month')],'Y':[m('Cancellation 2011 Ratio','2011'),m('Cancellation 2010 Ratio','2010')]},'Cancellation value / gross',chart(ORANGE,legend=True),sort=(col('dim_date','month_number'),'Ascending'),filters=[basic('dim_date','month_number',list(range(1,12)))])
 visual(p,'market_change','clusteredBarChart',32,590,752,246,{'Category':[col('dim_country','country_key','Market')],'Y':[m('Net Change GBP','Change vs 2010')]},'Five major markets | net sales change',chart(GREEN,True),sort=(m('Net Change GBP'),'Descending'),filters=[basic('dim_country','country_key',['United Kingdom','EIRE','Netherlands','Germany','France'])])
 visual(p,'top_products','clusteredBarChart',806,590,762,246,{'Category':[col('dim_product','Product label','Product')],'Y':[m('Net 2011 GBP','Net value')]},'Top 5 products | net sales',chart(GREEN,True),sort=(m('Net 2011 GBP'),'Descending'),filters=[rank(5)])
 # 02: Keep the cohort analysis readable by displaying six months for 2011 groups.
 p=PAGES[1];page(p,'02 | Customers','Customer return','SNAPSHOT  /  1 Dec 2011  /  identified buyers only')
 card(p,'rate','Repeat 90d Rate','Bought again within 90 days',32,158,496,118,precision=1)
 card(p,'mature','Mature 90d Customers','Eligible buyers | 90-day follow-up',552,158,496,118)
 card(p,'buyers','Snapshot Customers','Identified buyers | full history',1072,158,496,118)
 stops={'min':{'color':{'Literal':{'Value':"'#F2F5ED'"}},'value':{'Literal':{'Value':'0D'}}},'max':{'color':{'Literal':{'Value':"'#79B79D'"}},'value':{'Literal':{'Value':'0.5D'}}},'nullColoringStrategy':{'strategy':{'Literal':{'Value':"'noColor'"}}}}
 gradient={'solid':{'color':{'expr':{'FillRule':{'Input':{'SelectRef':{'ExpressionName':'fact_invoice_line.Purchase Retention Rate'}},'FillRule':{'linearGradient2':stops}}}}}}
 matrix={'rowHeaders':props({'fontSize':lit(13),'fontColor':color(INK)}),'columnHeaders':props({'fontSize':lit(13),'fontColor':color(MUTED)}),'values':[{'properties':{'fontSize':lit(13),'fontColorPrimary':color(INK),'fontColorSecondary':color(INK),'backColorPrimary':color(WHITE),'backColorSecondary':color(WHITE)}},{'properties':{'backColor':gradient},'selector':{'data':[{'dataViewWildcard':{'matchingOption':1}}],'metadata':'fact_invoice_line.Purchase Retention Rate'}}],'subTotals':props({'rowSubtotals':lit(False),'columnSubtotals':lit(False)}),'rowTotal':props({'show':lit(False)}),'columnTotal':props({'show':lit(False)}),'grid':props({'rowPadding':lit(8)})}
 visual(p,'cohort','pivotTable',32,300,850,485,{'Rows':[col('cohort_retention','cohort_month','First purchase')],'Columns':[col('cohort_retention','month_age','Months later')],'Values':[m('Purchase Retention Rate')]},'2011 customer groups | months after first purchase',matrix,filters=[basic('cohort_retention','Cohort Year',[2011]),basic('cohort_retention','month_age',list(range(1,7)))])
 visual(p,'segments','clusteredBarChart',904,300,664,485,{'Category':[col('customer_segments','segment','Group')],'Y':[m('Snapshot Customers','Buyers')]},'Customer groups | full-history snapshot',chart(GREEN,True,units=1),sort=(m('Snapshot Customers'),'Descending'))
 text(p,'key','GRID KEY  /  Darker = more customers bought again   /   Blank = not yet observable',32,805,1536,43,13,FOREST,SOFT)
 # 03: Readable product ranking and cancellation exposure.
 p=PAGES[2];page(p,'03 | Products','Product performance','JAN-NOV 2011  /  select a product bar to investigate  /  GBP',True)
 card(p,'net','Net 2011 GBP','Net merchandise value',32,158,496,118,1000000,2)
 card(p,'gross','Gross 2011 GBP','Gross merchandise sales',552,158,496,118,1000000,2)
 card(p,'cancel','Cancellations 2011 GBP','Cancellation postings',1072,158,496,118,1000,1,ORANGE)
 visual(p,'rank','clusteredBarChart',32,300,850,530,{'Category':[col('dim_product','Product label','Product')],'Y':[m('Net 2011 GBP','Net value')]},'Top 10 products | net sales',chart(GREEN,True),sort=(m('Net 2011 GBP'),'Descending'),filters=[rank(10)])
 visual(p,'cancellation_products','clusteredBarChart',904,300,664,530,{'Category':[col('dim_product','Product label','Product')],'Y':[m('Cancellations 2011 GBP','Cancellation value')]},'Cancellation value | top 10 selling products',chart(ORANGE,True,units=1),sort=(m('Cancellations 2011 GBP'),'Descending'),filters=[rank(10)])
 # 04: Reconciliation and exposure, stripped of audit prose.
 p=PAGES[3];page(p,'04 | Sales quality','Sales quality','JAN-NOV 2011  /  cancellation postings reduce merchandise value  /  GBP',True)
 card(p,'gross','Gross 2011 GBP','Gross merchandise sales',32,158,450,118,1000000,2)
 text(p,'minus','−',491,190,51,66,28,ORANGE)
 card(p,'cancel','Cancellations 2011 GBP','Cancellation postings',568,158,450,118,1000,1,ORANGE)
 text(p,'equals','=',1032,190,51,66,28,FOREST)
 card(p,'net','Net 2011 GBP','Net merchandise value',1118,158,450,118,1000000,2)
 visual(p,'canceltrend','clusteredColumnChart',32,300,970,530,{'Category':[col('dim_date','Month')],'Y':[m('Cancellations 2011 GBP','2011'),m('Cancellations 2010 GBP','2010')]},'Cancellation postings | monthly comparison',chart(ORANGE,legend=True),sort=(col('dim_date','month_number'),'Ascending'),filters=[basic('dim_date','month_number',list(range(1,12)))])
 card(p,'unknown','Anonymous 2011 Share','Gross sales without a customer ID',1024,300,544,155,precision=1,accent=ORANGE)
 card(p,'dedup','Duplicate 2011 GBP','Net value affected by duplicate policy',1024,475,544,155,1000,1,ORANGE)
 text(p,'audit','INVESTIGATE\nCustomer capture\nCancellation reasons\nRepeated source records',1040,656,512,174,17,FOREST,SOFT,True)
 # 05: Clear action queue, not a page of paragraphs.
 p=PAGES[4];page(p,'05 | Priorities','What should managers do next?','ACTION QUEUE  /  based on observed patterns  /  proposed actions, not achieved outcomes')
 actions=[('01','Sales volume','Invoice Comparison Growth','Sales invoices vs 2010','Review lost and dormant accounts','Commercial / CRM',ORANGE),('02','Cancellations','Cancellation Change Points','Cancellation ratio vs 2010','Investigate reasons and invoice links','Finance / Operations',ORANGE),('03','Customer identity','Anonymous 2011 Share','Gross sales without a customer ID','Improve customer capture at checkout','Data / CRM',FOREST)]
 for i,(number,title,n,label,action,owner,accent) in enumerate(actions):
  y=165+i*218
  text(p,number+'bg','',32,y,1536,192,1,bg=WHITE)
  text(p,number+'n',number,52,y+17,82,66,30,accent,WHITE,True)
  text(p,number+'title',title,149,y+17,560,55,23,FOREST,WHITE,True)
  text(p,number+'action',action,149,y+78,800,62,20,INK,WHITE)
  text(p,number+'owner',owner,149,y+143,800,42,13,MUTED,WHITE)
  card(p,number+'metric',n,label,1032,y+25,500,130,precision=1,accent=accent)
 write(definition/'pages/pages.json',{'$schema':SCHEMA+'item/report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':PAGES,'activePageName':PAGES[0]})
 write(definition/'version.json',{'$schema':SCHEMA+'item/report/definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
 theme={'name':'Retail | Forest and Linen','dataColors':[GREEN,'#A2B3A0',ORANGE,'#D7AE83','#668D7D'],'background':BG,'foreground':INK,'tableAccent':GREEN,'textClasses':{'title':{'fontFace':'Segoe UI Semibold','fontSize':15,'color':INK},'label':{'fontFace':'Segoe UI','fontSize':12,'color':MUTED},'callout':{'fontFace':'Segoe UI Semibold','fontSize':38,'color':FOREST}}}
 write(root/'powerbi/theme.json',theme);write(report/'StaticResources/RegisteredResources/RevenueQualityTheme.json',theme)
 write(definition/'report.json',{'$schema':SCHEMA+'item/report/definition/report/3.1.0/schema.json','themeCollection':{'customTheme':{'name':'RevenueQualityTheme','type':'RegisteredResources','reportVersionAtImport':{'visual':'2.4.0','page':'2.0.0','report':'3.1.0'}}},'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'RevenueQualityTheme','path':'RevenueQualityTheme.json','type':'CustomTheme'}]}],'settings':{'defaultFilterActionIsDataFilter':True,'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized'}})
 return {'pages':5,'visuals':count,'native_project':str(root/'powerbi/RevenueQuality.pbip')}
if __name__=='__main__':print(json.dumps(build_report(Path(__file__).resolve().parents[1]),indent=2))
