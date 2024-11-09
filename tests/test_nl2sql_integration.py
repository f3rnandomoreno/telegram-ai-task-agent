import pytest
import asyncio
from agents.nl2sql_agent import NL2SQLAgent
from utils.database import Database, Base
from models.task import Task
from models.user import User
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def test_db():
    """Configura la base de datos de prueba en memoria"""
    # Usa una base de datos SQLite en memoria
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    # Crear el motor de base de datos
    engine = create_engine('sqlite:///:memory:', echo=False)
    
    # Crear todas las tablas
    Base.metadata.create_all(engine)
    
    # Crear la sesión
    SessionLocal = sessionmaker(bind=engine)
    
    # Crear una instancia de Database con el motor de prueba
    db = Database()
    db.engine = engine
    db.SessionLocal = SessionLocal
    
    return db

@pytest.fixture(autouse=True)
def setup_teardown(test_db):
    """Configura los datos antes de cada prueba y limpia después"""
    session = test_db.get_session()
    
    # Crear usuario de prueba
    test_user = User(
        email="test@example.com",
        userId="123456",
        chatId="789012",
        userName="testuser",
        firstName="Test",
        lastName="User"
    )
    session.add(test_user)
    
    # Crear tareas de prueba
    tasks = [
        Task(description="Comprar leche", status="TODO"),
        Task(description="Llamar al médico", status="IN_PROGRESS"),
        Task(description="Enviar informe", status="DONE")
    ]
    session.add_all(tasks)
    session.commit()
    
    yield
    
    # Limpiar después de cada prueba
    session.query(Task).delete()
    session.query(User).delete()
    session.commit()
    session.close()

class TestNL2SQLIntegration:
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        self.db = test_db
        self.agent = NL2SQLAgent()

    @pytest.mark.asyncio
    async def test_create_task(self):
        """Prueba la creación de una nueva tarea a través del lenguaje natural"""
        query = "Crea una tarea de hacer la compra"
        result = await self.agent.process_natural_language(query)
        
        session = self.db.get_session()
        task = session.query(Task).filter(Task.description.like('%compra%')).first()
        session.close()

        assert task is not None
        assert task.status == "TODO"

    @pytest.mark.asyncio
    async def test_list_tasks(self):
        """Prueba listar todas las tareas a través del lenguaje natural"""
        query = "Muestra todas las tareas"
        result = await self.agent.process_natural_language(query)
        
        assert "Comprar leche" in result
        assert "Llamar al médico" in result
        assert "Enviar informe" in result

    @pytest.mark.asyncio
    async def test_update_task_status(self):
        """Prueba actualizar el estado de una tarea a través del lenguaje natural"""
        session = self.db.get_session()
        task = session.query(Task).filter_by(description="Comprar leche").first()
        task_id = task.id
        session.close()

        query = f"Pon la tarea {task_id} en progreso"
        result = await self.agent.process_natural_language(query)

        session = self.db.get_session()
        updated_task = session.query(Task).filter_by(id=task_id).first()
        session.close()

        assert updated_task.status == "IN_PROGRESS"

    @pytest.mark.asyncio
    async def test_assign_task(self):
        """Prueba asignar una tarea a un usuario a través del lenguaje natural"""
        session = self.db.get_session()
        task = session.query(Task).filter_by(description="Comprar leche").first()
        user = session.query(User).first()
        task_id = task.id
        session.close()

        query = f"Asigna la tarea {task_id} a Test User"
        result = await self.agent.process_natural_language(query)

        session = self.db.get_session()
        updated_task = session.query(Task).filter_by(id=task_id).first()
        session.close()

        assert updated_task.assignee == user.id

    @pytest.mark.asyncio
    async def test_delete_task(self):
        """Prueba eliminar una tarea a través del lenguaje natural"""
        session = self.db.get_session()
        task = session.query(Task).filter_by(description="Comprar leche").first()
        task_id = task.id
        session.close()

        query = f"Elimina la tarea {task_id}"
        result = await self.agent.process_natural_language(query)

        session = self.db.get_session()
        session.close()
        deleted_task = session.query(Task).filter_by(id=task_id).first()

        assert deleted_task is None
