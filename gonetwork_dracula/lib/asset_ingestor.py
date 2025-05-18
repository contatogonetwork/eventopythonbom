import os
import shutil
import time
import watchdog.events
import watchdog.observers
from datetime import datetime
from pathlib import Path
import hashlib
import threading
import logging
from db.models import Asset, get_db_session
from lib.event_context import EventContext

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ingest.log'
)
logger = logging.getLogger('AssetIngestor')

class AssetIngestor:
    """
    Sistema para monitorar uma pasta de entrada, fazer backup automático
    de arquivos e registrá-los no banco de dados.
    """
    def __init__(self, watch_dir, primary_backup_dir, secondary_backup_dir):
        self.watch_dir = Path(watch_dir)
        self.primary_backup_dir = Path(primary_backup_dir)
        self.secondary_backup_dir = Path(secondary_backup_dir)
        self.event_context = EventContext()
        self.observer = None
        self.file_handlers = []
        self.callbacks = []
        
        # Garantir que os diretórios existam
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.primary_backup_dir.mkdir(parents=True, exist_ok=True)
        self.secondary_backup_dir.mkdir(parents=True, exist_ok=True)
    
    def start_monitoring(self):
        """Inicia o monitoramento da pasta de entrada"""
        if self.observer is not None and self.observer.is_alive():
            logger.warning("Monitoramento já está ativo")
            return
        
        event_handler = AssetEventHandler(self)
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(event_handler, str(self.watch_dir), recursive=True)
        self.observer.start()
        logger.info(f"Monitoramento iniciado na pasta: {self.watch_dir}")
    
    def stop_monitoring(self):
        """Para o monitoramento da pasta de entrada"""
        if self.observer is not None and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("Monitoramento interrompido")
    
    def register_file_handler(self, handler):
        """
        Registra um manipulador para processar arquivos específicos
        O handler deve ser uma função que recebe (file_path, metadata)
        e retorna True se o arquivo foi manipulado
        """
        self.file_handlers.append(handler)
    
    def register_callback(self, callback):
        """
        Registra um callback a ser executado quando um novo arquivo for processado
        O callback deve ser uma função que recebe (file_path, asset_id)
        """
        self.callbacks.append(callback)
    
    def process_file(self, file_path):
        """
        Processa um novo arquivo encontrado
        Retorna o asset registrado no banco de dados
        """
        # Verificar se evento está selecionado
        event_id = self.event_context.event_id
        if not event_id:
            logger.error("Nenhum evento selecionado. O arquivo não será processado.")
            return None
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"Arquivo não existe: {file_path}")
            return None
        
        try:
            # Criar nomes de arquivo padronizados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = self._calculate_file_hash(file_path)[:8]
            new_filename = f"{timestamp}_{file_hash}_{file_path.name}"
            
            # Criar diretórios específicos do evento
            event_primary_dir = self.primary_backup_dir / event_id
            event_secondary_dir = self.secondary_backup_dir / event_id
            event_primary_dir.mkdir(exist_ok=True)
            event_secondary_dir.mkdir(exist_ok=True)
            
            # Caminhos para backup
            primary_dest = event_primary_dir / new_filename
            secondary_dest = event_secondary_dir / new_filename
            
            # Realizar backups
            shutil.copy2(file_path, primary_dest)
            shutil.copy2(file_path, secondary_dest)
            
            # Determinar tipo de arquivo e metadados
            file_type = self._determine_file_type(file_path)
            file_size = file_path.stat().st_size / (1024 * 1024)  # Tamanho em MB
            metadata = self._extract_metadata(file_path)
            
            # Registrar no banco de dados
            asset = self._register_in_database(
                event_id=event_id,
                file_path=str(primary_dest),
                backup_path=str(secondary_dest),
                file_name=new_filename,
                file_size=file_size,
                file_type=file_type,
                metadata=metadata
            )
            
            # Executar callbacks
            for callback in self.callbacks:
                try:
                    callback(str(primary_dest), asset.id)
                except Exception as e:
                    logger.error(f"Erro ao executar callback: {e}")
            
            logger.info(f"Arquivo processado com sucesso: {file_path} -> {new_filename}")
            return asset
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file_path}: {e}")
            return None
    
    def _calculate_file_hash(self, file_path):
        """Calcula um hash MD5 parcial do arquivo"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            # Ler apenas os primeiros 8192 bytes para velocidade
            data = f.read(8192)
            md5.update(data)
        return md5.hexdigest()
    
    def _determine_file_type(self, file_path):
        """Determina o tipo de arquivo baseado na extensão"""
        extension = file_path.suffix.lower()
        
        video_extensions = ['.mp4', '.mov', '.avi', '.mxf', '.mkv']
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.raw']
        audio_extensions = ['.mp3', '.wav', '.aac']
        
        if extension in video_extensions:
            return 'video'
        elif extension in image_extensions:
            return 'image'
        elif extension in audio_extensions:
            return 'audio'
        else:
            return 'other'
    
    def _extract_metadata(self, file_path):
        """Extrai metadados do arquivo"""
        # Na versão completa, usar ffmpeg ou outras ferramentas para extrair metadados
        # Versão simplificada:
        return "{}"
    
    def _register_in_database(self, **kwargs):
        """Registra o arquivo no banco de dados"""
        session = get_db_session()
        asset = Asset(**kwargs)
        session.add(asset)
        session.commit()
        
        # Recuperar ID
        asset_id = asset.id
        
        session.close()
        
        # Recarregar asset com ID para retornar
        session = get_db_session()
        asset = session.query(Asset).filter(Asset.id == asset_id).first()
        session.close()
        
        return asset


class AssetEventHandler(watchdog.events.FileSystemEventHandler):
    """Handler para eventos do watchdog"""
    
    def __init__(self, ingestor):
        self.ingestor = ingestor
        self.processing_files = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        # Evitar processamento duplicado
        if event.src_path in self.processing_files:
            return
        
        # Marcar como em processamento
        self.processing_files.add(event.src_path)
        
        # Processar em segundo plano após pequeno atraso para garantir conclusão da cópia
        threading.Timer(2.0, self._process_delayed, args=[event.src_path]).start()
    
    def _process_delayed(self, file_path):
        try:
            # Processar o arquivo
            self.ingestor.process_file(file_path)
        finally:
            # Remover da lista de processamento, independente do resultado
            self.processing_files.discard(file_path)


# Uso do sistema de ingestão
def setup_ingestor():
    """Configura e retorna uma instância do sistema de ingestão"""
    # Diretórios padrão
    base_dir = Path(os.path.expanduser('~')) / 'GoNetworkAI'
    watch_dir = base_dir / 'incoming'
    primary_backup_dir = base_dir / 'primary_backup'
    secondary_backup_dir = base_dir / 'secondary_backup'
    
    # Criar diretórios se não existirem
    for directory in [watch_dir, primary_backup_dir, secondary_backup_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Criar ingestor
    ingestor = AssetIngestor(
        watch_dir=watch_dir,
        primary_backup_dir=primary_backup_dir,
        secondary_backup_dir=secondary_backup_dir
    )
    
    return ingestor