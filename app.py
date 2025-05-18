import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import os

# Change working directory to project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add current directory to Python path
sys.path.append(os.getcwd())

# Import components for the application setup
from gonetwork_dracula.main import MainWindow
from db.setup import init_db

def main():
    # Set environment variable for high DPI support
    os.environ["QT_FONT_DPI"] = "96"
    
    # Initialize the database
    init_db()
    
    # Configure application
    QCoreApplication.setApplicationName("GoNetwork AI")
    QCoreApplication.setOrganizationName("GoNetwork")
    
    # Create application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./public/logo.png"))
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Execute application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
