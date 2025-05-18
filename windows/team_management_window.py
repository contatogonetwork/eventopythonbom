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
        if hasattr(self, 'event_context') and self.event_context and self.event_context.event_id:
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
        self.talent_table.setColumnCount(4)  # Aumentado para 4 para incluir a coluna ID
        self.talent_table.setHorizontalHeaderLabels(["Nome", "Função", "Contato", "ID"])
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
        self.event_team_table.setColumnCount(4)  # Aumentado para 4 para incluir a coluna ID
        self.event_team_table.setHorizontalHeaderLabels(["Nome", "Função no Evento", "Contato", "ID"])
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
            # Atualizar estado do botão baseado na seleção atual
            self.on_talent_selection_changed()
        else:
            self.setWindowTitle("Gerenciamento de Equipe")
            self.status_label.setText("Selecione um evento para gerenciar a equipe.")
            self.event_team_table.setRowCount(0)
            # Desabilitar botão quando não houver evento selecionado
            self.select_member_button.setEnabled(False)
    
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
        """Carrega a equipe do evento atual de forma mais segura"""
        # Limpar tabela por padrão
        self.event_team_table.setRowCount(0)
        
        # Verificação segura do contexto
        if not hasattr(self, 'event_context') or not self.event_context or not self.event_context.event_id:
            return
            
        session = get_db_session()
        try:
            event = session.query(Event).filter(Event.id == self.event_context.event_id).first()
            
            if not event or not event.team_members:
                return
                
            # Preencher tabela com membros da equipe
            members = event.team_members
            self.event_team_table.setRowCount(len(members))
            
            for i, member in enumerate(members):
                # Verificação segura para cada célula
                if member:
                    # Nome do membro
                    self.event_team_table.setItem(i, 0, QTableWidgetItem(member.name or ""))
                    
                    # Função no evento (se disponível na tabela de associação)
                    role = "A definir"  # Valor padrão
                    
                    # Em uma implementação completa, buscaríamos a função específica para este evento
                    # Por enquanto, usamos um valor padrão para cada membro
                    self.event_team_table.setItem(i, 1, QTableWidgetItem(role))
                    
                    # Contato
                    contact = member.contact_email or ""
                    self.event_team_table.setItem(i, 2, QTableWidgetItem(contact))
                    
                    # ID oculto
                    self.event_team_table.setItem(i, 3, QTableWidgetItem(member.id))
            
            # Esconder coluna de ID
            self.event_team_table.setColumnHidden(3, True)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro ao carregar equipe", f"Ocorreu um erro ao carregar a equipe: {str(e)}")
        finally:
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
        # 1. Verificar se há um evento selecionado
        if not hasattr(self, 'event_context') or not self.event_context or not self.event_context.event_id:
            QMessageBox.warning(self, "Evento não selecionado", "Selecione um evento antes de adicionar membros.")
            return
        
        event_id = self.event_context.event_id
        
        # 2. Verificar se o evento existe no banco de dados
        session = get_db_session()
        try:
            event = session.query(Event).filter(Event.id == event_id).first()
            if not event:
                QMessageBox.warning(self, "Erro", "O evento selecionado não foi encontrado no banco de dados.")
                return
            
            # 3. Obter índice da linha selecionada na tabela de talentos
            selected_row = self.talent_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Nenhum membro selecionado", "Selecione um membro do banco de talentos.")
                return
            
            # 4. Verificar se o item existe antes de acessá-lo
            id_item = self.talent_table.item(selected_row, 3)  # ID está na coluna oculta 3
            name_item = self.talent_table.item(selected_row, 0)  # Nome está na coluna 0
            
            if id_item is None or name_item is None:
                QMessageBox.warning(self, "Erro", "Não foi possível obter os dados do membro selecionado.")
                return
            
            member_id = id_item.text()
            member_name = name_item.text()
            
            # 5. Obter o membro do banco de dados para verificar sua existência
            try:
                member = session.query(TeamMember).filter(TeamMember.id == member_id).first()
                if not member:
                    QMessageBox.critical(self, "Erro", "Membro não encontrado no banco de dados.")
                    return
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao buscar membro: {str(e)}")
                return
            
            # 6. Verificar se já está na equipe
            if member in event.team_members:
                QMessageBox.information(self, "Já está na equipe", f"{member_name} já está na equipe deste evento.")
                return
            
            # 7. Abrir diálogo para definir função
            dialog = AssignRoleDialog(member_name, self)
            if dialog.exec_() == QDialog.Accepted:
                role = dialog.get_role()
                
                # 8. Adicionar membro à equipe com a função especificada
                event.team_members.append(member)
                
                # Adicionar função na tabela de associação - aqui precisamos acessar diretamente a tabela
                # Isso é uma aproximação, já que não temos acesso direto à associação
                # Em um ambiente de produção, você implementaria corretamente o armazenamento da função
                
                # 9. Commit das alterações
                try:
                    session.commit()
                    QMessageBox.information(self, "Sucesso", f"{member_name} adicionado à equipe como {role}.")
                    
                    # 10. Recarregar equipe
                    self.load_event_team()
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Erro", f"Erro ao salvar: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro inesperado: {str(e)}")
        finally:
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
        # Verificar se há uma linha selecionada na tabela
        selected = self.talent_table.currentRow() >= 0
        
        # Verificar se o evento está selecionado
        event_selected = False
        try:
            event_selected = hasattr(self, 'event_context') and self.event_context is not None and bool(self.event_context.event_id)
        except Exception:
            event_selected = False
            
        # Habilitar botão apenas se ambas condições forem verdadeiras
        self.select_member_button.setEnabled(selected and event_selected)
        
        # Atualizar status na interface
        if not event_selected:
            self.status_label.setText("Selecione um evento para gerenciar a equipe.")
        elif not selected:
            self.status_label.setText(f"Evento: {self.event_context.event_name or 'selecionado'}. Selecione um membro para adicionar.")
        else:
            self.status_label.setText(f"Evento: {self.event_context.event_name or 'selecionado'}. Clique em 'Adicionar à Equipe' para incluir o membro selecionado.")
    
    def on_team_selection_changed(self):
        """Habilita ou desabilita botões conforme seleção da tabela de equipe"""
        selected = len(self.event_team_table.selectedItems()) > 0
        self.assign_role_button.setEnabled(selected)
        self.remove_member_button.setEnabled(selected)