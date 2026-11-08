"""Configuração do sara-pacient: o único módulo que pode ler o ambiente (trilho python-on-rails).

Hoje o projeto não lê variável de ambiente: o canal ChatGPT Live é manual (ADR-0001). O canal por
API trará a chave para cá, como SecretStr, validada na partida.
"""
