# GoNetwork AI - Interface PyDracula

## Sobre o Projeto
O GoNetwork AI é um sistema de gerenciamento audiovisual em tempo real que permite configurar eventos, gerenciar equipes, criar briefings, timelines, captura, edição e entrega de conteúdo audiovisual.

Esta versão usa a moderna interface PyDracula, com tema escuro inspirado no Dracula Theme, adaptado do PySide6 para PyQt5.

## Funcionalidades
- **Configuração de Eventos**: Gerenciamento completo de eventos audiovisuais
- **Gerenciamento de Equipe**: Organização e alocação de pessoal
- **Briefing**: Criação e edição de briefings detalhados
- **Timeline**: Planejamento temporal dos eventos
- **Captura**: Interface para captura de mídia em tempo real
- **Edição**: Ferramentas para edição e pós-produção
- **Entregas**: Gestão de entregas de conteúdo
- **Análises**: Métricas e estatísticas dos eventos

## Requisitos
- Python 3.9 ou superior
- PyQt5
- SQLAlchemy

## Instalação

### 1. Instalar dependências
```bash
python install_dependencies.py
```

### 2. Executar a aplicação
```bash
python run_gonetwork_dracula.py
```

## Solução de Problemas

### Erro de Importação de Módulo
Se você encontrar erros como `ModuleNotFoundError: No module named 'modules'`, verifique:
- Certifique-se de executar o script a partir do diretório raiz
- Confirme que o PyQt5 está instalado corretamente

### Problemas de Interface
Se os botões ou páginas não estiverem aparecendo corretamente:
- Verifique as referências aos nomes dos widgets no arquivo `main.py`
- Confirme que todas as janelas foram inicializadas corretamente

### Erros de Renderização
Se você ver mensagens como "UpdateLayeredWindowIndirect failed":
- Estes são avisos comuns do PyQt5 no Windows e geralmente não afetam o funcionamento

## Arquitetura do Projeto
- `main.py`: Arquivo principal da aplicação
- `modules/`: Contém os arquivos de configuração da UI
- `windows/`: Implementações das janelas específicas
- `db/`: Modelos de banco de dados SQLAlchemy
- `lib/`: Utilitários e classes auxiliares

## Créditos
- Interface PyDracula original por Wanderson M. Pimenta
- Adaptação e integração com GoNetwork AI pela equipe GoNetwork
