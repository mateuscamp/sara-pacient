"""O caso clínico estruturado e a regra de quem pode saber cada fato (ADR-0002)."""

import re
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from typing import assert_never

# Licenças que permitem usar o relato como base de material de estudo; ND (sem derivação) não entra.
# Comparação pelo início do caminho na URL do creativecommons.org (skill casos-ai-first, seção 2).
LICENCAS_ACEITAS = (
    "/licenses/by/",
    "/licenses/by-sa/",
    "/licenses/by-nc/",
    "/licenses/by-nc-sa/",
    "/publicdomain/zero/",
)
# Id de fato em slug: a auditoria (ADR-0003) cita o fato pelo id, que não pode ser vazio nem
# ambíguo.
FORMATO_ID = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
HOSTS_CREATIVE_COMMONS = ("https://creativecommons.org", "http://creativecommons.org")


def licenca_aceita(url: str) -> bool:
    """Diz se a URL é de uma licença Creative Commons aceita.

    Exemplo: ``licenca_aceita("https://creativecommons.org/licenses/by/4.0/")`` é ``True``.
    """
    for host in HOSTS_CREATIVE_COMMONS:
        if url.startswith(host + "/"):
            return url.removeprefix(host).startswith(LICENCAS_ACEITAS)
    return False


class Especialidade(StrEnum):
    """Escopo do sara-pacient (ADR-0004, ADR-0007): psiquiatria em foco, dor e anestesiologia.

    Anestesiologia é só a avaliação pré-anestésica, que é entrevista; crise intraoperatória não
    cabe neste formato. A especialidade decide as instruções do ator e o título da seção de risco
    (ADR-0006).
    """

    PSIQUIATRIA = "psiquiatria"
    DOR = "dor"
    ANESTESIOLOGIA = "anestesiologia"


class Secao(StrEnum):
    """Parte do caso a que um fato pertence. Decide se o ator pode saber o fato."""

    PACIENTE_DIZ = "paciente_diz"
    ACOMPANHANTE_DIZ = "acompanhante_diz"
    OBSERVAVEL = "observavel"
    SO_COM_PERGUNTA_OU_MANOBRA = "so_com_pergunta_ou_manobra"
    EXAME_FISICO = "exame_fisico"
    EXAME_COMPLEMENTAR = "exame_complementar"
    EVOLUCAO = "evolucao"
    RISCO = "risco"
    DIAGNOSTICO_AUTORES = "diagnostico_autores"
    RELEITURA = "releitura"
    CONDUTA_DESFECHO = "conduta_desfecho"
    PONTOS_CHAVE = "pontos_chave"


class Revelacao(StrEnum):
    """Quando o paciente conta o fato."""

    ESPONTANEO = "espontaneo"
    SE_PERGUNTADO = "se_perguntado"
    CONDICIONAL = "condicional"


class CasoInvalidoError(ValueError):
    """O caso viola uma regra do formato (ADR-0002)."""


class FatoCondicionalSemCondicaoError(CasoInvalidoError):
    """Fato com revelação condicional e sem a condição escrita."""


class LicencaNaoAceitaError(CasoInvalidoError):
    """Relato publicado sem PMCID ou sem licença Creative Commons aceita."""


class IdDeFatoInvalidoError(CasoInvalidoError):
    """Id de fato vazio ou fora do formato slug (minúsculas, dígitos e hífen)."""


class CampoDeFatoInvalidoError(CasoInvalidoError):
    """Seção ou revelação de fato fora do conjunto fechado."""


class EspecialidadeForaDoEscopoError(CasoInvalidoError):
    """Especialidade que o sara-pacient não cobre (ADR-0004)."""


class CasoComIdRepetidoError(CasoInvalidoError):
    """Dois fatos com o mesmo id: a auditoria não saberia a qual a fala se liga."""


def ler_especialidade(texto: str) -> Especialidade:
    """Converte o texto do arquivo de caso na especialidade, ou recusa o que está fora do escopo.

    Exemplo: ``ler_especialidade("dor")`` é ``Especialidade.DOR``.
    """
    try:
        return Especialidade(texto)
    except ValueError as erro:
        aceitas = ", ".join(Especialidade)
        msg = f"especialidade {texto!r} fora do escopo: {aceitas}"
        raise EspecialidadeForaDoEscopoError(msg) from erro


