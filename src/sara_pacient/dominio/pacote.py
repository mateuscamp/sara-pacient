"""O pacote do ator: o que o canal de voz pode receber de um caso (ADR-0002)."""

from dataclasses import dataclass

from sara_pacient.dominio.caso import (
    Caso,
    Especialidade,
    Fato,
    ler_especialidade,
    visivel_ao_ator,
)


class PacoteSemFatosError(ValueError):
    """O caso não tem nenhum fato que o ator possa saber."""


class GabaritoNoPacoteError(ValueError):
    """O pacote recebeu fato de seção que o ator nunca vê."""


@dataclass(frozen=True, slots=True)
class PacoteAtor:
    """Abertura e fatos que o paciente simulado pode saber; nunca o gabarito."""

    caso_id: str
    especialidade: Especialidade
    abertura: str
    fatos: tuple[Fato, ...]

    def __post_init__(self) -> None:
        # A mesma guarda do Caso: pacote montado à mão com texto cru fora do escopo é recusado
        # aqui, com erro do domínio, e não no assert_never do canal; o texto válido vira o enum.
        object.__setattr__(self, "especialidade", ler_especialidade(self.especialidade))
        # "Nunca o gabarito" e "nunca vazio" valem para o tipo, não só para montar_pacote_ator:
        # pacote montado à mão com fato de gabarito só não vazava por falta de título no canal.
        gabarito = [fato.id for fato in self.fatos if not visivel_ao_ator(fato.secao)]
        if gabarito:
            msg = f"caso {self.caso_id!r}: fatos de gabarito {gabarito} não vão ao ator"
            raise GabaritoNoPacoteError(msg)
        if not self.fatos:
            msg = f"caso {self.caso_id!r} sem fato visível ao ator: confira a seção de cada fato"
            raise PacoteSemFatosError(msg)


def montar_pacote_ator(caso: Caso) -> PacoteAtor:
    """Filtra o caso para o canal de voz, mantendo a ordem dos fatos."""
    visiveis = tuple(fato for fato in caso.fatos if visivel_ao_ator(fato.secao))
    return PacoteAtor(caso.id, caso.especialidade, caso.abertura, visiveis)
