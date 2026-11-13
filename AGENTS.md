# sara-pacient

Paciente simulado a partir de relato de caso real: caso estruturado, pacote do ator sem gabarito
para o canal de voz e auditoria da transcrição. Material de estudo, não decisão clínica.
Arquitetura: monólito modular, CLI local · Quantum: 1. ADRs em `docs/adr/`.
Método clínico (fidelidade, correção): skill `casos-ai-first`, que este projeto implementa em código.

## Comandos

- Setup: `uv sync`.
- Testes: `make test`.
- Portão (formato, lint, tipos, fronteiras, testes, dependências): `make check`.
- Pacote do ator: `uv run sara-pacient pacote <caso.toml> <pasta-destino>`.

Rodar `make check` antes de declarar qualquer tarefa concluída e mostrar a saída.

## Fronteiras (ADR-0001)

| Pasta | Papel | Padrão | Testes |
|---|---|---|---|
| `src/sara_pacient/dominio/` | núcleo: caso, visibilidade, auditoria | modelo de domínio, funções puras | unidade, sem E/S |
| `src/sara_pacient/infra/` | leitura de caso, canais de voz | adaptadores | com arquivos em `tmp_path` |
| `src/sara_pacient/cli.py` | interface | casca fina | funcional da história |

- `dominio/` não importa `infra/`, `cli`, `config`, pydantic, `os` nem rede (import-linter).
- Canal de voz novo é módulo de `infra/`; `dominio/` não muda para recebê-lo.
- Pacote do ator só sai de `montar_pacote_ator`; nunca escreva texto de caso à mão em `infra/`.
- Seção nova de caso: decidir a visibilidade no `match` de `visivel_ao_ator`, com teste, e ADR se
  mudar o que o ator vê.
- Placar de auditoria só sai da validação do código; nunca conte à mão.
- Especialidades: psiquiatria (foco) e dor (ADR-0004). Anestesiologia fica só na skill, em texto.
- Regra do personagem por especialidade fica no `match` do canal, com teste; nunca no arquivo de
  caso (ADR-0006).
- sara-aux-diag só por arquivo (`transcricao.jsonl`); nunca importe `sara` (ADR-0005).
- Regra clínica que não está escrita aqui nem na skill: perguntar, não inferir.

## Linguagem

| Termo | Significa | Não usar |
|---|---|---|
| `Caso` | o relato estruturado, com fonte e fatos | ficha, case |
| `Especialidade` | psiquiatria ou dor; decide as instruções do ator e o título do risco | área |
| `Fato` | uma afirmação do caso, com `id`, `secao` e `revelacao` | item, dado |
| `Secao` | a parte do caso a que o fato pertence; decide a visibilidade | categoria |
| gabarito | seções que o ator nunca vê: diagnóstico, releitura, conduta e desfecho, pontos-chave | spoiler (no código) |
| `PacoteAtor` | o que o canal de voz recebe: abertura e fatos visíveis | prompt |
| canal | o meio da conversa por voz (ChatGPT Live manual; API no futuro) | provider |

## Estilo de código

- Funções de 4 a 20 linhas; arquivos abaixo de 500 linhas; máximo 2 níveis de indentação.
- Nomes específicos; proibidos `data`, `info`, `handler`, `manager`, `helper`, `utils`, `service`.
- Mensagem de exceção com o valor recebido e o formato esperado.
- Comentário diz o porquê; não apagar comentário de proveniência em refactor.

## Ciclo de mudança (TDD)

1. Vermelho: um teste, um comportamento, visto falhar NA ASSERÇÃO (`ImportError` não conta).
2. Verde: o mínimo que passa, sem editar o teste; suíte inteira.
3. Refatorar com a suíte verde; `make check`; commit.

- Antes do commit, erro deliberado: troque a implementação por uma errada plausível; se nenhum teste
  falha, falta teste.
- História com teste funcional: ele vem primeiro e é o critério de pronto.
- Bug: teste de regressão visto falhando, depois o conserto, no mesmo commit.
- O commit diz o comando, o vermelho de antes e o verde de depois.
- Proibido para ficar verde: mudar asserção, `skip`/`xfail` sem motivo, apagar teste, mockar o
  sujeito, `try/except` no teste, `sleep`.

## Revisão antes do PR

- Todo diff: `/code-review` no esforço da sessão (nunca abaixo de high, nível explícito) e depois a
  `code-audit`, que parte dos achados da review e confere o vermelho dos testes novos.
- Achado não se corrige sem o sim do humano.

## Python

- Ambiente: `uv`. Dependência entra com `uv add`, com justificativa no relatório. Hoje: pydantic
  (validação do arquivo de caso na borda).
- Proibido mexer em `[tool.ruff]`, `[tool.basedpyright]`, `[tool.pytest]`, `[tool.importlinter]`,
  `[tool.trilhos]`, `scripts/portao.sh`, `Makefile`, hook e CI, ou criar config paralela. Regra
  parece errada? Diga no relatório e pare. `trilhos: pare`: relate e pare.
- Supressão só com regra e motivo: `# pyright: ignore[reportX]  # motivo: ...`. `cast` também.
- Sem `Any`; sem `dict` solto atravessando funções. Miolo: `@dataclass(frozen=True, slots=True)`.
  Borda (arquivo TOML): pydantic, validado na entrada.
- Conjunto fechado: `Enum` + `match` com `assert_never`.
- Exceção de domínio própria; proibido `except Exception` e `except: pass`; `raise ... from`.
- `logging`, nunca `print` fora de `cli.py`.
- Fake de borda é classe tipada injetada; `Mock` reprova no portão.

## Dados

- Caso vem de relato publicado com licença CC aceita (CC BY, BY-SA, BY-NC, BY-NC-SA, CC0) ou é
  `montado`. Nada de dado de paciente real fora de relato publicado.
- Caso real de estudo não entra no repositório (`casos/` está no `.gitignore`); `exemplos/` só tem
  caso montado.

## Estrutura

```
src/sara_pacient/
  dominio/caso.py      Caso, Fato, Secao, Revelacao, Especialidade, visivel_ao_ator
  dominio/pacote.py    PacoteAtor, montar_pacote_ator
  infra/arquivo_caso.py  TOML -> Caso (pydantic)
  infra/canal_chatgpt_live.py  PacoteAtor -> arquivos para o Project do ChatGPT (instruções
                               e título do risco por especialidade)
  cli.py
tests/  espelha src/ (tests/dominio/test_pacote.py ...)
docs/adr/
exemplos/  casos montados para teste e demonstração
```
