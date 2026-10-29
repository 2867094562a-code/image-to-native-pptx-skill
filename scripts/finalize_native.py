"""Apply declared editable freeforms/gradients and normalize known generator issues."""
import argparse,json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
A='http://schemas.openxmlformats.org/drawingml/2006/main';P='http://schemas.openxmlformats.org/presentationml/2006/main';C='http://schemas.openxmlformats.org/drawingml/2006/chart';N={'a':A,'p':P,'c':C}
def sub(parent,tag,**kw):return E.SubElement(parent,'{'+A+'}'+tag,{k:str(v) for k,v in kw.items()})
def finalize(src,dst,overrides=None):
 overrides=overrides or {}
 with ZipFile(src) as z:parts={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
 for key,b in list(parts.items()):
  if not key.endswith('.xml'):continue
  d=E.fromstring(b)
  # Multiple rich-text runs can produce repeated paragraph properties. Keep the first.
  for para in d.findall('.//a:p',N):
   pp=para.findall('a:pPr',N)
   for duplicate in pp[1:]:para.remove(duplicate)
  if key.startswith('ppt/slides/'):
   for i,nv in enumerate(d.findall('.//p:cNvPr',N),1):nv.set('id',str(i))
   for sp in d.findall('.//p:sp',N):
    nv=sp.find('p:nvSpPr/p:cNvPr',N);prop=sp.find('p:spPr',N);o=overrides.get(nv.get('name',''),{}) if nv is not None else {}
    if 'commands' in o:
     for old in prop.findall('a:prstGeom',N)+prop.findall('a:custGeom',N):prop.remove(old)
     geom=E.Element('{'+A+'}custGeom')
     for tag in ['avLst','gdLst','ahLst','cxnLst']:sub(geom,tag)
     sub(geom,'rect',l='0',t='0',r='r',b='b');pl=sub(geom,'pathLst');pa=sub(pl,'path',w=100000,h=100000,fill='none' if o.get('fill')=='none' else 'norm',stroke=1 if o.get('stroke') else 0,extrusionOk=0)
     for cmd in o['commands']:
      if cmd[0]=='Z':sub(pa,'close');continue
      part=sub(pa,{'M':'moveTo','L':'lnTo','Q':'quadBezTo','C':'cubicBezTo'}[cmd[0]])
      for j in range(1,len(cmd),2):sub(part,'pt',x=round(cmd[j]*1000),y=round(cmd[j+1]*1000))
     prop.insert(1,geom)
    if 'gradient' in o:
     for old in prop.findall('a:solidFill',N)+prop.findall('a:gradFill',N):prop.remove(old)
     gr=E.Element('{'+A+'}gradFill',rotWithShape='1');gs=sub(gr,'gsLst');colors=o['gradient']['colors']
     for j,color in enumerate(colors):sub(sub(gs,'gs',pos=round(j/max(1,len(colors)-1)*100000)),'srgbClr',val=color)
     sub(gr,'lin',ang=round(o['gradient'].get('angle',0)*60000),scaled=1)
     ln=prop.find('a:ln',N);prop.insert(list(prop).index(ln) if ln is not None else len(prop),gr)
   for rp in d.xpath('//*[a:latin]',namespaces=N):
    face=rp.find('a:latin',N).get('typeface')
    # Insert East Asian/complex-script fonts in schema order, before symbol/hyperlinks.
    for tag in ['ea','cs']:
     el=rp.find('a:'+tag,N)
     if el is None:
      el=E.Element('{'+A+'}'+tag);after=rp.find('a:latin' if tag=='ea' else 'a:ea',N);rp.insert(list(rp).index(after)+1,el)
     el.set('typeface',face)
  if key.startswith('ppt/charts/'):
   plot=d.find('c:chart/c:plotArea',N)
   if plot is not None:
    valid={v.get('val') for tag in ['catAx','valAx','dateAx','serAx'] for v in plot.findall('c:'+tag+'/c:axId',N)}
    for child in plot:
     if E.QName(child).localname.endswith('Chart'):
      for axis in child.findall('c:axId',N):
       if axis.get('val') not in valid:child.remove(axis)
  parts[key]=E.tostring(d,encoding='utf-8',xml_declaration=True,standalone=True)
 dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
 with ZipFile(dst,'w',ZIP_DEFLATED) as z:
  for n,b in parts.items():z.writestr(n,b)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source');ap.add_argument('output');ap.add_argument('--overrides',type=Path);a=ap.parse_args();finalize(a.source,a.output,json.loads(a.overrides.read_text()) if a.overrides else {})
