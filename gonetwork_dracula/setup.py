import sys
import os
from cx_Freeze import setup, Executable

# ADD FILES
files = [
    'icon.ico',
    'themes/',
    'public/',
    'db/',
    'lib/',
    'windows/'
]

# TARGET
target = Executable(
    script="main.py",
    base="Win32GUI",
    icon="public/logo.png",
    target_name="GoNetworkAI.exe"
)

# SETUP CX FREEZE
setup(
    name = "GoNetwork AI",
    version = "1.0",
    description = "Sistema de Gerenciamento Audiovisual em Tempo Real",
    author = "GoNetwork Team",
    options = {'build_exe' : {'include_files' : files}},
    executables = [target]
    
)
