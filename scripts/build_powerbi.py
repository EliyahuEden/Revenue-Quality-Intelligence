"""Author native Power BI project files, with explicit import partitions and PBIR visuals."""
from pathlib import Path
import sys,json,re,uuid
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from pipeline import connect
P=R/'powerbi';SM=P/'RevenueQuality.SemanticModel';RP=P/'RevenueQuality.Report'
for d in [SM,RP/'definition/pages',RP/'StaticResources/RegisteredResources']:d.mkdir(parents=True,exist_ok=True)
def write(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,ensure_ascii=True),encoding='utf-8')
schema='https://developer.microsoft.com/json-schemas/fabric/'
write(P/'RevenueQuality.pbip',{'$schema':schema+'pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'RevenueQuality.Report'}}],'settings':{'enableAutoRecovery':True}})
write(RP/'definition.pbir',{'$schema':schema+'item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../RevenueQuality.SemanticModel'}}})
write(SM/'definition.pbism',{'$schema':schema+'item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.0','settings':{}})
c=connect();tables=[]
names=['dim_date','dim_customer','dim_product','dim_country','fact_invoice_line','fact_order','customer_lifecycle','customer_segments','cohort_retention']
def mtype(t):
 if t=='DATE':return 'type date'
 if t.startswith('TIMESTAMP'):return 'type datetime'
 if t=='BOOLEAN':return 'type logical'
 if 'INT' in t:return 'Int64.Type'
 if 'DECIMAL' in t or t in ('DOUBLE','FLOAT'):return 'type number'
 return 'type text'
def dtype(t):
 if t=='DATE' or t.startswith('TIMESTAMP'):return 'dateTime'
 if t=='BOOLEAN':return 'boolean'
 if 'INT' in t:return 'int64'
 if 'DECIMAL' in t or t in ('DOUBLE','FLOAT'):return 'double'
 return 'string'
for name in names:
 cols=c.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='mart' AND table_name=? ORDER BY ordinal_position",[name]).fetchall()
 fields=[]
 for col,typ in cols:
  field={'name':col,'dataType':dtype(typ),'sourceColumn':col,'summarizeBy':'none','lineageTag':str(uuid.uuid5(uuid.NAMESPACE_URL,name+'.'+col))}
  if typ=='DATE':field['formatString']='MMM yyyy' if col in ['month_start','cohort_month','activity_month'] else 'dd MMM yyyy'
  if name=='dim_date' and col=='date_key':field['isKey']=True
  if name=='fact_invoice_line' and col in ['customer_key','date_key','country_key','product_key','amount_pence','quantity','unit_price']:field['isHidden']=True
  fields.append(field)
 types=',\n'.join('        {"'+col+'", '+mtype(typ)+'}' for col,typ in cols)
 m='let\n    Source = Csv.Document(File.Contents(DataFolder & "\\'+name+'.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n    Typed = Table.TransformColumnTypes(Headers, {\n'+types+'\n    }, "en-GB")\nin\n    Typed'
 table={'name':name,'columns':fields,'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':m.splitlines()}}],
        'lineageTag':str(uuid.uuid5(uuid.NAMESPACE_URL,name))}
 if name=='dim_date':table['dataCategory']='Time'
 if name=='fact_order':table['isHidden']=True
 tables.append(table)
text=(P/'dax_measures/measures.dax').read_text(encoding='utf-8');text=re.sub(r'(?m)^//.*\n?','',text)
matches=list(re.finditer(r'(?m)^(?!VAR\b)([A-Za-z][^\n=]*?)\s*=\s*',text));measures=[]
for i,m in enumerate(matches):
 name=m.group(1).strip();expression=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)].strip()
 fmt='0.0%' if any(x in name for x in ['Ratio','Share','Rate','Growth']) else '£#,0.00;(£#,0.00)' if 'GBP' in name else '#,0'
 measure={'name':name,'expression':expression.splitlines(),'formatString':fmt,'displayFolder':'Financial performance' if any(x in name for x in ['GBP','Invoices','Ratio','Share']) else 'Customer continuity'}
 if 'Title' in name:measure.pop('formatString')
 measures.append(measure)
assert len(measures)==25 and all(not m['name'].startswith('VAR ') and m['expression'] for m in measures), 'Invalid DAX source parsing'
tables[names.index('fact_invoice_line')]['measures']=measures
relationships=[]
for fact in ['fact_invoice_line','fact_order']:
 for dim,col in [('dim_date','date_key'),('dim_customer','customer_key'),('dim_country','country_key')]:
  relationships.append({'name':fact+'_'+dim,'fromTable':fact,'fromColumn':col,'toTable':dim,'toColumn':col,'fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection'})
relationships.append({'name':'line_product','fromTable':'fact_invoice_line','fromColumn':'product_key','toTable':'dim_product','toColumn':'product_key','crossFilteringBehavior':'oneDirection','fromCardinality':'many','toCardinality':'one'})
# Snapshot tables deliberately disconnected: their own slicers avoid ambiguous temporal scope.
model={'name':'RevenueQuality','compatibilityLevel':1567,'model':{'culture':'en-GB','sourceQueryCulture':'en-GB','defaultPowerBIDataSourceVersion':'powerBI_V3',
 'discourageImplicitMeasures':True,'tables':tables,'relationships':relationships,
 'expressions':[{'name':'DataFolder','kind':'m','expression':'"'+str(R/'data/exports')+'" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'}],
 'annotations':[{'name':'PBI_ProTooling','value':'["DevMode"]'}]}}
write(SM/'model.bim',model)

from design_report import build_report
stats=build_report(R)
c.close()
print(json.dumps({'tables':len(tables),'measures':len(measures),'relationships':len(relationships),**stats},indent=2))
