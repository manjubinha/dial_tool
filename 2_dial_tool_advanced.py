"""
Discador desenvolvido para aparelhos Dual SIM card
Necessário customizar o script para cada modelo de aparelho, pois a interface do discador muda de acordo com a fabricante e versão do Android.
2026 - Daniel Vertamatti - Vonex Telecomunicações
"""

import os
import subprocess
import time
import re

ADB_CMD = os.path.join("platform-tools", "adb.exe")

serial_Galaxy_A01 = "R9XN60C4NEL"
serial_Galaxy_A03 = "R9XW106B78B"
serial_Galaxy_A04 = "R9XW109296Y"
serial_Galaxy_A31 = "RQ8R2032J1K"


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



def ligar(numero_telefone, serial_aparelho):
    """
    Apenas inicia a intenção de discagem. O Android perguntará qual chip usar.
    """
    print(f"[+] Preparando discagem para {numero_telefone}...")
    comando = [
        ADB_CMD, "-s", serial_aparelho, "shell", "am", "start",
        "-a", "android.intent.action.CALL",
        "-d", f"tel:{numero_telefone}"
    ]
    subprocess.run(comando, capture_output=True, text=True)


def desligar(serial_aparelho):
    """
    Encerra a chamada em andamento simulando o pressionamento do botão 'End Call'.
    """
    print("[-] Encerrando chamada...")
    comando = [ADB_CMD, "-s", serial_aparelho, "shell", "input", "keyevent", "KEYCODE_ENDCALL"]
    subprocess.run(comando)
    print("[✓] Chamada encerrada.")


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


# def aguardar_linha_livre(serial_aparelho, timeout=10):
#     """
#     Aguarda dinamicamente até que o modem do Android confirme o estado IDLE (0).
#     """
#     inicio = time.time()
#     while estado_da_linha(serial_aparelho) != 0:
#         if time.time() - inicio > timeout:
#             print("[!] Aviso: Tempo limite atingido aguardando liberação da linha.")
#             break
#         time.sleep(0.5)


# def estado_da_linha(serial_aparelho):
#     """
#     Retorna o estado atual da telefonia:
#     0 = IDLE (livre / em espera)
#     1 = RINGING (tocando / recebendo)
#     2 = OFFHOOK (em chamada ativa ou discando)
#     """
#     comando = [ADB_CMD, "-s", serial_aparelho, "shell", "dumpsys", "telephony.registry"]
#     saida = subprocess.run(comando, capture_output=True, text=True).stdout
#     for linha in saida.splitlines():
#         if "mCallState=" in linha:
#             try:
#                 return int(linha.split("mCallState=")[-1].split()[0])
#             except (ValueError, IndexError):
#                 continue
#     return 0


def ler_numeros(caminho="numbers.txt"):
    """
    Lê os números de telefone, um por linha, do arquivo informado.
    """
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return [linha.strip() for linha in arquivo if linha.strip()]


def ativar_viva_voz(serial_aparelho):
    """
    Ativar o viva-voz via toque de tela simulado.
    """
    time.sleep(1)
    # clicar_tela(271, 1695)
    clica_texto_na_tela("Viva-voz", serial_aparelho, timeout=5)


def clicar_tela(x_real, y_real, serial_aparelho):
    """
    Aguarda a tela de chamada estabilizar e clica no botão Viva-voz.
    Substitua x_real e y_real pelas coordenadas obtidas no Pointer Location.
    """
    time.sleep(2.5)  # Tempo para a interface do discador carregar por completo
    subprocess.run([ADB_CMD, "-s", serial_aparelho, "shell", "input", "tap", str(x_real), str(y_real)])


def clica_texto_na_tela(texto_botao, serial_aparelho, timeout=5):
    """
    Faz dump da hierarquia de tela, procura um elemento cujo texto
    contenha texto_botao e clica no centro dele. 
    Tenta repetidamente até atingir o timeout.
    """
    inicio = time.time()
    while time.time() - inicio < timeout:

        subprocess.run([ADB_CMD, "-s", serial_aparelho, "shell", "uiautomator", "dump", "/sdcard/ui.xml"], capture_output=True)

        resultado = subprocess.run(
            [ADB_CMD, "-s", serial_aparelho, "shell", "cat", "/sdcard/ui.xml"],
            capture_output=True, text=True
        )
        xml = resultado.stdout
        padrao = rf'text="[^"]*{re.escape(texto_botao)}[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        match = re.search(padrao, xml)
        
        if match:
            x1, y1, x2, y2 = map(int, match.groups())
            x_centro, y_centro = (x1 + x2) // 2, (y1 + y2) // 2
            subprocess.run([ADB_CMD, "-s", serial_aparelho, "shell", "input", "tap", str(x_centro), str(y_centro)])
            print(f"[✓] Clicou em '{texto_botao}' em ({x_centro}, {y_centro})")
            return True
            
        time.sleep(1)
    print(f"[!] Botão '{texto_botao}' não encontrado na tela após {timeout} segundos.")
    return False


