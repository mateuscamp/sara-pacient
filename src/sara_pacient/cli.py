"""Interface de linha de comando do sara-pacient. Único módulo que escreve no terminal."""

import argparse
import sys
from pathlib import Path

from sara_pacient.dominio.pacote import PacoteSemFatosError, montar_pacote_ator
from sara_pacient.infra.arquivo_caso import ArquivoDeCasoInvalidoError, ler_caso
from sara_pacient.infra.canal_chatgpt_live import DestinoInvalidoError, escrever_pacote

PASSOS_CHATGPT_LIVE = """\
Pacote pronto em {destino}

1. No ChatGPT, crie um Project novo para este caso.
2. Cole o conteúdo de instrucoes.md nas instruções do Project (não tem nada do caso).
3. Suba paciente.md como arquivo do Project SEM ABRIR (ele tem a história do paciente).
4. Abra uma conversa no Project, ligue o modo de voz e comece a consulta.
5. Ao terminar, diga "encerrar consulta" e exporte a transcrição para a auditoria.

Abertura do caso (é tudo o que você sabe antes de entrar):

{abertura}
"""


class _Argumentos(argparse.Namespace):
    # Namespace tipado: sem ele, todo atributo do argparse é Any (reportAny).
    comando: str = ""
    caso: Path = Path()
    destino: Path = Path()


def _argumentos(argv: list[str] | None) -> _Argumentos:
    parser = argparse.ArgumentParser(prog="sara-pacient")
    comandos = parser.add_subparsers(dest="comando", required=True)
    pacote = comandos.add_parser("pacote", help="gera o pacote do ator para o ChatGPT Live")
    _ = pacote.add_argument("caso", type=Path, help="arquivo .toml do caso")
    _ = pacote.add_argument("destino", type=Path, help="pasta nova ou vazia para o pacote")
    return parser.parse_args(argv, namespace=_Argumentos())


def _comando_pacote(caso_toml: Path, destino: Path) -> int:
    try:
        pacote = montar_pacote_ator(ler_caso(caso_toml))
        _ = escrever_pacote(pacote, destino)
    except (ArquivoDeCasoInvalidoError, PacoteSemFatosError, DestinoInvalidoError) as erro:
        _ = sys.stderr.write(f"erro: {erro}\n")
        return 2
    _ = sys.stdout.write(PASSOS_CHATGPT_LIVE.format(destino=destino, abertura=pacote.abertura))
    return 0


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada; devolve o código de saída. Exemplo: ``main(["pacote", "c.toml", "p"])``."""
    argumentos = _argumentos(argv)
    match argumentos.comando:
        case "pacote":
            return _comando_pacote(argumentos.caso, argumentos.destino)
        case outro:
            # O argparse já recusa comando desconhecido; chegar aqui é subcomando sem despacho.
            msg = f"subcomando {outro!r} sem despacho em main()"
            raise AssertionError(msg)
