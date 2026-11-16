"""Native OOXML fallback for an unavailable Artifact Session runtime.

Uses the project's existing PPTX package for masters/themes, writes two editable
slides and a native table. No python-pptx. Preview renderer reads final slide XML
(layout previews, not a claim of PowerPoint/LibreOffice rendering).
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as E
import re, sys, posixpath

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'presentation'/'second'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PK='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
E.register_namespace('p',P);E.register_namespace('a',A);E.register_namespace('r',R)
def el(parent,name,attrs=None):return E.SubElement(parent,name,attrs or {})
def q(ns,name):return '{'+ns+'}'+name
def x(v):return str(round(v*9525))
def xml(e):
 if e.tag.startswith('{'+CT+'}'):E.register_namespace('',CT)
 elif e.tag.startswith('{'+PK+'}'):E.register_namespace('',PK)
 return E.tostring(e,encoding='utf-8',xml_declaration=True)
def fill(parent,color):el(el(parent,q(A,'solidFill')),q(A,'srgbClr'),{'val':color})
def xfrm(parent,px,py,w,h,tag='xfrm'):
 n=el(parent,q(A,tag));el(n,q(A,'off'),{'x':x(px),'y':x(py)});el(n,q(A,'ext'),{'cx':x(w),'cy':x(h)})
 return n
def paragraph(parent,text,size,color='E7F0F5',bold=False):
 p=el(parent,q(A,'p'));props=el(p,q(A,'pPr'),{'algn':'l'})
 el(el(props,q(A,'lnSpc')),q(A,'spcPct'),{'val':'115000'})
 r=el(p,q(A,'r'));rp=el(r,q(A,'rPr'),{'lang':'ko-KR','sz':str(round(size*75)),'b':'1' if bold else '0'})
 fill(rp,color)
 for name in ('latin','ea','cs'):el(rp,q(A,name),{'typeface':'맑은 고딕'})
 el(r,q(A,'t')).text=text
 el(p,q(A,'endParaRPr'),{'lang':'ko-KR','sz':str(round(size*75))})
 return p
def text(tree,id,px,py,w,h,content,size=26,color='E7F0F5',bold=False):
 sp=el(tree,q(P,'sp'));nv=el(sp,q(P,'nvSpPr'))
 el(nv,q(P,'cNvPr'),{'id':str(id),'name':'Text '+str(id)})
 el(nv,q(P,'cNvSpPr'),{'txBox':'1'});el(nv,q(P,'nvPr'))
 pr=el(sp,q(P,'spPr'));xfrm(pr,px,py,w,h)
 el(el(pr,q(A,'prstGeom'),{'prst':'rect'}),q(A,'avLst'));el(pr,q(A,'noFill'))
 el(el(pr,q(A,'ln')),q(A,'noFill'))
 body=el(sp,q(P,'txBody'));el(body,q(A,'bodyPr'),{'wrap':'square','lIns':'0','rIns':'0','tIns':'0','bIns':'0','anchor':'t'})
 el(body,q(A,'lstStyle'))
 for line in content.split('\n'):paragraph(body,line,size,color,bold)
def slide():
 root=E.Element(q(P,'sld'));cs=el(root,q(P,'cSld'))
 bg=el(cs,q(P,'bg'));pr=el(bg,q(P,'bgPr'));fill(pr,'0D1521');el(pr,q(A,'effectLst'))
 tree=el(cs,q(P,'spTree'));nv=el(tree,q(P,'nvGrpSpPr'));el(nv,q(P,'cNvPr'),{'id':'1','name':''});el(nv,q(P,'cNvGrpSpPr'));el(nv,q(P,'nvPr'))
 gp=el(tree,q(P,'grpSpPr'));xf=el(gp,q(A,'xfrm'))
 for name,attrs in [('off',{'x':'0','y':'0'}),('ext',{'cx':'0','cy':'0'}),('chOff',{'x':'0','y':'0'}),('chExt',{'cx':'0','cy':'0'})]:el(xf,q(A,name),attrs)
 cm=el(root,q(P,'clrMapOvr'));el(cm,q(A,'masterClrMapping'))
 return root,tree
def picture(tree,id,px,py,w,h):
 pic=el(tree,q(P,'pic'));nv=el(pic,q(P,'nvPicPr'));el(nv,q(P,'cNvPr'),{'id':str(id),'name':'실제 게임 렌더러 캡처'})
 el(el(nv,q(P,'cNvPicPr')),q(A,'picLocks'),{'noChangeAspect':'1'});el(nv,q(P,'nvPr'))
 b=el(pic,q(P,'blipFill'));el(b,q(A,'blip'),{q(R,'embed'):'rScreenshot'});el(el(b,q(A,'stretch')),q(A,'fillRect'))
 pr=el(pic,q(P,'spPr'));xfrm(pr,px,py,w,h);el(el(pr,q(A,'prstGeom'),{'prst':'rect'}),q(A,'avLst'))
def native_table(tree,rows):
 f=el(tree,q(P,'graphicFrame'));nv=el(f,q(P,'nvGraphicFramePr'))
 el(nv,q(P,'cNvPr'),{'id':'20','name':'1차 개발 계획 대비 진행 상황'});el(nv,q(P,'cNvGraphicFramePr'));el(nv,q(P,'nvPr'))
 xf=el(f,q(P,'xfrm'));el(xf,q(A,'off'),{'x':x(60),'y':x(190)});el(xf,q(A,'ext'),{'cx':x(1160),'cy':x(378)})
 data=el(el(f,q(A,'graphic')),q(A,'graphicData'),{'uri':A+'/table'})
 table=el(data,q(A,'tbl'));el(table,q(A,'tblPr'),{'firstRow':'1','bandRow':'0'})
 grid=el(table,q(A,'tblGrid'))
 for width in [140,290,545,185]:el(grid,q(A,'gridCol'),{'w':x(width)})
 for i,row in enumerate(rows):
  tr=el(table,q(A,'tr'),{'h':x(50 if i==0 else 82)})
  for j,value in enumerate(row):
   tc=el(tr,q(A,'tc'));body=el(tc,q(A,'txBody'));el(body,q(A,'bodyPr'),{'wrap':'square','anchor':'ctr'});el(body,q(A,'lstStyle'))
   for line in value.split('\n'):paragraph(body,line,23,'4BE3D2' if i==0 or j==3 else 'E7F0F5',i==0)
   props=el(tc,q(A,'tcPr'),{'marL':x(10),'marR':x(10),'marT':x(7),'marB':x(7),'anchor':'ctr'})
   fill(props,'182B38' if i==0 else '0D1521')
   ln=el(props,q(A,'lnB'),{'w':'9525'});fill(ln,'344B5C');el(ln,q(A,'prstDash'),{'val':'solid'})

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 src=ROOT/'presentation'/'1차발표.pptx'
 with ZipFile(src) as z:files={n:z.read(n) for n in z.namelist()}
 root=E.fromstring(files['ppt/presentation.xml']);lst=root.find(q(P,'sldIdLst'))
 keepids={s.attrib[q(R,'id')] for s in list(lst)[:2]}
 for s in list(lst)[2:]:lst.remove(s)
 files['ppt/presentation.xml']=xml(root)
 rels=E.fromstring(files['ppt/_rels/presentation.xml.rels'])
 for rel in list(rels):
  if rel.attrib['Type'].endswith('/slide') and rel.attrib['Id'] not in keepids:rels.remove(rel)
 files['ppt/_rels/presentation.xml.rels']=xml(rels)
 # Eliminate unused original slides, notes and their package declarations.
 for n in list(files):
  match=re.search(r'(?:slides/slide|slides/_rels/slide|notesSlides/notesSlide|notesSlides/_rels/notesSlide)(\d+)',n)
  if match and int(match[1])>2:del files[n]
 types=E.fromstring(files['[Content_Types].xml'])
 for node in list(types):
  part=node.attrib.get('PartName','')
  if part.startswith(('/ppt/slides/','/ppt/notesSlides/')) and part.lstrip('/') not in files:types.remove(node)
 if not any(n.attrib.get('Extension')=='png' for n in types):el(types,q(CT,'Default'),{'Extension':'png','ContentType':'image/png'})
 files['[Content_Types].xml']=xml(types)
 s,tr=slide()
 text(tr,2,60,45,1160,72,'SHELLBOUND',56,'4BE3D2',True)
 text(tr,3,60,120,1160,48,'적의 몸을 빼앗아 길을 여는 2D 액션 퍼즐',32)
 text(tr,4,60,205,530,50,'핵심 플레이',30,'4BE3D2',True)
 text(tr,5,60,260,530,160,'공격을 피해서 기절 유도\n작은 본체로 적의 몸 탈취\n능력을 사용하고 다른 몸으로 교체',27)
 text(tr,6,60,445,530,47,'이번 구현',30,'4BE3D2',True)
 text(tr,7,60,500,530,120,'돌진형 · 포격형 2종 / 전투방 1개\n돌진 → 장갑 파괴 → 포격 → 탈출',25)
 picture(tr,8,620,205,600,425.455)
 text(tr,9,620,645,600,30,'실제 게임 렌더러 캡처 · 임시 도형 그래픽',19,'859CB2')
 text(tr,10,60,680,1100,30,'윤형균  /  2023184021                                            2차 프로젝트 발표  ·  01',19,'859CB2')
 files['ppt/slides/slide1.xml']=xml(s)
 rels=E.fromstring(files['ppt/slides/_rels/slide1.xml.rels'])
 for r in list(rels):
  if r.attrib['Type'].endswith('/image'):rels.remove(r)
 el(rels,q(PK,'Relationship'),{'Id':'rScreenshot','Type':R+'/image','Target':'../media/takeover-proof.png'})
 files['ppt/slides/_rels/slide1.xml.rels']=xml(rels)
 files['ppt/media/takeover-proof.png']=(OUT/'screenshots'/'04_armor_break.png').read_bytes()
 s,tr=slide()
 text(tr,2,60,45,1160,68,'개발 계획 대비 현재 진행 상황',46,'4BE3D2',True)
 text(tr,3,60,119,1160,50,'기획 변경: 자기 갑옷 회수 퍼즐 → 적의 몸 탈취 액션 퍼즐',27)
 rows=[['1차 일정','계획','현재 구현 / 확인','상태'],
 ['1주차','조준·입력·충돌 개선','기존 투척 유지 + 새 탑승·하차\n돌진 충돌·포격 착탄 판정 검증','해당 기능 완료'],
 ['2주차','세 방의 레벨 디자인','기존 세 방 유지 / 신규 전투방 1개\n전체 신규 캠페인은 미구현','부분 진행'],
 ['3주차','캐릭터 이미지·연출','공격 예고·기절·파편·효과음\n최종 캐릭터 이미지는 미적용','부분 진행'],
 ['4주차','플레이 테스트·마무리','규칙·UI 자동 검사 / 진행 경로 검증\n사용자 플레이·난이도 튜닝 예정','부분 진행']]
 native_table(tr,rows)
 text(tr,4,60,600,1160,35,'다음: 직접 플레이 검증 → 자석형·거미형 상호작용 → 최대 8스테이지',24,'4BE3D2')
 text(tr,5,60,642,1160,30,'현재 범위는 2종·1방 프로토타입이며, 확장 개체와 최종 아트는 향후 계획',22,'859CB2')
 text(tr,6,60,680,1160,28,'윤형균  /  2023184021                                           2차 프로젝트 발표  ·  02',19,'859CB2')
 files['ppt/slides/slide2.xml']=xml(s)
 # Keep original valid note infrastructure, replace body text completely.
 notes=[
 '게임 설명. 실제 구현: shellgame/takeover.py, takeover_app.py, takeover_view.py. 캡처는 SDL dummy 드라이버로 실제 게임 렌더러를 실행해 저장한 QA 화면이며 사람의 직접 플레이 녹화가 아님. 기존 세 방은 --classic. 자석형/거미형/8스테이지는 미구현. 발표자 윤형균 2023184021.',
 '1차 계획 출처: presentation/기획서.pptx 14번 슬라이드. 발표 요구사항 출처: C:/Users/yuneh/Downloads/2026_2DGP_2차발표가이드.pdf. 주차는 1차 기획의 상대 주차이며 완료일을 소급 주장하지 않음. 기존 게임과 새 몸 탈취 방은 별도 모드. 현재는 자동 검증과 임시 그래픽이며 재미, 최종 난이도와 아트는 미완료.']
 for i,note in enumerate(notes,1):
  key=f'ppt/notesSlides/notesSlide{i}.xml'
  if key not in files:continue
  nr=E.fromstring(files[key])
  for tx in nr.findall('.//'+q(P,'txBody')):
   for p in list(tx):
    if p.tag==q(A,'p'):tx.remove(p)
   paragraph(tx,note,18)
  files[key]=xml(nr)
 # Update package properties so slide-count metadata matches actual contents.
 if 'docProps/app.xml' in files:
  app=E.fromstring(files['docProps/app.xml'])
  for n in app.iter():
   if n.tag.endswith('}Slides'):n.text='2'
  files['docProps/app.xml']=xml(app)
 target=OUT/'SHELLBOUND_2차발표.pptx'
 with ZipFile(target,'w',ZIP_DEFLATED) as z:
  for n,data in files.items():z.writestr(n,data)
 print(target)
 render_preview(target)

def render_preview(path):
 # XML-driven layout preview. Text/table content stays editable in delivered PPTX.
 sys.path.insert(0,str(ROOT.parent/'.video_deps'))
 from PIL import Image,ImageDraw,ImageFont
 fonts={}
 def font(px):
  px=round(px)
  if px not in fonts:fonts[px]=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',px)
  return fonts[px]
 def draw_text(draw,tx,x,y,w,h):
  yy=y
  for p in tx.findall(q(A,'p')):
   content=''.join(n.text or '' for n in p.findall('.//'+q(A,'t')))
   rp=p.find('.//'+q(A,'rPr'));size=int(rp.attrib.get('sz',1800))/75 if rp is not None else 24
   color=rp.find('.//'+q(A,'srgbClr')) if rp is not None else None
   color='#'+color.attrib['val'] if color is not None else '#E7F0F5'
   line=''
   for ch in content:
    if draw.textlength(line+ch,font=font(size))>w and line:
     draw.text((x,yy),line,font=font(size),fill=color);yy+=size*1.15;line=''
    line+=ch
   draw.text((x,yy),line,font=font(size),fill=color);yy+=size*1.15
 with ZipFile(path) as z:
  for i in (1,2):
   r=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'));im=Image.new('RGB',(1280,720),'#0D1521');d=ImageDraw.Draw(im)
   for sp in r.findall('.//'+q(P,'sp')):
    xf=sp.find('./'+q(P,'spPr')+'/'+q(A,'xfrm'));tx=sp.find(q(P,'txBody'))
    if xf is None or tx is None:continue
    off=xf.find(q(A,'off'));ext=xf.find(q(A,'ext'))
    draw_text(d,tx,int(off.attrib['x'])/9525,int(off.attrib['y'])/9525,int(ext.attrib['cx'])/9525,int(ext.attrib['cy'])/9525)
   if i==1:
    import io
    shot=Image.open(io.BytesIO(z.read('ppt/media/takeover-proof.png'))).convert('RGB').resize((600,425))
    im.paste(shot,(620,205))
   for gf in r.findall('.//'+q(P,'graphicFrame')):
    table=gf.find('.//'+q(A,'tbl'))
    if table is None:continue
    widths=[int(col.attrib['w'])/9525 for col in table.find(q(A,'tblGrid'))];yy=190
    for ri,tr in enumerate(table.findall(q(A,'tr'))):
     ht=int(tr.attrib['h'])/9525;xx=60
     if ri==0:d.rectangle((60,yy,1220,yy+ht),fill='#182B38')
     for j,tc in enumerate(tr.findall(q(A,'tc'))):
      draw_text(d,tc.find(q(A,'txBody')),xx+10,yy+7,widths[j]-20,ht-14);xx+=widths[j]
     d.line((60,yy+ht,1220,yy+ht),fill='#344B5C');yy+=ht
   im.save(OUT/f'slide{i}_preview.png')

if __name__=='__main__':main()
