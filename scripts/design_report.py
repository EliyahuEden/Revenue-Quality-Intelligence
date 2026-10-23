"""Restore the reviewed native business report; model and query logic are separate."""
from pathlib import Path
import shutil,json
def build_report(root):
 root=Path(root);template=Path(__file__).resolve().parent/'report_template';report=root/'powerbi/RevenueQuality.Report'
 for name in ['definition','StaticResources']:
  target=report/name
  if target.exists():
   assert target.resolve().is_relative_to(root.resolve());shutil.rmtree(target)
  shutil.copytree(template/name,target)
 return {'pages':6,'native_project':str(root/'powerbi/RevenueQuality.pbip')}
if __name__=='__main__':print(json.dumps(build_report(Path(__file__).resolve().parents[1])))
