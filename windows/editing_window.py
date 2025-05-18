from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QComboBox, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSlot
from lib.event_context import EventContext, EventAwareWindow
from lib.video_player import VideoPlayer, TimecodeAnnotation
from db.models import Asset, Delivery, DeliveryVersion, get_db_session
import os
import datetime

class EditingWindow(QWidget, EventAwareWindow):
    def __init__(self):
        QWidget.__init__(self)
        EventAwareWindow.__init__(self)
        
        self.current_asset = None
        self.current_delivery = None
        
        self.init_ui()
        
        # Inicialmente carregar assets se evento já estiver selecionado
        if self.event_context.event_id:
            self.load_assets()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Splitter horizontal para dividir a tela
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel esquerdo: Lista de arquivos
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Arquivos Disponíveis:"))
        
        self.asset_table = QTableWidget()
        self.asset_table.setColumnCount(3)
        self.asset_table.setHorizontalHeaderLabels(["Arquivo", "Tipo", "Status"])
        self.asset_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.asset_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.asset_table.setSelectionMode(QTableWidget.SingleSelection)
        self.asset_table.itemSelectionChanged.connect(self.on_asset_selected)
        left_layout.addWidget(self.asset_table)
        
        # Controles para os arquivos
        file_control_layout = QHBoxLayout()
        
        self.load_asset_button = QPushButton("Carregar")
        self.load_asset_button.clicked.connect(self.load_selected_asset)
        self.load_asset_button.setEnabled(False)
        file_control_layout.addWidget(self.load_asset_button)
        
        self.mark_editing_button = QPushButton("Marcar como Editando")
        self.mark_editing_button.clicked.connect(self.mark_asset_editing)
        self.mark_editing_button.setEnabled(False)
        file_control_layout.addWidget(self.mark_editing_button)
        
        left_layout.addLayout(file_control_layout)
        
        # Painel direito: Player e controles de edição
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Player de vídeo
        self.video_player = VideoPlayer()
        self.video_player.annotationAdded.connect(self.on_annotation_added)
        right_layout.addWidget(self.video_player)
        
        # Controles de entrega
        delivery_layout = QVBoxLayout()
        
        delivery_header_layout = QHBoxLayout()
        delivery_header_layout.addWidget(QLabel("Entrega:"))
        
        self.delivery_combo = QComboBox()
        self.delivery_combo.currentIndexChanged.connect(self.on_delivery_selected)
        delivery_header_layout.addWidget(self.delivery_combo)
        
        self.create_delivery_button = QPushButton("Nova Entrega")
        self.create_delivery_button.clicked.connect(self.create_new_delivery)
        delivery_header_layout.addWidget(self.create_delivery_button)
        
        delivery_layout.addLayout(delivery_header_layout)
        
        # Área de anotações
        right_layout.addWidget(QLabel("Anotações:"))
        self.annotations_text = QTextEdit()
        self.annotations_text.setReadOnly(True)
        right_layout.addWidget(self.annotations_text)
        
        # Botões de aprovação
        approval_layout = QHBoxLayout()
        
        self.approve_button = QPushButton("Aprovar")
        self.approve_button.clicked.connect(self.approve_delivery)
        self.approve_button.setEnabled(False)
        approval_layout.addWidget(self.approve_button)
        
        self.reject_button = QPushButton("Solicitar Ajustes")
        self.reject_button.clicked.connect(self.reject_delivery)
        self.reject_button.setEnabled(False)
        approval_layout.addWidget(self.reject_button)
        
        self.create_version_button = QPushButton("Criar Nova Versão")
        self.create_version_button.clicked.connect(self.create_new_version)
        self.create_version_button.setEnabled(False)
        approval_layout.addWidget(self.create_version_button)
        
        right_layout.addLayout(approval_layout)
        
        # Adicionar painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Definir proporções iniciais do splitter
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        self.setWindowTitle("Edição e Aprovação")
        
    def on_event_changed(self, event_id, event_name):
        """Implementação do EventAwareWindow"""
        if event_id:
            self.setWindowTitle(f"Edição e Aprovação - {event_name}")
            self.load_assets()
            self.load_deliveries()
        else:
            self.setWindowTitle("Edição e Aprovação")
            self.asset_table.setRowCount(0)
            self.delivery_combo.clear()
    
    def load_assets(self):
        """Carrega os assets do evento atual"""
        if not self.event_context.event_id:
            return
            
        session = get_db_session()
        assets = session.query(Asset).filter(
            Asset.event_id == self.event_context.event_id
        ).order_by(Asset.ingest_time.desc()).all()
        
        self.asset_table.setRowCount(len(assets))
        
        for i, asset in enumerate(assets):
            self.asset_table.setItem(i, 0, QTableWidgetItem(asset.file_name))
            self.asset_table.setItem(i, 1, QTableWidgetItem(asset.file_type))
            self.asset_table.setItem(i, 2, QTableWidgetItem(asset.status))
            
            # Armazenar ID do asset para referência
            self.asset_table.setItem(i, 3, QTableWidgetItem(asset.id))
        
        # Esconder a coluna de ID
        self.asset_table.setColumnHidden(3, True)
        
        session.close()
    
    def load_deliveries(self):
        """Carrega as entregas do evento atual"""
        if not self.event_context.event_id:
            return
            
        session = get_db_session()
        deliveries = session.query(Delivery).filter(
            Delivery.event_id == self.event_context.event_id
        ).all()
        
        self.delivery_combo.clear()
        self.delivery_combo.addItem("Selecione uma entrega...", None)
        
        for delivery in deliveries:
            self.delivery_combo.addItem(
                f"{delivery.title} ({delivery.status})", 
                delivery.id
            )
        
        session.close()
    
    def on_asset_selected(self):
        """Chamado quando um asset é selecionado na tabela"""
        selected_items = self.asset_table.selectedItems()
        
        if selected_items:
            # Habilitar botões
            self.load_asset_button.setEnabled(True)
            self.mark_editing_button.setEnabled(True)
        else:
            # Desabilitar botões
            self.load_asset_button.setEnabled(False)
            self.mark_editing_button.setEnabled(False)
    
    def load_selected_asset(self):
        """Carrega o asset selecionado no player de vídeo"""
        selected_row = self.asset_table.currentRow()
        
        if selected_row >= 0:
            # Verificar se o item existe antes de acessá-lo
            id_item = self.asset_table.item(selected_row, 3)
            
            if id_item is None:
                QMessageBox.warning(self, "Erro", "Não foi possível obter os dados do asset selecionado.")
                return
                
            asset_id = id_item.text()
            
            session = get_db_session()
            asset = session.query(Asset).filter(Asset.id == asset_id).first()
            
            if asset:
                self.current_asset = asset
                
                # Carregar o arquivo no player
                if os.path.exists(asset.file_path):
                    self.video_player.load_video(asset.file_path)
                else:
                    QMessageBox.warning(
                        self,
                        "Arquivo não encontrado",
                        f"O arquivo {asset.file_name} não foi encontrado no caminho esperado."
                    )
            
            session.close()
    
    def mark_asset_editing(self):
        """Marca o asset selecionado como 'em edição'"""
        selected_row = self.asset_table.currentRow()
        
        if selected_row >= 0:
            # Verificar se o item existe antes de acessá-lo
            id_item = self.asset_table.item(selected_row, 3)
            
            if id_item is None:
                QMessageBox.warning(self, "Erro", "Não foi possível obter os dados do asset selecionado.")
                return
                
            asset_id = id_item.text()
            
            session = get_db_session()
            asset = session.query(Asset).filter(Asset.id == asset_id).first()
            
            if asset:
                asset.status = 'editing'
                session.commit()
                
                # Atualizar tabela
                self.asset_table.item(selected_row, 2).setText('editing')
            
            session.close()
    
    def on_delivery_selected(self, index):
        """Chamado quando uma entrega é selecionada no combo"""
        delivery_id = self.delivery_combo.itemData(index)
        
        if delivery_id:
            session = get_db_session()
            delivery = session.query(Delivery).filter(Delivery.id == delivery_id).first()
            
            if delivery:
                self.current_delivery = delivery
                
                # Habilitar botões de aprovação se houver versões
                has_versions = len(delivery.versions) > 0
                self.approve_button.setEnabled(has_versions)
                self.reject_button.setEnabled(has_versions)
                self.create_version_button.setEnabled(True)
                
                # Mostrar anotações da última versão
                if has_versions:
                    latest_version = max(delivery.versions, key=lambda v: v.version_number)
                    self.annotations_text.setText(latest_version.feedback or "Sem anotações")
                else:
                    self.annotations_text.clear()
            
            session.close()
        else:
            self.current_delivery = None
            self.approve_button.setEnabled(False)
            self.reject_button.setEnabled(False)
            self.create_version_button.setEnabled(False)
            self.annotations_text.clear()
    
    def create_new_delivery(self):
        """Cria uma nova entrega para o evento atual"""
        if not self.event_context.event_id:
            return
        
        from PyQt5.QtWidgets import QInputDialog
        
        title, ok = QInputDialog.getText(
            self,
            "Nova Entrega",
            "Título da entrega:"
        )
        
        if ok and title:
            session = get_db_session()
            
            new_delivery = Delivery(
                event_id=self.event_context.event_id,
                title=title,
                status='pending'
            )
            
            session.add(new_delivery)
            session.commit()
            
            # Recarregar combo de entregas
            self.load_deliveries()
            
            # Selecionar a nova entrega
            index = self.delivery_combo.count() - 1
            self.delivery_combo.setCurrentIndex(index)
            
            session.close()
    
    @pyqtSlot(float, str)
    def on_annotation_added(self, timestamp, text):
        """Chamado quando uma anotação é adicionada ao vídeo"""
        # Formatar timestamp para exibição
        formatted_time = self.video_player.format_timecode(int(timestamp * 1000))
        
        # Obter texto atual das anotações
        current_text = self.annotations_text.toPlainText()
        
        # Adicionar nova anotação ao texto existente
        if current_text and current_text.strip():
            new_text = f"{current_text}\n[{formatted_time}] {text}"
        else:
            new_text = f"[{formatted_time}] {text}"
        
        # Atualizar área de texto
        self.annotations_text.setText(new_text)
    
    def approve_delivery(self):
        """Aprova a entrega atual"""
        if not self.current_delivery:
            return
            
        session = get_db_session()
        delivery = session.query(Delivery).filter(Delivery.id == self.current_delivery.id).first()
        
        if delivery:
            # Obter a última versão
            if delivery.versions:
                latest_version = max(delivery.versions, key=lambda v: v.version_number)
                latest_version.status = 'approved'
                latest_version.approved_by = "Usuário atual"  # Em produção, usar autenticação
                latest_version.approved_at = datetime.datetime.utcnow()
                
                # Atualizar status da entrega
                delivery.status = 'approved'
                session.commit()
                
                # Recarregar combo de entregas
                self.load_deliveries()
                
                QMessageBox.information(
                    self,
                    "Entrega Aprovada",
                    f"A entrega '{delivery.title}' foi aprovada com sucesso!"
                )
            
        session.close()
    
    def reject_delivery(self):
        """Rejeita a entrega atual e solicita ajustes"""
        if not self.current_delivery:
            return
            
        from PyQt5.QtWidgets import QInputDialog
        
        feedback, ok = QInputDialog.getMultiLine(
            self,
            "Solicitar Ajustes",
            "Feedback para os ajustes necessários:",
            self.annotations_text.toPlainText()
        )
        
        if ok:
            session = get_db_session()
            delivery = session.query(Delivery).filter(Delivery.id == self.current_delivery.id).first()
            
            if delivery and delivery.versions:
                latest_version = max(delivery.versions, key=lambda v: v.version_number)
                latest_version.status = 'rejected'
                latest_version.feedback = feedback
                
                # Atualizar status da entrega
                delivery.status = 'in-progress'
                session.commit()
                
                # Recarregar combo de entregas
                self.load_deliveries()
                
                # Atualizar texto de anotações
                self.annotations_text.setText(feedback)
            
            session.close()
    
    def create_new_version(self):
        """Cria uma nova versão da entrega atual com base no asset carregado"""
        if not self.current_delivery or not self.current_asset:
            QMessageBox.warning(
                self,
                "Erro ao Criar Versão",
                "Selecione uma entrega e carregue um asset para criar uma versão."
            )
            return
            
        session = get_db_session()
        delivery = session.query(Delivery).filter(Delivery.id == self.current_delivery.id).first()
        
        if delivery:
            # Determinar número da nova versão
            version_number = 1
            if delivery.versions:
                version_number = max(v.version_number for v in delivery.versions) + 1
            
            # Criar nova versão
            new_version = DeliveryVersion(
                delivery_id=delivery.id,
                version_number=version_number,
                file_path=self.current_asset.file_path,
                file_size=self.current_asset.file_size,
                upload_time=datetime.datetime.utcnow(),
                status='pending'
            )
            
            session.add(new_version)
            
            # Atualizar status da entrega
            delivery.status = 'review'
            
            session.commit()
            
            # Habilitar botões de aprovação
            self.approve_button.setEnabled(True)
            self.reject_button.setEnabled(True)
            
            # Recarregar combo de entregas
            self.load_deliveries()
            
            QMessageBox.information(
                self,
                "Nova Versão",
                f"Versão {version_number} criada com sucesso para a entrega '{delivery.title}'."
            )
        
        session.close()