"""Extract slide sequences without redrawing native objects; keep only reachable parts."""
import argparse, json, posixpath, re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as E
P='http://schemas.openxmlformats.org/presentationml/2006/main';R='http://schemas.openxmlformats.org/officeDocument/2006/relationships';PKG='http://schemas.openxmlformats.org/package/2006/relationships'
def xml(b):return E.fromstring(b)
def data(e):return E.tostring(e,encoding='utf-8',xml_declaration=True)
def relpart(part):return posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels') if part else '_rels/.rels'
def resolve(part,target):return posixpath.normpath(posixpath.join(posixpath.dirname(part),target)) if not target.startswith('/') else target.lstrip('/')
def sequence(spec):
 out=[]
 for item in spec.split(','):
  ends=item.strip().split('-');out.extend(range(int(ends[0]),int(ends[-1])+1))
 if len(out)!=len(set(out)):raise ValueError('Duplicate slide numbers')
 return out
def split(src,dst,numbers):
 with ZipFile(src) as z:parts={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
 pres=xml(parts['ppt/presentation.xml']);rels=xml(parts['ppt/_rels/presentation.xml.rels']);lst=pres.find('{'+P+'}sldIdLst');ids=list(lst)
 if not numbers or min(numbers)<1 or max(numbers)>len(ids):raise ValueError('Slide number outside source sequence')
 selected=[ids[i-1] for i in numbers];keepids={v.get('{'+R+'}id') for v in selected}
 for el in list(lst):lst.remove(el)
 for el in selected:lst.append(el)
 # Custom shows and sections refer to the original sequence; omit stale navigational metadata.
 for tag in ['custShowLst','sectionLst']:
  el=pres.find('{'+P+'}'+tag)
  if el is not None:pres.remove(el)
 ext=pres.find('{'+P+'}extLst')
 if ext is not None:pres.remove(ext)
 for r in list(rels):
  if r.get('Type','').endswith('/slide') and r.get('Id') not in keepids:rels.remove(r)
 parts['ppt/presentation.xml']=data(pres);parts['ppt/_rels/presentation.xml.rels']=data(rels)
 # Package thumbnail is not a slide image; discard it so every delivered archive is bitmap-free.
 rootrels=xml(parts['_rels/.rels'])
 for r in list(rootrels):
  if r.get('Type','').endswith('/thumbnail'):rootrels.remove(r)
 parts['_rels/.rels']=data(rootrels)
 kept=set();pending=['']
 while pending:
  part=pending.pop()
  if part in kept:continue
  kept.add(part)
  rp=relpart(part)
  if part and part not in parts:raise ValueError('Missing package part: '+part)
  if rp not in parts:continue
  kept.add(rp)
  for r in xml(parts[rp]):
   if r.get('TargetMode')=='External':continue
   target=resolve(part,r.get('Target'))
   if target.startswith('../'):raise ValueError('Unsafe package target')
   if target not in kept:pending.append(target)
 ct=xml(parts['[Content_Types].xml'])
 for e in list(ct):
  if e.tag.endswith('Override') and e.get('PartName','').lstrip('/') not in kept:ct.remove(e)
 parts['[Content_Types].xml']=data(ct);kept.add('[Content_Types].xml')
 # PowerPoint's document summary is advisory, but update its slide count.
 if 'docProps/app.xml' in kept:
  a=xml(parts['docProps/app.xml']);v=a.find('{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Slides')
  if v is not None:v.text=str(len(numbers))
  parts['docProps/app.xml']=data(a)
 dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
 with ZipFile(dst,'w',ZIP_DEFLATED) as z:
  for n in sorted(kept):
   if n:z.writestr(n,parts[n])
 return {'output':str(dst),'slides':numbers,'slide_count':len(numbers),'parts':len(kept)-1}
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--slides',required=True,help='1-based sequence, e.g. 1-4,13-24');a=ap.parse_args();print(json.dumps(split(a.source,a.output,sequence(a.slides))))
