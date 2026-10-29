"""Real Microsoft PowerPoint round-trip + PNG export. Windows with Office required."""
import argparse,json,platform,hashlib
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def inventory(path):
 with ZipFile(path) as z:
  docs=[E.fromstring(z.read(n)) for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
 return {'slides':len(docs),'text':sorted(''.join(x.itertext()) for d in docs for x in d.findall('.//a:t',NS)),'shapes':sum(len(d.findall('.//p:sp',NS)) for d in docs),'tables':sum(len(d.findall('.//a:tbl',NS)) for d in docs),'charts':sum(len(d.findall('.//c:chart',NS)) for d in docs)}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--renders',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
 if platform.system()!='Windows':raise SystemExit('Requires Windows Microsoft PowerPoint; no Office verification was performed.')
 import pythoncom,win32com.client
 pythoncom.CoInitialize();app=None;pres=None;report={'office_verified':False,'platform':platform.platform(),'source':str(a.source),'output':str(a.output)}
 try:
  a.output.parent.mkdir(parents=True,exist_ok=True);a.renders.mkdir(parents=True,exist_ok=True);before=inventory(a.source);app=win32com.client.DispatchEx('PowerPoint.Application');app.Visible=1;pres=app.Presentations.Open(str(a.source.resolve()),ReadOnly=False,Untitled=False,WithWindow=True)
  # Rewrite one text range with identical content to exercise an actual native edit.
  edited=False
  for slide in pres.Slides:
   for shape in slide.Shapes:
    if shape.HasTextFrame and shape.TextFrame.HasText:
     rg=shape.TextFrame.TextRange.Characters(1,1);value=rg.Text;rg.Text=value;edited=True;break
   if edited:break
  pres.SaveAs(str(a.output.resolve()),24);pres.Close();pres=None
  after=inventory(a.output)
  if before!=after:raise RuntimeError('Office round-trip changed native content inventory; inspect before delivery')
  pres=app.Presentations.Open(str(a.output.resolve()),ReadOnly=True,Untitled=False,WithWindow=True)
  for i,slide in enumerate(pres.Slides,1):slide.Export(str((a.renders/f'slide-{i:02d}.png').resolve()),'PNG',1280,720)
  report.update(office_verified=True,text_edit_test=edited,reopened=True,page_count=pres.Slides.Count,office_version=app.Version,sha256=hashlib.sha256(a.output.read_bytes()).hexdigest())
 finally:
  if pres is not None:pres.Close()
  if app is not None:app.Quit()
  pythoncom.CoUninitialize();a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2),encoding='utf8')
if __name__=='__main__':main()
