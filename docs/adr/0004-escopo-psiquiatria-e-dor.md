# 0004 — O sara-pacient cobre psiquiatria e dor; anestesiologia fica só na skill, em texto

**Status:** Aceito; ampliado pelo ADR-0007 (anestesiologia entra, só como avaliação pré-anestésica)
**Data:** 2026-11-08
**Driver ★:** fidelidade clínica (ADR-0001)

## Contexto

A skill `casos-ai-first` tem referência por especialidade: psiquiatria preenchida, dor e
anestesiologia em esqueleto. O usuário decidiu o escopo do software: psiquiatria em foco, dor em
segundo plano, e anestesiologia só como treino em texto na skill. É o mesmo par do sara-aux-diag,
cujos protocolos são de psiquiatria e dor.

## Alternativas consideradas

| Opção | Ganha | Perde | Por que não |
|---|---|---|---|
| Especialidade livre (texto) | nada a decidir | caso de anestesiologia entraria sem regras de seção nem instrução própria | o usuário fechou o escopo |
| **Lista fechada: psiquiatria e dor** | caso fora do escopo é recusado na leitura | acrescentar especialidade exige mudar o domínio e este ADR | — |

## Decisão

`Caso.especialidade` só aceita `psiquiatria` ou `dor` (hoje o enum `Especialidade`, ADR-0006); outro
valor é `EspecialidadeForaDoEscopoError`.
As seções e as instruções do canal continuam as mesmas para as duas; se a dor pedir seção ou
instrução própria, isso entra com teste e, se mudar o que o ator vê, com ADR.

## Consequências

**Ganha:** o escopo fica no código, e o mesmo par do sara-aux-diag facilita a ligação entre os dois.

**Perde:** anestesiologia, inclusive a avaliação pré-anestésica, não roda por voz aqui.

**Aceito conscientemente:** o título "Pensamentos de morte, violência, autocuidado" da seção de risco
é de psiquiatria; num caso de dor ele ainda serve, mas pode pedir ajuste. Gatilho: o primeiro caso de dor.
Atingido em 2026-11-10: as instruções e o título do risco passam a ser por especialidade (ADR-0006).

## Governança

| O que verifica | Mecanismo | Onde roda | Falha quando |
|---|---|---|---|
| especialidade no escopo | teste do domínio | `make check` | `anestesiologia` ou outro valor carrega |

Regra derivada no `AGENTS.md`: "Especialidades: psiquiatria (foco) e dor (ADR-0004)."

## Notas

Autor: Claude (com Mateus Campelo) · Decidido pelo usuário em 2026-11-08
