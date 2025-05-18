#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GoNetwork AI - Interface Moderna com qt-material
# ///////////////////////////////////////////////////////////////

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QHeaderView
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon

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
        self.resize(1024, 700)

        # ACCESS THE EVENT CONTEXT
        self.event_context = EventContext()

        # CREATE CENTRAL WIDGET
        self.central_widget = QStackedWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # INITIALIZE WINDOWS
        self.init_windows()
        
        # SET DEFAULT PAGE
        self.show_welcome_message()
        
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
        self.central_widget.addWidget(self.event_config_window)  # índice 0
        self.central_widget.addWidget(self.team_management_window)  # índice 1
        self.central_widget.addWidget(self.briefing_window)  # índice 2
        self.central_widget.addWidget(self.timeline_window)  # índice 3
        self.central_widget.addWidget(self.capture_window)  # índice 4
        self.central_widget.addWidget(self.editing_window)  # índice 5
        self.central_widget.addWidget(self.delivery_window)  # índice 6
        self.central_widget.addWidget(self.analytics_window)  # índice 7
        
        # Set default page
        self.central_widget.setCurrentIndex(0)
    
    def switch_page(self, index):
        """Change to a specific page"""
        if 0 <= index < self.central_widget.count():
            self.central_widget.setCurrentIndex(index)
    
    def show_welcome_message(self):
        """Show welcome message"""
        QMessageBox.information(
            self,
            "Bem-vindo ao GoNetwork AI",
            "Sistema de gerenciamento audiovisual em tempo real.\n\n"
            "Esta é uma versão simplificada da interface para evitar problemas de renderização."
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
    app.setWindowIcon(QIcon("public/logo.png"))
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Execute application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
