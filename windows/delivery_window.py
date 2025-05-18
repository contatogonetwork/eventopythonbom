from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QTextEdit, QMessageBox,
    QFileDialog, QListWidget, QListWidgetItem, QTabWidget,
    QProgressBar, QMenu, QAction
)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QIcon, QColor, QBrush
from lib.event_context import EventContext, EventAwareWindow
from db.models import Event, Delivery, DeliveryVersion, Asset, TeamMember, get_db_session
import os
import shutil
import uuid
from datetime import datetime, timedelta

class CreateDeliveryDialog(QDialog):
    """Diálogo para criar uma nova entrega"""
    def __init__(self, event_id, parent=None):
        super().__init__(parent)
        self.event_id = event_id
        self.setWindowTitle("Criar Nova Entrega")
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        # Título da entrega
        self.title_input = QLineEdit()
        layout.addRow("Título:", self.title_input)
        
        # Descrição
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addRow("Descrição:", self.description_input)
        
        # Tipo de entrega
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Reel",
            "Story",
            "TikTok",
            "Aftermovie",
            "Melhores Momentos",
            "Teaser",
            "Ativação de Marca",
            "Outro"
        ])
        layout.addRow("Tipo:", self.type_combo)
        
        # Data de entrega
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate().addDays(1))
        layout.addRow("Prazo de entrega:", self.due_date_input)
        
        # Responsável
        self.responsible_combo = QComboBox()
        self.load_team_members()
        layout.addRow("Responsável:", self.responsible_combo)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.create_button = QPushButton("Criar")
        self.create_button.clicked.connect(self.accept)
        button_layout.addWidget(self.create_button)
        
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def load_team_members(self):
        """Carrega membros da equipe para o combo"""
        session = get_db_session()
        
        event = session.query(Event).filter(Event.id == self.event_id).first()
        
        if event:
            self.responsible_combo.addItem("Selecione um responsável", None)
            
            for member in event.team_members:
                self.responsible_combo.addItem(member.name, member.id)
        
        session.close()
    
    def get_delivery_data(self):
        """Retorna os dados da entrega"""
        return {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "delivery_type": self.type_combo.currentText(),
            "due_date": self.due_date_input.date().toPyDate(),
            "created_by_id": self.responsible_combo.currentData()
        }


