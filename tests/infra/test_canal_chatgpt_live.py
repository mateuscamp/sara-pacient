"""Canal ChatGPT Live: o pacote vira dois arquivos, sem caso nas instruções e sem sobrescrever."""

from pathlib import Path

import pytest

from sara_pacient.dominio.caso import Especialidade, Fato, Revelacao, Secao, visivel_ao_ator
from sara_pacient.dominio.pacote import PacoteAtor
from sara_pacient.infra.canal_chatgpt_live import (
    REGRAS_DA_ANESTESIOLOGIA,
    REGRAS_DA_DOR,
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
PACOTE = PacoteAtor("c1", Especialidade.PSIQUIATRIA, "Ambulatório, 42 anos.", (INSONIA, ALCOOL))


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
    pacote = PacoteAtor("c1", Especialidade.PSIQUIATRIA, "Abertura.", (fato,))

    escritos = escrever_pacote(pacote, tmp_path / "pacote")

    ficha = next(p for p in escritos if p.name == "paciente.md").read_text(encoding="utf-8")
    assert f"marca-{secao.value}" in ficha


def test_destino_que_e_arquivo_e_recusado_com_erro_proprio(tmp_path: Path) -> None:
    # Achado 2 da review: NotADirectoryError escapava como traceback.
    arquivo = tmp_path / "pacote"
    _ = arquivo.write_text("x", encoding="utf-8")

    with pytest.raises(DestinoInvalidoError, match="pacote"):
        _ = escrever_pacote(PACOTE, arquivo)


def test_pacote_que_nao_vira_texto_nao_deixa_pasta_criada(tmp_path: Path) -> None:
    # Achado B1 da review: o texto era montado depois do mkdir; especialidade crua fora do escopo
    # estourava no assert_never e deixava a pasta de destino criada e vazia.
    pacote = PacoteAtor(
        "c1",
        "cardiologia",  # pyright: ignore[reportArgumentType]  # motivo: tipo errado de propósito
        "Abertura.",
        (INSONIA,),
    )
    destino = tmp_path / "pacote"

    with pytest.raises(AssertionError, match="cardiologia"):
        _ = escrever_pacote(pacote, destino)

    assert not destino.exists()


def test_texto_multilinha_vira_um_item_so_da_ficha(tmp_path: Path) -> None:
    # Achado 3 da review: a segunda linha saía fora do item, sem a regra de revelação.
    fato = Fato("f1", Secao.PACIENTE_DIZ, "linha um\nlinha dois", Revelacao.SE_PERGUNTADO)
    pacote = PacoteAtor("c1", Especialidade.PSIQUIATRIA, "Abertura.", (fato,))

    escritos = escrever_pacote(pacote, tmp_path / "pacote")

    ficha = next(p for p in escritos if p.name == "paciente.md").read_text(encoding="utf-8")
    assert "- linha um linha dois (só se perguntarem)" in ficha


def _arquivo(escritos: tuple[Path, ...], nome: str) -> str:
    return next(p for p in escritos if p.name == nome).read_text(encoding="utf-8")


DOR_NA_LOMBAR = Fato("lombar", Secao.PACIENTE_DIZ, "Dói nas costas.", Revelacao.ESPONTANEO)
QUEDA = Fato("quedas", Secao.RISCO, "Caiu duas vezes no mês.", Revelacao.SE_PERGUNTADO)


@pytest.mark.parametrize(
    ("especialidade", "titulo"),
    [
        (Especialidade.PSIQUIATRIA, "## Pensamentos de morte, violência, autocuidado"),
        (Especialidade.DOR, "## Sinais de alerta, remédios e substâncias, pensamentos de morte"),
        (
            Especialidade.ANESTESIOLOGIA,
            "## Anestesias anteriores e na família, alergias, fumo, álcool e outras substâncias",
        ),
    ],
)
def test_titulo_do_risco_e_o_da_especialidade(
    especialidade: Especialidade, titulo: str, tmp_path: Path
) -> None:
    pacote = PacoteAtor("c1", especialidade, "Abertura.", (QUEDA,))

    ficha = _arquivo(escrever_pacote(pacote, tmp_path / "pacote"), "paciente.md")

    assert f"{titulo}\n\n- Caiu duas vezes no mês." in ficha


def _instrucoes_de(especialidade: Especialidade, destino: Path) -> str:
    pacote = PacoteAtor("c1", especialidade, "Abertura.", (DOR_NA_LOMBAR,))
    return _arquivo(escrever_pacote(pacote, destino), "instrucoes.md")


def test_regra_do_folego_nao_proibe_os_numeros_da_ficha(tmp_path: Path) -> None:
    # Achado A1 da auditoria: "nunca em números" fazia o ator sumir com "dois lances de escada",
    # que é o dado da ficha. O que não se quer é medida técnica.
    instrucoes = _instrucoes_de(Especialidade.ANESTESIOLOGIA, tmp_path / "pacote")

    assert "nunca em números" not in instrucoes
    assert "sem medida técnica" in instrucoes


def test_regra_da_nota_da_dor_nao_afirma_intensidade(tmp_path: Path) -> None:
    # Achado A2 da auditoria: "é forte" era intensidade que a ficha não traz, contra a regra da
    # fidelidade das mesmas instruções.
    instrucoes = _instrucoes_de(Especialidade.DOR, tmp_path / "pacote")

    assert "é forte" not in instrucoes
    assert '"não sei dar número"' in instrucoes


@pytest.mark.parametrize("especialidade", list(Especialidade))
def test_instrucoes_nao_trazem_exemplo_de_remedio(
    especialidade: Especialidade, tmp_path: Path
) -> None:
    # Achado A5 da auditoria: o modelo de voz repete o exemplo como se fosse fato do caso.
    instrucoes = _instrucoes_de(especialidade, tmp_path / "pacote")

    assert "o da pressão" not in instrucoes
    assert "que o posto dá" not in instrucoes


# As regras próprias vêm direto das tuplas do canal (achado B4 da review): com a tabela de
# marcadores mantida à mão, regra nova sem marcador ficava fora do teste de isolamento.
REGRAS_PROPRIAS: dict[Especialidade, tuple[str, ...]] = {
    Especialidade.PSIQUIATRIA: (),
    Especialidade.DOR: REGRAS_DA_DOR,
    Especialidade.ANESTESIOLOGIA: REGRAS_DA_ANESTESIOLOGIA,
}

# Os termos proibidos e os trechos que os quatro testes antigos de isolamento afirmavam, um por um
# (ADR-0006, ADR-0007). Ficam como âncora: se uma tupla de regras esvaziar, o teste das tuplas
# passa sozinho.
TRECHOS_FIXOS: dict[Especialidade, tuple[str, ...]] = {
    Especialidade.PSIQUIATRIA: ("anedonia",),
    Especialidade.DOR: ("alodinia", "0 a 10"),
    Especialidade.ANESTESIOLOGIA: (
        "hipertermia maligna",
        "Alergia:",
        "Exame da boca e do pescoço",
    ),
}


@pytest.mark.parametrize("especialidade", list(Especialidade))
def test_instrucoes_levam_todas_as_regras_proprias_e_nenhuma_das_outras(
    especialidade: Especialidade, tmp_path: Path
) -> None:
    instrucoes = _instrucoes_de(especialidade, tmp_path / "pacote")

    todas = {regra for regras in REGRAS_PROPRIAS.values() for regra in regras}
    assert {regra for regra in todas if regra in instrucoes} == set(REGRAS_PROPRIAS[especialidade])


@pytest.mark.parametrize("especialidade", list(Especialidade))
def test_instrucoes_levam_os_trechos_fixos_da_especialidade_e_nenhum_das_outras(
    especialidade: Especialidade, tmp_path: Path
) -> None:
    instrucoes = _instrucoes_de(especialidade, tmp_path / "pacote")

    todos = {trecho for trechos in TRECHOS_FIXOS.values() for trecho in trechos}
    assert {trecho for trecho in todos if trecho in instrucoes} == set(TRECHOS_FIXOS[especialidade])


def test_regras_de_remedio_nao_trazem_exemplo_entre_aspas() -> None:
    # Achado B6 da review: fixar só as duas frases removidas deixava passar qualquer outro exemplo.
    # Exemplo nas regras vem entre aspas, e o modelo de voz o repete como fato do caso.
    proprias = (*REGRAS_DA_DOR, *REGRAS_DA_ANESTESIOLOGIA)
    de_remedio = [regra for regra in proprias if regra.startswith("Remédios:")]

    assert len(de_remedio) == 2
    assert [regra for regra in de_remedio if '"' in regra] == []
