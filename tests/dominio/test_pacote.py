"""O pacote do ator leva só o que o paciente pode saber (ADR-0002)."""

import pytest

from sara_pacient.dominio.caso import (
    Caso,
    Especialidade,
    Fato,
    Fonte,
    Revelacao,
    Secao,
    visivel_ao_ator,
)
from sara_pacient.dominio.pacote import PacoteSemFatosError, montar_pacote_ator

MONTADO = Fonte(montado=True, origem="teste")


def _caso(*fatos: Fato) -> Caso:
    return Caso("c1", Especialidade.PSIQUIATRIA, "Ambulatório, 40 anos.", MONTADO, fatos)


@pytest.mark.parametrize("secao", list(Secao))
def test_fato_entra_no_pacote_so_se_a_secao_for_visivel(secao: Secao) -> None:
    fato = Fato("f1", secao, "texto", Revelacao.SE_PERGUNTADO)
    # Um fato visível ao lado: caso sem nenhum visível não vira pacote (achado 7).
    queixa = Fato("queixa", Secao.PACIENTE_DIZ, "dor", Revelacao.ESPONTANEO)

    pacote = montar_pacote_ator(_caso(fato, queixa))

    assert (fato in pacote.fatos) is visivel_ao_ator(secao)


def test_pacote_mantem_abertura_e_ordem_dos_fatos_visiveis() -> None:
    primeiro = Fato("a", Secao.PACIENTE_DIZ, "um", Revelacao.ESPONTANEO)
    gabarito = Fato("b", Secao.DIAGNOSTICO_AUTORES, "dois", Revelacao.SE_PERGUNTADO)
    segundo = Fato("c", Secao.RISCO, "três", Revelacao.SE_PERGUNTADO)

    pacote = montar_pacote_ator(_caso(primeiro, gabarito, segundo))

    assert pacote.abertura == "Ambulatório, 40 anos."
    assert pacote.fatos == (primeiro, segundo)


def test_caso_sem_fato_visivel_nao_vira_pacote() -> None:
    # Achado 7 da review: um paciente sem história faria o canal improvisar tudo.
    gabarito = Fato("d", Secao.RELEITURA, "x", Revelacao.SE_PERGUNTADO)

    with pytest.raises(PacoteSemFatosError, match="c1"):
        _ = montar_pacote_ator(_caso(gabarito))
