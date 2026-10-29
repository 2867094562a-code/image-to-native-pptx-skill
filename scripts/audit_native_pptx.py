"""Audit native OOXML objects. Never treats image-backed shapes as native evidence."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from collections import Counter
import json,re,argparse,hashlib
P='http://schemas.openxmlformats.org/presentationml/2006/main';A='http://schemas.openxmlformats.org/drawingml/2006/main';R='http://schemas.openxmlformats.org/package/2006/relationships';C='http://schemas.openxmlformats.org/drawingml/2006/chart';NS={'p':P,'a':A,'c':C}
def norm(t):return re.sub(r'\s+','',t or '')
def audit(path,layouts=None):
 report={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_only_pass':False,'violations':[],'pages':[],'scope_notes':['Text coverage compares against the declared layout inventory, not independent OCR ground truth.','Overlap checks exclude designed shape/text containment. Text-frame overlaps are review findings, not automatically a visual failure.']}
 with ZipFile(path) as z:
  entries={n:z.read(n) for n in z.namelist()};media=[n for n in entries if n.startswith('ppt/media/') and not n.endswith('/')];report['ppt_media_resources']=media
  if media:report['violations'].append({'kind':'media_resources','files':media})
  report['picture_objects']=0;report['blip_references']=0;report['ole_objects']=0;external=[]
  for n,b in entries.items():
   if not(n.endswith('.xml') or n.endswith('.rels')):continue
   d=E.fromstring(b)
   pc=d.findall('.//p:pic',NS);bl=d.findall('.//a:blip',NS);ole=d.findall('.//p:oleObj',NS)
   report['picture_objects']+=len(pc);report['blip_references']+=len(bl);report['ole_objects']+=len(ole)
   if pc or bl or ole:report['violations'].append({'part':n,'p_pic':len(pc),'a_blip':len(bl),'ole':len(ole)})
   for rel in d.findall('{'+R+'}Relationship'):
    if rel.get('Type','').endswith('/image') or rel.get('Type','').endswith('/oleObject'):
     external.append(dict(part=n,target=rel.get('Target'),type=rel.get('Type'),mode=rel.get('TargetMode')))
  report['image_or_ole_relationships']=external
  if external:report['violations'].append({'kind':'image_or_ole_relationships','items':external})
  pr=E.fromstring(entries['ppt/presentation.xml']);sz=pr.find('p:sldSz',NS);W=int(sz.get('cx'));H=int(sz.get('cy'));report['canvas_emu']=[W,H]
  import posixpath
  rels=E.fromstring(entries['ppt/_rels/presentation.xml.rels']);lookup={v.get('Id'):posixpath.normpath(posixpath.join('ppt',v.get('Target'))) if not v.get('Target').startswith('/') else v.get('Target').lstrip('/') for v in rels}
  relns='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
  slides=[lookup[v.get('{'+relns+'}id')] for v in pr.find('p:sldIdLst',NS)]
  for index,n in enumerate(slides,1):
   d=E.fromstring(entries[n]);shapes=d.findall('.//p:sp',NS);count={'textboxes':0,'shapes':0,'connectors':len(d.findall('.//p:cxnSp',NS)),'tables':len(d.findall('.//a:tbl',NS)),'charts':len(d.findall('.//c:chart',NS)),'pictures':len(d.findall('.//p:pic',NS)),'freeforms':len(d.findall('.//a:custGeom',NS))}
   native_ids=Counter(v.get('id') for v in d.findall('.//p:cNvPr',NS))
   duplicate_ids=[k for k,v in native_ids.items() if v>1]
   if duplicate_ids:report['violations'].append({'part':n,'duplicate_object_ids':duplicate_ids})
   actual=[''.join(t.text or '' for t in tc.findall('.//a:t',NS)) for tc in d.findall('.//a:tc',NS)];bounds=[];text_frames=[]
   for sp in shapes:
    strings=sp.findall('.//a:t',NS);tx=''.join(t.text or '' for t in strings);count['textboxes' if tx else 'shapes']+=1
    if tx:actual.append(tx)
    nv=sp.find('p:nvSpPr/p:cNvPr',NS);name=nv.get('name','') if nv is not None else ''
    xf=sp.find('p:spPr/a:xfrm',NS)
    if xf is not None:
     off=xf.find('a:off',NS);ex=xf.find('a:ext',NS)
     if off is not None and ex is not None:
      x,y,w,h=[int(a) for a in [off.get('x'),off.get('y'),ex.get('cx'),ex.get('cy')]]
      if x<-9525 or y<-9525 or x+w>W+9525 or y+h>H+9525 or w<0 or h<0:bounds.append({'name':name,'frame_emu':[x,y,w,h]})
      if tx:text_frames.append((name,tx,[x,y,w,h]))
   missing=[];expected_count=None;uncertain=0
   if layouts:
    lp=layouts/f'slide-{index:02d}.layout.json'
    if lp.exists():
     lay=json.loads(lp.read_text());expected=[o['text'] for o in lay['objects'] if o['type']=='textbox']+[str(cell) for o in lay['objects'] if o['type']=='table' for row in o.get('values',[]) for cell in row];expected_count=len(expected);uncertain=len(lay.get('unresolved_text',[]));ac=Counter(norm(t) for t in actual)
     for t in expected:
      key=norm(t)
      if ac[key]>0:ac[key]-=1
      else:missing.append(t)
   overlaps=[]
   for i,(name,tx,b) in enumerate(text_frames):
    for name2,tx2,c in text_frames[i+1:]:
     x=max(b[0],c[0]);y=max(b[1],c[1]);inter=max(0,min(b[0]+b[2],c[0]+c[2])-x)*max(0,min(b[1]+b[3],c[1]+c[3])-y)
     ratio=inter/max(1,min(b[2]*b[3],c[2]*c[3]))
     if ratio>.35:overlaps.append({'a':tx,'b':tx2,'intersection_over_smaller_frame':round(ratio,3)})
   report['pages'].append({'page':index,'part':n,'counts':count,'expected_ocr_text_boxes':expected_count,'low_confidence_source_lines':uncertain,'missing_expected_text':missing,'out_of_bounds':bounds,'text_overlap_review':overlaps,'native_pass':count['pictures']==0})
  report['page_count']=len(slides);report['native_only_pass']=not report['violations'];report['ocr_inventory_coverage_pass']=not any(p['missing_expected_text'] for p in report['pages']);report['bounds_pass']=not any(p['out_of_bounds'] for p in report['pages'])
  report['native_chart_workbooks']=[n for n in entries if n.startswith('ppt/embeddings/') and n.endswith('.xlsx')]
 return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('pptx',type=Path);ap.add_argument('--layouts',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();report=audit(args.pptx,args.layouts);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:report[k] for k in ['native_only_pass','page_count','picture_objects','blip_references','ole_objects','ocr_inventory_coverage_pass','bounds_pass']},ensure_ascii=False));raise SystemExit(0 if report['native_only_pass'] else 1)
