"""
Discador para aparelhos com apenas apenas um SIM card ativado.
2026 - Daniel Vertamatti - Vonex Telecomunicações
"""

import os
import subprocess
import time
import re

# Define o caminho para o executável ADB
ADB_CMD = os.path.join("platform-tools", "adb.exe")

serial_Galaxy_A01 = "R9XN60C4NEL"
serial_Galaxy_A03 = "R9XW106B78B"
serial_Galaxy_A04 = "R9XW109296Y"
serial_Galaxy_A31 = "RQ8R2032J1K"


def ligar(numero_telefone, serial_aparelho):
    """
    Apenas inicia a intenção de discagem. O Android perguntará qual chip usar.
    """
    print(f"[+] Discando: {numero_telefone}...")
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
    print("[✓] Chamada encerrada.\n")


def verificar_conexao():
    """
    Verifica se o celular está conectado e autorizado via ADB.
    """
    resultado = subprocess.run([ADB_CMD, "devices"], capture_output=True, text=True)
    linhas = [linha for linha in resultado.stdout.strip().split("\n")[1:] if linha.strip()]
    
    for linha in linhas:
        if "device" in linha and "unauthorized" not in linha:
            print("[✓] Aparelho conectado e pronto.")
            return True
            
    print("[!] Nenhum aparelho autorizado encontrado via ADB.")
    return False


def obter_seriais_adb():
    """
    Executa 'adb devices' e retorna uma lista (vetor) com os números seriais de todos os dispositivos listados.
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


def ler_numeros(caminho="numbers.txt"):
    """
    Lê os números de telefone, um por linha, do arquivo informado.
    """
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return [linha.strip() for linha in arquivo if linha.strip()]


# def ativar_viva_voz():
#     """
#     Ativar o viva-voz via toque de tela simulado.
#     """
#     time.sleep(1)
#     clicar_tela(271, 1695)


def clicar_tela(x_real, y_real):
    """
    Aguarda a tela de chamada estabilizar e clica no botão Viva-voz.
    Substitua x_real e y_real pelas coordenadas obtidas no Pointer Location.
    """
    time.sleep(2.0)  # Tempo para a interface do discador carregar por completo
    #print(f"[+] Ativando Viva-voz em X={x_real}, Y={y_real}...")
    subprocess.run([ADB_CMD, "shell", "input", "tap", str(x_real), str(y_real)])


def ativar_viva_voz(serial_aparelho):
    """
    Ativar o viva-voz via toque de tela simulado.
    """
    time.sleep(1)
    # clicar_tela(271, 1695)
    clica_texto_na_tela("Viva-voz", serial_aparelho, timeout=5)


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


def dismiss_banner():
    """
    Envia o keyevent KEYCODE_BACK para o dispositivo Android conectado via ADB. Equivale ao botão 'voltar' físico/virtual do Android.
    """
    resultado = subprocess.run(
        [ADB_CMD, "shell", "input", "keyevent", "KEYCODE_BACK"],
        capture_output=True,
        text=True
    )
    if resultado.returncode != 0:
        print(f"Erro ao executar comando: {resultado.stderr}")
    return resultado.returncode == 0


def normaliza_numero(numero):
    """
    Normaliza o número de telefone para o formato de discagem.
    Se começar com 55, retira o 55 e coloca 0
    Se não começar com 55, retorna o número como está.
    O aparelho coloca o CSP automaticamente.
    """
    return ("0" + 
            numero[2:] if numero.startswith("55")
            else numero
            )

# --- No bloco principal: ---
if __name__ == "__main__":
    

    # print("\nSIM 1 -  TIM  - (11) 96165-6108\nSIM 2 - Claro - (11) 99013-0849\n")

    if verificar_conexao():

        dispositivos = obter_seriais_adb()
        for item in dispositivos:
            print(f"Serial do dispositivo: {item} - {obter_info_aparelho(item)}")
        viva_voz = input("Deseja ativar o viva-voz? (s/n): ").strip().lower() == "s"
        #print("\n[+] Iniciando discagem...\n")
        if serial_Galaxy_A31 in dispositivos:
            for numero_alvo in ler_numeros():

                ligar(normaliza_numero(numero_alvo), serial_Galaxy_A31)
                time.sleep(1)  # Pequena pausa para garantir que a chamada foi iniciada

                if viva_voz:
                    ativar_viva_voz(serial_Galaxy_A31)

                time.sleep(10)
                desligar(serial_Galaxy_A31)
                time.sleep(2)

                # Mensagem da Claro após a chamada (caso exista)
                # descomente um dos 3 abaixo para fechar o banner de mensagem da Claro após a chamada:
                
                # clicar_tela(538, 2127)
                # dismiss_banner()
                # clica_texto_na_tela("OK", serial_aparelho=serial_selecionado, timeout=5)

