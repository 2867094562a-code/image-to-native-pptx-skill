/* Reusable native object recipes. Return layout objects; never rasterize. Units: pixels. */
const themes={B:{ink:'0A1C59',primary:'1762FF',pale:'E0ECFF'},E:{ink:'0B3038',primary:'087D73',pale:'DFF0EA'},I:{ink:'202052',primary:'626AB8',pale:'E9E8FB'}};
const shape=(id,bbox,fill,geometry='rect')=>({id,type:'shape',bbox,fill,geometry});
const text=(id,value,bbox,size,color,bold=false)=>({id,type:'textbox',text:value,bbox,font_px:size,color,bold});
function stat(id,x,y,w,h,value,label,theme='B'){const t=themes[theme];return[shape(id+'-bg',[x,y,w,h],t.pale),text(id+'-v',value,[x+18,y+12,w-36,h*.55],44,t.primary,true),text(id+'-l',label,[x+18,y+h*.66,w-36,h*.24],18,t.ink)];}
function progress(id,x,y,w,label,value,theme='B'){const t=themes[theme];return[text(id+'-l',label,[x,y,w*.33,30],18,t.ink),shape(id+'-track',[x+w*.35,y+9,w*.5,12],t.pale),shape(id+'-value',[x+w*.35,y+9,w*.5*value,12],t.primary),text(id+'-pct',Math.round(value*100)+'%',[x+w*.87,y,w*.13,30],16,t.ink)];}
function photoPlaceholder(id,x,y,w,h){return[shape(id+'-frame',[x,y,w,h],'E5EBF3'),shape(id+'-camera',[x+w/2-17,y+h/2-22,34,23],'none'),{...shape(id+'-lens',[x+w/2-7,y+h/2-17,14,14],'none','ellipse'),stroke:'91A4BC'},text(id+'-label','IMAGE PLACEHOLDER',[x+10,y+h/2+10,w-20,25],16,'73869F')].map((o,i)=>i===1?{...o,stroke:'91A4BC'}:o);}
function timeline(id,x,y,w,labels,theme='B'){const t=themes[theme],step=w/(labels.length-1);return[{id:id+'-line',type:'line',bbox:[x,y+10,w,0],color:t.primary},...labels.flatMap((label,i)=>[shape(id+'-n'+i,[x+i*step-7,y+3,14,14],t.primary,'ellipse'),text(id+'-t'+i,label,[x+i*step-60,y+30,120,40],18,t.ink,true)])];}
module.exports={themes,stat,progress,photoPlaceholder,timeline,shape,text};
