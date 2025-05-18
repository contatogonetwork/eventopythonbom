from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QTimeEdit, QDialog, QFormLayout, QLineEdit, QMessageBox,
    QMenu, QAction
)
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime
from PyQt5.QtGui import QColor, QBrush
from lib.event_context import EventContext, EventAwareWindow
from db.models import Event, TimelineTask, TeamMember, get_db_session, Briefing
import uuid
from datetime import datetime, timedelta

class AddTaskDialog(QDialog):
    """Diálogo para adicionar ou editar uma tarefa na timeline"""
    def __init__(self, event_id, parent=None, task=None):
        super().__init__(parent)
        self.event_id = event_id
        self.task = task
        
        if task:
            self.setWindowTitle("Editar Tarefa")
        else:
            self.setWindowTitle("Adicionar Nova Tarefa")
        
        self.init_ui()
        
        if task:
            self.load_task_data()
    
    def init_ui(self):
        layout = QFormLayout()
        
        # Título da tarefa
        self.title_input = QLineEdit()
        layout.addRow("Título:", self.title_input)
        
        # Descrição
        self.description_input = QLineEdit()
        layout.addRow("Descrição:", self.description_input)
        
        # Hora de início
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        layout.addRow("Hora de início:", self.start_time)
        
        # Hora de término
        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        layout.addRow("Hora de término:", self.end_time)
        
        # Local
        self.location_input = QLineEdit()
        layout.addRow("Local:", self.location_input)
        
        # Responsável
        self.team_member_combo = QComboBox()
        self.load_team_members()
        layout.addRow("Responsável:", self.team_member_combo)
        
        # Prioridade
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Alta", "Normal", "Baixa"])
        layout.addRow("Prioridade:", self.priority_combo)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pendente", "Em andamento", "Concluída"])
        layout.addRow("Status:", self.status_combo)
        
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
    
    def load_team_members(self):
        """Carrega os membros da equipe para o combo"""
        session = get_db_session()
        
        event = session.query(Event).filter(Event.id == self.event_id).first()
        
        if event:
            self.team_member_combo.addItem("Selecione um responsável", None)
            
            for member in event.team_members:
                self.team_member_combo.addItem(member.name, member.id)
        
        session.close()
    
    def load_task_data(self):
        """Carrega os dados da tarefa para edição"""
        if not self.task:
            return
        
        self.title_input.setText(self.task.title)
        self.description_input.setText(self.task.description or "")
        
        # Converter para QTime
        start_time = self.task.start_time
        self.start_time.setTime(QTime(start_time.hour, start_time.minute))
        
        if self.task.end_time:
            end_time = self.task.end_time
            self.end_time.setTime(QTime(end_time.hour, end_time.minute))
        
        self.location_input.setText(self.task.location or "")
        
        # Definir responsável
        if self.task.assigned_to_id:
            for i in range(self.team_member_combo.count()):
                if self.team_member_combo.itemData(i) == self.task.assigned_to_id:
                    self.team_member_combo.setCurrentIndex(i)
                    break
        
        # Definir prioridade
        priority_map = {"high": 0, "normal": 1, "low": 2}
        if self.task.priority in priority_map:
            self.priority_combo.setCurrentIndex(priority_map[self.task.priority])
        
        # Definir status
        status_map = {"pending": 0, "in-progress": 1, "completed": 2}
        if self.task.status in status_map:
            self.status_combo.setCurrentIndex(status_map[self.task.status])
    
    def get_task_data(self):
        """Retorna os dados da tarefa"""
        # Converter índices para valores
        priority_values = ["high", "normal", "low"]
        status_values = ["pending", "in-progress", "completed"]
        
        # Converter QTime para datetime
        start_time = self.start_time.time()
        end_time = self.end_time.time()
        
        # Data base do evento (por simplicidade usando hoje)
        base_date = datetime.now().date()
        
        # Criar datetimes completos
        start_datetime = datetime.combine(
            base_date, 
            datetime.min.time().replace(hour=start_time.hour(), minute=start_time.minute())
        )
        
        end_datetime = datetime.combine(
            base_date, 
            datetime.min.time().replace(hour=end_time.hour(), minute=end_time.minute())
        )
        
        # Se end_time < start_time, assumir que passa para o dia seguinte
        if end_time < start_time:
            end_datetime += timedelta(days=1)
        
        return {
            "title": self.title_input.text(),
            "description": self.description_input.text(),
            "start_time": start_datetime,
            "end_time": end_datetime,
            "location": self.location_input.text(),
            "assigned_to_id": self.team_member_combo.currentData(),
            "priority": priority_values[self.priority_combo.currentIndex()],
            "status": status_values[self.status_combo.currentIndex()]
        }


