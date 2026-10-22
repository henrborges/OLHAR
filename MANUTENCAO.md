# Atualizar os conteúdos e materiais

## Editar a página

| Alteração | Arquivo |
| --- | --- |
| Textos das aulas, roteiro de missões, checklist e referências | `content.json` |
| Estrutura, textos fixos e links da página | `index.html` |
| Cores, tipografia, espaçamento e responsividade | `style.css` |
| Comportamentos, seleção do guia e descrição dos vídeos | `app.js` |

Mantenha `content.json` como JSON válido. Os campos `id` vinculam os temas às
imagens e apostilas. Se alterar esses identificadores, atualize também as
referências e os nomes dos PDFs em `assets/pdf/`.

O campo `pdfPages` informa o número de páginas de uma apostila; quando ausente,
o site usa duas páginas. A apostila de Missões possui quatro. A capa do guia
personalizado acrescenta uma página à soma das apostilas selecionadas.

## Regenerar os PDFs

Os PDFs prontos já estão em `assets/pdf/`. Os passos abaixo são opcionais e
servem à manutenção. Use Python 3.10 ou mais recente, preferencialmente em um
ambiente virtual:

```sh
python -m venv .venv
```

Ative com `.venv/Scripts/activate` no Windows ou `source .venv/bin/activate`
no macOS/Linux. Em seguida:

```sh
python -m pip install -r tools/requirements.txt
python tools/make_pdfs.py
```

O script lê `content.json` e regrava as apostilas, o ebook e o checklist. Para
atualizar apenas uma apostila e o ebook completo:

```sh
python tools/make_pdfs.py --update-module missoes
```

Troque `missoes` pelo identificador do tema desejado. Depois de qualquer
alteração nos materiais, revise os PDFs e envie os arquivos atualizados à
hospedagem. Alterar o JSON não atualiza os PDFs automaticamente.

## Regenerar demonstrações e ilustrações

O script `tools/make_assets.py` utiliza as fotos e fontes já incluídas em
`assets/`. Além das bibliotecas Python acima, ele requer FFmpeg instalado no
computador e disponível no PATH, com o codificador `libx264`.

```sh
python tools/make_assets.py
```

Ele recria as seis ilustrações iniciais, o favicon, os três vídeos, capas e
legendas. A ilustração de Missões está incluída como `assets/missions.svg`.
Os vídeos são demonstrações ilustradas de 32 segundos, sem áudio; não são
gravações reais da tela de um celular.

Para substituir por vídeos próprios, mantenha os nomes ou ajuste `app.js`.
Atualize também duração, descrição, resumo em texto, capa e legendas `.vtt`.

## Arquivos temporários

`.venv/`, `__pycache__/` e `tmp/` são arquivos locais de trabalho, ignorados
pelo `.gitignore`. Não são necessários à publicação.

Os hashes em `INTEGRIDADE.sha256` descrevem a exportação original. Depois de
editar os arquivos, esses hashes deixam de representar os arquivos alterados.
