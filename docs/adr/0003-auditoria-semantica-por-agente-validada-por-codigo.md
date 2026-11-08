# 0003 — A auditoria da transcrição é classificada por um agente e validada por código

**Status:** Proposto
**Data:** 2026-11-08
**Driver ★:** fidelidade clínica

## Contexto

Depois da sessão de voz, cada afirmação do paciente precisa ser ligada a um fato do caso, a uma
omissão prevista, a um detalhe banal ou marcada como invenção. Ligar frase falada a fato é trabalho
semântico: exige modelo de linguagem. O usuário escolheu operar sem API nesta fase.

## Alternativas consideradas

| Opção | Ganha | Perde | Por que não |
|---|---|---|---|
| Casamento por palavras no código | determinístico, sem modelo | paráfrase falada não casa; falso "invenção" em massa | não mede o driver |
| API de modelo dentro da CLI | automático | chave de API, custo, e o usuário pediu sem API agora | fica como próximo canal (porta futura) |
| **Agente (Claude Code) classifica; código valida e conta** | sem API; o agente que já prepara o caso faz a leitura | a classificação depende da disciplina do agente | — |

## Decisão

O agente lê a transcrição e o caso e escreve um arquivo de auditoria em que cada afirmação do
paciente aponta um `id` de fato existente ou uma classe (`omissao_prevista`, `banal`, `invencao`).
A CLI valida esse arquivo contra o caso (todo `id` existe, toda fala do paciente foi classificada)
e calcula o placar. Quando houver API, o classificador vira uma porta com dois adaptadores: o
arquivo escrito pelo agente e a chamada ao modelo.

## Consequências

**Ganha:** a parte verificável (ids, cobertura, placar) é código testado; a parte semântica fica com
quem a faz melhor sem custo novo.

**Perde:** a classificação em si não é testada; um agente pode marcar como fato o que foi invenção.

**Aceito conscientemente:** esse risco, mitigado pela revisão humana do placar na correção. Gatilho:
divergência entre o placar e a percepção do usuário em duas sessões leva a uma segunda leitura
independente (outro agente) antes do placar.

## Governança

| O que verifica | Mecanismo | Onde roda | Falha quando |
|---|---|---|---|
| auditoria aponta fatos reais | validação com teste | `make check` | `id` inexistente no caso |
| nenhuma fala do paciente fica sem classe | validação com teste | `make check` | fala do paciente sem classificação |

Regra derivada no `AGENTS.md`: "Placar de auditoria só sai da validação do código; nunca conte à mão."

## Notas

Autor: Claude (com Mateus Campelo) · Criado em: 2026-11-08
Fatia de implementação: depois do pacote do ator (ADR-0002).
