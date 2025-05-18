from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCalendarWidget, QPushButton
from PyQt5.QtCore import QDate
from lib.event_context import EventContext, EventAwareWindow
from db.models import Event, get_db_session
from datetime import datetime

class EventConfigWindow(QWidget, EventAwareWindow):
    def __init__(self):
        QWidget.__init__(self)
        EventAwareWindow.__init__(self)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Título da janela baseado no contexto
        self.title_label = QLabel("Criar Novo Evento")
        layout.addWidget(self.title_label)
        
        # Campos do evento
        layout.addWidget(QLabel("Nome do Evento:"))
        self.event_name_input = QLineEdit()
        layout.addWidget(self.event_name_input)
        
        layout.addWidget(QLabel("Data do Evento:"))
        self.event_date_input = QCalendarWidget()
        layout.addWidget(self.event_date_input)
        
        layout.addWidget(QLabel("Local do Evento:"))
        self.event_location_input = QLineEdit()
        layout.addWidget(self.event_location_input)
        
        layout.addWidget(QLabel("Cliente:"))
        self.client_input = QLineEdit()
        layout.addWidget(self.client_input)
        
        layout.addWidget(QLabel("Responsável Interno:"))
        self.internal_responsible_input = QLineEdit()
        layout.addWidget(self.internal_responsible_input)
        
        # Botões de ação
        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self.save_event)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
        
        # Se houver um evento selecionado, carregar seus dados
        if self.event_context.event_id:
            self.load_event_data()
    
    def on_event_changed(self, event_id, event_name):
        """Implementação do EventAwareWindow"""
        if event_id:
            self.title_label.setText(f"Editar Evento: {event_name}")
            self.load_event_data()
        else:
            self.title_label.setText("Criar Novo Evento")
            self.clear_form()
    
    def load_event_data(self):
        """Carrega dados do evento atual nos campos do formulário"""
        session = get_db_session()
        event = session.query(Event).filter(Event.id == self.event_context.event_id).first()
        
        if event:
            self.event_name_input.setText(event.name)
            
            # Configurar a data no calendário
            event_date = event.start_date
            q_date = QDate(event_date.year, event_date.month, event_date.day)
            self.event_date_input.setSelectedDate(q_date)
            
            self.event_location_input.setText(event.location)
            self.client_input.setText(event.client)
            self.internal_responsible_input.setText(event.responsible_person)
        
        session.close()
    
    def clear_form(self):
        """Limpa todos os campos do formulário"""
        self.event_name_input.clear()
        self.event_date_input.setSelectedDate(QDate.currentDate())
        self.event_location_input.clear()
        self.client_input.clear()
        self.internal_responsible_input.clear()
    
    def save_event(self):
        """Salva um novo evento ou atualiza um existente"""
        session = get_db_session()
        
        # Preparar dados do evento
        name = self.event_name_input.text()
        selected_date = self.event_date_input.selectedDate()
        date = datetime(selected_date.year(), selected_date.month(), selected_date.day())
        location = self.event_location_input.text()
        client = self.client_input.text()
        responsible = self.internal_responsible_input.text()
        
        if self.event_context.event_id:
            # Atualizar evento existente
            event = session.query(Event).filter(Event.id == self.event_context.event_id).first()
            event.name = name
            event.start_date = date
            event.end_date = date  # Simplificação: mesmo dia de início e fim
            event.location = location
            event.client = client
            event.responsible_person = responsible
        else:
            # Criar novo evento
            event = Event(
                name=name,
                start_date=date,
                end_date=date,  # Simplificação: mesmo dia de início e fim
                location=location,
                client=client,
                responsible_person=responsible,
                event_type="show",  # Valor padrão
                coverage_type="real-time"  # Valor padrão
            )
            session.add(event)
        
        # Commit e atualizar contexto
        session.commit()
        
        # Atualizar o contexto
        self.event_context.event_id = event.id
        self.event_context.event_name = event.name
        
        session.close()
        self.close()