class TimelineWindow(QWidget, EventAwareWindow):
    def __init__(self):
        QWidget.__init__(self)
        EventAwareWindow.__init__(self)
        
        self.init_ui()
        
        # Carregar tarefas se houver evento selecionado
        if self.event_context.event_id:
            self.load_timeline_tasks()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Título
        self.title_label = QLabel("Timeline do Evento")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.title_label)
        
        # Controles da timeline
        controls_layout = QHBoxLayout()
        
        self.add_task_button = QPushButton("Adicionar Tarefa")
        self.add_task_button.clicked.connect(self.add_task)
        controls_layout.addWidget(self.add_task_button)
        
        self.generate_from_briefing_button = QPushButton("Gerar da Programação")
        self.generate_from_briefing_button.clicked.connect(self.generate_from_briefing)
        controls_layout.addWidget(self.generate_from_briefing_button)
        
        # Filtro de visão
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Visualizar:"))
        
        self.view_filter = QComboBox()
        self.view_filter.addItems(["Todas as tarefas", "Apenas pendentes", "Por responsável"])
        self.view_filter.currentIndexChanged.connect(self.apply_filter)
        controls_layout.addWidget(self.view_filter)
        
        main_layout.addLayout(controls_layout)
        
        # Tabela de tarefas
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(6)
        self.tasks_table.setHorizontalHeaderLabels(["Horário", "Título", "Local", "Responsável", "Prioridade", "Status"])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setSelectionMode(QTableWidget.SingleSelection)
        self.tasks_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tasks_table.customContextMenuRequested.connect(self.show_context_menu)
        main_layout.addWidget(self.tasks_table)
        
        # Status/informações
        self.status_label = QLabel("Selecione um evento para visualizar a timeline.")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Timeline do Evento")
    
    def on_event_changed(self, event_id, event_name):
        """Implementação do EventAwareWindow"""
        if event_id:
            self.title_label.setText(f"Timeline do Evento: {event_name}")
            self.setWindowTitle(f"Timeline - {event_name}")
            self.status_label.setText(f"Visualizando timeline do evento: {event_name}")
            self.load_timeline_tasks()
        else:
            self.title_label.setText("Timeline do Evento")
            self.setWindowTitle("Timeline")
            self.status_label.setText("Selecione um evento para visualizar a timeline.")
            self.tasks_table.setRowCount(0)
    
    def load_timeline_tasks(self):
        """Carrega as tarefas da timeline do evento atual"""
        if not self.event_context.event_id:
            return
        
        session = get_db_session()
        
        tasks = session.query(TimelineTask).filter(
            TimelineTask.event_id == self.event_context.event_id
        ).order_by(TimelineTask.start_time).all()
        
        self.tasks_table.setRowCount(len(tasks))
        
        for i, task in enumerate(tasks):
            # Formatação de horário
            start_time = task.start_time.strftime("%H:%M")
            if task.end_time:
                time_str = f"{start_time} - {task.end_time.strftime('%H:%M')}"
            else:
                time_str = start_time
            
            self.tasks_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.tasks_table.setItem(i, 1, QTableWidgetItem(task.title))
            self.tasks_table.setItem(i, 2, QTableWidgetItem(task.location or ""))
            
            # Nome do responsável
            responsible_name = task.assigned_to.name if task.assigned_to else "-"
            self.tasks_table.setItem(i, 3, QTableWidgetItem(responsible_name))
            
            # Prioridade com formatação
            priority_item = QTableWidgetItem(task.priority.capitalize())
            if task.priority == "high":
                priority_item.setBackground(QBrush(QColor(255, 200, 200)))  # Vermelho claro
            elif task.priority == "low":
                priority_item.setBackground(QBrush(QColor(200, 255, 200)))  # Verde claro
            self.tasks_table.setItem(i, 4, priority_item)
            
            # Status com formatação
            status_map = {
                "pending": "Pendente",
                "in-progress": "Em andamento",
                "completed": "Concluída"
            }
            status_item = QTableWidgetItem(status_map.get(task.status, task.status.capitalize()))
            if task.status == "completed":
                status_item.setBackground(QBrush(QColor(200, 255, 200)))  # Verde claro
            elif task.status == "in-progress":
                status_item.setBackground(QBrush(QColor(255, 255, 200)))  # Amarelo claro
            self.tasks_table.setItem(i, 5, status_item)
            
            # Armazenar ID da tarefa para referência
            self.tasks_table.setItem(i, 6, QTableWidgetItem(task.id))
        
        # Esconder coluna de ID
        self.tasks_table.setColumnHidden(6, True)
        
        session.close()
    
    def add_task(self):
        """Abre diálogo para adicionar nova tarefa"""
        if not self.event_context.event_id:
            QMessageBox.warning(self, "Erro", "Selecione um evento primeiro.")
            return
        
        dialog = AddTaskDialog(self.event_context.event_id, self)
        
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_task_data()
            
            # Adicionar ID do evento
            task_data["event_id"] = self.event_context.event_id
            
            session = get_db_session()
            
            new_task = TimelineTask(**task_data)
            session.add(new_task)
            session.commit()
            
            session.close()
            
            # Recarregar tarefas
            self.load_timeline_tasks()
    
    def edit_task(self):
        """Edita a tarefa selecionada"""
        selected_row = self.tasks_table.currentRow()
        
        if selected_row < 0:
            return
        
        task_id = self.tasks_table.item(selected_row, 6).text()
        
        session = get_db_session()
        
        task = session.query(TimelineTask).filter(TimelineTask.id == task_id).first()
        
        if task:
            dialog = AddTaskDialog(self.event_context.event_id, self, task)
            
            if dialog.exec_() == QDialog.Accepted:
                task_data = dialog.get_task_data()
                
                # Atualizar tarefa
                for key, value in task_data.items():
                    setattr(task, key, value)
                
                session.commit()
                
                # Recarregar tarefas
                self.load_timeline_tasks()
        
        session.close()
    
    def delete_task(self):
        """Exclui a tarefa selecionada"""
        selected_row = self.tasks_table.currentRow()
        
        if selected_row < 0:
            return
        
        task_id = self.tasks_table.item(selected_row, 6).text()
        task_title = self.tasks_table.item(selected_row, 1).text()
        
        # Confirmar exclusão
        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Excluir a tarefa '{task_title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            session = get_db_session()
            
            task = session.query(TimelineTask).filter(TimelineTask.id == task_id).first()
            
            if task:
                session.delete(task)
                session.commit()
                
                # Recarregar tarefas
                self.load_timeline_tasks()
            
            session.close()
    
    def change_status(self, status):
        """Altera o status da tarefa selecionada"""
        selected_row = self.tasks_table.currentRow()
        
        if selected_row < 0:
            return
        
        task_id = self.tasks_table.item(selected_row, 6).text()
        
        session = get_db_session()
        
        task = session.query(TimelineTask).filter(TimelineTask.id == task_id).first()
        
        if task:
            task.status = status
            session.commit()
            
            # Atualizar visualmente
            status_map = {
                "pending": "Pendente",
                "in-progress": "Em andamento",
                "completed": "Concluída"
            }
            
            status_item = QTableWidgetItem(status_map.get(status, status.capitalize()))
            if status == "completed":
                status_item.setBackground(QBrush(QColor(200, 255, 200)))  # Verde claro
            elif status == "in-progress":
                status_item.setBackground(QBrush(QColor(255, 255, 200)))  # Amarelo claro
            
            self.tasks_table.setItem(selected_row, 5, status_item)
        
        session.close()
    
    def show_context_menu(self, position):
        """Mostra menu de contexto para a tarefa selecionada"""
        selected_row = self.tasks_table.currentRow()
        
        if selected_row < 0:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("Editar Tarefa", self)
        edit_action.triggered.connect(self.edit_task)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        status_menu = QMenu("Alterar Status", self)
        
        pending_action = QAction("Pendente", self)
        pending_action.triggered.connect(lambda: self.change_status("pending"))
        status_menu.addAction(pending_action)
        
        in_progress_action = QAction("Em andamento", self)
        in_progress_action.triggered.connect(lambda: self.change_status("in-progress"))
        status_menu.addAction(in_progress_action)
        
        completed_action = QAction("Concluída", self)
        completed_action.triggered.connect(lambda: self.change_status("completed"))
        status_menu.addAction(completed_action)
        
        menu.addMenu(status_menu)
        
        menu.addSeparator()
        
        delete_action = QAction("Excluir Tarefa", self)
        delete_action.triggered.connect(self.delete_task)
        menu.addAction(delete_action)
        
        menu.exec_(self.tasks_table.viewport().mapToGlobal(position))
    
    def generate_from_briefing(self):
        """Gera tarefas baseadas na programação do briefing"""
        if not self.event_context.event_id:
            QMessageBox.warning(self, "Erro", "Selecione um evento primeiro.")
            return
        
        session = get_db_session()
        
        # Buscar briefing
        briefing = session.query(Briefing).filter(
            Briefing.event_id == self.event_context.event_id
        ).first()
        
        if not briefing or not briefing.schedule_info:
            QMessageBox.warning(
                self,
                "Erro",
                "Nenhuma programação encontrada no briefing. "
                "Por favor, preencha a programação no briefing primeiro."
            )
            session.close()
            return
        
        # Confirmar geração
        confirm = QMessageBox.question(
            self,
            "Confirmar Geração",
            "Gerar tarefas baseadas na programação do briefing?\n\n"
            "Isso pode criar tarefas duplicadas se já houver tarefas existentes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Na implementação real, faríamos um parser inteligente da programação
            # e criação de tarefas. Por simplicidade, apenas criamos algumas tarefas de exemplo.
            
            # Data base para as tarefas
            base_date = datetime.now().date()
            
            # Exemplo de tarefas geradas
            sample_tasks = [
                {
                    "title": "Setup de equipamentos",
                    "start_time": datetime.combine(base_date, datetime.min.time().replace(hour=14, minute=0)),
                    "end_time": datetime.combine(base_date, datetime.min.time().replace(hour=15, minute=0)),
                    "location": "Área técnica",
                    "priority": "high",
                    "status": "pending"
                },
                {
                    "title": "Captação de ambientação",
                    "start_time": datetime.combine(base_date, datetime.min.time().replace(hour=16, minute=0)),
                    "end_time": datetime.combine(base_date, datetime.min.time().replace(hour=17, minute=0)),
                    "location": "Todo o local",
                    "priority": "normal",
                    "status": "pending"
                },
                {
                    "title": "Show DJ X",
                    "start_time": datetime.combine(base_date, datetime.min.time().replace(hour=21, minute=0)),
                    "end_time": datetime.combine(base_date, datetime.min.time().replace(hour=22, minute=30)),
                    "location": "Palco Principal",
                    "priority": "high",
                    "status": "pending"
                },
                {
                    "title": "Ativação TikTok",
                    "start_time": datetime.combine(base_date, datetime.min.time().replace(hour=21, minute=30)),
                    "end_time": datetime.combine(base_date, datetime.min.time().replace(hour=22, minute=0)),
                    "location": "Área VIP",
                    "priority": "normal",
                    "status": "pending"
                },
                {
                    "title": "Primeira Entrega Real-time",
                    "start_time": datetime.combine(base_date, datetime.min.time().replace(hour=21, minute=30)),
                    "end_time": datetime.combine(base_date, datetime.min.time().replace(hour=22, minute=0)),
                    "location": "Ilha de Edição",
                    "priority": "high",
                    "status": "pending"
                }
            ]
            
            # Criar tarefas
            for task_data in sample_tasks:
                # Adicionar ID do evento
                task_data["event_id"] = self.event_context.event_id
                
                new_task = TimelineTask(**task_data)
                session.add(new_task)
            
            session.commit()
            
            # Recarregar tarefas
            self.load_timeline_tasks()
            
            QMessageBox.information(
                self,
                "Tarefas Geradas",
                f"{len(sample_tasks)} tarefas foram geradas com sucesso!"
            )
        
        session.close()
    
    def apply_filter(self, index):
        """Aplica filtro à tabela de tarefas"""
        if not self.event_context.event_id:
            return
        
        session = get_db_session()
        
        # Construir query base
        query = session.query(TimelineTask).filter(
            TimelineTask.event_id == self.event_context.event_id
        )
        
        # Aplicar filtro selecionado
        if index == 1:  # Apenas pendentes
            query = query.filter(TimelineTask.status != "completed")
        elif index == 2:  # Por responsável
            # Na implementação completa, abriríamos um diálogo para selecionar o responsável
            # Por simplicidade, apenas filtramos para mostrar tarefas com responsável atribuído
            query = query.filter(TimelineTask.assigned_to_id != None)
        
        # Ordenar por hora de início
        tasks = query.order_by(TimelineTask.start_time).all()
        
        # Atualizar tabela
        self.tasks_table.setRowCount(len(tasks))
        
        for i, task in enumerate(tasks):
            # Formatação de horário
            start_time = task.start_time.strftime("%H:%M")
            if task.end_time:
                time_str = f"{start_time} - {task.end_time.strftime('%H:%M')}"
            else:
                time_str = start_time
            
            self.tasks_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.tasks_table.setItem(i, 1, QTableWidgetItem(task.title))
            self.tasks_table.setItem(i, 2, QTableWidgetItem(task.location or ""))
            
            # Nome do responsável
            responsible_name = task.assigned_to.name if task.assigned_to else "-"
            self.tasks_table.setItem(i, 3, QTableWidgetItem(responsible_name))
            
            # Prioridade
            priority_item = QTableWidgetItem(task.priority.capitalize())
            if task.priority == "high":
                priority_item.setBackground(QBrush(QColor(255, 200, 200)))
            elif task.priority == "low":
                priority_item.setBackground(QBrush(QColor(200, 255, 200)))
            self.tasks_table.setItem(i, 4, priority_item)
            
            # Status
            status_map = {
                "pending": "Pendente",
                "in-progress": "Em andamento",
                "completed": "Concluída"
            }
            status_item = QTableWidgetItem(status_map.get(task.status, task.status.capitalize()))
            if task.status == "completed":
                status_item.setBackground(QBrush(QColor(200, 255, 200)))
            elif task.status == "in-progress":
                status_item.setBackground(QBrush(QColor(255, 255, 200)))
            self.tasks_table.setItem(i, 5, status_item)
            
            # Armazenar ID
            self.tasks_table.setItem(i, 6, QTableWidgetItem(task.id))
        
        session.close()