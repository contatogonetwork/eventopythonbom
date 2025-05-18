import sys
import os

# Adiciona os diretórios necessários ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
gonetwork_dir = os.path.join(current_dir, "gonetwork_dracula")
sys.path.insert(0, current_dir)
sys.path.insert(0, gonetwork_dir)

# Importa o arquivo main diretamente
from gonetwork_dracula.main import main

if __name__ == "__main__":
    main()
