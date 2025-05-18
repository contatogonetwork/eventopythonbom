import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import qdarkstyle
from windows.main_window import MainWindow
from db.setup import init_db

def main():
    # Inicializar o banco de dados
    init_db()
    
    # Configurar aplicação
    QCoreApplication.setApplicationName("GoNetwork AI")
    QCoreApplication.setOrganizationName("GoNetwork")
    
    # Criar aplicação
    app = QApplication(sys.argv)
    
    # Aplicar tema escuro
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    # Criar janela principal
    window = MainWindow()
    window.setWindowIcon(QIcon("./public/logo.png"))
    window.show()
    
    # Executar aplicação
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()