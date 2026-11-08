"""Leitura do arquivo de caso em TOML, validado na borda (ADR-0002).

O pydantic fica só aqui: valida o que veio do disco e entrega dataclasses do domínio.
"""

import tomllib
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, ValidationError

from sara_pacient.dominio.caso import Caso, CasoInvalidoError, Fato, Fonte, Revelacao, Secao


class ArquivoDeCasoInvalidoError(ValueError):
    """O arquivo de caso não abre, não é TOML válido ou viola o formato."""


class _Rigido(BaseModel):
    # Campo desconhecido é recusado: um "spoiler" ou um "diagnostico" solto no arquivo não pode
    # passar calado, porque o que não tem seção não tem visibilidade decidida.
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True)


class _FonteArquivo(_Rigido):
    montado: bool
    origem: str
    pmid: str | None = None
    pmcid: str | None = None
    doi: str | None = None
    licenca_url: str | None = None


class _FatoArquivo(_Rigido):
    id: str
    secao: Secao
    texto: str
    revelacao: Revelacao
    condicao: str | None = None


class _CasoArquivo(_Rigido):
    id: str
    especialidade: str
    abertura: str
    fonte: _FonteArquivo
    fatos: tuple[_FatoArquivo, ...]


def ler_caso(caminho: Path) -> Caso:
    """Lê e valida um caso. Exemplo: ``ler_caso(Path("exemplos/caso-montado-exemplo.toml"))``."""
    try:
        bruto = tomllib.loads(caminho.read_text(encoding="utf-8"))
        modelo = _CasoArquivo.model_validate(bruto)
        return _para_dominio(modelo)
    except ValidationError as erro:
        msg = f"{caminho}: {_sem_valores(erro)}"
        raise ArquivoDeCasoInvalidoError(msg) from erro
    except (OSError, tomllib.TOMLDecodeError, CasoInvalidoError) as erro:
        msg = f"{caminho}: {erro}"
        raise ArquivoDeCasoInvalidoError(msg) from erro


def _sem_valores(erro: ValidationError) -> str:
    # O str() do pydantic ecoa o valor recebido (input_value), que num fato de gabarito é o
    # próprio diagnóstico: o usuário veria o caso antes da consulta. Só local e motivo saem.
    problemas = erro.errors(include_input=False, include_url=False, include_context=False)
    return "; ".join(f"{'.'.join(map(str, p['loc']))}: {p['msg']}" for p in problemas)


def _para_dominio(modelo: _CasoArquivo) -> Caso:
    f = modelo.fonte
    fonte = Fonte(f.montado, f.origem, f.pmid, f.pmcid, f.doi, f.licenca_url)
    fatos = tuple(Fato(x.id, x.secao, x.texto, x.revelacao, x.condicao) for x in modelo.fatos)
    return Caso(modelo.id, modelo.especialidade, modelo.abertura.strip(), fonte, fatos)
