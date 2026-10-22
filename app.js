'use strict';
const icon = (name) => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const normalize = (value) => value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const storageKey = 'olhar-photography-v1';
const modulePageCount = m => m.pdfPages || 2;
const guidePageCount = modules => 1 + modules.reduce((sum,m)=>sum+modulePageCount(m),0);
let course, selected = new Set(), completed = new Set(), currentFilter = 'all', currentModule, exportBusy = false, toastTimer, lastDialogTrigger;
const videos = [
 {id:'configurar', title:'Prepare a câmera para começar', label:'Primeiros passos', duration:'0:32', module:'preparar', description:'Grade, lente principal e foco: uma rotina simples antes de fotografar.', transcript:[
  'Limpe a lente e abra o aplicativo nativo de câmera no modo Foto. A interface mostrada é ilustrativa.',
  'Procure Grade ou Linhas de grade nas configurações. No iPhone, busque Ajustes > Câmera > Grade. No Android, o caminho depende do fabricante.',
  'Comece com a lente principal em 1×. Escolha a orientação pensando no uso da foto e evite deixar filtros ativos sem perceber.',
  'Toque no assunto para orientar o foco, ajuste o brilho se necessário e faça uma foto de teste. Amplie o arquivo para conferir a nitidez.'
 ]},
 {id:'luz', title:'Toque, ajuste e encontre a luz', label:'Luz e exposição', duration:'0:32', module:'luz', description:'Veja como um pequeno ajuste ajuda a preservar os detalhes.', transcript:[
  'Antes de fotografar, encontre uma fonte de luz uniforme, como uma janela ou uma sombra aberta.',
  'Toque no rosto ou no assunto principal para orientar o foco e a medição da câmera.',
  'Ajuste o controle de exposição ou brilho. Se as áreas claras perderem detalhes, experimente reduzir um pouco. Os controles variam conforme o aparelho.',
  'Faça uma foto e confira o rosto e as áreas claras. A comparação mostrada é uma simulação didática de exposição, não uma captura real de um celular.'
 ]},
 {id:'enquadrar', title:'Enquadre com mais intenção', label:'Composição na prática', duration:'0:32', module:'composicao', description:'Use a grade, confira as bordas e varie os planos da mesma cena.', transcript:[
  'Escolha o protagonista da imagem. Pergunte-se qual informação essa foto precisa mostrar.',
  'Ative a grade e experimente posicionar o assunto perto de um terço. Essa é uma possibilidade, não uma regra obrigatória.',
  'Observe as quatro bordas e o horizonte. Mude de posição para evitar elementos que competem com o assunto principal.',
  'Registre um plano aberto, um médio e um detalhe. Faça versões horizontais e verticais quando o uso exigir. O vídeo mostra uma interface e recortes ilustrativos.'
 ]}
];

