"""
Conecta ao aparelho via TCP/IP usando o ADB (Android Debug Bridge).
"""
import re
import os
import subprocess

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

def obter_ip_adb():
    try:

        # Executa o comando do ADB no sistema operacional
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

    print("\n[+] Verificando conexão com o dispositivo via ADB/TCP/IP")
    if(verificar_conexao()):
        print("[✓] Dispositivo conectado e autorizado via ADB.\n")
    else:
        print("[!] Nenhum aparelho autorizado encontrado via ADB.\n")
        exit()

    connection_mode = input("Deseja cancelar o acesso TCP/IP? (1 para sim, qualquer outra tecla para não): ").strip().upper()
    if connection_mode == "1":
        print("Reconecte o cabo USB e pressione Enter para continuar...")
        input()
        print("[+] Conectando via USB...")
        resultado = subprocess.run([ADB_CMD, "disconnect"], capture_output=True, text=True)
        # disconnected everything
        if resultado.returncode == 0:
            print("[✓] Acesso TCP/IP cancelado com sucesso.")
        resultado = subprocess.run([ADB_CMD, "usb"], capture_output=True, text=True)
        if resultado.returncode == 0:
            print("[✓] Reconectado via USB com sucesso.")


    else:
        #IP_addr = input("Digite o endereço IP do dispositivo: ")
        ip_dispositivo = obter_ip_adb()
        print(f"[+] IP do dispositivo obtido: {ip_dispositivo}")
        print(f"[+] Habilitando o modo TCP/IP e conectando ao aparelho...")
        comando = f"{ADB_CMD} tcpip 5555 && {ADB_CMD} connect {ip_dispositivo}:5555 && {ADB_CMD} devices"
        subprocess.run(comando, shell=True)
        print("[✓] Conexão via TCP/IP estabelecida com sucesso.\nDesconecte o cabo USB e continue usando o ADB via TCP/IP.")

    



    #subprocess.run(f"{ADB_CMD} devices", shell=True)


