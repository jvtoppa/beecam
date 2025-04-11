import RPi.GPIO as GPIO
import os
import time
import shutil
import subprocess
import configs
import screen

def find_stick():

    media_dir = configs.MEDIA_DIR
    
    if not os.path.exists(media_dir):
        return None

    for nome in os.listdir(media_dir):
        caminho = os.path.join(media_dir, nome)
        if os.path.ismount(caminho):
            return caminho

    return None

def copy_to_stick(scr):
    final_location = find_stick()

    if not final_location:
         scr.get(1)
         return

    arquivos = os.listdir(configs.ORIGIN_FOLDER_MEMSTICK)

    if not arquivos:
        scr.get(2)
        return

    for arquivo in arquivos:
        origin_file = os.path.join(configs.ORIGIN_FOLDER_MEMSTICK, arquivo)
        final_location_file = os.path.join(final_location, arquivo)

        try:
            shutil.copy2(origin_file, final_location_file)

        except Exception as e:
            scr.get(5)
 
    os.sync()

    try:
        subprocess.run(["umount", final_location], check=True)
        scr.get(3)
    except subprocess.CalledProcessError:
        scr.get(4)