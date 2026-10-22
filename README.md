# Olhar — Fotografia com celular

Portal de aprendizagem com sete temas, vídeos ilustrados, apostilas, ebook,
checklist e montagem de PDF personalizado. Inclui o módulo **Cobertura de
Missões**, voltado a aprendizados, conexões e insights.

## Publicar rapidamente

1. Descompacte o ZIP e abra a pasta `olhar`.
2. Envie **o conteúdo dessa pasta** para a raiz do repositório no GitHub.
3. Abra **Settings → Pages**.
4. Em **Source**, escolha **Deploy from a branch**, branch **main** e pasta
   **/(root)**. Salve e aguarde a publicação.

O arquivo `index.html` precisa ficar na raiz do repositório, junto de `app.js`,
`style.css`, `content.json` e `assets/`. O arquivo `.nojekyll` já está incluído.
Leia [PUBLICACAO.md](PUBLICACAO.md) para o passo a passo e outras hospedagens.

## O que acompanha o pacote

| Caminho | Conteúdo |
| --- | --- |
| `index.html` | Estrutura da página |
| `style.css` | Identidade visual e layout responsivo |
| `app.js` | Aulas, busca, filtros, simulador e PDF personalizado |
| `content.json` | Textos das aulas, roteiro de missões e checklist |
| `assets/` | Imagens, fontes locais, vídeos, legendas, biblioteca PDF e licenças |
| `assets/pdf/` | Sete apostilas, ebook completo e checklist |
| `tools/` | Scripts opcionais para regenerar PDFs, ilustrações e vídeos |
| `CREDITOS.md` | Créditos e dependências |
| `INTEGRIDADE.sha256` | Hashes dos arquivos do pacote |

## Executar no computador

Abra um terminal dentro da pasta `olhar` e execute:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Em alguns sistemas, use `python3` ou `py -3` no lugar de `python`.
Abra [http://localhost:8000/](http://localhost:8000/) no navegador.
Para encerrar, pressione Ctrl+C no terminal.

O carregamento das aulas e a montagem do PDF usam `fetch`; por isso, execute
pelo servidor local ou por uma hospedagem HTTP/HTTPS. Abrir `index.html` por
duplo clique pode impedir essas funções.

## Manutenção

Edite `content.json` para atualizar os textos. Leia [MANUTENCAO.md](MANUTENCAO.md)
para manter os PDFs em sincronia e regenerar os materiais.

## Funcionamento e acesso

O site funciona com arquivos estáticos e JavaScript no navegador. A hospedagem
não precisa de Node.js, Python, banco de dados, chaves de API ou conta no
ChatGPT. Python só é usado para visualizar localmente ou recriar materiais.

A seleção do guia e a conclusão dos temas são salvas neste navegador, em
`localStorage`. Ao trocar de domínio, o navegador inicia um novo armazenamento;
o progresso do endereço anterior não é transferido automaticamente.

O pacote não inclui autenticação. Para uso restrito aos colaboradores,
configure o controle de acesso na hospedagem. Consulte a observação sobre
visibilidade do GitHub Pages em [PUBLICACAO.md](PUBLICACAO.md).
