"""Generate editable academic submission materials from the verified results."""
from pathlib import Path
import json, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from pptx import Presentation
from pptx.util import Inches as PI,Pt as PP
from pptx.dml.color import RGBColor as PC
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/processed/analysis.json').read_text())
CHARTS=ROOT/'docs/charts';CHARTS.mkdir(exist_ok=True,parents=True)
NAVY='#1a3d5f';BLUE='#17679a';TEAL='#487c86';GRAY='#6b7886'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#405466','xtick.color':'#607181','ytick.color':'#607181','axes.titleweight':'medium'})

hist=D['historical'];years=[r['year'] for r in hist]
fig,ax=plt.subplots(figsize=(9.6,3.35));ax.plot(years,[r['domestic']/1e6 for r in hist],marker='o',color=BLUE,linewidth=2.25,label='Domestic');ax.plot(years,[r['international']/1e6 for r in hist],marker='o',color=TEAL,linewidth=2,label='International');ax.set_ylabel('Passenger movements (millions)');ax.set_xticks(years);ax.grid(axis='y',alpha=.19);ax.legend(frameon=False,ncol=2,loc='upper left');fig.tight_layout();fig.savefig(CHARTS/'annual_traffic.png',dpi=200,bbox_inches='tight');plt.close(fig)
cs=D['clusters'];fig,ax=plt.subplots(figsize=(9.5,3.2));x=np.arange(3);ax.bar(x,[c['count'] for c in cs],color=['#aebdc9','#3c7ba9','#1d446c'],width=.55);ax.set_xticks(x,[c['name'] for c in cs]);ax.set_ylabel('Number of airports');ax.set_ylim(0,73);ax.grid(axis='y',alpha=.15)
for i,c in enumerate(cs):ax.text(i,c['count']+1.5,str(c['count']),ha='center',fontweight='medium',color=NAVY)
fig.tight_layout();fig.savefig(CHARTS/'cluster_groups.png',dpi=200,bbox_inches='tight');plt.close(fig)
reg=D['regression'];fig,ax=plt.subplots(figsize=(9.5,3.35));xx=np.arange(2);w=.30
bars=ax.bar(xx-w/2,[reg['forest']['mae']/1e6,reg['forest']['rmse']/1e6],width=w,color=BLUE,label='Random Forest');ax.bar(xx+w/2,[reg['baseline']['mae']/1e6,reg['baseline']['rmse']/1e6],width=w,color='#9caebb',label='Previous-year baseline');ax.set_xticks(xx,['MAE','RMSE']);ax.set_ylabel('Absolute error (millions of movements)');ax.legend(frameon=False);ax.grid(axis='y',alpha=.15);fig.tight_layout();fig.savefig(CHARTS/'regression_metrics.png',dpi=200,bbox_inches='tight');plt.close(fig)

# Create formal Word report from the content-verified Markdown master.
report=ROOT/'docs/PROJECT_REPORT.md';out=ROOT/'docs/AirConnect_India_Project_Report.docx'
doc=Document();section=doc.sections[0];section.top_margin=Inches(.83);section.bottom_margin=Inches(.78);section.left_margin=Inches(.92);section.right_margin=Inches(.84)
styles=doc.styles;normal=styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(11);normal.font.color.rgb=RGBColor(34,45,55);normal.paragraph_format.line_spacing=1.16;normal.paragraph_format.space_after=Pt(5)
for nm,size in [('Title',20),('Heading 1',15),('Heading 2',12.5),('Heading 3',11.5)]:
 s=styles[nm];s.font.name='Times New Roman';s.font.size=Pt(size);s.font.bold=True;s.font.color.rgb=RGBColor(26,61,95);s.paragraph_format.space_before=Pt(12);s.paragraph_format.space_after=Pt(5)

def rich(p,s):
 parts=re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)',s)
 for q in parts:
  if not q:continue
  if q.startswith('**') and q.endswith('**'):r=p.add_run(q[2:-2]);r.bold=True
  elif q.startswith('*') and q.endswith('*'):r=p.add_run(q[1:-1]);r.italic=True
  elif q.startswith('`') and q.endswith('`'):r=p.add_run(q[1:-1]);r.font.name='Consolas';r.font.size=Pt(9)
  else:p.add_run(q)

