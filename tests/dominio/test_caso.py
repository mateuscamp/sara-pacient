"""Regras do caso: visibilidade por seção, fato condicional, licença e ids (ADR-0002)."""

import pytest

from sara_pacient.dominio.caso import (
    Caso,
    CasoComIdRepetidoError,
    EspecialidadeForaDoEscopoError,
    Fato,
    FatoCondicionalSemCondicaoError,
    Fonte,
    IdDeFatoInvalidoError,
    LicencaNaoAceitaError,
    Revelacao,
    Secao,
    visivel_ao_ator,
)

GABARITO = {Secao.DIAGNOSTICO_AUTORES, Secao.RELEITURA, Secao.CONDUTA_DESFECHO, Secao.PONTOS_CHAVE}
MONTADO = Fonte(montado=True, origem="teste")


@pytest.mark.parametrize("secao", list(Secao))
def test_ator_ve_toda_secao_menos_o_gabarito(secao: Secao) -> None:
    assert visivel_ao_ator(secao) is (secao not in GABARITO)


def test_fato_condicional_exige_a_condicao_escrita() -> None:
    with pytest.raises(FatoCondicionalSemCondicaoError, match="alcool"):
        _ = Fato("alcool", Secao.PACIENTE_DIZ, "bebe à noite", Revelacao.CONDICIONAL)


def test_relato_publicado_exige_licenca_creative_commons_aceita() -> None:
    with pytest.raises(LicencaNaoAceitaError, match="by-nd"):
        _ = Fonte(
            montado=False,
            origem="relato",
            pmid="1",
            pmcid="PMC1",
            licenca_url="https://creativecommons.org/licenses/by-nd/4.0/",
        )


def test_relato_publicado_com_cc_by_carrega() -> None:
    fonte = Fonte(
        montado=False,
        origem="relato",
        pmid="1",
        pmcid="PMC1",
        licenca_url="https://creativecommons.org/licenses/by/4.0/",
    )

    assert fonte.pmcid == "PMC1"


def test_relato_publicado_exige_pmcid() -> None:
    with pytest.raises(LicencaNaoAceitaError, match="PMCID"):
        _ = Fonte(
            montado=False,
            origem="relato",
            licenca_url="https://creativecommons.org/licenses/by/4.0/",
        )


def test_caso_recusa_id_de_fato_repetido() -> None:
    fato = Fato("queixa", Secao.PACIENTE_DIZ, "dor", Revelacao.ESPONTANEO)

    with pytest.raises(CasoComIdRepetidoError, match="queixa"):
        _ = Caso("c1", "psiquiatria", "abertura", MONTADO, (fato, fato))


@pytest.mark.parametrize(
    "url",
    [
        "https://example.org/licenses/by/4.0/",
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    ],
)
def test_licenca_so_vale_no_creativecommons_e_sem_nd(url: str) -> None:
    with pytest.raises(LicencaNaoAceitaError):
        _ = Fonte(montado=False, origem="relato", pmcid="PMC1", licenca_url=url)


@pytest.mark.parametrize("id_ruim", ["", " ", "com espaço", "Maiuscula"])
def test_id_de_fato_e_slug_nao_vazio(id_ruim: str) -> None:
    # Achado 4 da review: id vazio ou com espaço impede a auditoria de apontar o fato.
    with pytest.raises(IdDeFatoInvalidoError):
        _ = Fato(id_ruim, Secao.PACIENTE_DIZ, "x", Revelacao.ESPONTANEO)


def test_especialidade_fora_do_escopo_e_recusada() -> None:
    # ADR-0004: o sara-pacient cobre psiquiatria e dor; anestesiologia fica só na skill, em texto.
    with pytest.raises(EspecialidadeForaDoEscopoError, match="anestesiologia"):
        _ = Caso("c1", "anestesiologia", "abertura", MONTADO, ())


@pytest.mark.parametrize("especialidade", ["psiquiatria", "dor"])
def test_psiquiatria_e_dor_sao_aceitas(especialidade: str) -> None:
    caso = Caso("c1", especialidade, "abertura", MONTADO, ())

    assert caso.especialidade == especialidade
