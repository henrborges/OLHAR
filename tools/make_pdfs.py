from pathlib import Path
import json, re, io, argparse
from xml.sax.saxutils import escape
from PIL import Image, ImageOps, ImageEnhance
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'assets'; OUT=A/'pdf';OUT.mkdir(exist_ok=True)
DATA=json.loads((ROOT/'content.json').read_text());W,H=595.28,841.89
INK=HexColor('#112322');BLUE=HexColor('#164cff');MUTED=HexColor('#66716f');PAPER=HexColor('#f8f9f6');LINE=HexColor('#dce2dd');NAVY=HexColor('#142c32');MINT=HexColor('#d8ed7d')
def module_pages(m):return m.get('pdfPages',2)
CHECKLIST_PAGE=3+sum(module_pages(m) for m in DATA['modules'])
REFERENCES_PAGE=CHECKLIST_PAGE+1
for name,n in [('DM',0),('DMBold',3),('Manrope',5),('ManropeBold',7)]:pdfmetrics.registerFont(TTFont(name,str(A/f'font-{n}.ttf')))
styles={
 'body':ParagraphStyle('body',fontName='DM',fontSize=10.3,leading=16,textColor=MUTED,spaceAfter=0),
 'small':ParagraphStyle('small',fontName='DM',fontSize=9,leading=14,textColor=MUTED),
 'title':ParagraphStyle('title',fontName='ManropeBold',fontSize=28,leading=35,textColor=INK),
 'principle':ParagraphStyle('principle',fontName='Manrope',fontSize=13,leading=20,textColor=INK),
 'white':ParagraphStyle('white',fontName='DM',fontSize=10,leading=17,textColor=white),
}
def para(c,text,x,top,width=499,style='body',**overrides):
    s=styles[style]
    if overrides:s=ParagraphStyle('custom',parent=s,**overrides)
    p=Paragraph(escape(text).replace('\n','<br/>'),s);_,h=p.wrap(width,1000);p.drawOn(c,x,top-h)
    return top-h
