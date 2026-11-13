"""Leitura do caso em TOML: o exemplo carrega e o arquivo errado é recusado com o motivo."""

from pathlib import Path

import pytest

from sara_pacient.dominio.caso import Especialidade, Revelacao, Secao
from sara_pacient.infra.arquivo_caso import ArquivoDeCasoInvalidoError, ler_caso

EXEMPLO = Path(__file__).parents[2] / "exemplos" / "caso-montado-exemplo.toml"

CABECALHO = """
id = "c1"
especialidade = "psiquiatria"
abertura = "Ambulatório."

[fonte]
montado = true
origem = "teste"
"""


UM_FATO = """
[[fatos]]
id = "f1"
secao = "paciente_diz"
texto = "x"
revelacao = "espontaneo"
"""


def _escrever(tmp_path: Path, corpo: str) -> Path:
    caminho = tmp_path / "caso.toml"
    _ = caminho.write_text(corpo, encoding="utf-8")
    return caminho


def test_exemplo_carrega_com_fatos_tipados() -> None:
    caso = ler_caso(EXEMPLO)

    assert caso.id == "exemplo-montado-insonia"
    alcool = next(f for f in caso.fatos if f.id == "alcool-noturno")
    assert alcool.secao is Secao.PACIENTE_DIZ
    assert alcool.revelacao is Revelacao.CONDICIONAL


def test_secao_desconhecida_e_recusada_com_o_valor(tmp_path: Path) -> None:
    corpo = (
        CABECALHO
        + """
[[fatos]]
id = "f1"
secao = "diagnostico"
texto = "x"
revelacao = "espontaneo"
"""
    )
    with pytest.raises(ArquivoDeCasoInvalidoError, match="diagnostico"):
        _ = ler_caso(_escrever(tmp_path, corpo))


def test_campo_desconhecido_e_recusado(tmp_path: Path) -> None:
    corpo = CABECALHO.replace('abertura = "Ambulatório."', 'abertura = "A."\nspoiler = "x"')
    with pytest.raises(ArquivoDeCasoInvalidoError, match="spoiler"):
        _ = ler_caso(_escrever(tmp_path, corpo))


def test_regra_do_dominio_vira_erro_do_arquivo(tmp_path: Path) -> None:
    corpo = (
        CABECALHO
        + """
[[fatos]]
id = "f1"
secao = "paciente_diz"
texto = "x"
revelacao = "condicional"
"""
    )
    with pytest.raises(ArquivoDeCasoInvalidoError, match="condicao"):
        _ = ler_caso(_escrever(tmp_path, corpo))


def test_especialidade_vira_o_tipo_do_dominio(tmp_path: Path) -> None:
    corpo = CABECALHO.replace('"psiquiatria"', '"dor"') + UM_FATO

    assert ler_caso(_escrever(tmp_path, corpo)).especialidade is Especialidade.DOR


def test_especialidade_fora_do_escopo_e_recusada_no_arquivo(tmp_path: Path) -> None:
    # ADR-0004 e ADR-0007: especialidade fora da lista fechada não carrega.
    corpo = CABECALHO.replace('"psiquiatria"', '"cardiologia"') + UM_FATO
    with pytest.raises(ArquivoDeCasoInvalidoError, match="cardiologia"):
        _ = ler_caso(_escrever(tmp_path, corpo))


def test_toml_quebrado_e_recusado_com_o_caminho(tmp_path: Path) -> None:
    caminho = _escrever(tmp_path, "id = ")
    with pytest.raises(ArquivoDeCasoInvalidoError, match=r"caso\.toml"):
        _ = ler_caso(caminho)


def test_erro_de_validacao_nao_mostra_o_texto_do_gabarito(tmp_path: Path) -> None:
    # Achado 1 da review: o pydantic ecoava o fato inteiro (input_value) no erro.
    corpo = (
        CABECALHO
        + """
[[fatos]]
id = "diagnostico"
secao = "diagnostico_autores"
texto = "SEGREDO-DO-GABARITO"
"""
    )
    with pytest.raises(ArquivoDeCasoInvalidoError) as erro:
        _ = ler_caso(_escrever(tmp_path, corpo))

    assert "revelacao" in str(erro.value)
    assert "SEGREDO-DO-GABARITO" not in str(erro.value)
