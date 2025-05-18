from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QLineEdit, QFormLayout, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from lib.event_context import EventContext, EventAwareWindow
from db.models import Event, TeamMember, get_db_session
import uuid

class AddTeamMemberDialog(QDialog):
    """Dialog for adding a new team member to the talent pool"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Membro ao Banco de Talentos")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # Nome
        self.name_input = QLineEdit()
        layout.addRow("Nome:", self.name_input)
        
        # Expertise
        self.expertise_input = QComboBox()
        self.expertise_input.addItems([
            "Filmmaker / Captação",
            "Editor de Vídeo",
            "Diretor de Produção",
            "Media Manager / Logger",
            "Motion Designer",
            "Diretor de Fotografia",
            "Assistente"
        ])
        layout.addRow("Função:", self.expertise_input)
        
        # Contato
        self.contact_input = QLineEdit()
        layout.addRow("Contato:", self.contact_input)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)
        
        layout.addRow("", button_layout)
        self.setLayout(layout)
    
    def get_member_data(self):
        """Returns the form data as a dict"""
        return {
            "name": self.name_input.text(),
            "expertise": self.expertise_input.currentText(),
            "contact_email": self.contact_input.text()
        }


class AssignRoleDialog(QDialog):
    """Dialog for assigning a role to a team member"""
    def __init__(self, member_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Atribuir Função para {member_name}")
        self.setMinimumWidth(300)
        
        layout = QFormLayout()
        
        # Função no evento
        self.role_input = QComboBox()
        self.role_input.addItems([
            "Captador Principal",
            "Captador Secundário",
            "Editor Real-Time",
            "Editor Pós-Produção",
            "Diretor de Produção",
            "Media Manager",
            "Motion Designer",
            "Assistente de Produção"
        ])
        layout.addRow("Função no evento:", self.role_input)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Atribuir")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)
        
        layout.addRow("", button_layout)
        self.setLayout(layout)
    
    def get_role(self):
        """Returns the selected role"""
        return self.role_input.currentText()


class TeamManagementWindow(QWidget, EventAwareWindow):
    def __init__(self):
        QWidget.__init__(self)
        EventAwareWindow.__init__(self)
        
        self.init_ui()
        
        # Carregar banco de talentos inicialmente
        self.load_talent_pool()
        
        # Carregar equipe do evento se houver evento selecionado
        if self.event_context.event_id:
            self.load_event_team()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Gerenciamento de Equipe")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Layout para as duas tabelas lado a lado
        tables_layout = QHBoxLayout()
        
        # Banco de Talentos (esquerda)
        talent_panel = QVBoxLayout()
        
        talent_label = QLabel("Banco de Talentos")
        talent_label.setStyleSheet("font-weight: bold;")
        talent_panel.addWidget(talent_label)
        
        self.talent_table = QTableWidget()
        self.talent_table.setColumnCount(3)
        self.talent_table.setHorizontalHeaderLabels(["Nome", "Função", "Contato"])
        self.talent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.talent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.talent_table.setSelectionMode(QTableWidget.SingleSelection)
        talent_panel.addWidget(self.talent_table)
        
        talent_buttons = QHBoxLayout()
        
        self.add_talent_button = QPushButton("Adicionar Talento")
        self.add_talent_button.clicked.connect(self.add_talent)
        talent_buttons.addWidget(self.add_talent_button)
        
        self.select_member_button = QPushButton("Adicionar à Equipe")
        self.select_member_button.clicked.connect(self.add_to_event_team)
        self.select_member_button.setEnabled(False)
        talent_buttons.addWidget(self.select_member_button)
        
        talent_panel.addLayout(talent_buttons)
        tables_layout.addLayout(talent_panel)
        
        # Equipe do Evento (direita)
        team_panel = QVBoxLayout()
        
        team_label = QLabel("Equipe do Evento")
        team_label.setStyleSheet("font-weight: bold;")
        team_panel.addWidget(team_label)
        
        self.event_team_table = QTableWidget()
        self.event_team_table.setColumnCount(3)
        self.event_team_table.setHorizontalHeaderLabels(["Nome", "Função no Evento", "Contato"])
        self.event_team_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.event_team_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.event_team_table.setSelectionMode(QTableWidget.SingleSelection)
        team_panel.addWidget(self.event_team_table)
        
        team_buttons = QHBoxLayout()
        
        self.assign_role_button = QPushButton("Atribuir Função")
        self.assign_role_button.clicked.connect(self.assign_role)
        self.assign_role_button.setEnabled(False)
        team_buttons.addWidget(self.assign_role_button)
        
        self.remove_member_button = QPushButton("Remover da Equipe")
        self.remove_member_button.clicked.connect(self.remove_from_event_team)
        self.remove_member_button.setEnabled(False)
        team_buttons.addWidget(self.remove_member_button)
        
        team_panel.addLayout(team_buttons)
        tables_layout.addLayout(team_panel)
        
        main_layout.addLayout(tables_layout)
        
        # Status/informações
        self.status_label = QLabel("Selecione um evento para gerenciar a equipe.")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Gerenciamento de Equipe")
        
        # Conectar sinais de seleção das tabelas
        self.talent_table.itemSelectionChanged.connect(self.on_talent_selection_changed)
        self.event_team_table.itemSelectionChanged.connect(self.on_team_selection_changed)
    
    def on_event_changed(self, event_id, event_name):
        """Implementação do EventAwareWindow"""
        if event_id:
            self.setWindowTitle(f"Gerenciamento de Equipe - {event_name}")
            self.status_label.setText(f"Gerenciando equipe para o evento: {event_name}")
            self.load_event_team()
        else:
            self.setWindowTitle("Gerenciamento de Equipe")
            self.status_label.setText("Selecione um evento para gerenciar a equipe.")
            self.event_team_table.setRowCount(0)
    
    def load_talent_pool(self):
        """Carrega a lista de membros do banco de talentos"""
        session = get_db_session()
        
        members = session.query(TeamMember).all()
        
        self.talent_table.setRowCount(len(members))
        
        for i, member in enumerate(members):
            self.talent_table.setItem(i, 0, QTableWidgetItem(member.name))
            self.talent_table.setItem(i, 1, QTableWidgetItem(member.expertise))
            self.talent_table.setItem(i, 2, QTableWidgetItem(member.contact_email or ""))
            
            # Armazenar ID para referência
            item = QTableWidgetItem(member.id)
            self.talent_table.setItem(i, 3, item)
        
        # Esconder coluna de ID
        self.talent_table.setColumnHidden(3, True)
        
        session.close()
    
    def load_event_team(self):
        """Carrega a equipe do evento atual"""
        if not self.event_context.event_id:
            self.event_team_table.setRowCount(0)
            return
        
        session = get_db_session()
        
        event = session.query(Event).filter(Event.id == self.event_context.event_id).first()
        
        if event and event.team_members:
            self.event_team_table.setRowCount(len(event.team_members))
            
            for i, member in enumerate(event.team_members):
                self.event_team_table.setItem(i, 0, QTableWidgetItem(member.name))
                
                # Buscar a função do membro neste evento específico
                role = ""
                for assoc in event.team_members:
                    if assoc.id == member.id:
                        # Em produção real, precisaríamos acessar a tabela de associação
                        # para obter a função específica
                        role = "A ser definido"
                        break
                
                self.event_team_table.setItem(i, 1, QTableWidgetItem(role))
                self.event_team_table.setItem(i, 2, QTableWidgetItem(member.contact_email or ""))
                
                # Armazenar ID para referência
                item = QTableWidgetItem(member.id)
                self.event_team_table.setItem(i, 3, item)
        else:
            self.event_team_table.setRowCount(0)
        
        # Esconder coluna de ID
        self.event_team_table.setColumnHidden(3, True)
        
        session.close()
    
    def add_talent(self):
        """Abre diálogo para adicionar membro ao banco de talentos"""
        dialog = AddTeamMemberDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_member_data()
            
            if not data["name"]:
                QMessageBox.warning(self, "Erro", "Nome é obrigatório.")
                return
            
            session = get_db_session()
            
            new_member = TeamMember(
                id=str(uuid.uuid4()),
                name=data["name"],
                expertise=data["expertise"],
                contact_email=data["contact_email"]
            )
            
            session.add(new_member)
            session.commit()
            
            session.close()
            
            # Recarregar banco de talentos
            self.load_talent_pool()
    
    def add_to_event_team(self):
        """Adiciona o membro selecionado do banco de talentos à equipe do evento"""
        if not self.event_context.event_id:
            QMessageBox.warning(self, "Erro", "Nenhum evento selecionado.")
            return
        
        selected_row = self.talent_table.currentRow()
        
        if selected_row < 0:
            return
        
        # Verificar se o item existe antes de acessá-lo
        id_item = self.talent_table.item(selected_row, 3)
        name_item = self.talent_table.item(selected_row, 0)
        
        if id_item is None or name_item is None:
            QMessageBox.warning(self, "Erro", "Não foi possível obter os dados do membro selecionado.")
            return
            
        member_id = id_item.text()
        member_name = name_item.text()
        
        # Verificar se já está na equipe
        for row in range(self.event_team_table.rowCount()):
            if member_id == self.event_team_table.item(row, 3).text():
                QMessageBox.information(self, "Informação", f"{member_name} já está na equipe.")
                return
        
        # Abrir diálogo para definir função
        dialog = AssignRoleDialog(member_name, self)
        
        if dialog.exec_() == QDialog.Accepted:
            role = dialog.get_role()
            
            session = get_db_session()
            
            event = session.query(Event).filter(Event.id == self.event_context.event_id).first()
            member = session.query(TeamMember).filter(TeamMember.id == member_id).first()
            
            if event and member:
                # Adicionar membro à equipe com a função especificada
                if member not in event.team_members:
                    event.team_members.append(member)
                    
                    # Em produção real, aqui definiriamos a função na tabela de associação
                    
                    session.commit()
                    
                    # Recarregar equipe
                    self.load_event_team()
            
            session.close()
    
    def remove_from_event_team(self):
        """Remove o membro selecionado da equipe do evento"""
        if not self.event_context.event_id:
            return
        
        selected_row = self.event_team_table.currentRow()
        
        if selected_row < 0:
            return
        
        # Verificar se o item existe antes de acessá-lo
        id_item = self.event_team_table.item(selected_row, 3)
        name_item = self.event_team_table.item(selected_row, 0)
        
        if id_item is None or name_item is None:
            QMessageBox.warning(self, "Erro", "Não foi possível obter os dados do membro selecionado.")
            return
            
        member_id = id_item.text()
        member_name = name_item.text()
        
        # Confirmar remoção
        confirm = QMessageBox.question(
            self,
            "Confirmar Remoção",
            f"Remover {member_name} da equipe do evento?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            session = get_db_session()
            
            event = session.query(Event).filter(Event.id == self.event_context.event_id).first()
            member = session.query(TeamMember).filter(TeamMember.id == member_id).first()
            
            if event and member and member in event.team_members:
                event.team_members.remove(member)
                session.commit()
                
                # Recarregar equipe
                self.load_event_team()
            
            session.close()
    
    def assign_role(self):
        """Atribui uma função ao membro selecionado da equipe do evento"""
        if not self.event_context.event_id:
            return
        
        selected_row = self.event_team_table.currentRow()
        
        if selected_row < 0:
            return
        
        # Verificar se o item existe antes de acessá-lo
        id_item = self.event_team_table.item(selected_row, 3)
        name_item = self.event_team_table.item(selected_row, 0)
        
        if id_item is None or name_item is None:
            QMessageBox.warning(self, "Erro", "Não foi possível obter os dados do membro selecionado.")
            return
            
        member_id = id_item.text()
        member_name = name_item.text()
        
        # Abrir diálogo para definir função
        dialog = AssignRoleDialog(member_name, self)
        
        if dialog.exec_() == QDialog.Accepted:
            role = dialog.get_role()
            
            # Atualizar visualmente
            self.event_team_table.setItem(selected_row, 1, QTableWidgetItem(role))
            
            # Em produção real, aqui atualizariamos a função na tabela de associação
    
    def on_talent_selection_changed(self):
        """Habilita ou desabilita botões conforme seleção da tabela de talentos"""
        selected = len(self.talent_table.selectedItems()) > 0
        self.select_member_button.setEnabled(selected and bool(self.event_context.event_id))
    
    def on_team_selection_changed(self):
        """Habilita ou desabilita botões conforme seleção da tabela de equipe"""
        selected = len(self.event_team_table.selectedItems()) > 0
        self.assign_role_button.setEnabled(selected)
        self.remove_member_button.setEnabled(selected)