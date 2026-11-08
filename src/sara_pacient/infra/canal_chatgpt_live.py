"""Canal ChatGPT Live, manual: escreve o pacote do ator em arquivos para um Project (ADR-0001).

Sem API: o usuário cola `instrucoes.md` nas instruções do Project, sobe `paciente.md` como
arquivo sem abrir e conversa pelo modo de voz. Canal por API, quando vier, é outro módulo.
"""

from pathlib import Path

from sara_pacient.dominio.caso import Fato, Revelacao, Secao
from sara_pacient.dominio.pacote import PacoteAtor

# Só as seções que o ator vê (visivel_ao_ator); uma seção de gabarito aqui seria um rótulo morto.
TITULOS: dict[Secao, str] = {
    Secao.PACIENTE_DIZ: "O que você (paciente) sabe e conta",
    Secao.ACOMPANHANTE_DIZ: "O que o acompanhante sabe e conta",
    Secao.OBSERVAVEL: "O que o médico vê e ouve sem perguntar",
    Secao.SO_COM_PERGUNTA_OU_MANOBRA: "O que só aparece se o médico perguntar ou examinar",
    Secao.EXAME_FISICO: "Exame físico (só se o médico disser que examina)",
    Secao.EXAME_COMPLEMENTAR: "Exames já feitos (só se o médico pedir)",
    Secao.EVOLUCAO: "Evolução (só se o médico disser que o tempo passou)",
    Secao.RISCO: "Pensamentos de morte, violência, autocuidado",
}

ROTULO_REVELACAO: dict[Revelacao, str] = {
    Revelacao.ESPONTANEO: "conta sem ser perguntado",
    Revelacao.SE_PERGUNTADO: "só se perguntarem",
    Revelacao.CONDICIONAL: "condição",
}

# Regras do personagem, da skill casos-ai-first (seção 5). Não contêm nada do caso: o usuário
# lê este arquivo ao colá-lo nas instruções do Project.
INSTRUCOES = """\
# Você é um paciente numa consulta

Quem fala com você é um médico em treinamento. Interprete o paciente descrito no arquivo
`paciente.md` deste projeto, em português do Brasil, por voz. Nunca diga que é uma IA, nunca
cite o arquivo e nunca saia do personagem, a menos que o médico diga "pausa".

1. Responda só ao que foi perguntado. Conte sem ser perguntado apenas o que a ficha marca como
   "conta sem ser perguntado".
2. Fale como pessoa, não como prontuário: nada de termos técnicos ("alucinação", "ideação
   suicida", "anedonia"). Descreva a experiência com suas palavras.
3. Fidelidade: não invente nada que mude o diagnóstico, o risco ou o tratamento. Se o médico
   perguntar algo que a ficha não traz, responda sem confirmar nem negar: "não sei dizer",
   "não lembro bem". Nunca responda "não" ou "nunca" a algo que a ficha não diz que é ausente.
4. Respeite as condições escritas na ficha (por exemplo, só contar algo na segunda pergunta).
5. Seu estado muda a forma de falar (lento, curto, prolixo, desconfiado), não os fatos.
6. Se o médico pedir para falar com o acompanhante, responda como ele, com o que a ficha dá a ele.
7. Se o médico perguntar o que observa, descreva o que se vê e ouve, em linguagem leiga, sem
   nomear a alteração.
8. Exame físico: só o que a ficha traz; se não traz, "não descrito". Exames: se a ficha não traz,
   "não foi feito". Passagem do tempo: só a evolução da ficha.
9. Não avalie o médico nem dê dicas. Quando ele disser "encerrar consulta", despeça-se e pare.
"""


class DestinoInvalidoError(OSError):
    """A pasta de destino não serve: é arquivo, não se cria ou não se escreve."""


class DestinoOcupadoError(DestinoInvalidoError):
    """A pasta de destino já tem arquivos: o pacote não sobrescreve nada."""


def escrever_pacote(pacote: PacoteAtor, destino: Path) -> tuple[Path, ...]:
    """Escreve `instrucoes.md` e `paciente.md` em `destino` e devolve os caminhos.

    Exemplo: ``escrever_pacote(montar_pacote_ator(caso), Path("pacotes/caso-1"))``.
    """
    _conferir_destino(destino)
    instrucoes = destino / "instrucoes.md"
    paciente = destino / "paciente.md"
    try:
        destino.mkdir(parents=True, exist_ok=True)
        _ = instrucoes.write_text(INSTRUCOES, encoding="utf-8")
        _ = paciente.write_text(_ficha_do_paciente(pacote), encoding="utf-8")
    except OSError as erro:
        msg = f"{destino}: não foi possível escrever o pacote ({erro.strerror})"
        raise DestinoInvalidoError(msg) from erro
    return (instrucoes, paciente)


def _conferir_destino(destino: Path) -> None:
    if destino.exists() and not destino.is_dir():
        msg = f"{destino} é um arquivo; o destino precisa ser uma pasta nova ou vazia"
        raise DestinoInvalidoError(msg)
    if destino.exists() and any(destino.iterdir()):
        msg = f"{destino} já tem arquivos; escolha uma pasta vazia ou nova"
        raise DestinoOcupadoError(msg)


def _ficha_do_paciente(pacote: PacoteAtor) -> str:
    linhas = ["# Ficha do paciente (não mostrar ao médico)", "", "## Abertura", "", pacote.abertura]
    for secao, titulo in TITULOS.items():
        fatos = [fato for fato in pacote.fatos if fato.secao is secao]
        if fatos:
            linhas += ["", f"## {titulo}", "", *(_linha_do_fato(fato) for fato in fatos)]
    return "\n".join(linhas) + "\n"


def _linha_do_fato(fato: Fato) -> str:
    regra = ROTULO_REVELACAO[fato.revelacao]
    if fato.condicao:
        regra = f"{regra}: {_uma_linha(fato.condicao)}"
    return f"- {_uma_linha(fato.texto)} ({regra})"


def _uma_linha(texto: str) -> str:
    # Texto longo vem em várias linhas no TOML; na ficha, cada fato é um item só, com a regra.
    return " ".join(texto.split())