def add_chart(path,caption):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True;p.add_run().add_picture(str(path),width=Inches(6.55))
 cp=doc.add_paragraph();cp.alignment=WD_ALIGN_PARAGRAPH.CENTER;rr=cp.add_run(caption);rr.italic=True;rr.font.size=Pt(9)

lines=report.read_text().splitlines();i=0;section_number=''
while i<len(lines):
 line=lines[i].strip()
 if not line or line=='---':i+=1;continue
 if line.startswith('#'):
  level=len(line)-len(line.lstrip('#'));txt=line[level:].strip()
  if level==1:p=doc.add_paragraph(style='Title');rich(p,txt)
  elif level==2:p=doc.add_paragraph(style='Heading 1');rich(p,txt)
  else:p=doc.add_paragraph(style='Heading 2');rich(p,txt)
  if txt=='3. Dataset and preprocessing':add_chart(CHARTS/'annual_traffic.png','Figure 1. National domestic and international passenger movements, 2016–2025. Source: DGCA-derived annual dataset.')
  if txt=='5. Experimental results':add_chart(CHARTS/'cluster_groups.png','Figure 2. K-Means segmentation of 129 airport records, 2025.')
  if txt=='5.2 Regression versus baseline':add_chart(CHARTS/'regression_metrics.png','Figure 3. Held-out 2025 regression error comparison; lower is better.')
  i+=1;continue
 if line.startswith('|') and i+1<len(lines) and lines[i+1].strip().startswith('|'):
  tab=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   tab.append([cell.strip() for cell in lines[i].strip().strip('|').split('|')]);i+=1
  tab=[row for row in tab if not all(re.fullmatch(r':?-{2,}:?',x) for x in row)]
  if not tab:continue
  cols=max(map(len,tab));table=doc.add_table(rows=0,cols=cols);table.style='Table Grid';table.alignment=WD_TABLE_ALIGNMENT.CENTER
  for ri,items in enumerate(tab):
   cells=table.add_row().cells
   for j,val in enumerate(items):
    p=cells[j].paragraphs[0];rich(p,val);p.paragraph_format.space_after=Pt(1)
    for run in p.runs:run.font.size=Pt(8.6);run.bold=(ri==0 or run.bold)
  doc.add_paragraph().paragraph_format.space_after=Pt(0)
  continue
 if re.match(r'^\d+\.\s+',line) or line.startswith('- '):
  p=doc.add_paragraph(style='List Bullet');rich(p,re.sub(r'^\d+\.\s+|^-\s+','',line));i+=1;continue
 p=doc.add_paragraph();rich(p,line);i+=1

sec=doc.sections[0]
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=footer.add_run('AirConnect India  |  MDI4001 — Machine Learning for Data Science');r.font.size=Pt(9);r.font.color.rgb=RGBColor(103,118,132)
doc.save(out)
print('DOCX:',out.stat().st_size)

# PPTX: conventional academic design with clean original charts, editable text.
ppt=Presentation();ppt.slide_width=PI(13.333);ppt.slide_height=PI(7.5)
NAV=PC(25,57,87);MUT=PC(105,117,128);LIGHT=PC(236,241,245);BORDER=PC(208,217,223)

def text_box(slide,text,x,y,w,h,size=PP(19),bold=False,color=NAV,align=None):
 shape=slide.shapes.add_textbox(PI(x),PI(y),PI(w),PI(h));tf=shape.text_frame;tf.clear();tf.word_wrap=True
 p=tf.paragraphs[0];p.text=text;p.font.name='Times New Roman';p.font.size=size;p.font.bold=bold;p.font.color.rgb=color;p.space_after=PP(4)
 if align:p.alignment=align
 return shape

def slide(title,kicker='AIRCONNECT INDIA  /  MDI4001'):
 sl=ppt.slides.add_slide(ppt.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=PC(255,255,255)
 text_box(sl,kicker,.62,.33,10,.30,PP(10),True,MUT)
 text_box(sl,title,.62,.85,12,.72,PP(30),True,NAV)
 ln=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,PI(.62),PI(1.68),PI(12.05),PI(.014));ln.fill.solid();ln.fill.fore_color.rgb=BORDER;ln.line.fill.background()
 text_box(sl,'Vellore Institute of Technology  |  Machine Learning for Data Science',.62,7.03,10,.26,PP(10),False,MUT)
 text_box(sl,f'{len(ppt.slides):02d}',12.10,7.02,.5,.25,PP(10),False,MUT,PP_ALIGN.RIGHT)
 return sl

