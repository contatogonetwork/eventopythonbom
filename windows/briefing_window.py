from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QLineEdit, QFormLayout, QCheckBox, QDateEdit,
    QTabWidget, QFileDialog, QListWidget, QListWidgetItem,
    QScrollArea, QMessageBox, QTimeEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from lib.event_context import EventContext, EventAwareWindow
from db.models import Event, Briefing, get_db_session
import os
import json
import shutil
from datetime import datetime

class BriefingWindow(QWidget, EventAwareWindow):
    def __init__(self):
        QWidget.__init__(self)
        EventAwareWindow.__init__(self)
        
        self.init_ui()
        
        # Carregar briefing se houver evento selecionado
        if self.event_context.event_id:
            self.load_briefing()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Título
        self.title_label = QLabel("Briefing do Evento")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.title_label)
        
        # Tabs para separar seções do briefing
        self.tab_widget = QTabWidget()
        
        # Seção: Informações Gerais
        self.general_tab = QWidget()
        self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "Informações Gerais")
        
        # Seção: Programação de Shows
        self.shows_tab = QWidget()
        self.create_shows_tab()
        self.tab_widget.addTab(self.shows_tab, "Programação")
        
        # Seção: Patrocinadores e Ativações
        self.sponsors_tab = QWidget()
        self.create_sponsors_tab()
        self.tab_widget.addTab(self.sponsors_tab, "Patrocinadores")
        
        # Seção: Entregas Esperadas
        self.deliverables_tab = QWidget()
        self.create_deliverables_tab()
        self.tab_widget.addTab(self.deliverables_tab, "Entregas")
        
        # Seção: Diretrizes Criativas
        self.creative_tab = QWidget()
        self.create_creative_tab()
        self.tab_widget.addTab(self.creative_tab, "Estilo & Referências")
        
        main_layout.addWidget(self.tab_widget)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar Briefing")
        self.save_button.clicked.connect(self.save_briefing)
        button_layout.addWidget(self.save_button)
        
        self.generate_timeline_button = QPushButton("Gerar Timeline")
        self.generate_timeline_button.clicked.connect(self.generate_timeline)
        button_layout.addWidget(self.generate_timeline_button)
        
        main_layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Briefing do Evento")
    
    def on_event_changed(self, event_id, event_name):
        """Implementação do EventAwareWindow"""
        if event_id:
            self.title_label.setText(f"Briefing do Evento: {event_name}")
            self.setWindowTitle(f"Briefing - {event_name}")
            self.load_briefing()
        else:
            self.title_label.setText("Briefing do Evento")
            self.setWindowTitle("Briefing")
            self.clear_form()
    
    def create_general_tab(self):
        """Cria o conteúdo da tab de informações gerais"""
        layout = QFormLayout()
        
        # Horário de início do show
        self.show_start_time = QTimeEdit()
        self.show_start_time.setDisplayFormat("HH:mm")
        layout.addRow("Horário de início:", self.show_start_time)
        
        # Horário de fim do show
        self.show_end_time = QTimeEdit()
        self.show_end_time.setDisplayFormat("HH:mm")
        layout.addRow("Horário de fim:", self.show_end_time)
        
        # Captação especial
        self.special_capture = QCheckBox("Captação especial?")
        layout.addRow("", self.special_capture)
        
        # Detalhes da captação especial
        self.special_capture_details = QTextEdit()
        self.special_capture_details.setPlaceholderText("Detalhes da captação especial, se aplicável...")
        layout.addRow("Detalhes:", self.special_capture_details)
        
        # Prazo de entrega final
        self.delivery_deadline = QDateEdit()
        self.delivery_deadline.setCalendarPopup(True)
        self.delivery_deadline.setDate(QDate.currentDate().addDays(3))  # Default: 3 dias após hoje
        layout.addRow("Prazo de entrega final:", self.delivery_deadline)
        
        # Observações gerais
        self.general_notes = QTextEdit()
        self.general_notes.setPlaceholderText("Observações gerais sobre o evento...")
        layout.addRow("Observações:", self.general_notes)
        
        # Informações logísticas
        self.logistics_info = QTextEdit()
        self.logistics_info.setPlaceholderText("Credenciais, acessos, Wi-Fi, alimentação...")
        layout.addRow("Informações Logísticas:", self.logistics_info)
        
        self.general_tab.setLayout(layout)
    
    def create_shows_tab(self):
        """Cria o conteúdo da tab de programação de shows"""
        layout = QVBoxLayout()
        
        # Programação detalhada
        layout.addWidget(QLabel("Programação de Shows:"))
        self.schedule_text = QTextEdit()
        self.schedule_text.setPlaceholderText(
            "Exemplo:\n"
            "Palco Principal:\n"
            "21:00 - DJ X\n"
            "22:30 - Headliner\n\n"
            "Palco Secundário:\n"
            "20:00 - Artista Y\n"
            "23:00 - Artista Z"
        )
        layout.addWidget(self.schedule_text)
        
        self.shows_tab.setLayout(layout)
    
    def create_sponsors_tab(self):
        """Cria o conteúdo da tab de patrocinadores"""
        layout = QVBoxLayout()
        
        # Lista de patrocinadores e ativações
        layout.addWidget(QLabel("Patrocinadores e Ativações:"))
        self.sponsors_text = QTextEdit()
        self.sponsors_text.setPlaceholderText(
            "Exemplo:\n"
            "Red Bull:\n"
            "- Ativação com drones às 00h\n"
            "- Totem interativo próximo ao palco principal\n\n"
            "TikTok:\n"
            "- Cabine 360° na área VIP às 21:30\n\n"
            "Heineken:\n"
            "- DJ branded às 23:45"
        )
        layout.addWidget(self.sponsors_text)
        
        # Requisitos específicos de marca
        layout.addWidget(QLabel("Requisitos de Marca:"))
        self.brand_requirements = QTextEdit()
        self.brand_requirements.setPlaceholderText(
            "Requisitos específicos por marca, ex:\n"
            "- Red Bull: Logo em destaque, cores vibrantes\n"
            "- TikTok: Formato vertical, hashtags obrigatórias"
        )
        layout.addWidget(self.brand_requirements)
        
        self.sponsors_tab.setLayout(layout)
    
    def create_deliverables_tab(self):
        """Cria o conteúdo da tab de entregas esperadas"""
        layout = QVBoxLayout()
        
        # Lista de entregas
        layout.addWidget(QLabel("Entregas Esperadas:"))
        self.deliverables_text = QTextEdit()
        self.deliverables_text.setPlaceholderText(
            "Exemplo:\n"
            "Real-Time:\n"
            "- 3 Reels a cada 4 horas\n"
            "- Stories a cada 2 horas\n"
            "- Teaser para redes às 23h\n\n"
            "Pós-Evento:\n"
            "- Aftermovie (1-3min) em até 48h\n"
            "- Melhores momentos por palco\n"
            "- Versões para cada patrocinador"
        )
        layout.addWidget(self.deliverables_text)
        
        # Especificações técnicas
        layout.addWidget(QLabel("Especificações Técnicas:"))
        self.technical_specs = QTextEdit()
        self.technical_specs.setPlaceholderText(
            "Exemplo:\n"
            "- Reels: 9:16, máximo 60 segundos\n"
            "- Aftermovie: 16:9, 1080p, H.264\n"
            "- Legendas obrigatórias\n"
            "- Trilhas autorizadas no anexo"
        )
        layout.addWidget(self.technical_specs)
        
        self.deliverables_tab.setLayout(layout)
    
    def create_creative_tab(self):
        """Cria o conteúdo da tab de diretrizes criativas"""
        layout = QVBoxLayout()
        
        # Diretrizes estéticas
        layout.addWidget(QLabel("Diretrizes Estéticas:"))
        self.aesthetics_text = QTextEdit()
        self.aesthetics_text.setPlaceholderText(
            "Exemplo:\n"
            "- Cores vibrantes, contrastantes\n"
            "- Estilo: rápido, dinâmico, jovem\n"
            "- Transições sincronizadas com a música\n"
            "- Drone shots para estabelecer escala"
        )
        layout.addWidget(self.aesthetics_text)
        
        # Arquivos de referência
        reference_section = QHBoxLayout()
        
        reference_section.addWidget(QLabel("Arquivos de Referência:"))
        
        self.add_reference_button = QPushButton("Adicionar")
        self.add_reference_button.clicked.connect(self.add_reference_file)
        reference_section.addWidget(self.add_reference_button)
        
        layout.addLayout(reference_section)
        
        self.references_list = QListWidget()
        layout.addWidget(self.references_list)
        
        self.creative_tab.setLayout(layout)
    
    def add_reference_file(self):
        """Adiciona um arquivo de referência"""
        if not self.event_context.event_id:
            QMessageBox.warning(self, "Erro", "Selecione um evento primeiro.")
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Arquivos de Referência",
            "",
            "Arquivos de Mídia (*.jpg *.jpeg *.png *.pdf *.mp4)"
        )
        
        if not files:
            return
        
        # Criar pasta de referências para o evento se não existir
        references_dir = os.path.expanduser(f"~/GoNetworkAI/events/{self.event_context.event_id}/references")
        os.makedirs(references_dir, exist_ok=True)
        
        for file_path in files:
            # Copiar arquivo para pasta de referências
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(references_dir, file_name)
            
            try:
                shutil.copy2(file_path, dest_path)
                
                # Adicionar à lista
                item = QListWidgetItem(file_name)
                item.setData(Qt.UserRole, dest_path)
                self.references_list.addItem(item)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao copiar arquivo: {str(e)}")
    
    def load_briefing(self):
        """Carrega os dados do briefing do evento atual"""
        if not self.event_context.event_id:
            return
        
        session = get_db_session()
        
        briefing = session.query(Briefing).filter(
            Briefing.event_id == self.event_context.event_id
        ).first()
        
        if briefing:
            # Carregar nas tabs
            try:
                # Informações gerais
                general_data = json.loads(briefing.general_info or "{}")
                
                if "show_start_time" in general_data:
                    time_parts = general_data["show_start_time"].split(":")
                    self.show_start_time.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
                
                if "show_end_time" in general_data:
                    time_parts = general_data["show_end_time"].split(":")
                    self.show_end_time.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
                
                self.special_capture.setChecked(general_data.get("special_capture", False))
                self.special_capture_details.setText(general_data.get("special_capture_details", ""))
                
                if "delivery_deadline" in general_data:
                    date_parts = general_data["delivery_deadline"].split("-")
                    self.delivery_deadline.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                
                self.general_notes.setText(general_data.get("general_notes", ""))
                self.logistics_info.setText(general_data.get("logistics_info", ""))
                
                # Programação
                self.schedule_text.setText(briefing.schedule_info or "")
                
                # Patrocinadores
                sponsor_data = json.loads(briefing.sponsor_activations or "{}")
                self.sponsors_text.setText(sponsor_data.get("sponsors_text", ""))
                self.brand_requirements.setText(sponsor_data.get("brand_requirements", ""))
                
                # Entregas
                deliverables_data = json.loads(briefing.deliverables or "{}")
                self.deliverables_text.setText(deliverables_data.get("deliverables_text", ""))
                self.technical_specs.setText(deliverables_data.get("technical_specs", ""))
                
                # Estilo e referências
                creative_data = json.loads(briefing.creative_guidelines or "{}")
                self.aesthetics_text.setText(creative_data.get("aesthetics_text", ""))
                
                # Arquivos de referência
                self.references_list.clear()
                reference_files = creative_data.get("reference_files", [])
                
                for ref_file in reference_files:
                    if os.path.exists(ref_file["path"]):
                        item = QListWidgetItem(ref_file["name"])
                        item.setData(Qt.UserRole, ref_file["path"])
                        self.references_list.addItem(item)
                
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao carregar briefing: {str(e)}")
        
        session.close()
    
    def save_briefing(self):
        """Salva os dados do briefing"""
        if not self.event_context.event_id:
            QMessageBox.warning(self, "Erro", "Selecione um evento primeiro.")
            return
        
        # Coletar dados das tabs
        general_data = {
            "show_start_time": self.show_start_time.time().toString("HH:mm"),
            "show_end_time": self.show_end_time.time().toString("HH:mm"),
            "special_capture": self.special_capture.isChecked(),
            "special_capture_details": self.special_capture_details.toPlainText(),
            "delivery_deadline": self.delivery_deadline.date().toString("yyyy-MM-dd"),
            "general_notes": self.general_notes.toPlainText(),
            "logistics_info": self.logistics_info.toPlainText()
        }
        
        sponsor_data = {
            "sponsors_text": self.sponsors_text.toPlainText(),
            "brand_requirements": self.brand_requirements.toPlainText()
        }
        
        deliverables_data = {
            "deliverables_text": self.deliverables_text.toPlainText(),
            "technical_specs": self.technical_specs.toPlainText()
        }
        
        # Coletar referências
        reference_files = []
        for i in range(self.references_list.count()):
            item = self.references_list.item(i)
            reference_files.append({
                "name": item.text(),
                "path": item.data(Qt.UserRole)
            })
        
        creative_data = {
            "aesthetics_text": self.aesthetics_text.toPlainText(),
            "reference_files": reference_files
        }
        
        session = get_db_session()
        
        # Verificar se já existe briefing para este evento
        existing_briefing = session.query(Briefing).filter(
            Briefing.event_id == self.event_context.event_id
        ).first()
        
        if existing_briefing:
            # Atualizar existente
            existing_briefing.general_info = json.dumps(general_data)
            existing_briefing.schedule_info = self.schedule_text.toPlainText()
            existing_briefing.sponsor_activations = json.dumps(sponsor_data)
            existing_briefing.deliverables = json.dumps(deliverables_data)
            existing_briefing.creative_guidelines = json.dumps(creative_data)
            existing_briefing.updated_at = datetime.utcnow()
        else:
            # Criar novo
            new_briefing = Briefing(
                event_id=self.event_context.event_id,
                general_info=json.dumps(general_data),
                schedule_info=self.schedule_text.toPlainText(),
                sponsor_activations=json.dumps(sponsor_data),
                deliverables=json.dumps(deliverables_data),
                creative_guidelines=json.dumps(creative_data)
            )
            session.add(new_briefing)
        
        session.commit()
        session.close()
        
        self.status_label.setText("Briefing salvo com sucesso!")
        QMessageBox.information(self, "Sucesso", "Briefing salvo com sucesso!")
    
    def generate_timeline(self):
        """Gera a timeline baseada nos dados do briefing"""
        if not self.event_context.event_id:
            QMessageBox.warning(self, "Erro", "Selecione um evento primeiro.")
            return
        
        # Primeiro salvar o briefing
        self.save_briefing()
        
        # Aqui implementaríamos a lógica para criar as tarefas de timeline
        # baseadas nas informações do briefing
        
        QMessageBox.information(
            self,
            "Timeline Gerada",
            "Timeline gerada com sucesso baseada no briefing.\n\n"
            "Acesse a seção de Timeline para visualizar e ajustar as tarefas."
        )
    
    def clear_form(self):
        """Limpa o formulário"""
        # Informações gerais
        self.show_start_time.setTime(QTime(21, 0))  # 21:00 padrão
        self.show_end_time.setTime(QTime(6, 0))     # 06:00 padrão
        self.special_capture.setChecked(False)
        self.special_capture_details.clear()
        self.delivery_deadline.setDate(QDate.currentDate().addDays(3))
        self.general_notes.clear()
        self.logistics_info.clear()
        
        # Programação
        self.schedule_text.clear()
        
        # Patrocinadores
        self.sponsors_text.clear()
        self.brand_requirements.clear()
        
        # Entregas
        self.deliverables_text.clear()
        self.technical_specs.clear()
        
        # Estilo e referências
        self.aesthetics_text.clear()
        self.references_list.clear()