class AddVersionDialog(QDialog):
    """Diálogo para adicionar uma nova versão de entrega"""
    def __init__(self, delivery_id, parent=None):
        super().__init__(parent)
        self.delivery_id = delivery_id
        self.setWindowTitle("Adicionar Nova Versão")
        self.setMinimumWidth(450)
        
        self.selected_assets = []
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Instruções
        layout.addWidget(QLabel("Selecione arquivos para esta versão:"))
        
        # Lista de arquivos disponíveis
        self.assets_list = QTableWidget()
        self.assets_list.setColumnCount(3)
        self.assets_list.setHorizontalHeaderLabels(["Arquivo", "Tipo", "Tamanho"])
        self.assets_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.assets_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.assets_list.setSelectionMode(QTableWidget.MultiSelection)
        layout.addWidget(self.assets_list)
        
        # Carregar arquivos
        self.load_available_assets()
        
        # Opção para selecionar arquivo externo
        self.external_file_button = QPushButton("Selecionar Arquivo Externo")
        self.external_file_button.clicked.connect(self.select_external_file)
        layout.addWidget(self.external_file_button)
        
        # Comentários
        layout.addWidget(QLabel("Comentários da versão:"))
        self.comments_input = QTextEdit()
        self.comments_input.setMaximumHeight(100)
        layout.addWidget(self.comments_input)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.add_button = QPushButton("Adicionar Versão")
        self.add_button.clicked.connect(self.accept)
        button_layout.addWidget(self.add_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_available_assets(self):
        """Carrega os assets disponíveis para seleção"""
        session = get_db_session()
        
        # Buscar a entrega para obter o event_id
        delivery = session.query(Delivery).filter(Delivery.id == self.delivery_id).first()
        
        if delivery:
            # Buscar assets do evento
            assets = session.query(Asset).filter(
                Asset.event_id == delivery.event_id,
                Asset.archived == False
            ).order_by(Asset.ingest_time.desc()).all()
            
            self.assets_list.setRowCount(len(assets))
            
            for i, asset in enumerate(assets):
                self.assets_list.setItem(i, 0, QTableWidgetItem(asset.file_name))
                self.assets_list.setItem(i, 1, QTableWidgetItem(asset.file_type))
                
                # Tamanho em MB
                size_mb = f"{asset.file_size:.2f} MB"
                self.assets_list.setItem(i, 2, QTableWidgetItem(size_mb))
                
                # Armazenar ID para referência
                self.assets_list.setItem(i, 3, QTableWidgetItem(asset.id))
            
            # Esconder coluna de ID
            self.assets_list.setColumnHidden(3, True)
        
        session.close()
    
    def select_external_file(self):
        """Permite selecionar um arquivo externo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo",
            "",
            "Arquivos de Mídia (*.mp4 *.mov *.avi *.jpg *.png)"
        )
        
        if file_path:
            # Por simplicidade, apenas adicionamos o caminho à lista de selecionados
            self.selected_external_file = file_path
            QMessageBox.information(
                self,
                "Arquivo Selecionado",
                f"Arquivo externo selecionado: {os.path.basename(file_path)}"
            )
    
    def get_selected_assets(self):
        """Retorna os IDs dos assets selecionados"""
        selected_rows = self.assets_list.selectedItems()
        selected_ids = []
        
        for item in selected_rows:
            row = item.row()
            asset_id = self.assets_list.item(row, 3).text()
            if asset_id not in selected_ids:
                selected_ids.append(asset_id)
        
        return selected_ids
    
    def get_version_data(self):
        """Retorna os dados da nova versão"""
        return {
            "delivery_id": self.delivery_id,
            "comments": self.comments_input.toPlainText(),
            "selected_assets": self.get_selected_assets(),
            "external_file": getattr(self, "selected_external_file", None)
        }


class DeliveryWindow(QWidget, EventAwareWindow):
    def __init__(self):
        QWidget.__init__(self)
        EventAwareWindow.__init__(self)
        
        self.init_ui()
        
        # Carregar entregas se houver evento selecionado
        if self.event_context.event_id:
            self.load_deliveries()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Título
        self.title_label = QLabel("Entregas")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.title_label)
        
        # Tabs para separar entregas por tipo
        self.tabs = QTabWidget()
        
        # Tab de todas as entregas
        self.all_tab = QWidget()
        self.setup_all_tab()
        self.tabs.addTab(self.all_tab, "Todas as Entregas")
        
        # Tab de entregas pendentes
        self.pending_tab = QWidget()
        self.setup_pending_tab()
        self.tabs.addTab(self.pending_tab, "Pendentes")
        
        # Tab de entregas em revisão
        self.review_tab = QWidget()
        self.setup_review_tab()
        self.tabs.addTab(self.review_tab, "Em Revisão")
        
        # Tab de entregas aprovadas
        self.approved_tab = QWidget()
        self.setup_approved_tab()
        self.tabs.addTab(self.approved_tab, "Aprovadas")
        
        main_layout.addWidget(self.tabs)
        
        # Status/informações
        self.status_label = QLabel("Selecione um evento para visualizar entregas.")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Entregas")
    
    def setup_all_tab(self):
        """Configura a tab de todas as entregas"""
        layout = QVBoxLayout()
        
        # Controles
        controls_layout = QHBoxLayout()
        
        self.create_delivery_button = QPushButton("Nova Entrega")
        self.create_delivery_button.clicked.connect(self.create_delivery)
        controls_layout.addWidget(self.create_delivery_button)
        
        controls_layout.addStretch()
        
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(lambda: self.load_deliveries())
        controls_layout.addWidget(self.refresh_button)
        
        layout.addLayout(controls_layout)
        
        # Tabela de entregas
        self.all_deliveries_table = QTableWidget()
        self.all_deliveries_table.setColumnCount(5)
        self.all_deliveries_table.setHorizontalHeaderLabels(["Título", "Tipo", "Prazo", "Status", "Responsável"])
        self.all_deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.all_deliveries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.all_deliveries_table.setSelectionMode(QTableWidget.SingleSelection)
        self.all_deliveries_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.all_deliveries_table.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, self.all_deliveries_table)
        )
        self.all_deliveries_table.itemDoubleClicked.connect(
            lambda item: self.view_delivery_details(self.all_deliveries_table)
        )
        layout.addWidget(self.all_deliveries_table)
        
        self.all_tab.setLayout(layout)
    
    def setup_pending_tab(self):
        """Configura a tab de entregas pendentes"""
        layout = QVBoxLayout()
        
        # Tabela de entregas pendentes
        self.pending_deliveries_table = QTableWidget()
        self.pending_deliveries_table.setColumnCount(5)
        self.pending_deliveries_table.setHorizontalHeaderLabels(["Título", "Tipo", "Prazo", "Status", "Responsável"])
        self.pending_deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pending_deliveries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pending_deliveries_table.setSelectionMode(QTableWidget.SingleSelection)
        self.pending_deliveries_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pending_deliveries_table.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, self.pending_deliveries_table)
        )
        self.pending_deliveries_table.itemDoubleClicked.connect(
            lambda item: self.view_delivery_details(self.pending_deliveries_table)
        )
        layout.addWidget(self.pending_deliveries_table)
        
        self.pending_tab.setLayout(layout)
    
    def setup_review_tab(self):
        """Configura a tab de entregas em revisão"""
        layout = QVBoxLayout()
        
        # Tabela de entregas em revisão
        self.review_deliveries_table = QTableWidget()
        self.review_deliveries_table.setColumnCount(5)
        self.review_deliveries_table.setHorizontalHeaderLabels(["Título", "Tipo", "Prazo", "Status", "Responsável"])
        self.review_deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.review_deliveries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.review_deliveries_table.setSelectionMode(QTableWidget.SingleSelection)
        self.review_deliveries_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.review_deliveries_table.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, self.review_deliveries_table)
        )
        self.review_deliveries_table.itemDoubleClicked.connect(
            lambda item: self.view_delivery_details(self.review_deliveries_table)
        )
        layout.addWidget(self.review_deliveries_table)
        
        self.review_tab.setLayout(layout)
    
    def setup_approved_tab(self):
        """Configura a tab de entregas aprovadas"""
        layout = QVBoxLayout()
        
        # Tabela de entregas aprovadas
        self.approved_deliveries_table = QTableWidget()
        self.approved_deliveries_table.setColumnCount(5)
        self.approved_deliveries_table.setHorizontalHeaderLabels(["Título", "Tipo", "Prazo", "Status", "Responsável"])
        self.approved_deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.approved_deliveries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.approved_deliveries_table.setSelectionMode(QTableWidget.SingleSelection)
        self.approved_deliveries_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.approved_deliveries_table.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, self.approved_deliveries_table)
        )
        self.approved_deliveries_table.itemDoubleClicked.connect(
            lambda item: self.view_delivery_details(self.approved_deliveries_table)
        )
        layout.addWidget(self.approved_deliveries_table)
        
        self.approved_tab.setLayout(layout)
    
    def on_event_changed(self, event_id, event_name):
        """Implementação do EventAwareWindow"""
        if event_id:
            self.title_label.setText(f"Entregas - {event_name}")
            self.setWindowTitle(f"Entregas - {event_name}")
            self.status_label.setText(f"Visualizando entregas do evento: {event_name}")
            self.load_deliveries()
        else:
            self.title_label.setText("Entregas")
            self.setWindowTitle("Entregas")
            self.status_label.setText("Selecione um evento para visualizar entregas.")
            self.clear_tables()
    
    def clear_tables(self):
        """Limpa todas as tabelas de entregas"""
        self.all_deliveries_table.setRowCount(0)
        self.pending_deliveries_table.setRowCount(0)
        self.review_deliveries_table.setRowCount(0)
        self.approved_deliveries_table.setRowCount(0)
    
    def load_deliveries(self):
        """Carrega as entregas do evento atual"""
        if not self.event_context.event_id:
            return
        
        session = get_db_session()
        
        deliveries = session.query(Delivery).filter(
            Delivery.event_id == self.event_context.event_id
        ).all()
        
        # Limpar tabelas
        self.clear_tables()
        
        # Separar por status
        pending = []
        review = []
        approved = []
        
        for delivery in deliveries:
            # Adicionar à tabela principal
            self.add_delivery_to_table(self.all_deliveries_table, delivery)
            
            # Separar por status
            if delivery.status in ['pending', 'in-progress']:
                pending.append(delivery)
            elif delivery.status == 'review':
                review.append(delivery)
            elif delivery.status in ['approved', 'published']:
                approved.append(delivery)
        
        # Configurar tabelas específicas
        for i, delivery in enumerate(pending):
            self.add_delivery_to_table(self.pending_deliveries_table, delivery, i)
        
        for i, delivery in enumerate(review):
            self.add_delivery_to_table(self.review_deliveries_table, delivery, i)
        
        for i, delivery in enumerate(approved):
            self.add_delivery_to_table(self.approved_deliveries_table, delivery, i)
        
        # Atualizar contadores nas tabs
        self.tabs.setTabText(1, f"Pendentes ({len(pending)})")
        self.tabs.setTabText(2, f"Em Revisão ({len(review)})")
        self.tabs.setTabText(3, f"Aprovadas ({len(approved)})")
        
        session.close()
    
    def add_delivery_to_table(self, table, delivery, row=None):
        """Adiciona uma entrega à tabela especificada"""
        if row is None:
            row = table.rowCount()
            table.insertRow(row)
        
        # Título
        table.setItem(row, 0, QTableWidgetItem(delivery.title))
        
        # Tipo
        table.setItem(row, 1, QTableWidgetItem(delivery.delivery_type))
        
        # Prazo
        due_date = delivery.due_date.strftime("%d/%m/%Y") if delivery.due_date else "-"
        table.setItem(row, 2, QTableWidgetItem(due_date))
        
        # Status com formatação
        status_map = {
            'pending': 'Pendente',
            'in-progress': 'Em andamento',
            'review': 'Em revisão',
            'approved': 'Aprovado',
            'published': 'Publicado'
        }
        status_item = QTableWidgetItem(status_map.get(delivery.status, delivery.status.capitalize()))
        
        if delivery.status == 'approved' or delivery.status == 'published':
            status_item.setBackground(QBrush(QColor(200, 255, 200)))  # Verde claro
        elif delivery.status == 'review':
            status_item.setBackground(QBrush(QColor(255, 255, 200)))  # Amarelo claro
        
        table.setItem(row, 3, status_item)
        
        # Responsável
        responsible_name = delivery.created_by.name if delivery.created_by else "-"
        table.setItem(row, 4, QTableWidgetItem(responsible_name))
        
        # Armazenar ID para referência
        table.setItem(row, 5, QTableWidgetItem(delivery.id))
        
        # Esconder coluna de ID
        table.setColumnHidden(5, True)
    
    def create_delivery(self):
        """Abre diálogo para criar uma nova entrega"""
        if not self.event_context.event_id:
            QMessageBox.warning(self, "Erro", "Selecione um evento primeiro.")
            return
        
        dialog = CreateDeliveryDialog(self.event_context.event_id, self)
        
        if dialog.exec_() == QDialog.Accepted:
            delivery_data = dialog.get_delivery_data()
            
            # Adicionar ID do evento
            delivery_data["event_id"] = self.event_context.event_id
            delivery_data["status"] = "pending"
            
            session = get_db_session()
            
            new_delivery = Delivery(**delivery_data)
            session.add(new_delivery)
            session.commit()
            
            session.close()
            
            # Recarregar entregas
            self.load_deliveries()
            
            # Informar usuário
            QMessageBox.information(
                self,
                "Entrega Criada",
                f"A entrega '{delivery_data['title']}' foi criada com sucesso."
            )
    
    def add_version(self, delivery_id):
        """Adiciona uma nova versão para a entrega"""
        dialog = AddVersionDialog(delivery_id, self)
        
        if dialog.exec_() == QDialog.Accepted:
            version_data = dialog.get_version_data()
            
            session = get_db_session()
            
            # Buscar entrega
            delivery = session.query(Delivery).filter(Delivery.id == delivery_id).first()
            
            if delivery:
                # Determinar número da versão
                version_number = 1
                if delivery.versions:
                    version_number = max(v.version_number for v in delivery.versions) + 1
                
                # Criar nova versão
                file_path = ""
                file_size = 0
                
                # Se um arquivo externo foi selecionado
                if version_data["external_file"]:
                    external_file = version_data["external_file"]
                    file_path = external_file
                    file_size = os.path.getsize(external_file) / (1024 * 1024)  # MB
                
                # Criar versão
                new_version = DeliveryVersion(
                    id=str(uuid.uuid4()),
                    delivery_id=delivery_id,
                    version_number=version_number,
                    file_path=file_path,
                    file_size=file_size,
                    upload_time=datetime.utcnow(),
                    status="pending",
                    feedback=version_data["comments"]
                )
                session.add(new_version)
                
                # Atualizar status da entrega
                delivery.status = "review"
                
                # Vincular assets à versão
                # Em uma implementação completa, aqui vincularíamos os assets selecionados
                
                session.commit()
                
                # Recarregar entregas
                self.load_deliveries()
                
                # Informar usuário
                QMessageBox.information(
                    self,
                    "Versão Adicionada",
                    f"A versão {version_number} foi adicionada com sucesso à entrega '{delivery.title}'."
                )
            
            session.close()
    
    def show_context_menu(self, position, table):
        """Mostra menu de contexto para a entrega selecionada"""
        selected_row = table.currentRow()
        
        if selected_row < 0:
            return
        
        delivery_id = table.item(selected_row, 5).text()
        delivery_title = table.item(selected_row, 0).text()
        
        menu = QMenu(self)
        
        # Visualizar detalhes
        view_action = QAction("Visualizar Detalhes", self)
        view_action.triggered.connect(lambda: self.view_delivery_details(table))
        menu.addAction(view_action)
        
        # Adicionar versão
        add_version_action = QAction("Adicionar Nova Versão", self)
        add_version_action.triggered.connect(lambda: self.add_version(delivery_id))
        menu.addAction(add_version_action)
        
        menu.addSeparator()
        
        # Alterar status
        status_menu = QMenu("Alterar Status", self)
        
        pending_action = QAction("Pendente", self)
        pending_action.triggered.connect(lambda: self.change_status(delivery_id, "pending"))
        status_menu.addAction(pending_action)
        
        in_progress_action = QAction("Em andamento", self)
        in_progress_action.triggered.connect(lambda: self.change_status(delivery_id, "in-progress"))
        status_menu.addAction(in_progress_action)
        
        review_action = QAction("Em revisão", self)
        review_action.triggered.connect(lambda: self.change_status(delivery_id, "review"))
        status_menu.addAction(review_action)
        
        approved_action = QAction("Aprovado", self)
        approved_action.triggered.connect(lambda: self.change_status(delivery_id, "approved"))
        status_menu.addAction(approved_action)
        
        published_action = QAction("Publicado", self)
        published_action.triggered.connect(lambda: self.change_status(delivery_id, "published"))
        status_menu.addAction(published_action)
        
        menu.addMenu(status_menu)
        
        menu.addSeparator()
        
        # Excluir entrega
        delete_action = QAction("Excluir Entrega", self)
        delete_action.triggered.connect(lambda: self.delete_delivery(delivery_id, delivery_title))
        menu.addAction(delete_action)
        
        menu.exec_(table.viewport().mapToGlobal(position))
    
    def view_delivery_details(self, table):
        """Abre diálogo com detalhes da entrega"""
        selected_row = table.currentRow()
        
        if selected_row < 0:
            return
        
        delivery_id = table.item(selected_row, 5).text()
        
        session = get_db_session()
        
        delivery = session.query(Delivery).filter(Delivery.id == delivery_id).first()
        
        if delivery:
            # Aqui seria implementado um diálogo detalhado mostrando todas as informações
            # da entrega, incluindo histórico de versões, comentários, etc.
            # Por simplicidade, apenas mostramos uma mensagem.
            
            versions_text = "Nenhuma versão ainda."
            if delivery.versions:
                versions = []
                for v in sorted(delivery.versions, key=lambda x: x.version_number):
                    status = "Pendente"
                    if v.status == "approved":
                        status = "Aprovada"
                    elif v.status == "rejected":
                        status = "Rejeitada"
                    
                    versions.append(f"Versão {v.version_number}: {status} ({v.upload_time.strftime('%d/%m/%Y %H:%M')})")
                
                versions_text = "\n".join(versions)
            
            QMessageBox.information(
                self,
                f"Detalhes da Entrega: {delivery.title}",
                f"Tipo: {delivery.delivery_type}\n"
                f"Status: {delivery.status.capitalize()}\n"
                f"Prazo: {delivery.due_date.strftime('%d/%m/%Y') if delivery.due_date else '-'}\n"
                f"Responsável: {delivery.created_by.name if delivery.created_by else '-'}\n\n"
                f"Descrição: {delivery.description or 'Sem descrição'}\n\n"
                f"Histórico de Versões:\n{versions_text}"
            )
        
        session.close()
    
    def change_status(self, delivery_id, status):
        """Altera o status da entrega"""
        session = get_db_session()
        
        delivery = session.query(Delivery).filter(Delivery.id == delivery_id).first()
        
        if delivery:
            delivery.status = status
            session.commit()
            
            # Recarregar entregas
            self.load_deliveries()
        
        session.close()
    
    def delete_delivery(self, delivery_id, delivery_title):
        """Exclui a entrega"""
        # Confirmar exclusão
        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Excluir a entrega '{delivery_title}'?\n\nEsta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            session = get_db_session()
            
            delivery = session.query(Delivery).filter(Delivery.id == delivery_id).first()
            
            if delivery:
                session.delete(delivery)
                session.commit()
                
                # Recarregar entregas
                self.load_deliveries()
                
                # Informar usuário
                QMessageBox.information(
                    self,
                    "Entrega Excluída",
                    f"A entrega '{delivery_title}' foi excluída com sucesso."
                )
            
            session.close()