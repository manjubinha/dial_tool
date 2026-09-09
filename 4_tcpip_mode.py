"""
Conecta/desconecta ao aparelho via TCP/IP usando o ADB (Android Debug Bridge).
"""
import re
import os
import subprocess
import time

ADB_CMD = os.path.join("platform-tools", "adb.exe")


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


def conectar_usb():
    """
    Conecta ao dispositivo via USB usando o ADB.
    """
    resultado = subprocess.run([ADB_CMD, "disconnect"], capture_output=True, text=True)
    # disconnected everything
    if resultado.returncode == 0:
        print("[✓] Acesso TCP/IP cancelado com sucesso.")
    resultado = subprocess.run([ADB_CMD, "usb"], capture_output=True, text=True)
    # print(resultado.stdout)
    if(resultado.returncode == 0):
        print("[✓] Conexão via USB estabelecida com sucesso.")
        resultado = subprocess.run([ADB_CMD, "devices"], capture_output=True, text=True)
        print(resultado.stdout)
            # print(resultado.stdout)


def conectar_tcpip(ip):
    """
    Conecta ao dispositivo via TCP/IP usando o ADB.
    """
    comando = [ADB_CMD, "tcpip", "5555"]
    subprocess.run(comando, capture_output=True, text=True)
    comando = [ADB_CMD, "connect", f"{ip}:5555"]
    subprocess.run(comando, capture_output=True, text=True)
    comando = [ADB_CMD, "devices"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if(resultado.returncode == 0):
        print("[✓] Conexão via TCP/IP estabelecida com sucesso.\nDesconecte o cabo USB e continue usando o ADB via TCP/IP.")
        resultado = subprocess.run([ADB_CMD, "devices"], capture_output=True, text=True)
        print(resultado.stdout)
    return



def obter_ip_adb():
    subprocess.run([ADB_CMD, "shell", "cmd", "connectivity", "airplane-mode", "disable"], capture_output=True, text=True)
    print("[+] Desativando o modo avião...")
    subprocess.run([ADB_CMD, "shell", "svc", "wifi", "enable"], capture_output=True, text=True)
    print("[+] Ativando o Wi-Fi...")
    print("[+] Aguardando 5 segundos para receber o IP do dispositivo...")
    time.sleep(5)  # Aguarda um momento para garantir que o Wi-Fi esteja ativado

    try:
        resultado = subprocess.run(
            [ADB_CMD, "shell", "ip", "route", "get", "1"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Usa Expressão Regular (Regex) para encontrar o IP após a palavra 'src'
        match = re.search(r'src\s+([0-9.]+)', resultado.stdout)
        
        if match:
            return match.group(1)
        else:
            return "Erro: Formato de resposta do ADB inesperado."
            
    except FileNotFoundError:
        return "Erro: O comando 'adb' não foi encontrado. Verifique se ele está no PATH."
    except subprocess.CalledProcessError:
        return "Erro: Nenhum dispositivo Android foi detectado via USB."


if __name__ == "__main__":

    print("Conecte o cabo USB do dispositivo e pressione Enter para continuar...")
    input()
    print("\n[+] Verificando conexão com o dispositivo via ADB/USB")
    if(verificar_conexao()):
        print("[✓] Dispositivo conectado e autorizado via ADB.\n")
    else:
        print("[!] Nenhum aparelho autorizado encontrado via ADB.\n")
        exit()

    connection_mode = input("Deseja conectar via (1)USB ou (2)TCP/IP?: ").strip().upper()
    if connection_mode == "1":
        print("[+] Conectando via USB...")
        conectar_usb()

    else:
        ip_dispositivo = obter_ip_adb()
        print(f"[+] IP do dispositivo obtido: {ip_dispositivo}")
        print(f"[+] Habilitando o modo TCP/IP e conectando ao aparelho...")
        conectar_tcpip(ip_dispositivo)
        