def text(c,s,x,y,size=10,font='DM',color=INK):c.setFont(font,size);c.setFillColor(color);c.drawString(x,y,s)
def line(c,y):c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(48,y,547,y)
def page_bg(c,label,number=None):
    c.setFillColor(PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
    text(c,'olhar.',48,790,23,'ManropeBold',BLUE);text(c,label.upper(),130,796,7.5,'DMBold',MUTED);line(c,774)
    line(c,57);text(c,'FOTOGRAFIA COM CELULAR  |  SEBRAE MT',48,39,7,'DM',MUTED)
    if number:text(c,str(number).zfill(2),527,39,8,'DM',MUTED)
def photo(c,name,box,kind=''):
    x,y,w,h=box;img=ImageOps.fit(Image.open(A/name).convert('RGB'),(int(w*2),int(h*2)),method=Image.Resampling.LANCZOS,centering=(.5,.18 if name=='portrait.jpg' else .5))
    c.saveState();p=c.beginPath();p.roundRect(x,y,w,h,6);c.clipPath(p,stroke=0);c.drawImage(ImageReader(img),x,y,w,h)
    if kind in ['composicao','preparar']:
        c.setStrokeColor(Color(1,1,1,.7));c.setLineWidth(.5)
        for f in [1/3,2/3]:c.line(x+w*f,y,x+w*f,y+h);c.line(x,y+h*f,x+w,y+h*f)
    if kind=='foco':
        c.setStrokeColor(HexColor('#fae270'));c.setLineWidth(1.2);c.rect(x+w*.48,y+h*.35,44,44,fill=0,stroke=1)
    c.restoreState()
def section(c,title,body,y):
    y=para(c,title,48,y,499,'body',fontName='DMBold',fontSize=11,leading=15,textColor=INK)-7
    y=para(c,body,48,y)-20
    return y
def note_box(c,title,body,y,fill=HexColor('#eaf0e3'),min_height=0):
    s=styles['small'];p=Paragraph(escape(body),s);_,h=p.wrap(463,800);height=max(min_height,h+52)
    c.setFillColor(fill);c.roundRect(48,y-height,499,height,6,fill=1,stroke=0)
    text(c,title,66,y-22,8,'DMBold',BLUE);p.drawOn(c,66,y-36-h)
    return y-height-18
def mission_banner(c,x,y,w,h):
    c.setFillColor(NAVY);c.roundRect(x,y,w,h,6,fill=1,stroke=0)
    text(c,'O QUE ESSA AGENDA ACRESCENTA?',x+22,y+h-25,8,'DMBold',MINT)
    for i,(title,desc) in enumerate([('Aprendizados','Observe a prática.'),('Conexões','Explique a troca.'),('Aplicação','Registre o próximo passo.')]):
        xx=x+22+i*157
        text(c,str(i+1).zfill(2),xx,y+73,9,'DM',HexColor('#a5b9bc'))
        text(c,title,xx,y+49,13,'ManropeBold',white)
        text(c,desc,xx,y+28,8,'DM',HexColor('#bdcecb'))
def add_module(c,m,start_number):
    page_bg(c,f'Tema {m["number"]} / Fundamentos e prática',start_number)
    text(c,f'TEMA {m["number"]}  /  {m["minutes"]} MIN COM EXERCÍCIO',48,746,8,'DMBold',BLUE)
    y=para(c,m['title'],48,724,499,'title')-14
    y=para(c,m['principle'],48,y,499,'principle')-20
    if m.get('toolkit'):mission_banner(c,48,y-143,499,143)
    else:
        name={'preparar':'hero.jpg','luz':'portrait.jpg','composicao':'hero.jpg','foco':'portrait.jpg','pessoas':'photographer.jpg','edicao':'hero.jpg'}[m['id']]
        photo(c,name,(48,y-143,499,143),m['id'])
    y-=163
    for s in m['sections'][:3]:y=section(c,s['title'],s['text'],y)
    if y<78:raise ValueError('Page overflow: '+m['id']+' first '+str(y))
    c.showPage()
    page_bg(c,f'Tema {m["number"]} / Aplique no dia a dia',start_number+1)
    text(c,'APLIQUE NO DIA A DIA',48,746,8,'DMBold',BLUE)
    y=para(c,m['title'],48,723,499,'title',fontSize=23,leading=29)-24
    for s in m['sections'][3:]:y=section(c,s['title'],s['text'],y)
    # Compact and printable four-step field routine.
    step_h=112;c.setFillColor(HexColor('#eaf0e3'));c.roundRect(48,y-step_h,499,step_h,6,fill=1,stroke=0)
    text(c,'NA HORA DE FOTOGRAFAR',66,y-21,8,'DMBold',BLUE)
    for i,step in enumerate(m['steps']):
        text(c,str(i+1).zfill(2),66,y-42-i*17,8,'DMBold',BLUE)
        para(c,step,91,y-34-i*17,431,'small',fontSize=9.1,leading=13)
    y-=step_h+19
    y=note_box(c,'AGORA É COM VOCÊ',m['exercise'],y,HexColor('#edf1ff'))
    y=note_box(c,'VALE EVITAR',m['avoid'],y,HexColor('#f2eee3'))
    y=para(c,m['takeaway'],48,y,499,'principle',fontSize=11,leading=17,textColor=BLUE)-15
    if y<75:raise ValueError('Page overflow: '+m['id']+' second '+str(y))
    if m['id'] in ['preparar','foco','luz']:
        text(c,'Referência de controles: Apple - Ferramentas de câmera do iPhone.',48,76,7,'DM',MUTED)
        c.linkURL(DATA['sources'][0]['url'],(48,72,400,86),relative=0)
    c.showPage()
    if m.get('toolkit'):add_mission_field_pages(c,m,start_number+2)
def add_mission_field_pages(c,m,start_number):
    t=m['toolkit']
    page_bg(c,f'Tema {m["number"]} / Roteiro de campo',start_number)
    text(c,'CENAS E PERGUNTAS',48,746,8,'DMBold',BLUE)
    y=para(c,'O que registrar e perguntar.',48,723,499,'title',fontSize=25,leading=32)-13
    y=para(c,'Adapte os registros à relevância de cada agenda. Busque cenas que expliquem o aprendizado e a participação das pessoas.',48,y,499,'small')-21
    for i,shot in enumerate(t['shots']):
        y=para(c,f'{i+1:02d}. {shot["title"]}',48,y,499,'small',fontName='DMBold',fontSize=10,leading=14,textColor=INK)-4
        y=para(c,shot['text'],68,y,479,'small',fontSize=9.2,leading=13)-12
    y=para(c,'Perguntas que aprofundam a cobertura',48,y-5,499,'body',fontName='DMBold',fontSize=12,leading=17,textColor=BLUE)-14
    for group in t['interviews']:
        y=para(c,group['role'],48,y,499,'small',fontName='DMBold',fontSize=9.5,textColor=INK)-3
        for q in group['questions']:y=para(c,'- '+q,60,y,487,'small',fontSize=9.2,leading=13)-3
        y-=9
    if y<76:raise ValueError('Mission field page overflow: '+str(y))
    c.showPage()
    page_bg(c,f'Tema {m["number"]} / Insight e entrega',start_number+1)
    text(c,'ORGANIZE O CONHECIMENTO',48,746,8,'DMBold',BLUE)
    para(c,'Do aprendizado à entrega.',48,723,499,'title',fontSize=25,leading=32)
    col=237;left_x=48;right_x=310
    text(c,'FICHA DE INSIGHT',left_x,666,8.5,'DMBold',BLUE)
    ly=para(c,t['exampleLabel']+'.',left_x,653,col,'small',fontSize=8.2,leading=12)-15
    for field in t['insight']:
        ly=para(c,field['label'],left_x,ly,col,'small',fontName='DMBold',fontSize=10,leading=14,textColor=INK)-3
        ly=para(c,field['text'],left_x,ly,col,'small',fontSize=8.7,leading=12)-6
        ly=para(c,field['example'],left_x+10,ly,col-10,'small',fontSize=8.8,leading=13,textColor=HexColor('#496244'))-17
    text(c,'UMA ENTREGA DIÁRIA POSSÍVEL',right_x,666,8.5,'DMBold',BLUE)
    ry=642
    for item in t['dailyPlan']:
        ry=para(c,item['format'],right_x,ry,col,'small',fontName='DMBold',fontSize=9.3,leading=13,textColor=INK)-4
        ry=para(c,item['text'],right_x,ry,col,'small',fontSize=8.8,leading=12.5)-15
    ry=para(c,t['captionLabel'],right_x,ry,col,'small',fontName='DMBold',fontSize=9,leading=13,textColor=BLUE)-7
    ry=para(c,t['caption'],right_x,ry,col,'small',fontSize=8.6,leading=12.5)-18
    ry=para(c,'Feche o dia com uma entrega organizada',right_x,ry,col,'small',fontName='DMBold',fontSize=9,leading=13,textColor=INK)-6
    ry=para(c,t['delivery'],right_x,ry,col,'small',fontSize=8.8,leading=12.5)-10
    if min(ly,ry)<76:raise ValueError('Mission insight page overflow: '+str((ly,ry)))
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(294,90,294,675)
    c.showPage()
def make_modules(only=None):
    for m in DATA['modules']:
        if only and m['id']!=only:continue
        path=OUT/f'{m["id"]}.pdf';c=canvas.Canvas(str(path),pagesize=(W,H));c.setTitle(m['title']+' | Olhar');c.setAuthor('Olhar | Sebrae MT');add_module(c,m,1);c.save();print(path.name,flush=True)
def cover(c):
    c.setFillColor(NAVY);c.rect(0,0,W,H,fill=1,stroke=0)
    text(c,'olhar.',46,756,53,'ManropeBold',white);text(c,'GUIA ESSENCIAL',49,701,9,'DMBold',MINT)
    text(c,'Fotografia',44,630,47,'ManropeBold',white);text(c,'com celular.',44,574,47,'ManropeBold',white)
    para(c,'Um novo olhar para os registros do dia a dia.',49,537,470,'white',fontSize=12,leading=18,textColor=HexColor('#c0ced0'))
    photo(c,'photographer.jpg',(48,196,499,296))
    c.setFillColor(MINT);c.roundRect(69,176,300,36,3,fill=1,stroke=0);text(c,'Olhe. Experimente. Registre.',87,189,11,'DMBold',INK)
    text(c,f'{len(DATA["modules"])} temas essenciais + exercícios + checklist',49,117,11,'DM',white)
    text(c,'SEBRAE MT  /  MATERIAL EDUCATIVO INTRODUTÓRIO',49,63,8,'DM',HexColor('#a5b9bc'))
    c.showPage()
def contents(c):
    page_bg(c,'Como usar este guia',2);text(c,'COMECE POR AQUI',48,745,8,'DMBold',BLUE)
    y=para(c,'Um passo de cada vez.',48,715,499,'title')-18
    y=para(c,'Você não precisa de um celular novo para começar. Este guia reúne cuidados simples para fotografar com mais intenção, observar a luz e entregar registros que ajudem a contar uma história.',48,y)-21
    y=note_box(c,'LEIA, EXPERIMENTE, REVISE','Escolha um tema, teste o exercício no seu ambiente e confira o resultado ampliando a foto. Os tempos são uma estimativa de leitura com prática. Os menus podem variar conforme o modelo e a versão do sistema.',y,HexColor('#edf1ff'))
    row_h=min(64,(y-165)/len(DATA['modules']));start=3
    if row_h<43:raise ValueError('Contents rows need another page')
    for i,m in enumerate(DATA['modules']):
        if i<len(DATA['modules'])-1: line(c,y-row_h+4)
        text(c,m['number'],48,y-14,11,'ManropeBold',BLUE);text(c,m['title'],86,y-12,11,'DMBold',INK);para(c,m['description'],86,y-22,423,'small',fontSize=8,leading=11);text(c,str(start),532,y-13,9,'DM',MUTED);y-=row_h;start+=module_pages(m)
    text(c,'CHECKLIST DE BOLSO',48,135,9,'DMBold',INK);text(c,str(CHECKLIST_PAGE),532,135,9,'DM',MUTED)
    text(c,'REFERÊNCIAS E CRÉDITOS',48,110,9,'DMBold',INK);text(c,str(REFERENCES_PAGE),532,110,9,'DM',MUTED);c.showPage()
def checklist(c,number=1):
    page_bg(c,'Checklist de bolso',number);text(c,'ANTES DO PRÓXIMO CLIQUE',48,745,8,'DMBold',BLUE)
    y=para(c,'Uma pausa. Onze cuidados.',48,714,499,'title')-15
    y=para(c,'Uma lista curta para consultar antes de fotografar e antes de compartilhar. Imprima, guarde no celular ou leve para a próxima cobertura.',48,y)-28
    for i,g in enumerate(DATA['checklist']):
        text(c,f'0{i+1}',48,y-2,12,'ManropeBold',BLUE);text(c,g['group'],88,y,16,'ManropeBold',INK);y-=30
        for item in g['items']:
            c.setStrokeColor(HexColor('#a9b7a0'));c.setLineWidth(.8);c.roundRect(90,y-9,9,9,1.5,fill=0,stroke=1)
            after=para(c,item,112,y+2,430,'body',fontSize=10,leading=16);y=after-18
        line(c,y+2);y-=28
    para(c,'Um bom registro começa com atenção, ganha força com contexto e fica completo com uma entrega bem cuidada.',48,105,499,'principle',fontSize=11,leading=17,textColor=BLUE)
    c.showPage()
def references(c):
    page_bg(c,'Referências e créditos',REFERENCES_PAGE);text(c,'PARA CONSULTAR',48,745,8,'DMBold',BLUE)
    y=para(c,'Continue a explorar.',48,713,499,'title')-20
    y=para(c,'Conteúdo educativo original. As orientações de controles foram conferidas nos materiais dos fabricantes em outubro de 2026. Este guia usa caminhos gerais e não substitui o manual do aparelho.',48,y)-28
    for s in DATA['sources']:
        y=para(c,s['label'],48,y,499,'body',fontName='DMBold',textColor=INK)-5
        old=y;y=para(c,s['url'],48,y,499,'small',fontSize=8,textColor=BLUE,leading=13)-24;c.linkURL(s['url'],(48,y+20,547,old),relative=0)
    y=section(c,'Ilustrações e demonstrações','As interfaces, a grade e os recortes são ilustrações didáticas. Não reproduzem um modelo específico. As fotografias de apoio não representam pessoas, espaços ou eventos do Sebrae.',y)
    photos=[('Pauline Loroy - pessoa fotografando','https://unsplash.com/photos/R0S_GXfMMeM'),('Paisagem urbana e celular - Unsplash','https://unsplash.com/photos/Yi3Un7xBb5U'),('Behrouz Sasani - retrato à janela','https://unsplash.com/photos/h9l1AKYK3Cg')]
    for label,url in photos:
        y=para(c,label,48,y,499,'small',fontName='DMBold')-4;old=y;y=para(c,url,48,y,499,'small',fontSize=8,textColor=BLUE)-17;c.linkURL(url,(48,y+15,547,old),relative=0)
    y=note_box(c,'CUIDADO COM A INFORMAÇÃO','Siga o fluxo interno para autorização e uso de imagem. Antes de divulgar, confira pessoas, documentos e telas presentes no enquadramento e preserve o contexto do registro.',y,HexColor('#eaf0e3'))
    c.showPage()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--update-module');args=parser.parse_args()
    if args.update_module and not any(m['id']==args.update_module for m in DATA['modules']):raise ValueError('Unknown module')
    make_modules(args.update_module)
    if not args.update_module:
        c=canvas.Canvas(str(OUT/'checklist-fotografia.pdf'),pagesize=(W,H));c.setTitle('Checklist de fotografia com celular');c.setAuthor('Olhar | Sebrae MT');checklist(c);c.save()
    c=canvas.Canvas(str(OUT/'olhar-guia-completo.pdf'),pagesize=(W,H));c.setTitle('Olhar - Guia essencial de fotografia com celular');c.setAuthor('Olhar | Sebrae MT');cover(c);contents(c)
    start=3
    for m in DATA['modules']:add_module(c,m,start);start+=module_pages(m)
    checklist(c,CHECKLIST_PAGE);references(c);c.save()
    for f in sorted(OUT.glob('*.pdf')):
        r=PdfReader(f);print(f.name,len(r.pages),'pages',f.stat().st_size,flush=True)
    assert len(PdfReader(OUT/'olhar-guia-completo.pdf').pages)==REFERENCES_PAGE
if __name__=='__main__':main()
