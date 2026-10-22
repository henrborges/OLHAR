from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import base64, io, math, subprocess, json

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets'
TMP=ROOT/'tmp'; TMP.mkdir(exist_ok=True)
BLUE='#164cff'; INK='#112322'; MUTED='#66716f'; BG='#edf1e9'
def font(size,bold=False,display=False):
    return ImageFont.truetype(str(A/f"font-{7 if display and bold else 5 if display else 3 if bold else 0}.ttf"),size)
def pic(name,size):return ImageOps.fit(Image.open(A/name).convert('RGB'),size,method=Image.Resampling.LANCZOS,centering=(.5,.18 if name=='portrait.jpg' else .5))
def uri(name,size):
    b=io.BytesIO();pic(name,size).save(b,'JPEG',quality=83)
    return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
def svg(name,inner):
    (A/name).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="360" viewBox="0 0 720 360"><defs><linearGradient id="shade" x2="0" y2="1"><stop stop-color="#001810" stop-opacity="0"/><stop offset="1" stop-color="#08291d" stop-opacity=".72"/></linearGradient><clipPath id="screen"><rect x="246" y="28" width="220" height="312" rx="16"/></clipPath></defs>'+inner+'</svg>')
def grid(w=720,h=360):
    return ''.join(f'<path d="M{x} 0V{h}" stroke="white" opacity=".55"/>' for x in [w/3,w*2/3])+''.join(f'<path d="M0 {y}H{w}" stroke="white" opacity=".55"/>' for y in [h/3,h*2/3])
def label(txt,x,y,fill=INK,size=14):return f'<text x="{x}" y="{y}" fill="{fill}" font-family="Arial,sans-serif" font-size="{size}">{txt}</text>'

