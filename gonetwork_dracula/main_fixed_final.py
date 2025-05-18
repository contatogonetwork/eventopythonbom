#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import traceback
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMessageBox, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QFont

# Import event context
from lib.event_context import EventContext

# Import application windows
from windows.event_config_window import EventConfigWindow
from windows.team_management_window import TeamManagementWindow
from windows.briefing_window import BriefingWindow
from windows.timeline_window import TimelineWindow
from windows.capture_window import CaptureWindow
from windows.editing_window import EditingWindow
from windows.delivery_window import DeliveryWindow
from windows.analytics_window import AnalyticsWindow

# Import database setup
from db.setup import init_db

# HIGH DPI SUPPORT
os.environ["QT_FONT_DPI"] = "96"


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET WINDOW TITLE AND SIZE
        self.setWindowTitle("GoNetwork AI - Produção Audiovisual em Tempo Real")
        self.resize(1200, 800)
        
        # SET BASE STYLES
        self.setStyleSheet("""
            QMainWindow {
                background-color: #282a36;
                color: #f8f8f2;
            }
            QLabel {
                color: #f8f8f2;
            }
            QPushButton {
                background-color: #44475a;
                color: #f8f8f2;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #6272a4;
            }
            QPushButton:pressed {
                background-color: #bd93f9;
            }
            QPushButton:checked {
                background-color: #bd93f9;
                font-weight: bold;
            }
        """)

        # ACCESS THE EVENT CONTEXT
        self.event_context = EventContext()

        # CREATE MAIN WIDGET AND LAYOUT
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.main_widget)
        
        # CREATE SIDEBAR
        self.setup_sidebar()
        
        # CREATE STACKEDWIDGET FOR CONTENT
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack, 1)
        
        # INITIALIZE WINDOWS
        self.init_windows()
        
        # SET DEFAULT PAGE
        self.switch_page(0)
        self.show_welcome_message()
        
    def setup_sidebar(self):
        """Create sidebar with navigation buttons"""
        # Sidebar container
        sidebar = QFrame()
        sidebar.setMinimumWidth(220)
        sidebar.setMaximumWidth(220)
        sidebar.setStyleSheet("""
            background-color: #21222c;
            border-right: 1px solid #44475a;
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(5)
        
        # Logo/title area
        title_area = QWidget()
        title_layout = QVBoxLayout(title_area)
        
        title_label = QLabel("GoNetwork AI")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #bd93f9; margin-top: 20px;")
        title_layout.addWidget(title_label)
        
        subtitle = QLabel("Produção Audiovisual")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6272a4; margin-bottom: 20px;")
        title_layout.addWidget(subtitle)
        
        sidebar_layout.addWidget(title_area)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #44475a; max-height: 1px;")
        sidebar_layout.addWidget(line)
        
        nav_items = [
            {"text": "📋 Eventos", "index": 0},
            {"text": "👥 Equipe", "index": 1},
            {"text": "📝 Briefing", "index": 2},
            {"text": "⏱️ Timeline", "index": 3},
            {"text": "📷 Captura", "index": 4},
            {"text": "✂️ Edição", "index": 5},
            {"text": "📦 Entregas", "index": 6},
            {"text": "📊 Análises", "index": 7}
        ]
        
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(15, 10, 15, 10)
        nav_layout.setSpacing(8)
        
        for item in nav_items:
            button = QPushButton(item["text"])
            button.setCheckable(True)
            button.setFont(QFont("Segoe UI", 10))
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(40)
            
            # Connect the button to the page change function
            idx = item["index"]
            button.clicked.connect(lambda checked=False, i=idx: self.switch_page(i))
            
            nav_layout.addWidget(button)
            self.nav_buttons.append(button)
        
        sidebar_layout.addWidget(nav_container)
        
        # Add stretch to push everything to the top
        sidebar_layout.addStretch()
        
        # Adicionar botão de reload
        reload_button = QPushButton("🔄 Recarregar")
        reload_button.setFont(QFont("Segoe UI", 10))
        reload_button.setCursor(Qt.PointingHandCursor)
        reload_button.setMinimumHeight(40)
        reload_button.setStyleSheet("""
            background-color: #44475a;
            margin: 10px 15px;
        """)
        reload_button.clicked.connect(self.reload_current_window)
        sidebar_layout.addWidget(reload_button)
        
        # Version label at the bottom
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #6272a4; padding: 15px 0;")
        sidebar_layout.addWidget(version_label)
        
        # Add the sidebar to the main layout
        self.main_layout.addWidget(sidebar, 0)
    
    def init_windows(self):
        """Initialize all application windows"""
        windows = [
            ("Configuração de Eventos", EventConfigWindow),
            ("Gerenciamento de Equipe", TeamManagementWindow),
            ("Briefing", BriefingWindow),
            ("Timeline", TimelineWindow),
            ("Captura", CaptureWindow),
            ("Edição", EditingWindow),
            ("Entregas", DeliveryWindow),
            ("Análises", AnalyticsWindow)
        ]
        
        error_messages = []
        
        for name, window_class in windows:
            try:
                window_instance = window_class()
                self.content_stack.addWidget(window_instance)
                setattr(self, f"{window_class.__name__.lower()}_instance", window_instance)
            except Exception as e:
                error_messages.append(f"Erro ao inicializar {name}: {str(e)}")
                print(f"Erro ao inicializar {name}:")
                print(traceback.format_exc())
                
                # Adicionar um widget vazio com mensagem de erro
                error_widget = QWidget()
                error_layout = QVBoxLayout(error_widget)
                
                error_label = QLabel(f"Erro ao carregar a janela {name}:")
                error_details = QLabel(str(e))
                error_label.setStyleSheet("color: #ff5555; font-weight: bold;")
                error_details.setStyleSheet("color: #ff5555;")
                error_details.setWordWrap(True)
                
                error_layout.addWidget(error_label)
                error_layout.addWidget(error_details)
                error_layout.addStretch()
                
                self.content_stack.addWidget(error_widget)
        
        # Se houver erros, mostrar um resumo
        if error_messages:
            QMessageBox.warning(
                self, 
                "Erros ao inicializar janelas", 
                "Algumas janelas não puderam ser inicializadas corretamente:\n\n" + 
                "\n".join(error_messages)
            )
    
    def switch_page(self, index):
        """Change to a specific page"""
        if 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)
            
            # Update button states
            for i, button in enumerate(self.nav_buttons):
                button.setChecked(i == index)
    
    def show_welcome_message(self):
        """Show welcome message"""
        QMessageBox.information(
            self,
            "Bem-vindo ao GoNetwork AI",
            "Sistema de gerenciamento audiovisual em tempo real.\n\n"
            "Esta versão utiliza uma interface minimalista no estilo Dracula.\n"
            "Use os botões no painel lateral para navegar entre as funcionalidades."
        )
        
    def reload_current_window(self):
        """Recarrega a janela atual"""
        current_index = self.content_stack.currentIndex()
        
        # Salvar o índice atual
        current_index = self.content_stack.currentIndex()
        
        # Criar uma mensagem informando sobre o recarregamento
        QMessageBox.information(
            self,
            "Recarregando",
            "A página atual será recarregada.\nIsso pode resolver problemas temporários."
        )
        
        # Recarregar todas as janelas (mais simples que recarregar apenas uma)
        self.content_stack.setCurrentIndex(0)  # Mudar para a primeira página enquanto recarrega
        
        # Limpar o stackedWidget
        while self.content_stack.count() > 0:
            widget = self.content_stack.widget(0)
            self.content_stack.removeWidget(widget)
            if widget:
                widget.deleteLater()
        
        # Reinicializar as janelas
        self.init_windows()
        
        # Voltar para a página que estava sendo visualizada, se possível
        if current_index < self.content_stack.count():
            self.content_stack.setCurrentIndex(current_index)
        else:
            self.content_stack.setCurrentIndex(0)
            
        # Atualizar os botões
        if current_index < len(self.nav_buttons):
            for i, button in enumerate(self.nav_buttons):
                button.setChecked(i == current_index)


def main():
    # Initialize the database
    init_db()
    
    # Configure application
    QCoreApplication.setApplicationName("GoNetwork AI")
    QCoreApplication.setOrganizationName("GoNetwork")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set app icon
    icon_path = os.path.join("gonetwork_dracula", "public", "logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Execute application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
