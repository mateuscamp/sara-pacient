"""O pacote do ator leva só o que o paciente pode saber (ADR-0002)."""

import pytest

from sara_pacient.dominio.caso import (
    Caso,
    Especialidade,
    EspecialidadeForaDoEscopoError,
    Fato,
    Fonte,
    Revelacao,
    Secao,
    visivel_ao_ator,
)
from sara_pacient.dominio.pacote import (
    GabaritoNoPacoteError,
    PacoteAtor,
    PacoteSemFatosError,
    montar_pacote_ator,
)

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


QUEIXA = Fato("queixa", Secao.PACIENTE_DIZ, "dor", Revelacao.ESPONTANEO)


def test_pacote_recusa_especialidade_crua_fora_do_escopo() -> None:
    # Achado C3 da review: o pacote inválido só estourava no canal, como AssertionError do
    # assert_never, que a CLI não trata. A recusa é a do domínio, a mesma do Caso.
    with pytest.raises(EspecialidadeForaDoEscopoError, match="cardiologia"):
        _ = PacoteAtor(
            "c1",
            "cardiologia",  # pyright: ignore[reportArgumentType]  # motivo: tipo errado de propósito
            "Abertura.",
            (QUEIXA,),
        )


def test_pacote_guarda_a_especialidade_como_enum_mesmo_vinda_em_texto() -> None:
    pacote = PacoteAtor(
        "c1",
        "dor",  # pyright: ignore[reportArgumentType]  # motivo: tipo errado de propósito
        "Abertura.",
        (QUEIXA,),
    )

    assert pacote.especialidade is Especialidade.DOR


def test_pacote_montado_a_mao_recusa_fato_de_gabarito() -> None:
    # Achado D1 da review: o filtro vivia só em montar_pacote_ator; o gabarito só não chegava à
    # ficha porque o canal não tem título para a seção.
    gabarito = Fato("dx", Secao.DIAGNOSTICO_AUTORES, "diagnóstico", Revelacao.SE_PERGUNTADO)

    # Achado E1 da review: com ValueError aqui, trocar a exceção própria pela classe-mãe
    # passava na suíte.
    with pytest.raises(GabaritoNoPacoteError, match="dx"):
        _ = PacoteAtor("c1", Especialidade.DOR, "Abertura.", (QUEIXA, gabarito))


def test_pacote_montado_a_mao_recusa_ficar_sem_fatos() -> None:
    # Achado E5 da review: a mensagem vai ao stderr da CLI e tinha sido encurtada só para caber
    # na linha; o texto fica fixado aqui.
    with pytest.raises(PacoteSemFatosError, match="'c1' sem nenhum fato visível ao ator"):
        _ = PacoteAtor("c1", Especialidade.DOR, "Abertura.", ())