async function init(){
 try {
  const response = await fetch('content.json');
  if(!response.ok) throw new Error('Conteúdo indisponível');
  course = await response.json();
  document.querySelector('#topic-count').textContent=String(course.modules.length).padStart(2,'0');
  document.querySelector('#ebook-meta').textContent=`PDF · ${3+guidePageCount(course.modules)} páginas`;
  document.querySelector('#ebook-description-topics').textContent=`Os ${course.modules.length} temas, exercícios e checklist em um só arquivo.`;
  document.querySelector('.estimated').textContent=`Cerca de ${course.modules.reduce((sum,m)=>sum+m.minutes,0)} min com os exercícios`;
  restoreState(); renderModules(); renderGuideLists(); renderVideos(); renderChecklist(); updateState();
  document.querySelector('#sources-list').innerHTML=course.sources.map(s=>`<li><a href="${escapeHTML(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(s.label)}</a></li>`).join('');
  document.querySelector('#module-search').addEventListener('input',renderModules);
  document.querySelector('#grid-toggle').addEventListener('change',e=>{document.querySelector('#thirds-grid').hidden=!e.target.checked;});
  document.addEventListener('click',handleClick);
  document.addEventListener('change',e=>{if(e.target.matches('[data-guide-id]'))toggleSelection(e.target.dataset.guideId,e.target.checked);});
  document.querySelectorAll('dialog').forEach(dialog=>{
   dialog.addEventListener('close',()=>{dialog.querySelectorAll('video').forEach(v=>v.pause());if(lastDialogTrigger?.isConnected)lastDialogTrigger.focus({preventScroll:true});});
   dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
  });
  window.addEventListener('hashchange',handleHash);handleHash();
 } catch(error) {
  console.error(error);document.querySelector('#modules-grid').innerHTML='<div class="empty-state">Não foi possível carregar as aulas. Recarregue a página ou <a href="assets/pdf/olhar-guia-completo.pdf" style="color:var(--blue);text-decoration:underline">baixe o e-book completo</a>.</div>';
 }
}
function restoreState(){
 try{const saved=JSON.parse(localStorage.getItem(storageKey)||'{}');const ids=new Set(course.modules.map(m=>m.id));selected=new Set((Array.isArray(saved.selected)?saved.selected:[]).filter(id=>ids.has(id)));completed=new Set((Array.isArray(saved.completed)?saved.completed:[]).filter(id=>ids.has(id)));}catch{selected=new Set();completed=new Set();}
}
function persistState(){try{localStorage.setItem(storageKey,JSON.stringify({selected:[...selected],completed:[...completed]}));}catch{document.querySelector('#progress-label').title='O navegador não permitiu salvar o progresso.';document.querySelector('.progress-widget small').textContent='Progresso apenas nesta visita';}}
function updateState(){
 document.querySelectorAll('[data-selected-count]').forEach(el=>el.textContent=selected.size);
 document.querySelectorAll('[data-topic-plural]').forEach(el=>el.textContent=selected.size===1?'tema selecionado':'temas selecionados');
 document.querySelectorAll('[data-action="export"]').forEach(el=>el.disabled=selected.size===0||exportBusy);
 document.querySelectorAll('[data-guide-id]').forEach(el=>el.checked=selected.has(el.dataset.guideId));
 document.querySelectorAll('[data-action="select"]').forEach(el=>{const yes=selected.has(el.dataset.id);el.classList.toggle('selected',yes);el.setAttribute('aria-pressed',String(yes));el.innerHTML=icon(yes?'check':'plus');el.setAttribute('aria-label',`${yes?'Remover':'Adicionar'} ${course.modules.find(m=>m.id===el.dataset.id)?.title||'tema'} ${yes?'do':'ao'} meu guia`);});
 document.querySelector('#progress-label').textContent=`${completed.size} de ${course.modules.length}`;
 document.querySelector('#progress-bar').style.width=`${completed.size/course.modules.length*100}%`;
 const pageSummary=selected.size?`${guidePageCount(course.modules.filter(m=>selected.has(m.id)))} páginas com capa`:'Escolha os temas acima';
 document.querySelector('#selected-pages').textContent=pageSummary;
 document.querySelector('#modal-page-summary').textContent=pageSummary;
 persistState();
}
function renderModules(){
 const search=normalize(document.querySelector('#module-search').value.trim());
 const list=course.modules.filter((m,i)=>{
  const filter=currentFilter==='all'||(currentFilter==='basics'&&i<4)||(currentFilter==='work'&&i>=4);
  const text=normalize([m.title,m.tag,m.description,...m.sections.map(s=>s.title+' '+s.text),m.toolkit?JSON.stringify(m.toolkit):''].join(' '));
  return filter&&(!search||text.includes(search));
 });
 document.querySelector('#modules-grid').innerHTML=list.map(m=>`<article class="module-card ${m.toolkit?'mission-card':''}"><div class="module-image"><img src="assets/${m.image}" alt="" loading="lazy"><span class="module-num">${m.number}</span><button class="add-guide ${selected.has(m.id)?'selected':''}" data-action="select" data-id="${m.id}" aria-label="Adicionar ${escapeHTML(m.title)} ao meu guia" aria-pressed="${selected.has(m.id)}">${icon(selected.has(m.id)?'check':'plus')}</button></div><div class="module-body"><div class="module-meta"><span>${escapeHTML(m.tag)}</span><span class="time">${icon('clock')}${m.minutes} min</span></div><h3>${escapeHTML(m.title)}</h3><p>${escapeHTML(m.description)}</p>${m.toolkit?'<div class="mission-pill-row"><span>Aprendizados</span><span>Conexões</span><span>Insights para aplicar</span></div>':''}<div class="module-bottom"><button data-action="module" data-id="${m.id}" aria-label="Abrir tema: ${escapeHTML(m.title)}">${completed.has(m.id)?'Revisar tema':'Explorar tema'} ${icon('arrow')}</button>${m.toolkit?`<a class="text-link blue mission-download" href="assets/pdf/${m.id}.pdf" download>Baixar guia · ${modulePageCount(m)} p. ${icon('download')}</a>`:''}<span class="module-state ${completed.has(m.id)?'done':''}">${completed.has(m.id)?icon('check')+'Concluído':'Leitura + exercício'}</span></div></div></article>`).join('');
 document.querySelector('#empty-state').hidden=list.length>0;
}
function renderGuideLists(){
 const html=course.modules.map(m=>`<label class="guide-item"><input type="checkbox" data-guide-id="${m.id}" aria-label="Incluir ${escapeHTML(m.title)} no PDF"><span class="guide-number">${m.number}</span><span class="guide-title">${escapeHTML(m.title)}</span><span class="guide-pages">${modulePageCount(m)} páginas</span></label>`).join('');
 document.querySelector('#guide-inline-list').innerHTML=html;document.querySelector('#guide-modal-list').innerHTML=html;
}
function renderVideos(){document.querySelector('#videos-grid').innerHTML=videos.map((v,i)=>`<button class="video-card" data-action="video" data-id="${v.id}" aria-label="Assistir: ${escapeHTML(v.title)}"><div class="video-thumb"><img src="assets/video-${v.id}-poster.jpg" alt="" loading="lazy"><span class="play-circle">${icon('play')}</span><span class="video-duration">${v.duration}</span></div><span>0${i+1} · ${escapeHTML(v.label)}</span><h3>${escapeHTML(v.title)}</h3><p>${escapeHTML(v.description)}</p></button>`).join('');}
function renderChecklist(){document.querySelector('#checklist-groups').innerHTML=course.checklist.map((g,i)=>`<div class="checklist-group"><span>0${i+1}</span><h3>${escapeHTML(g.group)}</h3><ul>${g.items.map(item=>`<li>${escapeHTML(item)}</li>`).join('')}</ul></div>`).join('');}
function renderMissionToolkit(m){
 const t=m.toolkit;if(!t)return '';
 return `<section class="mission-toolkit"><div class="mission-toolkit-label">GUIA DE CAMPO · PARA USAR NA PRÓXIMA AGENDA</div><h3>${escapeHTML(t.captureTitle)}</h3><ol class="mission-shot-list">${t.shots.map(s=>`<li><div><h4>${escapeHTML(s.title)}</h4><p>${escapeHTML(s.text)}</p></div></li>`).join('')}</ol><h3>Perguntas que aprofundam a cobertura</h3><div class="mission-interviews">${t.interviews.map(group=>`<section><h4>${escapeHTML(group.role)}</h4><ul>${group.questions.map(q=>`<li>${escapeHTML(q)}</li>`).join('')}</ul></section>`).join('')}</div><h3>${escapeHTML(t.insightTitle)}</h3><p class="mission-example-label">${escapeHTML(t.exampleLabel)}</p><dl class="mission-insight">${t.insight.map(field=>`<div><dt>${escapeHTML(field.label)}</dt><dd>${escapeHTML(field.text)}</dd><dd class="insight-example">${escapeHTML(field.example)}</dd></div>`).join('')}</dl><h3>${escapeHTML(t.dailyTitle)}</h3><div class="mission-daily">${t.dailyPlan.map(s=>`<section><h4>${escapeHTML(s.format)}</h4><p>${escapeHTML(s.text)}</p></section>`).join('')}</div><div class="mission-caption"><h4>${escapeHTML(t.captionLabel)}</h4><blockquote>${escapeHTML(t.caption)}</blockquote></div><section class="mission-delivery"><h4>Feche o dia com uma entrega organizada</h4><p>${escapeHTML(t.delivery)}</p></section></section>`;
}
function toggleSelection(id,checked){if(!course.modules.some(m=>m.id===id))return;const yes=checked===undefined?!selected.has(id):checked;if(yes)selected.add(id);else selected.delete(id);updateState();}
function openDialog(id,trigger){lastDialogTrigger=trigger||document.activeElement;const target=document.querySelector(id);document.querySelectorAll('dialog[open]').forEach(d=>{if(d!==target)d.close();});if(!target.open)target.showModal();}
function openModule(id,trigger){
 const m=course.modules.find(item=>item.id===id);if(!m)return;currentModule=id;
 const index=course.modules.indexOf(m),done=completed.has(id);
 document.querySelector('#module-dialog-content').innerHTML=`<div class="module-head"><div class="dialog-header"><span class="eyebrow blue">TEMA ${m.number} DE ${String(course.modules.length).padStart(2,'0')} · ${m.minutes} MIN COM PRÁTICA</span><button class="icon-button" data-action="close" aria-label="Fechar aula">${icon('close')}</button></div><h2 id="lesson-title">${escapeHTML(m.title)}</h2><p>${escapeHTML(m.description)}</p></div><div class="module-content"><aside class="lesson-side"><span>SUA TRILHA</span>${course.modules.map(x=>`<button class="${x.id===id?'active':''}" data-action="module" data-id="${x.id}"><span>${x.number}</span>${escapeHTML(x.title)}</button>`).join('')}<hr><a href="assets/pdf/${m.id}.pdf" download>${icon('download')}Baixar este tema</a></aside><div class="lesson-main"><p class="lesson-principle">${escapeHTML(m.principle)}</p>${m.sections.map(s=>`<section class="lesson-section"><h3>${escapeHTML(s.title)}</h3><p>${escapeHTML(s.text)}</p></section>`).join('')}${renderMissionToolkit(m)}<div class="lesson-steps"><h3>Na hora de fotografar</h3><ol>${m.steps.map(s=>`<li>${escapeHTML(s)}</li>`).join('')}</ol></div><div class="exercise-box"><span>AGORA É COM VOCÊ</span><p>${escapeHTML(m.exercise)}</p></div><div class="avoid-box"><b>Vale evitar</b><p>${escapeHTML(m.avoid)}</p></div><p class="lesson-section" style="font-size:12px;color:var(--blue)">${escapeHTML(m.takeaway)}</p><div class="lesson-actions"><button class="button primary" data-action="complete" data-id="${id}">${icon(done?'check':'plus')}${done?'Tema concluído':'Marcar como concluído'}</button><a class="text-link blue" href="assets/pdf/${m.id}.pdf" download>Baixar tema ${icon('download')}</a>${index<course.modules.length-1?`<button class="text-link" data-action="module" data-id="${course.modules[index+1].id}">Próximo ${icon('arrow')}</button>`:''}</div></div></div>`;
 openDialog('#module-dialog',trigger);document.querySelector('#module-dialog').scrollTop=0;
}
function openVideo(id,trigger){
 const v=videos.find(x=>x.id===id);if(!v)return;
 document.querySelector('#video-content').innerHTML=`<h2 id="video-title">${escapeHTML(v.title)}</h2><video controls playsinline preload="metadata" poster="assets/video-${v.id}-poster.jpg" aria-label="Demonstração ilustrada: ${escapeHTML(v.title)}"><source src="assets/video-${v.id}.mp4" type="video/mp4"><track kind="captions" src="assets/video-${v.id}.vtt" srclang="pt-BR" label="Português">Seu navegador não reproduz este vídeo. Use o link abaixo para baixar.</video><div class="video-detail"><span>32 segundos · vídeo ilustrado · sem áudio<br>Os recursos e menus variam conforme o aparelho.</span><a class="text-link blue" href="assets/video-${v.id}.mp4" download>Baixar vídeo ${icon('download')}</a></div><details class="video-transcript" open><summary>Resumo em texto</summary><ol>${v.transcript.map(t=>`<li>${escapeHTML(t)}</li>`).join('')}</ol></details><button class="text-link blue" style="margin-top:20px" data-action="module" data-id="${v.module}">Explorar este tema ${icon('arrow')}</button>`;
 openDialog('#video-dialog',trigger);
}
function handleHash(){if(location.hash.startsWith('#tema=')){const id=decodeURIComponent(location.hash.slice(6));if(course.modules.some(m=>m.id===id))openModule(id);}}
async function handleClick(e){
 const actionEl=e.target.closest('[data-action]'),filterEl=e.target.closest('[data-filter]'),formatEl=e.target.closest('[data-format]');
 if(filterEl){currentFilter=filterEl.dataset.filter;document.querySelectorAll('[data-filter]').forEach(el=>{el.classList.toggle('active',el===filterEl);el.setAttribute('aria-pressed',String(el===filterEl));});renderModules();return;}
 if(formatEl){const portrait=formatEl.dataset.format==='portrait';document.querySelector('#simulator-frame').classList.toggle('portrait',portrait);document.querySelector('#frame-ratio').textContent=portrait?'3:4':'4:3';document.querySelector('#format-tip').textContent=portrait?'O vertical aproxima o olhar de uma parte da cena. Cuide para não cortar informações importantes.':'O horizontal dá espaço ao ambiente. Confira se o assunto principal continua claro.';document.querySelectorAll('[data-format]').forEach(el=>{el.classList.toggle('active',el===formatEl);el.setAttribute('aria-pressed',String(el===formatEl));});return;}
 if(!actionEl){if(e.target.closest('nav a'))closeMenu();return;}
 const action=actionEl.dataset.action,id=actionEl.dataset.id;
 if(action==='module')openModule(id,actionEl);
 if(action==='video')openVideo(id,actionEl);
 if(action==='guide')openDialog('#guide-dialog',actionEl);
 if(action==='sources')openDialog('#sources-dialog',actionEl);
 if(action==='close')actionEl.closest('dialog').close();
 if(action==='select'){toggleSelection(id);notify(selected.has(id)?'Tema adicionado ao seu guia.':'Tema removido do seu guia.');}
 if(action==='select-all'){course.modules.forEach(m=>selected.add(m.id));updateState();}
 if(action==='clear'){selected.clear();updateState();}
 if(action==='complete'){
  const done=completed.has(id);if(done)completed.delete(id);else completed.add(id);updateState();renderModules();
  actionEl.innerHTML=icon(done?'plus':'check')+(done?'Marcar como concluído':'Tema concluído');notify(done?'Tema disponível para revisar.':'Tema concluído. Seu próximo clique já pode ser diferente.');
 }
 if(action==='export')await exportPDF();
 if(action==='menu'){const open=!document.querySelector('nav').classList.contains('open');document.querySelector('nav').classList.toggle('open',open);actionEl.setAttribute('aria-expanded',String(open));actionEl.setAttribute('aria-label',open?'Fechar navegação':'Abrir navegação');}
}
function closeMenu(){document.querySelector('nav').classList.remove('open');document.querySelector('[data-action="menu"]').setAttribute('aria-expanded','false');document.querySelector('[data-action="menu"]').setAttribute('aria-label','Abrir navegação');}
function notify(message){const toast=document.querySelector('#toast');toast.textContent=message;toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),3500);}
async function exportPDF(){
 if(exportBusy||selected.size===0)return;exportBusy=true;updateState();
 document.querySelectorAll('[data-action="export"]').forEach(b=>{b.innerHTML='Preparando seu PDF…';b.setAttribute('aria-busy','true');});
 const chosen=course.modules.filter(m=>selected.has(m.id));
 try{
  if(!window.PDFLib)throw new Error('Ferramenta de PDF indisponível');
  const {PDFDocument,StandardFonts,rgb}=PDFLib,doc=await PDFDocument.create();
  const font=await doc.embedFont(StandardFonts.Helvetica),bold=await doc.embedFont(StandardFonts.HelveticaBold);
  const page=doc.addPage([595.28,841.89]);
  const blue=rgb(.086,.298,1),ink=rgb(.067,.137,.133),gray=rgb(.39,.45,.42);
  page.drawRectangle({x:0,y:0,width:595.28,height:841.89,color:rgb(.973,.977,.961)});
  page.drawText('olhar.',{x:49,y:745,size:52,font:bold,color:blue});
  page.drawText('SEU GUIA PERSONALIZADO',{x:51,y:688,size:9,font:bold,color:gray});
  page.drawText('Fotografia',{x:49,y:620,size:39,font:bold,color:ink});
  page.drawText('com celular',{x:49,y:573,size:39,font:bold,color:ink});
  page.drawText('Um novo olhar para os registros do dia a dia.',{x:51,y:531,size:12,font,color:gray});
  page.drawLine({start:{x:51,y:493},end:{x:544,y:493},thickness:1,color:rgb(.83,.87,.82)});
  page.drawText('NESTA SELEÇÃO',{x:51,y:467,size:9,font:bold,color:blue});
  let nextPage=2;
  chosen.forEach((m,i)=>{const y=430-i*43;page.drawText(m.number,{x:51,y,size:10,font,color:gray});page.drawText(m.title,{x:82,y,size:12,font:bold,color:ink});page.drawText(String(nextPage),{x:526,y,size:10,font,color:gray});nextPage+=modulePageCount(m);});
  page.drawText(`${chosen.length} ${chosen.length===1?'tema selecionado':'temas selecionados'} | ${guidePageCount(chosen)} páginas`,{x:51,y:115,size:10,font,color:gray});
  page.drawText('Material educativo | Sebrae MT',{x:51,y:69,size:9,font,color:gray});
  page.drawText('Menus e recursos variam conforme o aparelho.',{x:51,y:51,size:8,font,color:gray});
  for(const m of chosen){const response=await fetch(`assets/pdf/${m.id}.pdf`);if(!response.ok)throw new Error('Não foi possível carregar uma apostila');const src=await PDFDocument.load(await response.arrayBuffer());const pages=await doc.copyPages(src,src.getPageIndices());pages.forEach(p=>{doc.addPage(p);p.drawRectangle({x:510,y:30,width:38,height:23,color:rgb(.973,.977,.961)});p.drawText(String(doc.getPageCount()).padStart(2,'0'),{x:527,y:39,size:8,font,color:gray});});}
  doc.setTitle('Meu guia de fotografia com celular');doc.setAuthor('Olhar | Sebrae MT');doc.setSubject(chosen.map(m=>m.title).join('; '));
  const bytes=await doc.save();const blob=new Blob([bytes],{type:'application/pdf'});const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='meu-guia-fotografia.pdf';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);notify('Seu PDF está pronto. Confira os downloads do navegador.');
 }catch(error){console.error(error);notify('Não foi possível gerar o PDF. Tente novamente ou baixe o e-book completo.');}
 finally{exportBusy=false;document.querySelectorAll('[data-action="export"]').forEach(b=>{b.innerHTML='Baixar meu PDF '+icon('download');b.removeAttribute('aria-busy');});updateState();}
}
init();
