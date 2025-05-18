from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QValueAxis, QPieSeries
from lib.event_context import EventContext, EventAwareWindow
from db.models import Event, Delivery, TimelineTask, Analytics, get_db_session
import os
from datetime import datetime, timedelta

class AnalyticsWidget(QWidget):
    """Widget base para gráficos analíticos"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Container para o gráfico
        self.chart_container = QVBoxLayout()
        layout.addLayout(self.chart_container)
        
        self.setLayout(layout)
    
    def update_chart(self):
        """
        Método a ser implementado pelas subclasses
        para atualizar o conteúdo do gráfico
        """
        pass


class DeliveryStatusChart(AnalyticsWidget):
    """Gráfico de pizza com status das entregas"""
    def __init__(self, parent=None):
        super().__init__("Status das Entregas", parent)
        
        # Criar gráfico vazio
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_container.addWidget(self.chart_view)
    
    def update_chart(self, deliveries):
        """Atualiza o gráfico com base nas entregas"""
        self.chart.removeAllSeries()
        
        # Contar entregas por status
        status_counts = {
            "pending": 0,
            "in-progress": 0,
            "review": 0,
            "approved": 0,
            "published": 0
        }
        
        for delivery in deliveries:
            if delivery.status in status_counts:
                status_counts[delivery.status] += 1
        
        # Criar série de pizza
        series = QPieSeries()
        
        # Adicionar fatias coloridas
        if status_counts["pending"] > 0:
            slice_pending = series.append("Pendente", status_counts["pending"])
            slice_pending.setBrush(QColor(255, 200, 200))
        
        if status_counts["in-progress"] > 0:
            slice_progress = series.append("Em andamento", status_counts["in-progress"])
            slice_progress.setBrush(QColor(255, 255, 200))
        
        if status_counts["review"] > 0:
            slice_review = series.append("Em revisão", status_counts["review"])
            slice_review.setBrush(QColor(200, 200, 255))
        
        if status_counts["approved"] > 0:
            slice_approved = series.append("Aprovado", status_counts["approved"])
            slice_approved.setBrush(QColor(200, 255, 200))
        
        if status_counts["published"] > 0:
            slice_published = series.append("Publicado", status_counts["published"])
            slice_published.setBrush(QColor(180, 255, 180))
        
        self.chart.addSeries(series)
        self.chart.setTitle(f"Total: {sum(status_counts.values())} entregas")


class TeamProductivityChart(AnalyticsWidget):
    """Gráfico de barras com produtividade da equipe"""
    def __init__(self, parent=None):
        super().__init__("Produtividade da Equipe", parent)
        
        # Criar gráfico vazio
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_container.addWidget(self.chart_view)
    
    def update_chart(self, team_data):
        """Atualiza o gráfico com base nos dados da equipe"""
        self.chart.removeAllSeries()
        
        if not team_data:
            self.chart.setTitle("Sem dados de produtividade")
            return
        
        # Criar conjunto de barras
        bar_set = QBarSet("Tarefas Concluídas")
        
        # Adicionar valores
        names = []
        for member_name, task_count in team_data:
            bar_set.append(task_count)
            names.append(member_name)
        
        series = QBarSeries()
        series.append(bar_set)
        
        self.chart.addSeries(series)
        
        # Criar eixo X
        axis_x = QValueAxis()
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Criar eixo Y
        axis_y = QValueAxis()
        axis_y.setRange(0, max(member[1] for member in team_data) + 1)
        axis_y.setTickCount(5)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        self.chart.setTitle("Tarefas concluídas por membro")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)


class DeliveryTimelineChart(AnalyticsWidget):
    """Gráfico de linha com tempo de processamento de entregas"""
    def __init__(self, parent=None):
        super().__init__("Tempo de Processamento", parent)
        
        # Container de estatísticas
        stats_layout = QHBoxLayout()
        
        # Tempo médio de processamento
        self.avg_time_frame = QFrame()
        self.avg_time_frame.setFrameShape(QFrame.StyledPanel)
        avg_time_layout = QVBoxLayout()
        self.avg_time_label = QLabel("Tempo médio de processamento")
        avg_time_layout.addWidget(self.avg_time_label)
        self.avg_time_value = QLabel("0 min")
        self.avg_time_value.setStyleSheet("font-size: 18px; font-weight: bold;")
        avg_time_layout.addWidget(self.avg_time_value)
        self.avg_time_frame.setLayout(avg_time_layout)
        stats_layout.addWidget(self.avg_time_frame)
        
        # Taxa de aprovação na primeira versão
        self.approval_rate_frame = QFrame()
        self.approval_rate_frame.setFrameShape(QFrame.StyledPanel)
        approval_rate_layout = QVBoxLayout()
        self.approval_rate_label = QLabel("Taxa de aprovação na primeira versão")
        approval_rate_layout.addWidget(self.approval_rate_label)
        self.approval_rate_value = QLabel("0%")
        self.approval_rate_value.setStyleSheet("font-size: 18px; font-weight: bold;")
        approval_rate_layout.addWidget(self.approval_rate_value)
        self.approval_rate_frame.setLayout(approval_rate_layout)
        stats_layout.addWidget(self.approval_rate_frame)
        
        self.chart_container.addLayout(stats_layout)
    
    def update_chart(self, processing_times, approval_rate):
        """Atualiza as estatísticas de processamento"""
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            self.avg_time_value.setText(f"{avg_time:.1f} min")
        else:
            self.avg_time_value.setText("N/A")
        
        self.approval_rate_value.setText(f"{approval_rate:.1f}%")


class AnalyticsWindow(QWidget, EventAwareWindow):
    def __init__(self):
        QWidget.__init__(self)
        EventAwareWindow.__init__(self)
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Título
        self.title_label = QLabel("Métricas e Insights")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.title_label)
        
        # Área de rolagem para os widgets analíticos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        self.analytics_layout = QVBoxLayout(scroll_content)
        
        # Widget de estatísticas resumidas
        self.summary_widget = QWidget()
        summary_layout = QHBoxLayout()
        
        # Volume de produção
        self.volume_frame = QFrame()
        self.volume_frame.setFrameShape(QFrame.StyledPanel)
        volume_layout = QVBoxLayout()
        volume_layout.addWidget(QLabel("Volume de Produção"))
        self.volume_label = QLabel("0 GB")
        self.volume_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        volume_layout.addWidget(self.volume_label)
        self.volume_frame.setLayout(volume_layout)
        summary_layout.addWidget(self.volume_frame)
        
        # Total de entregas
        self.deliveries_frame = QFrame()
        self.deliveries_frame.setFrameShape(QFrame.StyledPanel)
        deliveries_layout = QVBoxLayout()
        deliveries_layout.addWidget(QLabel("Total de Entregas"))
        self.deliveries_label = QLabel("0")
        self.deliveries_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        deliveries_layout.addWidget(self.deliveries_label)
        self.deliveries_frame.setLayout(deliveries_layout)
        summary_layout.addWidget(self.deliveries_frame)
        
        # Conclusão de tarefas
        self.completion_frame = QFrame()
        self.completion_frame.setFrameShape(QFrame.StyledPanel)
        completion_layout = QVBoxLayout()
        completion_layout.addWidget(QLabel("Conclusão de Tarefas"))
        self.completion_progress = QProgressBar()
        self.completion_progress.setRange(0, 100)
        self.completion_progress.setValue(0)
        completion_layout.addWidget(self.completion_progress)
        self.completion_frame.setLayout(completion_layout)
        summary_layout.addWidget(self.completion_frame)
        
        self.summary_widget.setLayout(summary_layout)
        self.analytics_layout.addWidget(self.summary_widget)
        
        # Gráficos analíticos
        self.delivery_status_chart = DeliveryStatusChart()
        self.analytics_layout.addWidget(self.delivery_status_chart)
        
        self.team_productivity_chart = TeamProductivityChart()
        self.analytics_layout.addWidget(self.team_productivity_chart)
        
        self.delivery_timeline_chart = DeliveryTimelineChart()
        self.analytics_layout.addWidget(self.delivery_timeline_chart)
        
        # Tabela de performance por entrega
        self.analytics_layout.addWidget(QLabel("Performance por Entrega"))
        self.delivery_performance_table = QTableWidget()
        self.delivery_performance_table.setColumnCount(4)
        self.delivery_performance_table.setHorizontalHeaderLabels([
            "Entrega", "Tempo de Processamento", "Versões", "Status"
        ])
        self.delivery_performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.analytics_layout.addWidget(self.delivery_performance_table)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Botões
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Atualizar Dados")
        refresh_button.clicked.connect(self.update_analytics)
        button_layout.addWidget(refresh_button)
        
        generate_report_button = QPushButton("Gerar Relatório PDF")
        generate_report_button.clicked.connect(self.generate_report)
        button_layout.addWidget(generate_report_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Métricas e Insights")
    
    def on_event_changed(self, event_id, event_name):
        """Implementação do EventAwareWindow"""
        if event_id:
            self.title_label.setText(f"Métricas e Insights - {event_name}")
            self.setWindowTitle(f"Métricas - {event_name}")
            self.update_analytics()
        else:
            self.title_label.setText("Métricas e Insights")
            self.setWindowTitle("Métricas e Insights")
            self.clear_analytics()
    
    def clear_analytics(self):
        """Limpa os dados analíticos"""
        self.volume_label.setText("0 GB")
        self.deliveries_label.setText("0")
        self.completion_progress.setValue(0)
        self.delivery_performance_table.setRowCount(0)
    
    def update_analytics(self):
        """Atualiza os dados analíticos"""
        if not self.event_context.event_id:
            return
        
        session = get_db_session()
        
        # Buscar dados do evento
        event = session.query(Event).filter(Event.id == self.event_context.event_id).first()
        
        if event:
            # Buscar entregas
            deliveries = session.query(Delivery).filter(Delivery.event_id == event.id).all()
            
            # Buscar tarefas
            tasks = session.query(TimelineTask).filter(TimelineTask.event_id == event.id).all()
            
            # Buscar assets
            from sqlalchemy import func, text
            assets_query = session.execute(
                text(f"SELECT SUM(file_size) FROM assets WHERE event_id = '{event.id}'")
            )
            total_size = assets_query.scalar() or 0
            
            # Atualizar volume de produção
            self.volume_label.setText(f"{total_size:.1f} GB")
            
            # Atualizar total de entregas
            self.deliveries_label.setText(str(len(deliveries)))
            
            # Atualizar conclusão de tarefas
            if tasks:
                completed_tasks = sum(1 for task in tasks if task.status == "completed")
                completion_percentage = (completed_tasks / len(tasks)) * 100
                self.completion_progress.setValue(int(completion_percentage))
            else:
                self.completion_progress.setValue(0)
            
            # Atualizar gráfico de status das entregas
            self.delivery_status_chart.update_chart(deliveries)
            
            # Atualizar gráfico de produtividade da equipe
            team_data = self.calculate_team_productivity(tasks)
            self.team_productivity_chart.update_chart(team_data)
            
            # Atualizar estatísticas de processamento
            processing_times, approval_rate = self.calculate_delivery_metrics(deliveries)
            self.delivery_timeline_chart.update_chart(processing_times, approval_rate)
            
            # Atualizar tabela de performance por entrega
            self.update_delivery_performance_table(deliveries)
        
        session.close()
    
    def calculate_team_productivity(self, tasks):
        """Calcula métricas de produtividade da equipe"""
        team_productivity = {}
        
        for task in tasks:
            if task.status == "completed" and task.assigned_to:
                member_name = task.assigned_to.name
                team_productivity[member_name] = team_productivity.get(member_name, 0) + 1
        
        # Ordenar por quantidade de tarefas
        return sorted(team_productivity.items(), key=lambda x: x[1], reverse=True)
    
    def calculate_delivery_metrics(self, deliveries):
        """Calcula métricas de processamento de entregas"""
        processing_times = []
        first_version_approvals = 0
        multi_version_deliveries = 0
        
        for delivery in deliveries:
            if delivery.versions:
                # Calcular tempo de processamento
                if len(delivery.versions) > 1:
                    first_version = min(delivery.versions, key=lambda x: x.version_number)
                    last_version = max(delivery.versions, key=lambda x: x.version_number)
                    
                    if first_version.upload_time and last_version.upload_time:
                        delta = last_version.upload_time - first_version.upload_time
                        processing_time = delta.total_seconds() / 60  # minutos
                        processing_times.append(processing_time)
                
                # Verificar aprovações na primeira versão
                if len(delivery.versions) == 1 and delivery.status == "approved":
                    first_version_approvals += 1
                
                if len(delivery.versions) > 1:
                    multi_version_deliveries += 1
        
        # Calcular taxa de aprovação na primeira versão
        total_reviewed = first_version_approvals + multi_version_deliveries
        approval_rate = (first_version_approvals / total_reviewed * 100) if total_reviewed > 0 else 0
        
        return processing_times, approval_rate
    
    def update_delivery_performance_table(self, deliveries):
        """Atualiza a tabela de performance por entrega"""
        self.delivery_performance_table.setRowCount(0)
        
        for delivery in deliveries:
            row = self.delivery_performance_table.rowCount()
            self.delivery_performance_table.insertRow(row)
            
            # Título
            self.delivery_performance_table.setItem(row, 0, QTableWidgetItem(delivery.title))
            
            # Tempo de processamento
            processing_time = "N/A"
            if delivery.versions and len(delivery.versions) > 1:
                first_version = min(delivery.versions, key=lambda x: x.version_number)
                last_version = max(delivery.versions, key=lambda x: x.version_number)
                
                if first_version.upload_time and last_version.upload_time:
                    delta = last_version.upload_time - first_version.upload_time
                    processing_time = f"{delta.total_seconds() / 60:.1f} min"
            
            self.delivery_performance_table.setItem(row, 1, QTableWidgetItem(processing_time))
            
            # Versões
            version_count = len(delivery.versions) if delivery.versions else 0
            self.delivery_performance_table.setItem(row, 2, QTableWidgetItem(str(version_count)))
            
            # Status
            status_map = {
                'pending': 'Pendente',
                'in-progress': 'Em andamento',
                'review': 'Em revisão',
                'approved': 'Aprovado',
                'published': 'Publicado'
            }
            status_item = QTableWidgetItem(status_map.get(delivery.status, delivery.status.capitalize()))
            self.delivery_performance_table.setItem(row, 3, status_item)
    
    def generate_report(self):
        """Gera um relatório PDF com as métricas e gráficos"""
        if not self.event_context.event_id:
            return
        
        # Em uma implementação real, geraríamos um PDF com reportlab ou outra biblioteca
        # Por simplicidade, apenas mostramos uma mensagem
        
        from PyQt5.QtWidgets import QMessageBox
        
        QMessageBox.information(
            self,
            "Relatório Gerado",
            "O relatório foi gerado com sucesso!\n\n"
            "Em uma implementação completa, aqui seria gerado um arquivo PDF "
            "com todos os gráficos, tabelas e métricas."
        )