def obter_serial_fisico(identificador_adb):
    """
    Descobre o serial físico do aparelho, independentemente se está 
    conectado via USB (retorna o próprio serial) ou TCP/IP (lê do sistema).
    """
    comando = [ADB_CMD, "-s", identificador_adb, "shell", "getprop", "ro.serialno"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    return resultado.stdout.strip()


# --- No bloco principal: ---
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
            "id": serial,
            "info": info,
            "sim1": operadoras[0],
            "sim2": operadoras[1]
        })
        
        print(f"{i + 1}. {serial} - {obter_serial_fisico(serial)} - {info}\n")
        if(operadoras[0]):
            print(f"   SIM 1: {operadoras[0]}")
        if(operadoras[1]):
            print(f"   SIM 2: {operadoras[1]}")

        if(obter_serial_fisico(serial) == serial_Galaxy_A31):
            print("\nNúmero(s):")
            if(operadoras[0]):
                print("SIM 1 -  TIM  - (11) 96165-6108")
            if(operadoras[1]):
                print("SIM 2 - Claro - (11) 99013-0849\n")

        if(obter_serial_fisico(serial) == serial_Galaxy_A03):
            print("\nNúmeros:\nSIM 1 - Claro - (11) 99360-3420\nSIM 2 - Vivo - (11) 9XXXX-XXXX\n")

        if(obter_serial_fisico(serial) == serial_Galaxy_A04):
            print("\nNúmeros:\nSIM 1 -  Vivo - (11) 96489-4500\nSIM 2 - Tim  - (11) 9XXXX-XXXX\n")


    while True:
        escolha_aparelho = input(f"Selecione o aparelho que deseja usar (1 a {len(meus_aparelhos)}): ").strip()
        if escolha_aparelho.isdigit() and 1 <= int(escolha_aparelho) <= len(meus_aparelhos):
            indice = int(escolha_aparelho) - 1
            aparelho_alvo = lista_aparelhos[indice]
            serial_selecionado = aparelho_alvo["id"]
            sim1_selecionado = aparelho_alvo["sim1"]
            sim2_selecionado = aparelho_alvo["sim2"]
            break
        print("[!] Opção inválida.")
        
    print(f"\n[+] Aparelho selecionado: {serial_selecionado} ({aparelho_alvo['info']})\n")

    vv = int(input("Deseja ativar o viva-voz durante as chamadas?\n  1 - Sim\n  2 - Não\nDigite a opção desejada (1 ou 2): "))

    while True:
        opcao_sim = input(
            "Realizar chamadas usando qual SIM?\n\n"
            f"  1 - apenas SIM 1 ({sim1_selecionado})\n"
            f"  2 - apenas SIM 2 ({sim2_selecionado})\n" 
            f"  3 - ambos SIM cards ({sim1_selecionado} e {sim2_selecionado})\n\n" 
            "Digite a opção desejada (1, 2 ou 3): "
        ).strip()
        if opcao_sim in {"1", "2", "3"}:
            break
        print("[!] Opção inválida. Digite 1, 2 ou 3.")

    print("\n")


    # --- 4. Loop de Discagem ---
    for numero_alvo in ler_numeros():
        numero_para_discagem = "0" + numero_alvo[2:] if numero_alvo.startswith("55") else numero_alvo

        if opcao_sim in {"1", "3"}:
            #aguardar_linha_livre(serial_selecionado)
            ligar(numero_para_discagem, serial_selecionado)
            time.sleep(1)

            if(serial_selecionado == serial_Galaxy_A04):
                clica_texto_na_tela("Vivo", serial_aparelho=serial_selecionado, timeout=5)

            if(serial_selecionado == serial_Galaxy_A31):
                clica_texto_na_tela("SIM 1", serial_aparelho=serial_selecionado, timeout=5)


            # Ativa o viva-voz
            if vv == 1:
                ativar_viva_voz(serial_aparelho=serial_selecionado)


            time.sleep(10)
            desligar(serial_selecionado)
            #aguardar_linha_livre(serial_selecionado)
            time.sleep(2)
            print("\n")




        if opcao_sim in {"2", "3"}:
            # ==========================================
            # EXEMPLO DE CHAMADA USANDO O SIM 2
            # ==========================================
            #aguardar_linha_livre(serial_selecionado)
            ligar(numero_para_discagem, serial_selecionado)
            time.sleep(1)

            if(serial_selecionado == serial_Galaxy_A04):
                clica_texto_na_tela("Tim", serial_aparelho=serial_selecionado, timeout=5)
            if(serial_selecionado == serial_Galaxy_A31):
                clica_texto_na_tela("SIM 2", serial_aparelho=serial_selecionado, timeout=5)

            # Ativa o viva-voz
            if vv == 1:
                ativar_viva_voz(serial_aparelho=serial_selecionado)

            time.sleep(10)
            desligar(serial_selecionado)
            #aguardar_linha_livre(serial_selecionado)
            time.sleep(2)
            
            # Mensagem da Claro após a chamada (caso exista)
            if(serial_selecionado == serial_Galaxy_A31):
                clica_texto_na_tela("OK", serial_aparelho=serial_selecionado, timeout=5)

            print("\n")



