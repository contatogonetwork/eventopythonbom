import os
import shutil
import hashlib
from pathlib import Path

def create_directory_if_not_exists(directory_path):
    """Cria um diretório se ele não existir"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return directory_path

def get_file_extension(file_path):
    """Retorna a extensão de um arquivo"""
    return os.path.splitext(file_path)[1].lower()

def is_media_file(file_path):
    """Verifica se um arquivo é de mídia (vídeo, imagem ou áudio)"""
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.mxf']
    image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.raw', '.bmp']
    audio_extensions = ['.mp3', '.wav', '.aac', '.ogg', '.flac']
    
    ext = get_file_extension(file_path)
    return ext in video_extensions or ext in image_extensions or ext in audio_extensions

def get_file_hash(file_path, block_size=8192):
    """Calcula o hash MD5 de um arquivo"""
    md5 = hashlib.md5()
    
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    
    return md5.hexdigest()

def get_file_size_mb(file_path):
    """Retorna o tamanho de um arquivo em MB"""
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)

def copy_file_with_unique_name(source_path, dest_directory, prefix=""):
    """
    Copia um arquivo para um diretório de destino,
    garantindo que o nome seja único.
    """
    create_directory_if_not_exists(dest_directory)
    
    filename = os.path.basename(source_path)
    name, ext = os.path.splitext(filename)
    
    if prefix:
        name = f"{prefix}_{name}"
    
    dest_path = os.path.join(dest_directory, f"{name}{ext}")
    
    # Se o arquivo já existe, adiciona um número ao nome
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(dest_directory, f"{name}_{counter}{ext}")
        counter += 1
    
    shutil.copy2(source_path, dest_path)
    return dest_path