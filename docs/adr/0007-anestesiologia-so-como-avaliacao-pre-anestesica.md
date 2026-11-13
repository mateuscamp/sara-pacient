# 0007 — Anestesiologia entra no escopo, só como avaliação pré-anestésica

**Status:** Aceito
**Data:** 2026-11-13
**Driver ★:** fidelidade clínica (ADR-0001)

## Contexto

O ADR-0004 fechou o escopo em psiquiatria e dor e deixou a anestesiologia só na skill, em texto. Em
2026-11-13 o usuário pediu o módulo de anestesiologia aqui. A skill `casos-ai-first` (seção 9) e a
`references/anestesiologia.md` dela separam dois formatos:

- a **avaliação pré-anestésica** é entrevista e cabe nas mesmas seções de caso;
- a **crise intraoperatória** (monitor, relógio, decisão em segundos) não é entrevista e pede skill
  própria.

A `references/anestesiologia.md` continua "não preenchida". As regras do personagem saíram do
material de estudo do usuário (`~/Documents/Estudo Anestesiologia`): apostila do Portal Anestesia,
TSA 2019, aula 09, "Avaliação pré-operatória", seções Anamnese, Vias aéreas, Exame físico e
Fitoterápicos. O que a apostila diz e virou regra:

- o paciente alega "alergia" ao que foi efeito colateral esperado, e o médico precisa perguntar
  qual foi a reação;
- a história pessoal e familiar de complicação anestésica é pesquisada por pergunta, e o paciente
  não sabe o nome do que houve;
- suplemento e fitoterápico não entram na lista de remédios do paciente se não forem perguntados;
- a tolerância ao exercício se mede por atividade do dia a dia;
- o exame das vias aéreas é a parte do exame físico que mais importa ao anestesiologista.

## Alternativas consideradas

| Opção | Ganha | Perde | Por que não |
|---|---|---|---|
| Manter o ADR-0004 | nada muda | a pré-anestésica não roda por voz | o usuário pediu o módulo |
| Anestesiologia inteira, com a crise | um nome só cobre tudo | a crise não tem seção, visibilidade nem canal neste formato | não é entrevista |
| Esperar a skill preencher a referência | a regra nasce no lugar certo | o módulo para até lá | o usuário apontou a fonte; a skill recebe as mesmas regras depois |
| **`Especialidade.ANESTESIOLOGIA`, só pré-anestésica, com regras e título próprios no `match`** | o caso roda hoje; o `match` obriga a decidir instruções e título | o nome do enum é mais largo que o formato coberto | — |

## Decisão

`Especialidade` ganha `anestesiologia`, que neste repositório significa avaliação pré-anestésica.
O canal ChatGPT Live dá a ela, pelo `match` do ADR-0006:

- exemplos de termo técnico proibido: "via aérea difícil", "apneia obstrutiva", "hipertermia maligna";
- cinco regras próprias: alergia, anestesias anteriores e de parentes, remédios e produtos
  naturais, fôlego por atividade, exame da boca e do pescoço;
- título da seção `risco`: "Anestesias anteriores e na família, alergias, fumo, álcool e outras
  substâncias".

As regras não levam exemplo de complicação (febre, rigidez, demora para acordar): o modelo de voz
tende a repetir o exemplo como se fosse fato do caso. As seções e a visibilidade não mudam.

## Consequências

**Ganha:** caso de pré-anestésica gera pacote sem gabarito, com exemplo montado em
`exemplos/caso-montado-anestesiologia.toml`.

**Perde:** o ADR-0004 deixa de valer na parte "anestesiologia fica só na skill"; a lista continua
fechada, e `cardiologia` ou outro valor segue recusado. Crise intraoperatória continua fora.
O sara-aux-diag só tem protocolos de psiquiatria e dor (ADR-0005): a sessão de pré-anestésica não
ganha cobertura nem FALTA de lá, e "o que faltou perguntar" fica com a leitura dos pontos-chave do
caso, até existir protocolo de anestesiologia no sara-aux-diag.

**Aceito conscientemente:**

- As regras e o título nasceram da apostila (2019), lidas por um agente, não de uma sessão nem da
  skill. Gatilho: a primeira sessão de pré-anestésica por voz revisa as regras e o título.
- A `references/anestesiologia.md` da skill segue "não preenchida", e o código está à frente dela.
  Gatilho: ao preencher a referência, conferir as cinco regras contra ela e ajustar aqui.
- O gabarito do exemplo montado cita só o que a aula 09 traz (estado físico, preditores de via
  aérea, apneia do sono, fitoterápicos); conduta não entra nele.

## Governança

| O que verifica | Mecanismo | Onde roda | Falha quando |
|---|---|---|---|
| anestesiologia carrega; fora da lista, não | testes do domínio e da leitura | `make check` | `anestesiologia` é recusada ou `cardiologia` carrega |
| anestesiologia tem instruções e título de risco | `match` com `assert_never` no canal | basedpyright | especialidade sem caso no `match` |
| instruções de uma especialidade não levam as da outra | teste do canal | `make check` | "hipertermia maligna" nas de psiquiatria ou dor; "anedonia" ou "0 a 10" nas de anestesiologia |
| caso de pré-anestésica gera pacote sem gabarito | teste funcional com o exemplo montado | `make check` | estado físico ou pontos-chave no pacote |

Regra derivada no `AGENTS.md`: "Especialidades: psiquiatria (foco), dor (ADR-0004) e anestesiologia,
só a avaliação pré-anestésica (ADR-0007)."

## Notas

Autor: Claude (com Mateus Campelo) · Escopo decidido e regras e título lidos e aprovados pelo
usuário em 2026-11-13.
