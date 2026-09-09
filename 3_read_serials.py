import os
import subprocess
import re

ADB_CMD = os.path.join("platform-tools", "adb.exe")

serial_Galaxy_A01 = "R9XN60C4NEL"
serial_Galaxy_A03 = "R9XW106B78B"
serial_Galaxy_A04 = "R9XW109296Y"
serial_Galaxy_A31 = "RQ8R2032J1K"


def obter_status_sim(serial_aparelho):
    """
    Verifica o estado de cada SIM card.
    Retorna uma tupla de booleanos: (sim1_ativo, sim2_ativo)
    """
    comando = [ADB_CMD, "-s", serial_aparelho, "shell", "getprop", "gsm.sim.state"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    # A saída padrão é algo como "LOADED,LOADED" ou "LOADED,UNKNOWN" ou "ABSENT,ABSENT"
    estados = resultado.stdout.strip().split(',')
    # print(estados)
    # Verifica se a palavra "LOADED" está na posição do SIM 1 e SIM 2
    sim1_ativo = len(estados) > 0 and estados[0] == "LOADED"
    sim2_ativo = len(estados) > 1 and estados[1] == "LOADED"
    
    return sim1_ativo, sim2_ativo


def obter_operadoras_sim(serial_aparelho):
    """
    Lê a propriedade do sistema para descobrir as operadoras dos SIM 1 e SIM 2.
    Retorna uma lista, ex: ['TIM', 'Claro'] ou ['TIM', ''] se o slot 2 estiver vazio.
    """
    comando = [ADB_CMD, "-s", serial_aparelho, "shell", "getprop", "gsm.sim.operator.alpha"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    
    # A saída padrão é algo como "TIM,Claro\n"
    saida = resultado.stdout.strip()
    
    if not saida:
        return ["Desconhecido", "Desconhecido"]
        
    # Divide a string pela vírgula
    operadoras = saida.split(',')
    
    # Garante que sempre teremos 2 posições na lista (SIM 1 e SIM 2)
    while len(operadoras) < 2:
        operadoras.append("Vazio")
        
    return operadoras


def obter_seriais_adb():
    """
    Executa 'adb devices' e retorna uma lista (vetor) com os números seriais 
    de todos os dispositivos listados.
    """
    seriais = []
    
    # Executa o comando e captura a saída em formato de texto
    resultado = subprocess.run([ADB_CMD, "devices"], capture_output=True, text=True)
    
    # Quebra a saída em linhas e ignora a primeira ("List of devices attached")
    linhas = resultado.stdout.strip().split("\n")[1:]
    
    for linha in linhas:
        linha = linha.strip()
        if linha: # Garante que a linha não está vazia
            # O serial é sempre o primeiro item antes do espaço/tabulação
            serial = linha.split()[0]
            seriais.append(serial)
            
    return seriais

def obter_info_aparelho(serial_aparelho):
    """
    Busca a fabricante e o modelo do aparelho conectado via ADB.
    """
    cmd_marca = [ADB_CMD, "-s", serial_aparelho, "shell", "getprop", "ro.product.manufacturer"]
    cmd_modelo = [ADB_CMD, "-s", serial_aparelho, "shell", "getprop", "ro.product.model"]
    
    # Executa os comandos e limpa quebras de linha com .strip()
    marca = subprocess.run(cmd_marca, capture_output=True, text=True).stdout.strip()
    modelo = subprocess.run(cmd_modelo, capture_output=True, text=True).stdout.strip()
    
    # Capitaliza a primeira letra da marca (ex: 'samsung' vira 'Samsung')
    marca = marca.capitalize() if marca else "Desconhecida"
    modelo = modelo if modelo else "Desconhecido"
    
    return f"{marca} {modelo}"


def verificar_conexao():
    """
    Verifica se o celular está conectado e autorizado via ADB.
    """
    resultado = subprocess.run([ADB_CMD, "devices"], capture_output=True, text=True)
    linhas = [linha for linha in resultado.stdout.strip().split("\n")[1:] if linha.strip()]

    for linha in linhas:
        if "device" in linha and "unauthorized" not in linha:
            return True
            
    return False


# --- Exemplo de uso ---
if __name__ == "__main__":

    print("\n[+] Verificando conexão com o(s) dispositivo(s) via ADB...")
    if(verificar_conexao()):
        print("[✓] Dispositivo conectado e autorizado via ADB.\n")
    else:
        print("[!] Nenhum aparelho autorizado encontrado via ADB.\n")
        exit()

    meus_aparelhos = obter_seriais_adb()

    lista_aparelhos = []
    print("\n--- Aparelhos Encontrados ---")
    for i, serial in enumerate(meus_aparelhos):
        info = obter_info_aparelho(serial)
        operadoras = obter_operadoras_sim(serial)
        
        lista_aparelhos.append({
            "serial": serial,
            "info": info,
            "sim1": operadoras[0],
            "sim2": operadoras[1]
        })

        sim1_ativo, sim2_ativo = obter_status_sim(serial)

        print(f"{i + 1}. {serial} - {info}\n")
        if(operadoras[0]):
            print(f"   SIM 1: {operadoras[0]} - {'Ativo' if sim1_ativo else 'Desativado'}")
        if(operadoras[1]):
            print(f"   SIM 2: {operadoras[1]} - {'Ativo' if sim2_ativo else 'Desativado'}")


        if(serial == serial_Galaxy_A31):
            print("\nNúmero(s):")
            if(operadoras[0]):
                print("SIM 1 -  TIM  - (11) 96165-6108")
            if(operadoras[1]):
                print("SIM 2 - Claro - (11) 99013-0849\n")

        if(serial == serial_Galaxy_A03):
            print("\nNúmeros:\nSIM 1 - Claro - (11) 99360-3420\nSIM 2 - Vivo - (11) 9XXXX-XXXX\n")

        if(serial == serial_Galaxy_A04):
            print("\nNúmeros:\nSIM 1 -  Vivo - (11) 96489-4500\nSIM 2 - Tim  - (11) 9XXXX-XXXX\n")