def thumbs():
    city=uri('hero.jpg',(720,360)); portrait=uri('portrait.jpg',(720,360)); photographer=uri('photographer.jpg',(720,360))
    svg('camera.svg',f'<rect width="720" height="360" fill="#dce7d3"/><circle cx="600" cy="100" r="190" fill="#c9dbbd"/>'+label('ANTES DO CLIQUE',60,161,INK,15)+label('Um ajuste.',60,199,INK,29)+label('Outro resultado.',60,237,INK,29)+f'<rect x="364" y="-14" width="235" height="395" rx="32" fill="#142c32" transform="rotate(11 481 180)"/><g transform="rotate(11 481 180)"><image href="{city}" x="376" y="18" width="211" height="279" preserveAspectRatio="xMidYMid slice"/><path d="M446 18V297M516 18V297M376 111H587M376 204H587" stroke="#ffffff99"/><rect x="458" y="146" width="45" height="45" fill="none" stroke="#f5e274" stroke-width="2"/><circle cx="481" cy="332" r="22" fill="white"/><circle cx="481" cy="332" r="18" fill="none" stroke="#142c32"/>'+label('FOTO',461,288,'white',11)+'</g>')
    svg('light.svg',f'<image href="{portrait}" width="720" height="360" preserveAspectRatio="xMidYMid slice"/><rect width="720" height="360" fill="url(#shade)"/><path d="M60 50 190 132M60 110 170 164M60 170 154 194" stroke="#fff7d1" stroke-width="2" opacity=".75"/>'+label('LUZ SUAVE',49,312,'white',17)+label('Observe a direção da luz.',413,312,'white',14))
    svg('composition.svg',f'<image href="{city}" width="720" height="360" preserveAspectRatio="xMidYMid slice"/>{grid()}<rect x="224" y="104" width="32" height="32" fill="none" stroke="#f4ed77" stroke-width="2"/><circle cx="480" cy="240" r="6" fill="#f4ed77"/>'+label('UM ASSUNTO. UM ENQUADRAMENTO.',42,322,'white',13))
    svg('focus.svg',f'<image href="{portrait}" width="720" height="360" preserveAspectRatio="xMidYMid slice"/><rect width="720" height="360" fill="#122417" opacity=".14"/><path d="M316 90h30M316 90v30M412 90h-30M412 90v30M316 196v-30M316 196h30M412 196h-30M412 196v-30" stroke="#f5e66d" stroke-width="2"/><circle cx="447" cy="142" r="8" fill="none" stroke="#f5e66d" stroke-width="2"/><path d="M447 100V125M447 159V184" stroke="#f5e66d"/>'+label('TOQUE PARA FOCAR',44,312,'white',16)+f'<circle cx="590" cy="302" r="22" fill="#18312c"/>'+label('1×',580,307,'#f5e66d',14))
    svg('people.svg',f'<image href="{photographer}" width="720" height="360" preserveAspectRatio="xMidYMid slice"/><rect width="720" height="360" fill="url(#shade)"/>'+label('PESSOAS. AÇÃO. CONTEXTO.',40,300,'white',17)+''.join(f'<rect x="{x}" y="47" width="{w}" height="{h}" rx="2" fill="none" stroke="#ffffffab"/>' for x,w,h in [(50,65,44),(130,44,44),(190,28,44)]))
    svg('edit.svg',f'<rect width="720" height="360" fill="#e9dfcd"/><image href="{city}" x="0" y="0" width="440" height="360" preserveAspectRatio="xMidYMid slice"/><rect x="0" width="220" height="360" fill="#001915" opacity=".4"/><path d="M220 0V360" stroke="white" stroke-width="2"/><circle cx="220" cy="180" r="17" fill="white"/>'+label('↔',209,185,INK,18)+''.join(label(t,480,100+i*70,MUTED,13)+f'<path d="M480 {120+i*70}H657" stroke="#b5b1a3"/><circle cx="{[585,538,606][i]}" cy="{120+i*70}" r="7" fill="#164cff"/>' for i,t in enumerate(['Exposição','Contraste','Temperatura'])))
    (A/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="10" fill="#164cff"/><circle cx="20" cy="20" r="12" fill="none" stroke="white" stroke-width="2"/><circle cx="20" cy="20" r="6" fill="white"/></svg>')
    print('Six module illustrations ready.',flush=True)

def rounded_photo(canvas,image,box,radius=12):
    x,y,w,h=box;crop=ImageOps.fit(image,(w,h),method=Image.Resampling.LANCZOS);mask=Image.new('L',(w,h));ImageDraw.Draw(mask).rounded_rectangle((0,0,w,h),radius,fill=255);canvas.paste(crop,(x,y),mask)
def wrap(draw,text,f,width):
    words=text.split();lines=[];s=''
    for word in words:
        candidate=(s+' '+word).strip()
        if draw.textlength(candidate,font=f)>width and s:lines.append(s);s=word
        else:s=candidate
    if s:lines.append(s)
    return lines
def draw_text(draw,text,xy,size,color=INK,width=450,bold=False,display=False,leading=1.45):
    f=font(size,bold,display);x,y=xy
    for line in wrap(draw,text,f,width):draw.text((x,y),line,font=f,fill=color);y+=int(size*leading)
    return y

LESSONS={
 'configurar':[
  ('Prepare o básico.','Limpe a lente e abra a câmera nativa no modo Foto.','Câmera limpa. Foto mais clara.'),
  ('Ative a grade.','Procure Grade ou Linhas de grade nas configurações da câmera.','Os caminhos variam conforme o aparelho.'),
  ('Comece com 1×.','Use a lente principal e escolha a orientação pensando no destino da foto.','Evite filtros ativos sem perceber.'),
  ('Toque e confira.','Toque no assunto, ajuste o brilho se preciso e faça uma foto de teste.','Amplie o arquivo para conferir a nitidez.')],
 'luz':[
  ('Primeiro, a luz.','Procure uma janela ou uma área de sombra aberta para iluminar o rosto.','Uma mudança de posição pode ajudar.'),
  ('Toque no assunto.','Oriente a câmera para o que importa. Em um retrato, toque no rosto.','A interface mostrada é ilustrativa.'),
  ('Ajuste o brilho.','Se as áreas claras perderem detalhes, reduza um pouco a exposição.','Compare o rosto e as áreas claras.'),
  ('Confira o resultado.','Fotografe e observe se a pele e as roupas claras mantêm os detalhes.','Simulação didática de exposição.')],
 'enquadrar':[
  ('Escolha o protagonista.','Pergunte-se: qual informação esta foto precisa mostrar?','Um assunto claro facilita a leitura.'),
  ('Experimente os terços.','A grade ajuda a organizar a cena. Centralizar também pode funcionar.','Composição é escolha, não obrigação.'),
  ('Revise as bordas.','Confira o horizonte e os elementos que competem com o assunto.','Mude o ângulo antes de clicar.'),
  ('Varie os planos.','Faça uma foto aberta, uma média e um detalhe significativo.','Contexto, ação e detalhe se complementam.')]
}

def make_frame(key,step,t):
    W,H=960,540;im=Image.new('RGB',(W,H),'#edf1e9');d=ImageDraw.Draw(im)
    d.text((51,31),'olhar.',font=font(31,True,True),fill=BLUE)
    d.text((185,44),'FOTOGRAFIA COM CELULAR',font=font(10,True),fill=MUTED)
    d.text((53,122),f'0{step+1} / 04  ·  DEMONSTRAÇÃO ILUSTRADA',font=font(10,True),fill=BLUE)
    title,body,tip=LESSONS[key][step]
    y=draw_text(d,title,(50,160),35,width=470,bold=True,display=True,leading=1.18)
    y=draw_text(d,body,(53,y+25),20,width=455,color=MUTED,leading=1.5)
    d.rounded_rectangle((53,415,520,469),radius=7,fill='#e0e7d8')
    draw_text(d,tip,(68,429),12,width=432,color='#4b5d44',leading=1.3)
    d.text((53,500),'Vídeo sem áudio · menus e recursos variam por aparelho',font=font(10),fill=MUTED)
    # Schematically drawn phone, deliberately not a reproduction of a specific device.
    d.rounded_rectangle((612,27,875,508),radius=34,fill='#122b32')
    d.rounded_rectangle((622,38,865,496),radius=27,fill='#f5f6f1')
    d.rounded_rectangle((701,46,787,56),radius=5,fill='#122b32')
    screen=(630,76,227,310)
    source=Image.open(A/('portrait.jpg' if key=='luz' else 'hero.jpg')).convert('RGB')
    photo=ImageOps.fit(source,(227,310),method=Image.Resampling.LANCZOS)
    if key=='luz':
        brightness=1.45 if step<2 else 1.45-min(t/3,1)*.45 if step==2 else 1.0
        photo=ImageEnhance.Brightness(photo).enhance(brightness)
    if key=='enquadrar' and step==3:
        phase=int(t/2.65)%3
        if phase:photo=ImageOps.fit(source,(int(227*(1+phase*.36)),int(310*(1+phase*.36))),method=Image.Resampling.LANCZOS).crop((int(227*phase*.18),int(310*phase*.18),int(227*phase*.18)+227,int(310*phase*.18)+310))
    im.paste(photo,(630,76));d=ImageDraw.Draw(im)
    if (key=='configurar' and step>=1) or (key=='enquadrar' and step>=1):
        for x in [706,781]:d.line((x,76,x,386),fill='#e9eee7',width=1)
        for y1 in [179,283]:d.line((630,y1,857,y1),fill='#e9eee7',width=1)
    if (key=='configurar' and step==3) or (key=='luz' and step>=1):
        fx,fy=(765,150) if key=='luz' else (743,200)
        d.rectangle((fx-27,fy-27,fx+27,fy+27),outline='#f8e367',width=2)
        d.line((fx+40,fy-45,fx+40,fy+45),fill='#f8e367',width=1)
        sy=int(fy+(8 if step<2 else min(t/3,1)*30))
        d.ellipse((fx+35,sy-5,fx+45,sy+5),fill='#f8e367')
        if t<3:
            r=int(11+9*math.sin(t*math.pi))
            d.ellipse((fx-r,fy-r,fx+r,fy+r),outline='white',width=2)
    if key=='enquadrar' and step==2:
        d.rectangle((635,81,852,381),outline='#f8e367',width=3)
    d.rounded_rectangle((721,352,767,377),radius=13,fill='#15352e');d.text((734,356),'1×',font=font(12,True),fill='#f8e367')
    d.text((674,402),'PORTRAIT',font=font(8),fill='#879284');d.text((735,402),'FOTO',font=font(9,True),fill=BLUE);d.text((784,402),'VÍDEO',font=font(8),fill='#879284')
    d.ellipse((720,431,768,479),outline='#142d32',width=2);d.ellipse((725,436,763,474),fill='#142d32')
    d.text((637,483),'INTERFACE ILUSTRATIVA',font=font(7),fill=MUTED)
    # Progress is the only motion outside the active illustration.
    total=(step*8+t)/32
    d.rectangle((0,536,960,540),fill='#d6dfcf');d.rectangle((0,536,int(total*960),540),fill=BLUE)
    return im

def videos():
    for key in LESSONS:
        poster=make_frame(key,1,5);poster.save(A/f'video-{key}-poster.jpg',quality=90)
        cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','960x540','-r','12','-i','-','-an','-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(A/f'video-{key}.mp4')]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for frame in range(32*12):
            seconds=frame/12;step=min(3,int(seconds//8));p.stdin.write(make_frame(key,step,seconds%8).tobytes())
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('Video encoding failed: '+key)
        vtt='WEBVTT\n\n'
        for i,(title,body,tip) in enumerate(LESSONS[key]):
            vtt+=f'00:00:{i*8:02d}.000 --> 00:00:{(i+1)*8:02d}.000\n{title} {body}\n\n'
        (A/f'video-{key}.vtt').write_text(vtt)
        print(key,'video ready:',(A/f'video-{key}.mp4').stat().st_size,flush=True)

if __name__=='__main__':
    thumbs();videos()