def bullets(sl,items,y=2.04,size=PP(21),step=.74):
 for i,s in enumerate(items):
  text_box(sl,'•',.83,y+i*step,.28,.50,size,False,NAV)
  text_box(sl,s,1.18,y+i*step,11.3,.62,size,False,NAV)

def chart(sl,name,x=.85,y=1.95,w=11.5):
 from PIL import Image
 image=Image.open(CHARTS/name);ratio=image.height/image.width
 sl.shapes.add_picture(str(CHARTS/name),PI(x),PI(y),width=PI(w),height=PI(w*ratio))

s=slide('AirConnect India','COURSE PROJECT  /  2026–2027')
text_box(s,'Machine Learning-Based Analysis of Indian Airport Passenger Traffic and Connectivity',.82,2.04,11.8,1.7,PP(28),False,NAV)
text_box(s,'K-Means  ·  Random Forest regression  ·  Offline research interface',.83,4.18,11.8,.7,PP(19),False,MUT)
text_box(s,'Group members: [Names / Register numbers / University emails]',.83,5.67,11.8,.5,PP(17))

s=slide('Problem and motivation')
bullets(s,['India: 74 operational facilities in 2014; 165 as of July 2026.','Infrastructure growth ≠ number of airports reporting passenger movements.','Does traffic growth appear balanced? What patterns separate airports?','Can a simple model beat a previous-year prediction?'])

s=slide('Data collection and preprocessing')
bullets(s,['DGCA-derived national passenger movements: 2016–2025.','Airport-level source rows: 614, covering 2022–2025.','Arrival + departure movements; not unique passenger counts.','Validate keys and totals; pivot airport/year; transform numeric features.'])

s=slide('National traffic patterns')
chart(s,'annual_traffic.png',.80,1.93,11.8)
text_box(s,'2016–2025 domestic passenger movements: +67.8%. A sharp decline is visible in 2020.',.97,6.37,11.4,.42,PP(15))

s=slide('Machine learning workflow')
bullets(s,['Input CSV → validation → airport-year features.','K-Means: log traffic features → standard scaling → 3 clusters.','Random Forest: lag-1 and lag-2 domestic traffic → annual target.','Chronological holdout: 2024 train, 2025 test.'])

s=slide('K-Means results')
chart(s,'cluster_groups.png',.95,1.88,10.6)
text_box(s,'129 airports  |  k = 3  |  Silhouette Score = 0.6235',1.05,6.33,10.8,.45,PP(17),True)

s=slide('Random Forest evaluation')
chart(s,'regression_metrics.png',.95,1.88,10.6)
text_box(s,'Test 2025: Random Forest MAE 451,552  |  Prior-year baseline MAE 182,476',1.05,6.33,11.0,.45,PP(16),True)

s=slide('Website demonstration')
bullets(s,['Offline HTML / CSS / JavaScript; no login, server or cloud.','Overview: aviation growth indicators and historical traffic chart.','Explorer: India map, year filter, airport search, CSV export.','ML: cluster groups, prediction comparison and method definitions.','Methodology: reproducible steps, definitions and source citations.'])

s=slide('Findings and limitations')
bullets(s,['Observed domestic and international traffic increased over the period.','K-Means distinguishes substantially different traffic groups.','Prior-year forecast outperforms this Random Forest on 2025 holdout.','Low traffic ≠ proven underutilisation; international activity ≠ route permission.'])

s=slide('Conclusion and references')
bullets(s,['Airport traffic is measurable, but capacity utilisation needs other data.','Simpler forecast models can outperform complex alternatives.','A transparent, reproducible offline interface supports evaluation.'],y=2.03,step=.72,size=PP(19))
text_box(s,'Sources: DGCA-derived India Aviation Stats (Kubicek, 2026); Ministry of Civil Aviation; airport coordinates (Himpfen); Natural Earth.',.92,5.48,11.5,.85,PP(15),False,MUT)
ppt.save(ROOT/'docs/AirConnect_India_Presentation.pptx')
print('PPTX:',(ROOT/'docs/AirConnect_India_Presentation.pptx').stat().st_size)
