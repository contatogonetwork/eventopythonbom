#!/usr/bin/env python
# Script para iniciar o aplicativo GoNetwork AI com interface final
import sys
import os

# Adiciona os diretórios necessários ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
gonetwork_dir = os.path.join(current_dir, "gonetwork_dracula")
sys.path.insert(0, current_dir)
sys.path.insert(0, gonetwork_dir)

# Executa o arquivo main_final.py diretamente
if __name__ == "__main__":
    # Em vez de importar, executamos o arquivo diretamente
    main_file = os.path.join(gonetwork_dir, "main_final.py")
    with open(main_file) as f:
        exec(f.read())
