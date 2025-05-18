from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSlider, QStyle, QSizePolicy
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, pyqtSlot, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen
import os

class TimecodeAnnotation:
    """Representa uma anotação em um ponto específico do vídeo"""
    def __init__(self, timestamp, text, author, color="#FF0000"):
        self.timestamp = timestamp  # Em milissegundos
        self.text = text
        self.author = author
        self.color = color

class VideoPlayer(QWidget):
    """
    Player de vídeo com controles básicos e suporte para anotações
    em timecodes específicos.
    """
    annotationAdded = pyqtSignal(float, str)  # timestamp, text
    positionChanged = pyqtSignal(int)  # position in ms
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = AnnotationVideoWidget(self)
        self.videoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.toggle_playback)
        
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.set_position)
        
        self.timecodeLabel = QLabel("00:00:00 / 00:00:00")
        
        self.annotateButton = QPushButton("Anotar")
        self.annotateButton.clicked.connect(self.add_annotation)
        self.annotateButton.setEnabled(False)
        
        # Layout
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.timecodeLabel)
        controlLayout.addWidget(self.annotateButton)
        
        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addLayout(controlLayout)
        
        self.setLayout(layout)
        
        # Conectar sinais
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.media_state_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.error.connect(self.handle_error)
        
        # Anotações
        self.annotations = []
    
    def load_video(self, file_path):
        """Carrega um arquivo de vídeo"""
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return False
        
        url = QUrl.fromLocalFile(file_path)
        content = QMediaContent(url)
        self.mediaPlayer.setMedia(content)
        self.playButton.setEnabled(True)
        self.annotateButton.setEnabled(True)
        self.videoWidget.clear_annotations()
        self.annotations = []
        
        return True
    
    def toggle_playback(self):
        """Alterna entre reprodução e pausa"""
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
    
    def media_state_changed(self, state):
        """Atualiza os controles conforme o estado do player"""
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
    
    def position_changed(self, position):
        """Chamado quando a posição de reprodução muda"""
        self.positionSlider.setValue(position)
        
        # Emitir sinal de mudança de posição para uso externo
        self.positionChanged.emit(position)
        
        # Atualizar label de timecode
        self.update_timecode_label(position)
        
        # Verificar anotações próximas
        self.check_annotations(position)
    
    def duration_changed(self, duration):
        """Chamado quando a duração do vídeo é determinada"""
        self.positionSlider.setRange(0, duration)
    
    def set_position(self, position):
        """Define a posição de reprodução"""
        self.mediaPlayer.setPosition(position)
    
    def handle_error(self):
        """Manipula erros do player de vídeo"""
        self.playButton.setEnabled(False)
        error_msg = f"Erro: {self.mediaPlayer.errorString()}"
        print(error_msg)
    
    def update_timecode_label(self, position):
        """Atualiza o label com o timecode atual"""
        duration = self.mediaPlayer.duration()
        
        # Converter para formato HH:MM:SS
        position_sec = position // 1000
        duration_sec = duration // 1000
        
        position_str = f"{position_sec // 3600:02d}:{(position_sec % 3600) // 60:02d}:{position_sec % 60:02d}"
        duration_str = f"{duration_sec // 3600:02d}:{(duration_sec % 3600) // 60:02d}:{duration_sec % 60:02d}"
        
        self.timecodeLabel.setText(f"{position_str} / {duration_str}")
    
    def add_annotation(self):
        """Abre diálogo para adicionar anotação no timecode atual"""
        from PyQt5.QtWidgets import QInputDialog
        
        position = self.mediaPlayer.position()
        
        text, ok = QInputDialog.getText(
            self, "Adicionar Anotação", 
            f"Anotação em {self.format_timecode(position)}:"
        )
        
        if ok and text:
            annotation = TimecodeAnnotation(position, text, "Usuário", "#FF0000")
            self.annotations.append(annotation)
            self.videoWidget.set_annotations(self.annotations)
            
            # Emitir sinal de anotação adicionada
            self.annotationAdded.emit(position / 1000.0, text)
    
    def check_annotations(self, position):
        """Verifica se há anotações próximas da posição atual"""
        # Na versão completa, exibir indicadores visuais ou notificações
        pass
    
    def set_annotations(self, annotations):
        """Define a lista de anotações"""
        self.annotations = annotations
        self.videoWidget.set_annotations(annotations)
    
    def format_timecode(self, position_ms):
        """Formata um timecode em milissegundos para formato legível"""
        position_sec = position_ms // 1000
        return f"{position_sec // 3600:02d}:{(position_sec % 3600) // 60:02d}:{position_sec % 60:02d}"


class AnnotationVideoWidget(QVideoWidget):
    """
    Widget de vídeo personalizado que suporta exibição de anotações
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.annotations = []
        self.current_position = 0
    
    def set_annotations(self, annotations):
        """Define a lista de anotações"""
        self.annotations = annotations
        self.update()
    
    def clear_annotations(self):
        """Remove todas as anotações"""
        self.annotations = []
        self.update()
    
    def update_position(self, position):
        """Atualiza a posição atual de reprodução"""
        self.current_position = position
    
    def paintEvent(self, event):
        """Sobrescreve o método paintEvent para desenhar anotações"""
        # Primeiro, desenha o vídeo normalmente
        super().paintEvent(event)
        
        # Depois, desenha as marcações de anotações
        painter = QPainter(self)
        
        # Desenhar linha de tempo na parte inferior
        if self.annotations:
            timeline_height = 20
            timeline_y = self.height() - timeline_height
            timeline_width = self.width() - 20  # Margem nas bordas
            timeline_x = 10
            
            # Desenhar linha de base
            painter.setPen(QPen(QColor(200, 200, 200), 2))
            painter.drawLine(timeline_x, timeline_y, timeline_x + timeline_width, timeline_y)
            
            # Desenhar marcadores de anotações
            total_duration = self.parent().mediaPlayer.duration() or 1
            for annotation in self.annotations:
                # Calcular posição X proporcional ao tempo
                marker_x = timeline_x + int((annotation.timestamp / total_duration) * timeline_width)
                
                # Desenhar marcador vertical
                painter.setPen(QPen(QColor(annotation.color), 3))
                painter.drawLine(marker_x, timeline_y - 5, marker_x, timeline_y + 5)
        
        painter.end()