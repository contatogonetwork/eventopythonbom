# Correções aplicadas ao GoNetwork AI Dracula

## 1. Conversão de PySide6 para PyQt5
- Substituídas todas as importações de PySide6 por PyQt5 nos seguintes arquivos:
  - `modules/__init__.py`
  - `modules/resources_rc.py`
  - `widgets/custom_grips/custom_grips.py`

## 2. Correções estruturais
- Corrigida a indentação do método `init_windows` no arquivo `main.py`
- Corrigida a indentação do método `show_welcome_message` no arquivo `main.py`
- Modificado o método `init_windows` para usar uma abordagem mais robusta de gerenciamento de widgets

## 3. Configuração de importação
- Atualizado o arquivo `run_gonetwork_dracula.py` para adicionar os diretórios corretos ao path do Python
- Corrigida a forma de importação do módulo principal

## 4. Correções de bugs específicos
- Corrigida a referência às páginas no stackedWidget (removida a dependência de nomes hardcoded)
- Simplificado o processo de remoção e adição de widgets

## 5. Dependências
- Criado um script `install_dependencies.py` para instalar todas as bibliotecas necessárias

## Uso
1. Execute `python install_dependencies.py` para instalar as dependências
2. Execute `python run_gonetwork_dracula.py` para iniciar o aplicativo

## Problemas conhecidos
- Certifique-se de ter o PyQt5 instalado corretamente no ambiente
- Em caso de problemas de importação, verifique o arquivo `__init__.py` nos diferentes módulos
