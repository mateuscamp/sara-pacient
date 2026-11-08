# 0005 — O sara-pacient fala com o sara-aux-diag por arquivo, sem importar código

**Status:** Aceito
**Data:** 2026-11-08
**Driver ★:** fidelidade clínica (ADR-0001), com troca de canal sem mexer no núcleo

## Contexto

O sara-aux-diag (`~/Projetos/sara-aux-diag`) preenche, a partir da transcrição, os critérios dos
protocolos de psiquiatria e dor e mostra cobertura e FALTA. Numa sessão simulada, o FALTA é o que o
médico em treino não perguntou: a parte da correção que hoje dependeria da leitura de um agente
já existe lá, medida e testada. O usuário pediu a ligação e um módulo de pacientes simulados no
sara-aux-diag.

Quantum: continuam 2 unidades independentes, uma por repositório, cada uma com seu dado e seu portão.

## Alternativas consideradas

| Opção | Ganha | Perde | Por que não |
|---|---|---|---|
| Juntar no sara-aux-diag | um portão, reuso direto | mistura a ferramenta de consulta real (consentimento, mascarador) com o simulador | o usuário escolheu manter separado |
| sara-pacient importa o sara-aux-diag | integração rápida | mudança interna do motor quebra o sara-pacient; portões amarrados | acoplamento de código |
| **Contrato por arquivo** | cada lado muda por dentro sem quebrar o outro | o formato do arquivo vira contrato; mudá-lo exige mudar os dois | — |

## Decisão

O contrato é o `transcricao.jsonl` do sara-aux-diag (`fala_id`, `falante_id`, `papel`,
`instante_s`, `texto`). O módulo de simulação mora no sara-aux-diag (`src/sara/simulacao/`, com ADR
lá) e traz a transcrição da sessão simulada pelo mascarador, como qualquer fonte. O sara-pacient não
importa nada do sara-aux-diag e vice-versa. A correção de uma sessão simulada usa os dois: a
fidelidade do paciente vem do sara-pacient (ADR-0003), a cobertura e o FALTA vêm do sara-aux-diag.

## Consequências

**Ganha:** o "o que faltou perguntar" sai de um motor já testado, não da leitura de um agente.

**Perde:** a transcrição exportada do ChatGPT Live precisa virar o formato do sara-aux-diag, e a
conversão é código novo de um dos lados; os dois repositórios precisam ser abertos para fechar uma
sessão.

**Aceito conscientemente:** mudança no formato do `transcricao.jsonl` passa a quebrar a ligação.
Gatilho: qualquer mudança nesse formato no sara-aux-diag pede teste de contrato dos dois lados.

## Governança

| O que verifica | Mecanismo | Onde roda | Falha quando |
|---|---|---|---|
| nenhum import cruzado | o outro pacote não é dependência no `pyproject.toml` (basedpyright reprova import não resolvido) e revisão | `make check` dos dois | um repositório declara o outro como dependência ou o importa |
| formato do contrato | teste de contrato no lado que converte, com transcrição de exemplo | `make check` | campo exigido ausente ou com tipo errado |

Regra derivada no `AGENTS.md`: "sara-aux-diag só por arquivo (`transcricao.jsonl`); nunca importe `sara`."

## Notas

Autor: Claude (com Mateus Campelo) · Decidido pelo usuário em 2026-11-08
