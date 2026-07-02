"""
Cliente central para falar com IAs locais via Ollama ou LM Studio.

Ollama expõe uma API compatível com o padrão OpenAI em:
    http://localhost:11434/v1/chat/completions
    
LM Studio expõe uma API compatível com o padrão OpenAI em:
    http://localhost:1234/v1/chat/completions

Configure qual provider usar em config/ia.json:
- "provider": "ollama" ou "lm_studio" (padrão: ollama)
- "modelo_interpretador": ID do modelo a usar

Para descobrir os modelos disponíveis:
- Ollama: http://localhost:11434/api/tags
- LM Studio: http://localhost:1234/v1/models
"""

import json
import os
import requests

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "ia.json"
)

MODELO_PADRAO = "mistral"
PROVIDER_PADRAO = "ollama"


def carregar_configuracoes():
    """Lê o provider e modelo configurados em config/ia.json."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
        provider = dados.get("provider", PROVIDER_PADRAO)
        modelo = dados.get("modelo_interpretador", MODELO_PADRAO)
        return provider, modelo
    except Exception:
        return PROVIDER_PADRAO, MODELO_PADRAO


def obter_url_api(provider):
    """Retorna a URL da API baseado no provider."""
    if provider.lower() == "lm_studio":
        return LM_STUDIO_URL
    else:  # ollama é o padrão
        return OLLAMA_URL


def chamar_llm(prompt, modelo=None, provider=None, temperature=0.1, timeout=60):
    """
    Envia um prompt para o Ollama ou LM Studio e retorna o texto puro da resposta.

    Levanta requests.exceptions.ConnectionError se o servidor não estiver rodando,
    e requests.exceptions.HTTPError se a resposta vier com erro HTTP.
    
    Args:
        prompt: Texto do prompt
        modelo: ID do modelo (carrega de config se não informado)
        provider: "ollama" ou "lm_studio" (carrega de config se não informado)
        temperature: Temperatura da resposta (0.0 a 1.0)
        timeout: Timeout em segundos
    """
    if provider is None or modelo is None:
        provider_config, modelo_config = carregar_configuracoes()
        provider = provider or provider_config
        modelo = modelo or modelo_config
    
    url_api = obter_url_api(provider)

    resposta = requests.post(
        url_api,
        json={
            "model": modelo,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "stream": False
        },
        timeout=timeout
    )

    resposta.raise_for_status()

    return resposta.json()["choices"][0]["message"]["content"].strip()
