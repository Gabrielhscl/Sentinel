import os
import cv2
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from app.models.database_models import Base, CameraDB, EventDB, LogEntryDB
class DatabaseService:
    def __init__(self, db_path="sentinel_data.db"):
        # 1. Configura a Engine do SQLAlchemy
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        
        # 2. Cria as tabelas se elas não existirem
        Base.metadata.create_all(self.engine)
        
        # 3. Cria a fábrica de sessões
        self.Session = sessionmaker(bind=self.engine)
        
        # 4. Garante que as pastas de evidências físicas existem no disco
        self.storage_path = os.path.join(os.getcwd(), "storage", "evidences")
        os.makedirs(os.path.join(self.storage_path, "photos"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "videos"), exist_ok=True)

    def _get_or_create_camera(self, session, slot_id: int) -> CameraDB:
        """Busca a câmera no banco ou cria se não existir."""
        cam = session.query(CameraDB).filter(CameraDB.slot_id == slot_id).first()
        if not cam:
            cam = CameraDB(slot_id=slot_id, nome=f"Canal {slot_id}")
            session.add(cam)
            session.commit()
        return cam

    def registrar_evento(self, slot_id: int, tipo_alvo: str, frame_numpy=None) -> EventDB:
        """
        Salva a imagem no disco e cria o registro estruturado no banco.
        """
        session = self.Session()
        try:
            cam = self._get_or_create_camera(session, slot_id)
            caminho_foto_final = None

            # Em vez de salvar BLOB no banco, salvamos no HD e guardamos o caminho
            if frame_numpy is not None:
                nome_arquivo = f"cam_{slot_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                caminho_foto_final = os.path.join("storage", "evidences", "photos", nome_arquivo)
                caminho_absoluto = os.path.join(self.storage_path, "photos", nome_arquivo)
                
                # Salva o arquivo fisicamente
                cv2.imwrite(caminho_absoluto, frame_numpy)

            # Cria o objeto usando o Modelo estruturado
            novo_evento = EventDB(
                camera_id=cam.id,
                tipo_alvo=tipo_alvo,
                timestamp=datetime.now(),
                caminho_foto=caminho_foto_final
            )
            
            session.add(novo_evento)
            session.commit()
            
            return novo_evento
            
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao salvar no banco: {e}")
            return None
        finally:
            session.close()

    # =========================================================================
    # CORREÇÃO AQUI: Restaurado o nome antigo (get_recent_events) que a UI espera
    # =========================================================================
    def get_recent_events(self, limit: int = 50):
        """Busca os eventos no banco usando o ORM e ordenação otimizada."""
        session = self.Session()
        try:
            # CORREÇÃO: Usa o joinedload para carregar a câmera ANTES de fechar a sessão
            eventos = session.query(EventDB).options(
                joinedload(EventDB.camera)
            ).order_by(EventDB.timestamp.desc()).limit(limit).all()
            
            return eventos
        finally:
            session.close()
            
    def salvar_nota_log(self, mensagem, categoria="Geral"):
        session = self.Session()
        try:
            nova_nota = LogEntryDB(mensagem=mensagem, categoria=categoria)
            session.add(nova_nota)
            session.commit()
            return nova_nota
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao salvar log: {e}")
        finally:
            session.close()

    def get_all_logs(self, limit=100):
        session = self.Session()
        try:
            return session.query(LogEntryDB).order_by(LogEntryDB.timestamp.desc()).limit(limit).all()
        finally:
            session.close()
            

    def editar_nota_log(self, log_id: int, nova_mensagem: str, nova_categoria: str):
        session = self.Session()
        try:
            log = session.query(LogEntryDB).filter_by(id=log_id).first()
            if log:
                log.mensagem = nova_mensagem
                log.categoria = nova_categoria
                session.commit()
                return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao editar log: {e}")
        finally:
            session.close()
        return False

    def apagar_nota_log(self, log_id: int):
        session = self.Session()
        try:
            log = session.query(LogEntryDB).filter_by(id=log_id).first()
            if log:
                session.delete(log)
                session.commit()
                return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao apagar log: {e}")
        finally:
            session.close()
        return False