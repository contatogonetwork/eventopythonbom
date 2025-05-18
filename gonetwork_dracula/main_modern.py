#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GoNetwork AI - Interface Moderna com qt-material
# ///////////////////////////////////////////////////////////////

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMessageBox, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
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

        # ACCESS THE EVENT CONTEXT
        self.event_context = EventContext()

        # CREATE MAIN WIDGET AND LAYOUT
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)
        
        # CREATE SIDEBAR
        self.setup_sidebar()
        
        # CREATE STACKEDWIDGET FOR CONTENT
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)
        
        # Set content to 80% of the width
        self.main_layout.setStretch(1, 80)
        
        # INITIALIZE WINDOWS
        self.init_windows()
        
        # SET DEFAULT PAGE
        self.show_welcome_message()
        
    def setup_sidebar(self):
        """Create sidebar with navigation buttons"""
        # Sidebar container
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet("""
            #sidebar {
                background-color: #2D2D2D;
                border-right: 1px solid #555555;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Logo/title area
        title_label = QLabel("GoNetwork AI")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #FFFFFF; margin: 10px 0;")
        sidebar_layout.addWidget(title_label)
        
        # Subtitle
        subtitle = QLabel("Produção Audiovisual")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #AAAAAA; margin-bottom: 20px;")
        sidebar_layout.addWidget(subtitle)
        
        # Navigation buttons
        self.nav_buttons = []
        
        nav_items = [
            {"text": "Eventos", "index": 0},
            {"text": "Equipe", "index": 1},
            {"text": "Briefing", "index": 2},
            {"text": "Timeline", "index": 3},
            {"text": "Captura", "index": 4},
            {"text": "Edição", "index": 5},
            {"text": "Entregas", "index": 6},
            {"text": "Análises", "index": 7}
        ]
        
        for item in nav_items:
            button = QPushButton(item["text"])
            button.setCheckable(True)
            button.setFixedHeight(45)
            button.setFont(QFont("Segoe UI", 10))
            button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 20px;
                    background-color: transparent;
                    color: #DDDDDD;
                    border: none;
                    border-radius: 5px;
                    margin: 3px 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:checked {
                    background-color: rgba(0, 128, 128, 0.5);
                    color: white;
                    font-weight: bold;
                }
            """)
            
            # Connect the button to the page change function
            idx = item["index"]
            button.clicked.connect(lambda checked=False, i=idx: self.switch_page(i))
            
            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)
        
        # Add stretch to push everything to the top
        sidebar_layout.addStretch()
        
        # Version label at the bottom
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #888888; margin: 10px 0;")
        sidebar_layout.addWidget(version_label)
        
        # Add the sidebar to the main layout
        self.main_layout.addWidget(sidebar)
    
    def init_windows(self):
        """Initialize all application windows"""
        self.event_config_window = EventConfigWindow()
        self.team_management_window = TeamManagementWindow()
        self.briefing_window = BriefingWindow()
        self.timeline_window = TimelineWindow()
        self.capture_window = CaptureWindow()
        self.editing_window = EditingWindow()
        self.delivery_window = DeliveryWindow()
        self.analytics_window = AnalyticsWindow()
        
        # Add windows to stackedWidget
        self.content_stack.addWidget(self.event_config_window)  # índice 0
        self.content_stack.addWidget(self.team_management_window)  # índice 1
        self.content_stack.addWidget(self.briefing_window)  # índice 2
        self.content_stack.addWidget(self.timeline_window)  # índice 3
        self.content_stack.addWidget(self.capture_window)  # índice 4
        self.content_stack.addWidget(self.editing_window)  # índice 5
        self.content_stack.addWidget(self.delivery_window)  # índice 6
        self.content_stack.addWidget(self.analytics_window)  # índice 7
        
        # Set default page
        self.switch_page(0)
    
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
            "Use os botões no painel lateral para navegar entre as funcionalidades."
        )


def main():
    # Initialize the database
    init_db()
    
    # Configure application
    QCoreApplication.setApplicationName("GoNetwork AI")
    QCoreApplication.setOrganizationName("GoNetwork")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Apply material theme (dark_teal)
    try:
        from qt_material import apply_stylesheet
        apply_stylesheet(app, theme='dark_teal.xml')
    except ImportError:
        print("qt-material não encontrado, usando estilo padrão")
    
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
