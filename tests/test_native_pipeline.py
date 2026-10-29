"""Behavioral acceptance for generated OOXML, image rejection and native splitting."""
import unittest,sys,subprocess,tempfile,json,os
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from audit_native_pptx import audit
from split_pptx import split
from finalize_native import finalize
class NativePipeline(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  os.environ['PYTHON']=sys.executable
  cls.tmp=tempfile.TemporaryDirectory();cls.base=Path(cls.tmp.name);cls.pptx=cls.base/'example.pptx';subprocess.run(['node',str(ROOT/'scripts/build_native.cjs'),str(ROOT/'examples/layout.json'),str(cls.pptx)],check=True)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_native_example_has_real_chart_table_and_data(self):
  r=audit(self.pptx);self.assertTrue(r['native_only_pass']);self.assertEqual(r['page_count'],2);self.assertEqual(sum(p['counts']['tables'] for p in r['pages']),1);self.assertEqual(sum(p['counts']['charts'] for p in r['pages']),1);self.assertEqual(len(r['native_chart_workbooks']),1)
  with ZipFile(self.pptx) as z:
   for n in r['native_chart_workbooks']:
    import io
    with ZipFile(io.BytesIO(z.read(n))) as book:self.assertIn('xl/worksheets/sheet1.xml',book.namelist())
 def test_injected_hidden_image_reference_fails(self):
  bad=self.base/'bad.pptx'
  with ZipFile(self.pptx) as z:parts={n:z.read(n) for n in z.namelist()}
  p='ppt/slides/slide1.xml';root=E.fromstring(parts[p]);sp=root.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}spPr');E.SubElement(sp,'{http://schemas.openxmlformats.org/drawingml/2006/main}blip');parts[p]=E.tostring(root)
  with ZipFile(bad,'w',ZIP_DEFLATED) as z:
   for n,b in parts.items():z.writestr(n,b)
  r=audit(bad);self.assertFalse(r['native_only_pass']);self.assertGreater(r['blip_references'],0)
 def test_split_retains_native_selected_page_and_prunes_others(self):
  out=self.base/'one.pptx';split(self.pptx,out,[2]);r=audit(out);self.assertEqual(r['page_count'],1);self.assertTrue(r['native_only_pass']);self.assertEqual(r['pages'][0]['counts']['tables'],1);self.assertEqual(r['pages'][0]['counts']['charts'],1)
  with ZipFile(out) as z:self.assertNotIn('ppt/slides/slide1.xml',z.namelist());self.assertIn(b'Editable table and chart',z.read('ppt/slides/slide2.xml'))
 def test_template_reuse_preserves_native_table_and_chart(self):
  out=self.base/'reuse.pptx';subprocess.run(['node',str(ROOT/'scripts/reuse_native.cjs'),str(self.pptx),str(out),'2'],check=True);r=audit(out);self.assertTrue(r['native_only_pass']);self.assertEqual(r['page_count'],1);self.assertEqual(r['pages'][0]['counts']['tables'],1);self.assertEqual(r['pages'][0]['counts']['charts'],1)
if __name__=='__main__':unittest.main()
