from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "lures.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Lure(Base):
    __tablename__ = "Lures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    path = Column(String, nullable=False)
    path_copy = Column(String, nullable=False)

    def __repr__(self):
        return f"<Lure(id={self.id}, filename='{self.filename}', path='{self.path}')>"

def init_database():
    Base.metadata.create_all(engine)
    os.chmod(DB_PATH, 0o600)
    print(f"✅ Table 'Lures' ready at {DB_PATH} !")

def insert_lure_in_db(filename, signature, path, path_copy):
    session = Session()
    try:
        lure = Lure(filename=filename, signature=signature, path=path, path_copy=path_copy)
        session.add(lure)
        session.commit()
        print(f"[➕] Lure inserted: {filename} at {path}")
    except Exception as e:
        session.rollback()
        print(f"[❌] Error inserting lure: {e}")
    finally:
        session.close()

def lure_exists(path):
    session = Session()
    try:
        exists = session.query(Lure).filter_by(path=path).first() is not None
        return exists
    finally:
        session.close()