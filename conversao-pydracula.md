# Conversão do GoNetwork AI para PyDracula

## Transformações Implementadas

### 1. Estrutura do Projeto
- **Clonado** o repositório PyDracula para a pasta `gonetwork_dracula/`
- **Convertido** o código de PySide6 para PyQt5 nos arquivos principais:
  - `modules/__init__.py`
  - `modules/ui_main.py`
  - `modules/ui_functions.py`
  - `main.py`

### 2. Integração com o Projeto Existente
- **Copiado** diretórios essenciais do projeto original:
  - `db/` (modelos de banco de dados SQLAlchemy)
  - `lib/` (utilitários como `event_context.py`)
  - `windows/` (contendo todas as janelas da aplicação)
  - `public/` (recursos como logo.png)

### 3. Adaptação da Interface
- **Renomeado** botões e rótulos da interface para corresponder às funcionalidades:
  - Home -> Eventos
  - Widgets -> Equipe
  - New -> Briefing
  - Save -> Timeline
  - Exit -> Captura
  - Settings -> Edição
  - Info -> Entregas
  - Analytics (novo) -> Análises

### 4. Integração de Páginas
- **Substituído** as páginas de exemplo por janelas funcionais do GoNetwork AI:
  - Integradas todas as 8 janelas principais ao `stackedWidget`
  - Configurada a navegação entre páginas
  - Mapeados os botões para as páginas correspondentes

### 5. Estilo e Tema
- **Configurado** o tema escuro Dracula como padrão
- Ajustados cores e estilos para manter a uniformidade
- Adaptado o esquema de cores para focar na experiência do usuário

### 6. Ajustes Técnicos
- **Atualizado** os caminhos de importação para funcionar na nova estrutura
- Criado script independente `run_gonetwork_dracula.py` para iniciar o aplicativo
- Implementada integração com o contexto de evento existente
- Configurados ícones e descrições personalizados

### 7. Documentação
- **Criado** README.md com instruções completas
- Atualizado requirements.txt para incluir as dependências necessárias
- Implementado arquivo setup.py para compilação em executável

## Arquivos Modificados
1. `modules/__init__.py` - Convertido de PySide6 para PyQt5
2. `modules/ui_main.py` - Convertido de PySide6 para PyQt5
3. `modules/app_settings.py` - Adicionado configurações personalizadas
4. `main.py` - Integrado com janelas do GoNetwork AI
5. `setup.py` - Atualizado para incluir recursos do GoNetwork AI
6. `requirements.txt` - Atualizado com dependências necessárias

## Scripts Criados
- `run_gonetwork_dracula.py` - Script de inicialização principal

## Conclusão
O projeto GoNetwork AI foi convertido com sucesso para utilizar a interface moderna PyDracula, mantendo todas as funcionalidades existentes enquanto melhora significativamente a experiência visual do usuário.
