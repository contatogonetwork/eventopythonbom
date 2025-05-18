# GoNetwork AI - Versão Dracula Theme

## Sobre o Projeto
O GoNetwork AI é um sistema de gerenciamento audiovisual em tempo real que foi convertido para usar uma interface moderna no estilo Dracula Theme.

## Versões da Interface

### 1. Versão Original com PyDracula (com erros)
- Arquivo: `run_gonetwork_dracula.py`
- Baseada no template PyDracula original
- Problema: Erros de renderização "UpdateLayeredWindowIndirect failed"

### 2. Versão Simplificada (intermediária)
- Arquivo: `run_gonetwork_simple.py`
- Interface básica e limpa
- Soluciona erros de renderização

### 3. Versão com Material Design (com erros de SVG)
- Arquivo: `run_gonetwork_modern.py`
- Usa qt-material para temas
- Problema: Erros ao carregar arquivos SVG

### 4. Versão Final Recomendada (estável)
- Arquivo: `run_gonetwork_final.py`
- Interface moderna inspirada no Dracula Theme
- Design completamente estável e funcional
- Barra lateral para navegação
- Recursos para tratamento de erros e recarregamento

## Como Usar

### Executar a Aplicação (versão recomendada)
```bash
cd c:\novo
python run_gonetwork_final.py
```

### Navegação
- Use os botões na barra lateral para navegar entre as diferentes seções
- O botão "Recarregar" permite reiniciar a janela atual em caso de problemas

## Solução de Problemas

### Erros Corrigidos
- Erro na janela Timeline ao editar tarefas (NoneType no objeto text)
- Erro "wrapped C/C++ object has been deleted" ao salvar eventos
- A versão final inclui tratamento mais robusto de erros e gerenciamento de ciclo de vida

### Erros de Interface
- A versão final não depende de efeitos de transparência problemáticos
- Implementação própria do tema escuro sem dependências externas

## Tecnologias
- PyQt5 (em vez de PySide6 original)
- SQLAlchemy para banco de dados
- Tema visual personalizado inspirado no Dracula Theme

## Créditos
- Interface original PyDracula por Wanderson M. Pimenta
- Adaptação e melhorias pela equipe GoNetwork AI
