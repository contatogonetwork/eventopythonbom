#!/usr/bin/env python
"""
Instalador de dependências para o GoNetwork AI Dracula.
Este script instala todas as bibliotecas necessárias para executar o projeto.
"""
import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências do projeto"""
    print("Instalando dependências do GoNetwork AI Dracula...")
    requirements = [
        "PyQt5",
        "PyQt5-tools",
        "sqlalchemy",
        "pillow",
        "opencv-python"
    ]
    
    for req in requirements:
        print(f"Instalando {req}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    
    print("Todas as dependências foram instaladas com sucesso!")

if __name__ == "__main__":
    install_requirements()
