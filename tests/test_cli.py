"""Teste funcional da história: o pacote do ator para o ChatGPT Live (ADR-0001, ADR-0002)."""

from pathlib import Path

import pytest

from sara_pacient.cli import main

EXEMPLO = Path(__file__).parents[1] / "exemplos" / "caso-montado-exemplo.toml"


def _texto_de_todos(pasta: Path) -> str:
    return "\n".join(arquivo.read_text(encoding="utf-8") for arquivo in sorted(pasta.iterdir()))


def test_pacote_leva_o_que_o_paciente_sabe_e_nunca_o_gabarito(tmp_path: Path) -> None:
    destino = tmp_path / "pacote"

    codigo = main(["pacote", str(EXEMPLO), str(destino)])

    assert codigo == 0
    gerado = _texto_de_todos(destino)
    assert "Acorda às 4 da manhã" in gerado
    assert "Só conta se perguntarem sobre bebida duas vezes" in gerado
    assert "Episódio depressivo maior" not in gerado
    assert "excluir hipotireoidismo" not in gerado


def test_caso_invalido_sai_com_2_e_motivo_no_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Achado 6 da review: o caminho de erro da CLI não tinha teste.
    caso = tmp_path / "caso.toml"
    _ = caso.write_text("id = ", encoding="utf-8")

    codigo = main(["pacote", str(caso), str(tmp_path / "p")])

    assert codigo == 2
    assert "caso.toml" in capsys.readouterr().err


def test_destino_que_e_arquivo_sai_com_2_sem_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    destino = tmp_path / "ocupado"
    _ = destino.write_text("x", encoding="utf-8")

    codigo = main(["pacote", str(EXEMPLO), str(destino)])

    assert codigo == 2
    assert "ocupado" in capsys.readouterr().err
