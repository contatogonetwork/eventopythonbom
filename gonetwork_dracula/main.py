# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA (ORIGINAL TEMPLATE)
# MODIFIED BY: GONETWORK AI TEAM
# PROJECT MADE WITH: Qt Designer and PyQt5
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import platform

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget, QMessageBox, QMainWindow, QHeaderView
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon

# Ensure modules directory is in path 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# Import database setup
from db.setup import init_db

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

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # ACCESS THE EVENT CONTEXT
        # ///////////////////////////////////////////////////////////////
        self.event_context = EventContext()
        
        # INITIALIZE WINDOWS
        # ///////////////////////////////////////////////////////////////
        self.init_windows()

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True
        
        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "GoNetwork AI - Produção Audiovisual em Tempo Real"
        description = "Gerenciamento de eventos audiovisuais em tempo real"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)
        
        # CONFIGURE UI TEXTS
        # ///////////////////////////////////////////////////////////////
        Settings.setup_ui_text(widgets)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS - conectando os botões disponíveis
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)
        
        # Botões adicionais - verificando se existem antes de conectar
        if hasattr(widgets, "btn_share"):
            widgets.btn_share.clicked.connect(self.buttonClick)
            
        if hasattr(widgets, "btn_adjustments"):
            widgets.btn_adjustments.clicked.connect(self.buttonClick)
            
        if hasattr(widgets, "btn_more"):
            widgets.btn_more.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)
            
        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(0)) # Event Config as default
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))
        
        # Display welcome message
        self.show_welcome_message()


    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # EVENTO CONFIG (HOME)
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(0))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            widgets.titleRightInfo.setText("Configuração de Eventos")

        # TEAM MANAGEMENT
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(1))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            widgets.titleRightInfo.setText("Gerenciamento de Equipe")

        # BRIEFING
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(2))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            widgets.titleRightInfo.setText("Briefing")
            
        # TIMELINE
        if btnName == "btn_save":
            widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(3))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            widgets.titleRightInfo.setText("Timeline")
            
        # CAPTURE
        if btnName == "btn_exit":
            widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(4))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            widgets.titleRightInfo.setText("Captura de Mídia")
              # EDITING (novo nome: btn_share)
        if btnName == "btn_share":
            widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(5))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            widgets.titleRightInfo.setText("Edição")
            
        # DELIVERY (novo nome: btn_adjustments)
        if btnName == "btn_adjustments":
            widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(6))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            widgets.titleRightInfo.setText("Entregas")
            
        # ANALYTICS (novo nome: btn_more)
        if btnName == "btn_more":
            widgets.stackedWidget.setCurrentWidget(widgets.stackedWidget.widget(7))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            widgets.titleRightInfo.setText("Análises")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')


    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

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
        
        # Limpar o stackedWidget e adicionar novas páginas
        # Remover as páginas existentes
        if hasattr(self.ui, "home"):
            self.ui.stackedWidget.removeWidget(self.ui.home)
        
        if hasattr(self.ui, "widgets"):
            self.ui.stackedWidget.removeWidget(self.ui.widgets)
            
        if hasattr(self.ui, "new_page"):
            self.ui.stackedWidget.removeWidget(self.ui.new_page)
        
        # Adicionar novas páginas
        # Página 1 - Event Config
        self.ui.stackedWidget.insertWidget(0, self.event_config_window)
        
        # Página 2 - Team Management
        self.ui.stackedWidget.insertWidget(1, self.team_management_window)
        
        # Página 3 - Briefing
        self.ui.stackedWidget.insertWidget(2, self.briefing_window)
        
        # Página 4 - Timeline
        self.ui.stackedWidget.insertWidget(3, self.timeline_window)
        
        # Página 5 - Capture
        self.ui.stackedWidget.insertWidget(4, self.capture_window)
        
        # Página 6 - Editing
        self.ui.stackedWidget.insertWidget(5, self.editing_window)
        
        # Página 7 - Delivery
        self.ui.stackedWidget.insertWidget(6, self.delivery_window)
        
        # Página 8 - Analytics
        self.ui.stackedWidget.insertWidget(7, self.analytics_window)
    
    def show_welcome_message(self):
        """Show welcome message"""
        QMessageBox.information(
            self,
            "Bem-vindo ao GoNetwork AI",
            "Sistema de gerenciamento audiovisual em tempo real.\n\n"
            "Selecione um evento existente ou crie um novo para começar."
        )

def main():
    # Initialize the database
    init_db()
    
    # Configure application
    QCoreApplication.setApplicationName("GoNetwork AI")
    QCoreApplication.setOrganizationName("GoNetwork")
    
    # Create application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("public/logo.png"))
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Execute application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
