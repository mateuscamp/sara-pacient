# 0001 — O sara-pacient é uma CLI local com núcleo puro, e o canal de voz é um adaptador

**Status:** Proposto
**Data:** 2026-11-08
**Driver ★:** fidelidade clínica do paciente simulado

## Contexto

O treino com paciente simulado nasceu como protocolo em texto (skill `casos-ai-first`, usada no
estudo-psi). O usuário quer conversar com o paciente por voz. Hoje a voz é o modo Live do ChatGPT,
sem API: o caso entra num Project do ChatGPT como arquivo, e a transcrição volta depois. Mais tarde,
a voz pode vir por API (GPT-Live-1, gpt-realtime, Gemini Live), e essa troca não pode reescrever o
resto. Um usuário, uma máquina, dezenas de casos por ano, custo de operação zero hoje.

Quantum atual: 1. Uma CLI Python local; o dado são arquivos de caso e de sessão no disco do usuário.

## Drivers

| ★ | Característica | Origem | Como se mede |
|---|---|---|---|
| ★ | Fidelidade clínica | "o paciente não pode inventar histórico, mudar sintoma ou se contradizer" | afirmações do paciente classificadas como invenção pela auditoria; meta 0 que mude diagnóstico ou risco |
| | Ocultação do gabarito | o usuário não pode ver o diagnóstico antes de fechar o caso | nenhum fato de seção de gabarito no pacote do ator (teste) |
| | Troca do canal de voz | "sem API agora, mas essa opção deve ser possível no futuro" | arquivos de `dominio/` alterados ao acrescentar um canal: 0 |
| | Testabilidade | o núcleo precisa provar fidelidade sem voz, rede nem modelo | suíte sem rede; `make check` em menos de 60 s |
| | Rastreabilidade da fonte | relato real com licença aberta, ou caso montado declarado | caso sem PMCID e licença CC aceita, e não montado, não carrega |

## Alternativas consideradas

| Opção | Ganha | Perde | Por que não |
|---|---|---|---|
| Só a skill, sem código | zero manutenção | o pacote do ator e a auditoria ficam na disciplina do agente, sem teste | foi o que mostrou o limite: regra escrita não impede o vazamento |
| App com voz por API já | experiência final | custo por minuto, chave de API, frontend de áudio, antes de saber se a voz ensina | sem evidência de que a voz paga o custo |
| Serviço web com banco | multiusuário | rede, deploy e banco para um usuário só | nenhum driver de modularidade com evidência |
| **CLI local, núcleo puro, canal como adaptador** | testa a fidelidade sem voz; troca de canal sem tocar o núcleo | a voz manual (subir arquivo, exportar transcrição) é passo humano | — |

## Decisão

Monólito modular numa CLI. `dominio/` guarda o caso, a regra de visibilidade (o que o ator pode
saber) e, depois, a auditoria; não importa E/S, pydantic nem `infra/`. `infra/` lê os arquivos de
caso e implementa os canais. O primeiro canal é o ChatGPT Live manual: a CLI escreve o pacote do
ator (instruções e ficha só com o que o paciente sabe), o usuário sobe no Project sem abrir, conversa
e exporta a transcrição. O canal por API, quando vier, é outro módulo de `infra/` que consome o mesmo
pacote.

## Consequências

**Ganha:** a fidelidade e a ocultação viram testes do núcleo, que rodam sem voz; o canal por API
entra sem mudar `dominio/`.

**Perde:** no ChatGPT Live não controlamos o modelo durante a conversa: não há como impedir a
invenção ao vivo, só detectá-la depois na transcrição. O passo manual (subir, exportar) depende do
usuário e do que o ChatGPT deixa exportar.

**Aceito conscientemente:** a voz do ChatGPT pode improvisar mais que o protocolo permite. Gatilho
para revisitar: se a auditoria contar invenção que muda diagnóstico ou risco em sessões seguidas, o
canal por API (com o controlador clínico fora do modelo de voz) passa a ser necessário.

## Governança

| O que verifica | Mecanismo | Onde roda | Falha quando |
|---|---|---|---|
| `dominio/` sem E/S nem borda | import-linter, contrato do `pyproject.toml` | `make check`, hook Stop, CI | `dominio/` importa `infra`, `cli`, `config`, `pydantic`, `os`, rede |
| pacote do ator sem gabarito | teste parametrizado por toda seção do caso | `make check` | um fato de seção de gabarito aparece no pacote |
| toda seção tem visibilidade decidida | `match` com `assert_never` no domínio | basedpyright | seção nova sem caso no `match` |

Regra derivada no `AGENTS.md`: "Canal de voz novo é módulo de `infra/`; `dominio/` não muda para recebê-lo."

## Notas

Autor: Claude (com Mateus Campelo) · Criado em: 2026-11-08
