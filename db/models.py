from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, DateTime, Boolean,
    ForeignKey, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid
from datetime import datetime

Base = declarative_base()

# Associação entre eventos e membros da equipe
event_team_association = Table(
    'event_team', Base.metadata,
    Column('event_id', String(36), ForeignKey('events.id')),
    Column('team_member_id', String(36), ForeignKey('team_members.id')),
    Column('role', String(100)),
    Column('assigned_at', DateTime, default=datetime.utcnow)
)

class Event(Base):
    __tablename__ = 'events'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String(255))
    client = Column(String(255))
    responsible_person = Column(String(255))
    event_type = Column(String(50))
    coverage_type = Column(String(255))
    status = Column(String(20), default='planning')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team_members = relationship("TeamMember", secondary=event_team_association, back_populates="events")
    briefing = relationship("Briefing", uselist=False, back_populates="event")
    timeline_tasks = relationship("TimelineTask", back_populates="event")
    assets = relationship("Asset", back_populates="event")
    deliveries = relationship("Delivery", back_populates="event")
    analytics = relationship("Analytics", backref="event", uselist=False)


class TeamMember(Base):
    __tablename__ = 'team_members'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    expertise = Column(String(100))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    photo_url = Column(String(255))
    notes = Column(Text)
    availability_status = Column(String(20), default='available')
    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship("Event", secondary=event_team_association, back_populates="team_members")
    timeline_tasks = relationship("TimelineTask", back_populates="assigned_to")
    assets_created = relationship("Asset", back_populates="created_by")
    deliveries_created = relationship("Delivery", back_populates="created_by")


class Briefing(Base):
    __tablename__ = 'briefings'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    general_info = Column(Text)
    schedule_info = Column(Text)
    sponsor_activations = Column(Text)
    deliverables = Column(Text)
    creative_guidelines = Column(Text)
    reference_files = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event = relationship("Event", back_populates="briefing")


class TimelineTask(Base):
    __tablename__ = 'timeline_tasks'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    assigned_to_id = Column(String(36), ForeignKey('team_members.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    location = Column(String(255))
    priority = Column(String(20), default='normal')
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event = relationship("Event", back_populates="timeline_tasks")
    assigned_to = relationship("TeamMember", back_populates="timeline_tasks")
    assets = relationship("Asset", back_populates="related_task")


class Asset(Base):
    __tablename__ = 'assets'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    created_by_id = Column(String(36), ForeignKey('team_members.id'))
    related_task_id = Column(String(36), ForeignKey('timeline_tasks.id'))
    file_path = Column(String(500), nullable=False)
    backup_path = Column(String(500))
    file_name = Column(String(255), nullable=False)
    file_size = Column(Float)
    file_type = Column(String(50))
    duration = Column(Float)
    resolution = Column(String(20))
    extra_data = Column(Text)  # substituto para 'metadata'
    status = Column(String(20), default='raw')
    ingest_time = Column(DateTime, default=datetime.utcnow)
    archived = Column(Boolean, default=False)

    event = relationship("Event", back_populates="assets")
    created_by = relationship("TeamMember", back_populates="assets_created")
    related_task = relationship("TimelineTask", back_populates="assets")
    delivery_versions = relationship("DeliveryVersion", back_populates="source_asset")


class Delivery(Base):
    __tablename__ = 'deliveries'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    created_by_id = Column(String(36), ForeignKey('team_members.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    delivery_type = Column(String(50))
    due_date = Column(DateTime)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_url = Column(String(500))

    event = relationship("Event", back_populates="deliveries")
    created_by = relationship("TeamMember", back_populates="deliveries_created")
    versions = relationship("DeliveryVersion", back_populates="delivery")


class DeliveryVersion(Base):
    __tablename__ = 'delivery_versions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    delivery_id = Column(String(36), ForeignKey('deliveries.id'), nullable=False)
    source_asset_id = Column(String(36), ForeignKey('assets.id'))
    version_number = Column(Integer, default=1)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending')
    feedback = Column(Text)
    approved_by = Column(String(255))
    approved_at = Column(DateTime)

    delivery = relationship("Delivery", back_populates="versions")
    source_asset = relationship("Asset", back_populates="delivery_versions")


class Analytics(Base):
    __tablename__ = 'analytics'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    total_assets = Column(Integer, default=0)
    total_deliveries = Column(Integer, default=0)
    avg_processing_time = Column(Float)
    first_capture_time = Column(DateTime)
    last_delivery_time = Column(DateTime)
    approval_rate = Column(Float)
    event_duration = Column(Float)
    total_team_size = Column(Integer)
    calculated_at = Column(DateTime, default=datetime.utcnow)


# Inicialização do banco de dados
def init_db(db_path='gonetwork.db'):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Sessão de uso do banco
def get_db_session(db_path='gonetwork.db'):
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()
