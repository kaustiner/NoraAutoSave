from core.speaker import falar

NOME = "Calculadora"
DESCRICAO = "Abre a calculadora do sistema"
COMANDOS = {
"abrir": [
"abrir calculadora",
"calculadora"
]
}

def executar(acao, comando):
    if acao == "abrir":
        falar("Abrindo a calculadora...")
        import subprocess
        subprocess.run(["calc.exe"])