"""Trava de repositório aberto: todo caso versionado é montado (AGENTS.md, Dados).

Caso derivado de relato publicado, mesmo com licença CC, fica fora do git (`casos/`). A varredura
cobre o repositório inteiro, não só `exemplos/`: a /code-review achou um caso real salvo em
`tests/fixtures/` passando pela versão que só olhava `exemplos/`.
"""

import tomllib
from pathlib import Path

import pytest

from sara_pacient.infra.arquivo_caso import ler_caso

RAIZ = Path(__file__).parents[1]
# Pastas fora do git (.gitignore) ou de ferramenta: nada ali é publicado.
FORA_DO_GIT = {".venv", ".git", "casos", "pacotes", ".ruff_cache", ".pytest_cache"}


def _e_caso(caminho: Path) -> bool:
    # Arquivo de caso é o TOML com a tabela [fonte]; pyproject.toml e outros ficam de fora.
    return "fonte" in tomllib.loads(caminho.read_text(encoding="utf-8"))


def _casos_versionaveis() -> list[Path]:
    todos = (p for p in RAIZ.rglob("*.toml") if not FORA_DO_GIT & set(p.relative_to(RAIZ).parts))
    return sorted(p for p in todos if _e_caso(p))


CASOS = _casos_versionaveis()


@pytest.mark.parametrize("nome", ["caso-montado-exemplo.toml", "caso-montado-dor.toml"])
def test_os_exemplos_montados_sao_encontrados(nome: str) -> None:
    assert RAIZ / "exemplos" / nome in CASOS


@pytest.mark.parametrize("caminho", CASOS, ids=[str(p.relative_to(RAIZ)) for p in CASOS])
def test_todo_caso_versionado_e_montado(caminho: Path) -> None:
    assert ler_caso(caminho).fonte.montado, f"{caminho} não é montado: tire do repositório"
