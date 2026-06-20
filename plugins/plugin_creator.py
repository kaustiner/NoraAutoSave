from core.speaker import falar

import requests
import re
import os

NOME = "plugin_creator"

DESCRICAO = "Cria plugins usando Ollama"

COMANDOS = {
    "criar": [
        "criar plugin",
        "gerar plugin",
        "novo plugin"
    ]
}

MODELO = "qwen3:8b"

OLLAMA_URL = "http://localhost:11434/api/generate"


def gerar_prompt(descricao):
    return f"""
Você é um gerador especializado de plugins da NORA.

Retorne APENAS código Python.

NÃO utilize markdown.

NÃO utilize blocos ```.

NÃO explique nada.

NÃO escreva texto fora do código.

Preencha EXATAMENTE este modelo:

from core.speaker import falar

NOME = ""

DESCRICAO = ""

COMANDOS = {{
"abrir": [
"comando exemplo"
]
}}

def executar(acao, comando):

    pass

REGRAS OBRIGATÓRIAS:

1. O plugin deve possuir:

- NOME
- DESCRICAO
- COMANDOS
- executar()

1. O dicionário COMANDOS deve utilizar intenções reais.
Exemplos válidos:

COMANDOS = {{
"abrir": [
"abrir calculadora",
"calculadora"
]
}}

COMANDOS = {{
"pesquisar": [
"pesquisar youtube",
"buscar youtube"
]
}}

COMANDOS = {{
"criar": [
"criar nota",
"adicionar nota"
]
}}

Nunca utilize:

"acao"
"comando"
"funcao"
"executar"

como chave principal.

1. Utilize comandos naturais.
Correto:

"abrir calculadora"

Errado:

"abrir_calculadora"

1. Nunca utilizar:
print()

1. Sempre utilizar:
from core.speaker import falar

1. Não criar classes.
2. Não criar múltiplos arquivos.
3. Não modificar arquivos existentes.
4. Não modificar o core.
5. O plugin deve funcionar imediatamente após ser salvo.
6. Retorne apenas o código Python.
OBJETIVO:

{descricao}
"""


def limpar_codigo(codigo):
    codigo = codigo.replace("```python", "")
    codigo = codigo.replace("```", "")
    return codigo.strip()


def validar(codigo):
    obrigatorios = [
        "NOME",
        "DESCRICAO",
        "COMANDOS",
        "def executar"
    ]

    for item in obrigatorios:
        if item not in codigo:
            return False

    acoes_proibidas = [
        '"acao"',
        "'acao'",
        '"comando"',
        "'comando'",
        '"funcao"',
        "'funcao'"
    ]

    for item in acoes_proibidas:
        if item in codigo:
            return False

    proibidos = [
        "print(",
        "class ",
        "```",
        "shutil.rmtree",
        "os.remove",
        "os.rmdir"
    ]

    for item in proibidos:
        if item in codigo:
            return False

    if not re.search(
        r'COMANDOS\s*=\s*\{.*\[(.*?)\]',
        codigo,
        re.DOTALL
    ):
        return False

    return True


def validar_imports(codigo):
    permitidos = [
        "from core.speaker import falar"
    ]

    for linha in codigo.splitlines():
        linha = linha.strip()

        if linha.startswith("from core."):
            if linha not in permitidos:
                return False

    return True


def nome_arquivo(codigo):
    match = re.search(
        r'NOME\s*=\s*"([^"]+)"',
        codigo
    )

    if not match:
        return None

    nome = match.group(1)

    nome = nome.lower()
    nome = nome.replace(" ", "_")

    nome = re.sub(
        r"[^a-z0-9_]",
        "",
        nome
    )

    return nome


def gerar_plugin(descricao):
    prompt = gerar_prompt(descricao)

    resposta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    resposta.raise_for_status()

    codigo = resposta.json()["response"]

    codigo = limpar_codigo(codigo)

    # Proteção contra comandos em snake_case e casos específicos
    if "abrir_calculadora" in codigo:
        return ""

    if re.search(r'"[a-z]+_[a-z]+"', codigo):
        return ""

    return codigo


def executar(acao, comando):
    try:
        descricao = comando

        for prefixo in [
            "criar plugin",
            "gerar plugin",
            "novo plugin"
        ]:
            if descricao.startswith(prefixo):
                descricao = descricao.replace(
                    prefixo,
                    "",
                    1
                ).strip()
                break

        if not descricao:
            falar("Descreva o plugin.")
            return

        falar("Gerando plugin...")

        codigo = gerar_plugin(descricao)

        if not validar(codigo):
            falar(
                "Primeira tentativa inválida. Tentando novamente."
            )

            codigo = gerar_plugin(descricao)

        if not validar(codigo):
            falar(
                "A IA não conseguiu gerar um plugin válido."
            )
            return

        if not validar_imports(codigo):
            falar(
                "Plugin rejeitado. Imports não permitidos."
            )
            return

        nome = nome_arquivo(codigo)

        if not nome:
            falar(
                "Não foi possível identificar o nome do plugin."
            )
            return

        caminho = os.path.join(
            "plugins",
            f"{nome}.py"
        )

        if os.path.exists(caminho):
            falar(
                "Já existe um plugin com esse nome."
            )
            return

        with open(
            caminho,
            "w",
            encoding="utf-8"
        ) as arquivo:
            arquivo.write(codigo)

        falar(
            f"Plugin criado com sucesso: {nome}"
        )

    except Exception as erro:
        falar(
            f"Erro ao gerar plugin: {erro}"
        )