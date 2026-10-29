"""Generate side-by-side review sheets; no similarity score or PPTX mutation."""
import argparse
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('references',type=Path);ap.add_argument('renders',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
for ref in sorted(a.references.glob('slide-*.png')):
 render=a.renders/ref.name
 if not render.exists():raise SystemExit('Missing rendered page: '+str(render))
 out=Image.new('RGB',(1600,490),'#e6eaf0');d=ImageDraw.Draw(out);d.text((10,5),'REFERENCE | '+ref.name,fill='black');d.text((810,5),'OFFICE RENDER | '+ref.name,fill='black')
 for i,p in enumerate([ref,render]):
  with Image.open(p) as im:im=ImageOps.contain(im.convert('RGB'),(790,445));out.paste(im,(i*800+(790-im.width)//2,30+(445-im.height)//2))
 out.save(a.output/ref.name)
