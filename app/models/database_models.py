from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Base para todos os modelos do banco
Base = declarative_base()

class CameraDB(Base):
    __tablename__ = 'cameras'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    slot_id = Column(Integer, unique=True, index=True, nullable=False)
    nome = Column(String(100), default="Câmera Desconhecida")
    ativa = Column(Boolean, default=True)
    
    # Normalização: Uma câmera tem vários eventos
    eventos = relationship("EventDB", back_populates="camera", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CameraDB(slot={self.slot_id}, nome='{self.nome}')>"

class EventDB(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Relacionamento com a tabela de câmeras
    camera_id = Column(Integer, ForeignKey('cameras.id'), nullable=False, index=True)
    
    # Datas reais (não mais strings) com índice de busca
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    # O que causou o evento (ex: "Pessoa", "Veículo", "Movimento")
    tipo_alvo = Column(String(50), index=True)
    
    # NUNCA MAIS BLOB: Armazenamos apenas os caminhos rápidos no disco
    caminho_foto = Column(String(500), nullable=True)
    caminho_video = Column(String(500), nullable=True)
    
    # Relacionamento inverso
    camera = relationship("CameraDB", back_populates="eventos")

    def __repr__(self):
        return f"<EventDB(tipo='{self.tipo_alvo}', hora='{self.timestamp}')>"

class LogEntryDB(Base):
    __tablename__ = 'log_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    operador = Column(String(100), default="Gabriel Henrique") # Nome padrão do utilizador
    mensagem = Column(String(1000), nullable=False)
    categoria = Column(String(50), default="Geral") # Ex: "Troca de Turno", "Incidente", "Manutenção"

    def __repr__(self):
        return f"<LogEntry(operador='{self.operador}', msg='{self.mensagem[:20]}...')>"