from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QTimer, pyqtSlot
from lib.event_context import EventContext, EventAwareWindow
from lib.asset_ingestor import setup_ingestor
from db.models import Asset, get_db_session
import os
import subprocess

class CaptureWindow(QWidget, EventAwareWindow):
    def __init__(self):
        QWidget.__init__(self)
        EventAwareWindow.__init__(self)
        
        # Inicializar sistema de ingestão
        self.ingestor = setup_ingestor()
        self.ingestor.register_callback(self.on_file_ingested)
        
        # Status do monitoramento
        self.monitoring_active = False
        
        self.init_ui()
        
        # Timer para atualizar a tabela periodicamente
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(5000)  # 5 segundos
        self.update_timer.timeout.connect(self.update_asset_table)
        self.update_timer.start()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Status de monitoramento
        self.status_label = QLabel("Monitoramento inativo")
        layout.addWidget(self.status_label)
        
        # Caminho da pasta monitorada
        watch_dir = self.ingestor.watch_dir
        self.watch_dir_label = QLabel(f"Pasta monitorada: {watch_dir}")
        layout.addWidget(self.watch_dir_label)
        
        # Botões de controle
        self.toggle_button = QPushButton("Iniciar Monitoramento")
        self.toggle_button.clicked.connect(self.toggle_monitoring)
        layout.addWidget(self.toggle_button)
        
        open_folder_button = QPushButton("Abrir Pasta de Entrada")
        open_folder_button.clicked.connect(self.open_watch_folder)
        layout.addWidget(open_folder_button)
        
        ingest_files_button = QPushButton("Ingerir Arquivos Manualmente")
        ingest_files_button.clicked.connect(self.ingest_files_manually)
        layout.addWidget(ingest_files_button)
        
        # Tabela de arquivos recentes
        layout.addWidget(QLabel("Arquivos Recentes:"))
        self.asset_table = QTableWidget()
        self.asset_table.setColumnCount(4)
        self.asset_table.setHorizontalHeaderLabels(["Nome do Arquivo", "Tipo", "Tamanho (MB)", "Horário"])
        self.asset_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.asset_table)
        
        self.setLayout(layout)
        self.setWindowTitle("Captação e Ingestão")
        
        # Atualizar tabela inicialmente
        self.update_asset_table()
    
    def on_event_changed(self, event_id, event_name):
        """Implementação do EventAwareWindow"""
        # Atualizar a tabela de assets quando o evento mudar
        self.update_asset_table()
        
        # Atualizar título da janela
        if event_name:
            self.setWindowTitle(f"Captação e Ingestão - {event_name}")
        else:
            self.setWindowTitle("Captação e Ingestão")
    
    def toggle_monitoring(self):
        """Inicia ou para o monitoramento da pasta"""
        if self.monitoring_active:
            self.ingestor.stop_monitoring()
            self.monitoring_active = False
            self.status_label.setText("Monitoramento inativo")
            self.toggle_button.setText("Iniciar Monitoramento")
        else:
            if not self.event_context.event_id:
                self.status_label.setText("Erro: Nenhum evento selecionado")
                return
                
            self.ingestor.start_monitoring()
            self.monitoring_active = True
            self.status_label.setText("Monitoramento ativo - Aguardando novos arquivos")
            self.toggle_button.setText("Parar Monitoramento")
    
    def open_watch_folder(self):
        """Abre a pasta monitorada no explorador de arquivos"""
        watch_dir = str(self.ingestor.watch_dir)
        
        if os.name == 'nt':  # Windows
            os.startfile(watch_dir)
        elif os.name == 'posix':  # Linux/Mac
            try:
                subprocess.Popen(['xdg-open', watch_dir])
            except:
                subprocess.Popen(['open', watch_dir])
    
    def ingest_files_manually(self):
        """Abre diálogo para ingestão manual de arquivos"""
        if not self.event_context.event_id:
            self.status_label.setText("Erro: Nenhum evento selecionado")
            return
            
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Arquivos para Ingestão",
            "",
            "Arquivos de Mídia (*.mp4 *.mov *.avi *.jpg *.png *.raw *.wav)"
        )
        
        if files:
            for file_path in files:
                self.ingestor.process_file(file_path)
            
            # Atualizar tabela após ingestão
            self.update_asset_table()
    
    @pyqtSlot(str, str)
    def on_file_ingested(self, file_path, asset_id):
        """Callback chamado quando um arquivo é ingerido com sucesso"""
        self.status_label.setText(f"Arquivo processado: {os.path.basename(file_path)}")
        self.update_asset_table()
    
    def update_asset_table(self):
        """Atualiza a tabela de assets com os arquivos mais recentes"""
        if not self.event_context.event_id:
            self.asset_table.setRowCount(0)
            return
        
        session = get_db_session()
        recent_assets = session.query(Asset).filter(
            Asset.event_id == self.event_context.event_id
        ).order_by(Asset.ingest_time.desc()).limit(20).all()
        
        self.asset_table.setRowCount(len(recent_assets))
        
        for i, asset in enumerate(recent_assets):
            self.asset_table.setItem(i, 0, QTableWidgetItem(asset.file_name))
            self.asset_table.setItem(i, 1, QTableWidgetItem(asset.file_type))
            self.asset_table.setItem(i, 2, QTableWidgetItem(f"{asset.file_size:.2f}"))
            self.asset_table.setItem(i, 3, QTableWidgetItem(asset.ingest_time.strftime("%H:%M:%S")))
        
        session.close()