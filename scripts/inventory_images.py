"""Inventory accessible reference images; discovery order is not approved page order."""
import argparse,json
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('directory',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();items=[]
for p in sorted(a.directory.rglob('*')):
 if p.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.tif','.tiff','.bmp'}:continue
 try:
  with Image.open(p) as im:w,h=im.size;items.append({'path':str(p.resolve()),'width_px':w,'height_px':h,'aspect_ratio':round(w/h,6)})
 except (OSError,ValueError) as e:items.append({'path':str(p),'error':str(e)})
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'order_status':'discovery_only_confirm_original_sequence','images':items},ensure_ascii=False,indent=2),encoding='utf8');print(len(items),'references')
