# Publicar o Olhar

Este pacote contém uma cópia portátil do portal, com caminhos relativos.
Pode ser servido na raiz de um domínio ou em uma subpasta como `/olhar/`.
Os arquivos do site estão prontos: não há instalação de pacotes nem compilação
para publicar. Envie os arquivos extraídos, não apenas o ZIP, ao repositório.

## 1. GitHub Pages pelo navegador

1. Descompacte o pacote e abra a pasta `olhar`.
2. No GitHub, crie um repositório, por exemplo `olhar-fotografia`.
3. Envie o conteúdo de `olhar` pelo comando **Add file → Upload files**.
4. Confirme que `index.html`, `app.js`, `style.css`, `content.json` e `assets/`
   aparecem na raiz do repositório. Evite uma pasta `olhar` adicional nessa raiz.
5. Confirme que `.nojekyll` também foi enviado. Se a seleção de arquivos ocultos
   não o incluiu, crie-o usando **Add file → Create new file**, nome `.nojekyll`.
6. Confirme os arquivos no branch `main`.
7. Acesse **Settings → Pages → Build and deployment**.
8. Em **Source**, selecione **Deploy from a branch**; escolha **main** e
   **/(root)**. Clique em **Save**.
9. Aguarde a publicação e abra o endereço apresentado pelo GitHub.

O endereço de um site de projeto terá o formato
`https://SEU-USUARIO.github.io/olhar-fotografia/`, conforme sua conta e o nome
do repositório. Para atualizar, envie os arquivos alterados ao mesmo branch.
O arquivo `.nojekyll` indica que os arquivos estáticos serão servidos sem Jekyll.

### Visibilidade

Na configuração padrão, o site do GitHub Pages é público, inclusive quando
o repositório é privado. Repositório privado e acesso privado ao site são
configurações diferentes. Para restringir o portal à equipe, escolha e configure
uma hospedagem com autenticação compatível com a organização. A disponibilidade
do Pages para repositórios privados depende do plano.

Documentação oficial:

- [Configurar a fonte de publicação](https://docs.github.com/pt/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Criar um site do GitHub Pages](https://docs.github.com/pt/pages/getting-started-with-github-pages/creating-a-github-pages-site)

## 2. GitHub usando Git no computador

Crie primeiro um repositório vazio na sua conta. Abra o terminal dentro da
pasta `olhar` e substitua o endereço abaixo pelo endereço real do repositório:

```sh
git init
git branch -M main
git add .
git commit -m "Adicionar portal Olhar"
git remote add origin https://github.com/SEU-USUARIO/olhar-fotografia.git
git push -u origin main
```

Conclua a configuração do Pages em **Settings → Pages**, como descrito acima.
Use a autenticação normal do GitHub ou do seu cliente Git, sem inserir senhas
em arquivos do projeto.

## 3. Netlify

Para publicação manual, descompacte o ZIP e envie a pasta `olhar`, que contém
`index.html`, à área de publicação por arrastar e soltar do Netlify.
Confira o endereço informado após a publicação. Atualizações manuais usam a
mesma pasta com os arquivos atualizados.

Ao conectar um repositório, configure o diretório de publicação como `.` e
deixe o comando de build vazio. O arquivo `netlify.toml` incluído já indica
o diretório de publicação.

Documentação: [Netlify Drop](https://docs.netlify.com/start/quickstarts/netlify-drop-quickstart/).

## 4. Outras hospedagens estáticas ou servidor da organização

Envie para o diretório público do servidor:

- `index.html`, `style.css`, `app.js` e `content.json`;
- a pasta `assets/` completa, preservando nomes e subpastas.

Esses são os arquivos necessários à execução. A documentação e `tools/` podem
ficar somente no repositório de manutenção. Ative HTTPS e confira se o servidor
serve `.json`, `.js`, `.css`, `.svg`, `.ttf`, `.mp4`, `.vtt` e `.pdf` com tipos
de conteúdo adequados. Preserve o carregamento normal de arquivos estáticos;
não redirecione requisições de JSON ou PDFs para `index.html`.

Se a plataforma solicitar configurações: projeto estático/HTML, pasta pública
`.` e nenhum comando de build. As configurações de autenticação pertencem à
hospedagem escolhida.

## 5. Domínio próprio

Cadastre o domínio ou subdomínio no painel da hospedagem escolhida. Use os
registros DNS e as validações fornecidos por ela e conclua a ativação de HTTPS.
Não há um arquivo `CNAME` com endereço predefinido neste pacote.

## 6. Conferência após publicar

- A página carrega os sete temas, incluindo Cobertura de Missões.
- A busca encontra textos das aulas e do roteiro de missões.
- Os três vídeos abrem e seus arquivos podem ser baixados.
- Apostilas, ebook e checklist abrem normalmente.
- O PDF personalizado de todos os temas tem 17 páginas; só Missões tem 5.
- O layout funciona no celular e na tela do computador.

Se a página abrir, mas as aulas não aparecerem, confira se `content.json` está
na mesma pasta de `index.html`. Para erros em vídeos ou PDFs, confira o envio
integral de `assets/` e mantenha os nomes originais, incluindo maiúsculas e
minúsculas.