def _ler_campo_de_fato[Membro: StrEnum](conjunto: type[Membro], texto: str, campo: str) -> Membro:
    """Converte o texto no membro do conjunto fechado, ou recusa dizendo os valores aceitos.

    Exemplo: ``_ler_campo_de_fato(Secao, "risco", "secao")`` é ``Secao.RISCO``.
    """
    try:
        return conjunto(texto)
    except ValueError as erro:
        aceitos = ", ".join(conjunto)
        msg = f"{campo} {texto!r} fora do conjunto: {aceitos}"
        raise CampoDeFatoInvalidoError(msg) from erro


def visivel_ao_ator(secao: Secao) -> bool:
    """Diz se o canal de voz pode receber fatos desta seção.

    Exemplo: ``visivel_ao_ator(Secao.RISCO)`` é ``True``; ``Secao.PONTOS_CHAVE`` é ``False``.
    """
    match secao:
        case (
            Secao.PACIENTE_DIZ
            | Secao.ACOMPANHANTE_DIZ
            | Secao.OBSERVAVEL
            | Secao.SO_COM_PERGUNTA_OU_MANOBRA
            | Secao.EXAME_FISICO
            | Secao.EXAME_COMPLEMENTAR
            | Secao.EVOLUCAO
            | Secao.RISCO
        ):
            return True
        case (
            Secao.DIAGNOSTICO_AUTORES
            | Secao.RELEITURA
            | Secao.CONDUTA_DESFECHO
            | Secao.PONTOS_CHAVE
        ):
            return False
        case _:
            assert_never(secao)


@dataclass(frozen=True, slots=True)
class Fato:
    """Uma afirmação do caso, identificada para a auditoria ligar fala a fato."""

    id: str
    secao: Secao
    texto: str
    revelacao: Revelacao
    condicao: str | None = None

    def __post_init__(self) -> None:
        # O tipo não segura texto cru em tempo de execução, e o código compara estes dois campos
        # por identidade (`is`): em texto, o fato sumia da ficha e a condição não era exigida.
        object.__setattr__(self, "secao", _ler_campo_de_fato(Secao, self.secao, "secao"))
        revelacao = _ler_campo_de_fato(Revelacao, self.revelacao, "revelacao")
        object.__setattr__(self, "revelacao", revelacao)
        if not FORMATO_ID.fullmatch(self.id):
            msg = f"id de fato {self.id!r} fora do formato slug (ex.: 'alcool-noturno')"
            raise IdDeFatoInvalidoError(msg)
        if self.revelacao is Revelacao.CONDICIONAL and not self.condicao:
            msg = (
                f"fato {self.id!r}: revelacao condicional exige 'condicao' com o texto da condição"
            )
            raise FatoCondicionalSemCondicaoError(msg)


@dataclass(frozen=True, slots=True)
class Fonte:
    """De onde o caso veio: relato publicado com licença aberta, ou montado."""

    montado: bool
    origem: str
    pmid: str | None = None
    pmcid: str | None = None
    doi: str | None = None
    licenca_url: str | None = None

    def __post_init__(self) -> None:
        if self.montado:
            return
        if not self.pmcid:
            msg = f"relato publicado sem PMCID (pmid={self.pmid!r})"
            raise LicencaNaoAceitaError(msg)
        licenca = self.licenca_url or ""
        if not licenca_aceita(licenca):
            msg = f"licença {licenca!r} fora da lista aceita: CC BY, BY-SA, BY-NC, BY-NC-SA ou CC0"
            raise LicencaNaoAceitaError(msg)


@dataclass(frozen=True, slots=True)
class Caso:
    """O relato estruturado: abertura, fonte e fatos."""

    id: str
    especialidade: Especialidade
    abertura: str
    fonte: Fonte
    fatos: tuple[Fato, ...]

    def __post_init__(self) -> None:
        # O tipo não segura texto cru em tempo de execução: sem a recusa aqui, especialidade fora
        # do escopo só estourava no assert_never do canal. O texto válido vira o membro do enum,
        # para que comparar por identidade (`is`) não tome o ramo errado em silêncio.
        object.__setattr__(self, "especialidade", ler_especialidade(self.especialidade))
        repetidos = sorted(i for i, n in Counter(f.id for f in self.fatos).items() if n > 1)
        if repetidos:
            msg = f"caso {self.id!r}: ids de fato repetidos {repetidos}"
            raise CasoComIdRepetidoError(msg)
