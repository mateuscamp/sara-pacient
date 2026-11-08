# 0002 — O caso é um arquivo TOML validado, e a visibilidade vem da seção de cada fato

**Status:** Proposto
**Data:** 2026-11-08
**Driver ★:** ocultação do gabarito (a serviço da fidelidade, ADR-0001)

## Contexto

Na skill, a ficha é Markdown com as seções de gabarito "no fim", separadas por uma linha. Para o
ChatGPT Live, o usuário sobe um arquivo sem abrir: se o gabarito estiver nele, o modelo de voz o lê
e pode vazá-lo, e qualquer descuido do usuário estraga o caso. A separação precisa ser feita por
código, a partir de um dado que diga, fato por fato, a quem ele pertence.

## Alternativas consideradas

| Opção | Ganha | Perde | Por que não |
|---|---|---|---|
| Markdown com marcador de spoiler | igual à skill | separar é cortar texto por marcador; um título trocado vaza | frágil, sem tipo |
| Dois arquivos escritos à mão (ator e gabarito) | simples | o mesmo fato escrito duas vezes diverge; a auditoria não consegue ligar afirmação a fato | sem identidade de fato |
| YAML | legível, multilinha | dependência (PyYAML) e armadilhas de tipo implícito ("no" vira falso) | TOML resolve sem dependência |
| **TOML com fatos identificados por seção** | `tomllib` da stdlib; cada fato tem `id`, `secao`, `revelacao` | TOML é mais verboso que YAML para listas longas | — |

## Decisão

Um caso é um `.toml`: abertura, fonte (PMID, PMCID, DOI, licença ou `montado`) e uma lista de
`[[fatos]]`, cada um com `id` único, `secao`, `texto` e `revelacao` (`espontaneo`, `se_perguntado`
ou `condicional`, com a condição escrita). A seção decide a visibilidade num único `match`: as seções
do paciente, do acompanhante, do exame, da evolução e do risco vão ao ator; diagnóstico dos autores,
releitura, conduta e desfecho, e pontos-chave, nunca. O pacote do ator é gerado desse dado, nunca
escrito à mão. A borda valida com pydantic e entrega dataclasses congeladas ao domínio.

## Consequências

**Ganha:** a ocultação é uma função testada; o `id` do fato permite à auditoria apontar de onde veio
cada afirmação do paciente (ADR-0003).

**Perde:** quem prepara o caso (hoje um subagente da skill) escreve TOML, mais trabalhoso que
Markdown; as fichas Markdown já feitas no estudo-psi precisam de conversão.

**Aceito conscientemente:** a seção errada num fato (um diagnóstico posto em "paciente diz") vaza o
gabarito, e o código não percebe. Gatilho: se acontecer uma vez, acrescentar a revisão do caso antes
de gerar o pacote.

## Governança

| O que verifica | Mecanismo | Onde roda | Falha quando |
|---|---|---|---|
| caso inválido não carrega | validação pydantic na leitura, com teste | `make check` | campo faltando, `id` repetido, seção ou revelação desconhecida, licença fora da lista |
| fato condicional tem condição | validação no domínio, com teste | `make check` | `revelacao = "condicional"` sem `condicao` |

Regra derivada no `AGENTS.md`: "Pacote do ator só sai de `montar_pacote_ator`; nunca escreva texto de caso à mão em `infra/`."

## Notas

Autor: Claude (com Mateus Campelo) · Criado em: 2026-11-08
