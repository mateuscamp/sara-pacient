# 0006 — As instruções do ator e o título do risco dependem da especialidade

**Status:** Proposto
**Data:** 2026-11-10
**Driver ★:** fidelidade clínica (ADR-0001)

## Contexto

O ADR-0004 deixou as seções e as instruções do canal iguais para psiquiatria e dor, com um gatilho:
o primeiro caso de dor. Ele chegou com o módulo de dor (skill `casos-ai-first`, `references/dor.md`,
preenchida a partir do estudo-dor: Benzon, 6ª ed., caps. 2, 15, 18, 22 e 51, e PCDT Dor Crônica
2024). Dois pontos das instruções de psiquiatria não servem à dor:

- os exemplos de termo técnico proibido ("alucinação", "ideação suicida", "anedonia") não dizem
  nada ao paciente de dor, que tende a dizer "dor neuropática" ou "irradia";
- o título da seção de risco ("Pensamentos de morte, violência, autocuidado") esconde o que a dor
  põe nela: sinais de alerta de doença grave, uso de opioide e outras substâncias, quedas.

E a dor tem regras que a psiquiatria não tem: a nota de 0 a 10 só quando pedida, o remédio dito
como leigo, a manobra de exame que a ficha não traz dita "não descrita", nunca "negativa".

## Alternativas consideradas

| Opção | Ganha | Perde | Por que não |
|---|---|---|---|
| Instruções únicas, com exemplos das duas | um texto só | o ator de psiquiatria lê regra de dor e vice-versa; regra que não se aplica é ruído que o modelo de voz segue mal | mistura |
| Instruções no arquivo de caso | quem prepara o caso ajusta | a regra do personagem vira texto escrito à mão por caso, contra a regra do `AGENTS.md` | sem teste, diverge |
| Seção nova `sinais_de_alerta` | o alerta fica separado | muda o formato do caso (ADR-0002) e a visibilidade, para um conteúdo que já é risco | maior que o problema |
| **`Especialidade` como enum; o canal escolhe instruções e título por `match`** | cada ator lê só as regras dele; especialidade nova não compila sem decidir as duas coisas | o canal guarda texto por especialidade | — |

## Decisão

`Especialidade` vira `Enum` fechado no domínio (`psiquiatria`, `dor`), lido do arquivo por
`ler_especialidade`, que recusa o que está fora do escopo (ADR-0004). O canal ChatGPT Live monta as
instruções a partir de regras comuns, com os exemplos de termo técnico e as regras próprias da
especialidade, e dá à seção `risco` o título da especialidade. As seções e a visibilidade não mudam:
o que vai ao ator continua decidido só por `visivel_ao_ator`.

## Consequências

**Ganha:** o paciente de dor recebe as regras de `references/dor.md`; as instruções de psiquiatria
mantêm o conteúdo (só muda a quebra de uma linha).

**Perde:** um canal por API, quando vier, precisa da mesma escolha por especialidade; o texto fica em
`infra/`, e o segundo canal terá de reaproveitá-lo em vez de copiar.

**Aceito conscientemente:** as regras da dor nasceram do livro, não de uma sessão. Gatilho: a primeira
sessão de dor por voz revisa as regras e o título, e o que mudar entra aqui e na skill.

## Governança

| O que verifica | Mecanismo | Onde roda | Falha quando |
|---|---|---|---|
| toda especialidade tem instruções e título de risco | `match` com `assert_never` no canal | basedpyright | especialidade nova sem caso no `match` |
| instruções de uma especialidade não levam as da outra | teste do canal | `make check` | "alodinia" nas de psiquiatria ou "anedonia" nas de dor |
| caso de dor gera pacote sem gabarito | teste funcional com `exemplos/caso-montado-dor.toml` | `make check` | diagnóstico ou pontos-chave no pacote |

Regra derivada no `AGENTS.md`: "Regra do personagem por especialidade fica no `match` do canal, com
teste; nunca no arquivo de caso."

## Notas

Autor: Claude (com Mateus Campelo) · Criado em: 2026-11-10
