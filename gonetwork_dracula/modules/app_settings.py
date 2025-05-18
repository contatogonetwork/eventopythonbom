class Settings():
    # APP SETTINGS
    # ///////////////////////////////////////////////////////////////
    ENABLE_CUSTOM_TITLE_BAR = True
    MENU_WIDTH = 240
    LEFT_BOX_WIDTH = 240
    RIGHT_BOX_WIDTH = 240
    TIME_ANIMATION = 500

    # BTNS LEFT AND RIGHT BOX COLORS
    BTN_LEFT_BOX_COLOR = "background-color: rgb(44, 49, 58);"
    BTN_RIGHT_BOX_COLOR = "background-color: #ff79c6;"

    # MENU SELECTED STYLESHEET
    MENU_SELECTED_STYLESHEET = """
    border-left: 22px solid qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 rgba(255, 121, 198, 255), stop:0.5 rgba(85, 170, 255, 0));
    background-color: rgb(40, 44, 52);
    """
    
    # Função para configurar os textos e ícones da interface    @staticmethod
    def setup_ui_text(widgets):
        """
        Configura os textos e ícones da interface com base no template Dracula,
        adaptando para as funcionalidades do GoNetwork AI.
        
        Args:
            widgets: Referência global para os widgets da interface (UI_MainWindow)
        """
        # Botões da barra lateral (verificando se existem antes de modificar)
        if hasattr(widgets, "btn_home"):
            widgets.btn_home.setText("Eventos")
            
        if hasattr(widgets, "btn_widgets"):
            widgets.btn_widgets.setText("Equipe")
            
        if hasattr(widgets, "btn_new"):
            widgets.btn_new.setText("Briefing")
            
        if hasattr(widgets, "btn_save"):
            widgets.btn_save.setText("Timeline")
            
        if hasattr(widgets, "btn_exit"):
            widgets.btn_exit.setText("Captura")
            
        # Buttons para funcionalidades adicionais
        if hasattr(widgets, "btn_share"):
            widgets.btn_share.setText("Edição")
            
        if hasattr(widgets, "btn_adjustments"):
            widgets.btn_adjustments.setText("Entregas")
            
        if hasattr(widgets, "btn_more"):
            widgets.btn_more.setText("Análises")
          # Textos gerais da interface (verificando se existem antes de modificar)
        if hasattr(widgets, "creditsLabel"):
            widgets.creditsLabel.setText("GoNetwork AI - v1.0.0")
            
        if hasattr(widgets, "titleLeftDescription"):
            widgets.titleLeftDescription.setText("Sistema de Gerenciamento Audiovisual")
        
        # Atualiza o título da página inicial 
        if hasattr(widgets, "titleRightInfo"):
            widgets.titleRightInfo.setText("Configuração de Eventos")
