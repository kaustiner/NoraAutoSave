from core.speaker import falar
import importlib.util, os
_path = os.path.join(os.path.dirname(__file__), "..", "core", "intent_router.py")
_spec = importlib.util.spec_from_file_location("intent_router", os.path.abspath(_path))
intent_router = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intent_router)
from plugins import plugin_creator

NOME = "comando_desconhecido"

DESCRICAO = "Intercepta comandos não reconhecidos e tenta rotear ou criar um plugin via LLM"

# Este plugin é chamado pelo core quando nenhum outro plugin reconhece o comando.
# Não precisa de COMANDOS pois é acionado diretamente pelo dispatcher.
COMANDOS = {}


def executar(acao, comando):
    falar("Não reconheci esse comando. Deixa eu pensar...")

    resultado = intent_router.rotear(comando)

    if not resultado:
        falar("Não consegui entender o que você quer.")
        return

    if resultado["acao"] == "rotear":
        nome_plugin = resultado.get("plugin", "")
        acao_plugin = resultado.get("acao_plugin", "")

        falar(f"Encontrei o plugin {nome_plugin}. Executando...")

        sucesso = intent_router.executar_plugin(nome_plugin, acao_plugin, comando)

        if not sucesso:
            falar("Não consegui executar o plugin encontrado.")

    elif resultado["acao"] == "criar":
        descricao = resultado.get("descricao", "")

        if not descricao:
            falar("Não consegui entender o que o plugin deveria fazer.")
            return

        falar("Nenhum plugin existente resolve isso. Vou criar um novo.")

        plugin_creator.executar("criar", f"criar plugin {descricao}")

    elif resultado["acao"] == "erro":
        motivo = resultado.get("motivo", "erro desconhecido")
        falar(f"Erro ao analisar o comando: {motivo}")