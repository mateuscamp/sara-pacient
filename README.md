# sara-pacient

Paciente simulado a partir de relato de caso real, para treino de entrevista clínica por voz.
Material de estudo, não decisão clínica.

Hoje a voz é o modo Live do ChatGPT, sem API: a CLI gera o pacote do ator a partir de um caso
estruturado, sem nada do gabarito, e o usuário o leva a um Project do ChatGPT. A auditoria da
transcrição contra o caso é a próxima fatia (ADR-0003). O canal por API (GPT-Live-1, Gemini Live)
entra depois como outro adaptador, sem mudar o núcleo (ADR-0001).

```bash
uv sync
uv run sara-pacient pacote exemplos/caso-montado-exemplo.toml pacotes/exemplo
```

- Formato do caso: `exemplos/caso-montado-exemplo.toml` e ADR-0002.
- Decisões: `docs/adr/`. Regras para o agente: `AGENTS.md`. Portão: `make check`.
- Método clínico: skill `casos-ai-first` (github.com/mateuscamp/claude-skills).
