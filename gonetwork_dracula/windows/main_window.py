from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QWidget, QStackedWidget, QMenu, QAction,
    QToolBar, QStatusBar, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from lib.event_context import EventContext
from windows.event_config_window import EventConfigWindow
from windows.team_management_window import TeamManagementWindow
from windows.briefing_window import BriefingWindow
from windows.timeline_window import TimelineWindow
from windows.capture_window import CaptureWindow
from windows.editing_window import EditingWindow
from windows.delivery_window import DeliveryWindow
from windows.analytics_window import AnalyticsWindow
from db.models import Event, get_db_session

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GoNetwork AI - Produção Audiovisual em Tempo Real")
        self.setGeometry(100, 100, 1200, 800)
        
        # Acesso ao contexto do evento
        self.event_context = EventContext()
        
        # Inicializar as janelas
        self.init_windows()
        
        # Criar interface
        self.init_ui()
        
        # Mostrar janela de boas-vindas
        self.show_welcome_message()
    
    def init_windows(self):
        """Inicializa todas as janelas da aplicação"""
        self.event_config_window = EventConfigWindow()
        self.team_management_window = TeamManagementWindow()
        self.briefing_window = BriefingWindow()
        self.timeline_window = TimelineWindow()
        self.capture_window = CaptureWindow()
        self.editing_window = EditingWindow()
        self.delivery_window = DeliveryWindow()
        self.analytics_window = AnalyticsWindow()
    
    def init_ui(self):
        # Widget principal
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Banner do evento atual
        self.event_banner = QWidget()
        event_banner_layout = QHBoxLayout()
        event_banner_layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("./public/logo.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        event_banner_layout.addWidget(logo_label)
        
        # Título do evento
        self.event_title = QLabel("Nenhum evento selecionado")
        self.event_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        event_banner_layout.addWidget(self.event_title)
        
        event_banner_layout.addStretch()
        
        # Menu de seleção de evento
        self.select_event_button = QPushButton("Selecionar Evento")
        self.select_event_button.clicked.connect(self.show_select_event_menu)
        event_banner_layout.addWidget(self.select_event_button)
        
        # Botão de novo evento
        self.new_event_button = QPushButton("Novo Evento")
        self.new_event_button.clicked.connect(self.show_event_config)
        event_banner_layout.addWidget(self.new_event_button)
        
        self.event_banner.setLayout(event_banner_layout)
        self.event_banner.setStyleSheet("background-color: #2C3E50;")
        main_layout.addWidget(self.event_banner)
        
        # Container para as janelas
        self.windows_container = QStackedWidget()
        self.windows_container.addWidget(self.event_config_window)
        self.windows_container.addWidget(self.team_management_window)
        self.windows_container.addWidget(self.briefing_window)
        self.windows_container.addWidget(self.timeline_window)
        self.windows_container.addWidget(self.capture_window)
        self.windows_container.addWidget(self.editing_window)
        self.windows_container.addWidget(self.delivery_window)
        self.windows_container.addWidget(self.analytics_window)
        main_layout.addWidget(self.windows_container)
        
        # Configurar widget principal
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Criar toolbar
        self.create_toolbar()
        
        # Criar barra de status
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Pronto")
        
        # Observar mudanças no contexto do evento
        self.event_context.add_observer(self)
    
    def create_toolbar(self):
        """Cria a toolbar com botões para as diferentes telas"""
        toolbar = QToolBar("Navegação")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        
        # Botões da toolbar
        # Configuração do Evento
        event_action = QAction(QIcon("./public/icons/event.png"), "Evento", self)
        event_action.triggered.connect(lambda: self.windows_container.setCurrentWidget(self.event_config_window))
        toolbar.addAction(event_action)
        
        # Gerenciamento de Equipe
        team_action = QAction(QIcon("./public/icons/team.png"), "Equipe", self)
        team_action.triggered.connect(lambda: self.windows_container.setCurrentWidget(self.team_management_window))
        toolbar.addAction(team_action)
        
        # Briefing
        briefing_action = QAction(QIcon("./public/icons/briefing.png"), "Briefing", self)
        briefing_action.triggered.connect(lambda: self.windows_container.setCurrentWidget(self.briefing_window))
        toolbar.addAction(briefing_action)
        
        # Timeline
        timeline_action = QAction(QIcon("./public/icons/timeline.png"), "Timeline", self)
        timeline_action.triggered.connect(lambda: self.windows_container.setCurrentWidget(self.timeline_window))
        toolbar.addAction(timeline_action)
        
        # Captação
        capture_action = QAction(QIcon("./public/icons/capture.png"), "Captação", self)
        capture_action.triggered.connect(lambda: self.windows_container.setCurrentWidget(self.capture_window))
        toolbar.addAction(capture_action)
        
        # Edição
        editing_action = QAction(QIcon("./public/icons/editing.png"), "Edição", self)
        editing_action.triggered.connect(lambda: self.windows_container.setCurrentWidget(self.editing_window))
        toolbar.addAction(editing_action)
        
        # Entregas
        delivery_action = QAction(QIcon("./public/icons/delivery.png"), "Entregas", self)
        delivery_action.triggered.connect(lambda: self.windows_container.setCurrentWidget(self.delivery_window))
        toolbar.addAction(delivery_action)
        
        # Analytics
        analytics_action = QAction(QIcon("./public/icons/analytics.png"), "Métricas", self)
        analytics_action.triggered.connect(lambda: self.windows_container.setCurrentWidget(self.analytics_window))
        toolbar.addAction(analytics_action)
    
    def on_event_changed(self, event_id, event_name):
        """Chamado quando o evento atual é alterado"""
        if event_id:
            self.event_title.setText(f"Evento: {event_name}")
        else:
            self.event_title.setText("Nenhum evento selecionado")
    
    def show_event_config(self):
        """Mostra a janela de configuração de evento"""
        # Limpar o evento atual para criar um novo
        self.event_context.clear()
        self.windows_container.setCurrentWidget(self.event_config_window)
    
    def show_select_event_menu(self):
        """Mostra o menu de seleção de eventos"""
        menu = QMenu(self)
        
        session = get_db_session()
        events = session.query(Event).order_by(Event.created_at.desc()).all()
        
        if events:
            for event in events:
                action = QAction(event.name, self)
                action.triggered.connect(lambda checked, e=event: self.select_event(e.id, e.name))
                menu.addAction(action)
        else:
            no_events_action = QAction("Nenhum evento encontrado", self)
            no_events_action.setEnabled(False)
            menu.addAction(no_events_action)
        
        session.close()
        
        menu.exec_(self.select_event_button.mapToGlobal(
            self.select_event_button.rect().bottomLeft()
        ))
    
    def select_event(self, event_id, event_name):
        """Seleciona um evento existente"""
        self.event_context.event_id = event_id
        self.event_context.event_name = event_name
        
        # Ir para a tela de timeline por padrão
        self.windows_container.setCurrentWidget(self.timeline_window)
    
    def show_welcome_message(self):
        """Mostra mensagem de boas-vindas"""
        QMessageBox.information(
            self,
            "Bem-vindo ao GoNetwork AI",
            "Bem-vindo ao sistema de gerenciamento audiovisual em tempo real!\n\n"
            "Para começar, crie um novo evento ou selecione um existente.\n\n"
            "Criado por: GoNetwork Team"
        )