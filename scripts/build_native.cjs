/* Measured pixel layout -> native editable PowerPoint. No image API is exposed. */
const fs=require('fs'),path=require('path'),cp=require('child_process'),PptxGenJS=require('pptxgenjs');
async function build(input,output){
 const spec=JSON.parse(fs.readFileSync(input,'utf8')), p=new PptxGenJS(),overrides={};
 const W=spec.width_px,H=spec.height_px;if(!(W>0&&H>0))throw Error('Positive canvas dimensions required');
 p.defineLayout({name:'MEASURED',width:W/96,height:H/96});p.layout='MEASURED';p.title=spec.title||'Native reconstruction';p.author='image-to-native-pptx';p.lang=spec.lang||'en-US';p.theme={headFontFace:spec.font||'Arial',bodyFontFace:spec.font||'Arial',lang:p.lang};
 const box=b=>({x:b[0]/96,y:b[1]/96,w:b[2]/96,h:b[3]/96});
 for(const [page,specSlide] of spec.slides.entries()){
  const s=p.addSlide();s.background={color:specSlide.background||'FFFFFF'};
  for(const [i,o] of specSlide.objects.entries()){
   const id=`p${page+1}-${o.id||i+1}`,b=o.bbox;if(!b||b.length!==4||b.some(v=>!Number.isFinite(v))||b[2]<0||b[3]<0)throw Error(`Invalid bbox ${id}`);
   const base={...box(b),objectName:id},color=o.color||'172342';
   if(o.type==='textbox')s.addText(o.text,{...base,fontFace:o.font||spec.font||'Arial',fontSize:(o.font_px||24)*.75,color,bold:!!o.bold,margin:0,align:o.align||'left',valign:o.valign||'mid',wrap:o.wrap!==false,breakLine:false,paraSpaceAfter:0});
   else if(o.type==='shape'||o.type==='freeform'){
    const fill=typeof o.fill==='object'?o.fill.colors[0]:o.fill;
    s.addShape(o.type==='freeform'?'rect':o.geometry||'rect',{...base,fill:{color:fill&&fill!=='none'?fill:'FFFFFF',transparency:fill==='none'?100:0},line:{color:o.stroke||'FFFFFF',transparency:o.stroke?0:100,width:(o.stroke_px||1)*.75}});
    if(o.type==='freeform'||typeof o.fill==='object')overrides[id]={...(o.commands?{commands:o.commands,fill:o.fill,stroke:o.stroke}:{}),...(typeof o.fill==='object'?{gradient:o.fill}:{})};
   }else if(o.type==='line')s.addShape('line',{...base,flipH:!!o.flipH,flipV:!!o.flipV,line:{color,width:(o.stroke_px||2)*.75,...(o.arrow?{endArrowType:'triangle'}:{})}});
   else if(o.type==='table')s.addTable(o.values.map((row,j)=>row.map(t=>({text:String(t),options:{fill:j?(o.body_fill||'FFFFFF'):(o.header_fill||'E5EDF8'),color,fontFace:o.font||spec.font||'Arial',margin:5}}))),{...base,fontSize:(o.font_px||20)*.75,border:{color:o.stroke||'BECDE3',pt:.5},rowH:b[3]/o.values.length/96,colW:(o.col_px||o.values[0].map(()=>b[2]/o.values[0].length)).map(x=>x/96),autoPage:false});
   else if(o.type==='chart'){
    const types={bar:p.ChartType.bar,line:p.ChartType.line,donut:p.ChartType.doughnut,radar:p.ChartType.radar};if(!types[o.chart_type])throw Error('Unsupported chart type');
    s.addChart(types[o.chart_type],o.series,{...base,showLegend:o.legend!==false,showTitle:false,chartColors:o.colors||['1762FF','6DAAFF','0A2A54'],showValue:!!o.labels,showPercent:o.chart_type==='donut'&&!!o.labels,dataLabelFormatCode:o.chart_type==='donut'?'0%':'0.#',catAxisLabelFontFace:spec.font||'Arial',valAxisLabelFontFace:spec.font||'Arial',showShadow:false,...o.options});
   }else throw Error(`Unsupported object ${o.type}; raster/image objects are forbidden`);
  }
 }
 fs.mkdirSync(path.dirname(path.resolve(output)),{recursive:true});const raw=output+'.draft.pptx',ov=output+'.overrides.json';await p.writeFile({fileName:raw});fs.writeFileSync(ov,JSON.stringify(overrides));
 const result=cp.spawnSync(process.env.PYTHON||'python3',[path.join(__dirname,'finalize_native.py'),raw,output,'--overrides',ov],{stdio:'inherit'});if(result.status!==0)throw Error('Native finalization failed');fs.unlinkSync(raw);fs.unlinkSync(ov);console.log(output);
}
if(require.main===module){if(process.argv.length<4){console.error('node scripts/build_native.cjs layout.json output.pptx');process.exit(2);}build(process.argv[2],process.argv[3]).catch(e=>{console.error(e.message);process.exit(1)});}module.exports={build};
