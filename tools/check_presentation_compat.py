"""Regression checks for unintended theme bullets and unsupported table URIs."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
NS={'p':P,'a':A}
path=Path(__file__).resolve().parent.parent/'presentation/second/SHELLBOUND_2차발표.pptx'
with ZipFile(path) as z:
    total=0
    for index in (1,2):
        root=E.fromstring(z.read(f'ppt/slides/slide{index}.xml'))
        for para in root.findall('.//a:p',NS):
            if para.find('.//a:t',NS) is None:continue
            props=para.find('a:pPr',NS)
            assert props is not None and props.find('a:buNone',NS) is not None,'Inherited bullet'
            for key in ['spcBef','spcAft']:
                node=props.find('a:'+key+'/a:spcPts',NS)
                assert node is not None and node.attrib['val']=='0','Inherited spacing'
            total+=1
        for graphic in root.findall('.//a:graphicData',NS):
            if graphic.find('a:tbl',NS) is not None:
                assert graphic.attrib['uri']=='http://schemas.openxmlformats.org/drawingml/2006/table'
                widths=[int(n.attrib['w']) for n in graphic.findall('a:tbl/a:tblGrid/a:gridCol',NS)]
                assert sum(widths)==1160*9525
    print('PASS: 2 slides, explicit paragraph styles:',total,'native table URI and widths valid')
