import RPi.GPIO as GPIO
import os
import time
import shutil
import subprocess

PIN_BOTAO = 17
ORIGEM = "/home/neepc/Desktop/detectabee/data"

def encontrar_pendrive():
    media_dir = "/media/neepc"
    if not os.path.exists(media_dir):
        return None

    for nome in os.listdir(media_dir):
        caminho = os.path.join(media_dir, nome)
        if os.path.ismount(caminho):
            return caminho

    return None

def copiar_para_pendrive():
    destino = encontrar_pendrive()
    if not destino:
        print("[ERRO] Nenhum pendrive encontrado.")
        return

    print("[INFO] Pendrive encontrado em", destino)
    arquivos = os.listdir(ORIGEM)

    if not arquivos:
        print("[INFO] Nenhum arquivo para copiar.")
        return

    for arquivo in arquivos:
        origem_arquivo = os.path.join(ORIGEM, arquivo)
        destino_arquivo = os.path.join(destino, arquivo)

        try:
            shutil.copy2(origem_arquivo, destino_arquivo)
            print("[OK] Copiado:", arquivo)
        except Exception as e:
            print("[ERRO] Falha ao copiar", arquivo, ":", str(e))

    print("[INFO] Sincronizando dados...")
    os.sync()

    print("[INFO] Desmontando pendrive...")
    try:
        subprocess.run(["umount", destino], check=True)
        print("[OK] Pendrive pode ser removido com seguranca.")
    except subprocess.CalledProcessError:
        print("[ERRO] Falha ao desmontar o pendrive.")

def botao_pressionado(channel):
    print("[INFO] Botao pressionado. Iniciando copia...")
    copiar_para_pendrive()

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_BOTAO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(PIN_BOTAO, GPIO.RISING, callback=botao_pressionado, bouncetime=500)

    print("[PRONTO] Aguardando botao.")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[SAINDO] Encerrando script.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
