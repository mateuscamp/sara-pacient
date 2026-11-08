"""Canal ChatGPT Live: o pacote vira dois arquivos, sem caso nas instruções e sem sobrescrever."""

from pathlib import Path

import pytest

from sara_pacient.dominio.caso import Fato, Revelacao, Secao, visivel_ao_ator
from sara_pacient.dominio.pacote import PacoteAtor
from sara_pacient.infra.canal_chatgpt_live import (
    DestinoInvalidoError,
    DestinoOcupadoError,
    escrever_pacote,
)

INSONIA = Fato("insonia", Secao.PACIENTE_DIZ, "Acorda às 4 da manhã.", Revelacao.ESPONTANEO)
ALCOOL = Fato(
    "alcool",
    Secao.PACIENTE_DIZ,
    "Bebe à noite.",
    Revelacao.CONDICIONAL,
    "Só conta na segunda pergunta.",
)
PACOTE = PacoteAtor("c1", "psiquiatria", "Ambulatório, 42 anos.", (INSONIA, ALCOOL))


def test_ficha_do_paciente_leva_cada_fato_com_a_regra_de_revelacao(tmp_path: Path) -> None:
    escritos = escrever_pacote(PACOTE, tmp_path / "pacote")

    ficha = next(p for p in escritos if p.name == "paciente.md").read_text(encoding="utf-8")
    assert "Acorda às 4 da manhã." in ficha
    assert "Só conta na segunda pergunta." in ficha
    assert "Ambulatório, 42 anos." in ficha


def test_instrucoes_nao_carregam_nada_do_caso(tmp_path: Path) -> None:
    escritos = escrever_pacote(PACOTE, tmp_path / "pacote")

    instrucoes = next(p for p in escritos if p.name == "instrucoes.md").read_text(encoding="utf-8")
    assert instrucoes.strip()
    assert "Acorda às 4" not in instrucoes
    assert "Bebe à noite" not in instrucoes


def test_destino_com_arquivos_e_recusado_sem_tocar_nele(tmp_path: Path) -> None:
    destino = tmp_path / "pacote"
    destino.mkdir()
    antigo = destino / "paciente.md"
    _ = antigo.write_text("anterior", encoding="utf-8")

    with pytest.raises(DestinoOcupadoError, match="pacote"):
        _ = escrever_pacote(PACOTE, destino)

    assert antigo.read_text(encoding="utf-8") == "anterior"


@pytest.mark.parametrize("secao", [s for s in Secao if visivel_ao_ator(s)])
def test_nenhum_fato_visivel_some_da_ficha(secao: Secao, tmp_path: Path) -> None:
    fato = Fato("f1", secao, f"marca-{secao.value}", Revelacao.SE_PERGUNTADO)
    pacote = PacoteAtor("c1", "psiquiatria", "Abertura.", (fato,))

    escritos = escrever_pacote(pacote, tmp_path / "pacote")

    ficha = next(p for p in escritos if p.name == "paciente.md").read_text(encoding="utf-8")
    assert f"marca-{secao.value}" in ficha


def test_destino_que_e_arquivo_e_recusado_com_erro_proprio(tmp_path: Path) -> None:
    # Achado 2 da review: NotADirectoryError escapava como traceback.
    arquivo = tmp_path / "pacote"
    _ = arquivo.write_text("x", encoding="utf-8")

    with pytest.raises(DestinoInvalidoError, match="pacote"):
        _ = escrever_pacote(PACOTE, arquivo)


def test_texto_multilinha_vira_um_item_so_da_ficha(tmp_path: Path) -> None:
    # Achado 3 da review: a segunda linha saía fora do item, sem a regra de revelação.
    fato = Fato("f1", Secao.PACIENTE_DIZ, "linha um\nlinha dois", Revelacao.SE_PERGUNTADO)
    pacote = PacoteAtor("c1", "psiquiatria", "Abertura.", (fato,))

    escritos = escrever_pacote(pacote, tmp_path / "pacote")

    ficha = next(p for p in escritos if p.name == "paciente.md").read_text(encoding="utf-8")
    assert "- linha um linha dois (só se perguntarem)" in ficha
