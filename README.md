# GoNetwork AI - Guia de Instalação

Este documento descreve como configurar e executar o projeto GoNetwork AI.

## Requisitos

- Python 3.8 ou superior
- Pacotes listados em `requirements.txt`

## Configuração do Ambiente

1. **Criar e ativar ambiente virtual:**

   ```powershell
   # No Windows (PowerShell)
   python -m venv env
   .\env\Scripts\Activate.ps1
   
   # No Linux/macOS
   python -m venv env
   source env/bin/activate
   ```

2. **Instalar dependências:**

   ```
   pip install -r requirements.txt
   ```

3. **Inicializar o banco de dados:**

   ```
   python -m db.setup
   ```

## Execução

Para iniciar o aplicativo:

```
python main.py
```

## Estrutura do Projeto

- `main.py` - Ponto de entrada do aplicativo
- `db/` - Contém modelos de dados e scripts de configuração do banco de dados
- `windows/` - Interfaces de usuário do aplicativo
- `lib/` - Módulos de biblioteca e utilitários
- `public/` - Recursos estáticos como imagens

## Notas de Desenvolvimento

- O aplicativo usa SQLite para armazenamento de dados
- A interface gráfica é construída com PyQt5
- O banco de dados usa SQLAlchemy ORM
