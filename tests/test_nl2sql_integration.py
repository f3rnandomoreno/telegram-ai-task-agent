import pytest
import asyncio
from agents.nl2sql_agent import NL2SQLAgent
from utils.database import Database, Base
from models.task import Task
from models.user import User
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from sqlalchemy import inspect

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def test_db():
    """Configura la base de datos de prueba en memoria"""
    logger.info("Iniciando configuración de base de datos de prueba")
    
    # Usa una base de datos SQLite en memoria
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    logger.debug(f"DATABASE_URL configurada como: {os.environ['DATABASE_URL']}")
    
    # Crear el motor de base de datos
    engine = create_engine('sqlite:///:memory:', echo=True)  # echo=True para ver las consultas SQL
    
    # Asegurarse de que todas las tablas estén registradas antes de crearlas
    from models.user import User  # Asegurarse de importar todos los modelos
    from models.task import Task
    
    # Crear todas las tablas
    logger.info("Creando tablas en la base de datos")
    Base.metadata.drop_all(engine)  # Limpiar tablas existentes
    Base.metadata.create_all(engine)
    
    # Verificar tablas creadas y sus columnas
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        logger.info(f"Tabla {table} creada con columnas: {columns}")
    
    # Crear la sesión
    SessionLocal = sessionmaker(bind=engine)
    
    # Crear una instancia de Database con el motor de prueba
    db = Database(engine=engine, session_maker=SessionLocal)

    
    logger.info("Configuración de base de datos completada")
    return db

@pytest.fixture(autouse=True)
def setup_teardown(test_db):
    """Configura los datos antes de cada prueba y limpia después"""
    logger.info("Iniciando setup de datos de prueba")
    session = test_db.get_session()
    
    try:
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
        logger.debug("Usuario de prueba creado")
        
        # Crear tareas de prueba
        tasks = [
            Task(description="Comprar leche", status="TODO"),
            Task(description="Llamar al médico", status="IN_PROGRESS"),
            Task(description="Enviar informe", status="DONE")
        ]
        session.add_all(tasks)
        session.commit()
        logger.debug("Tareas de prueba creadas")
        
        # Verificar datos insertados
        users_count = session.query(User).count()
        tasks_count = session.query(Task).count()
        logger.info(f"Datos iniciales: {users_count} usuarios, {tasks_count} tareas")
        
        yield
        
        # Limpiar después de cada prueba
        logger.info("Limpiando datos de prueba")
        session.query(Task).delete()
        session.query(User).delete()
        session.commit()
        
        # Verificar limpieza
        users_count = session.query(User).count()
        tasks_count = session.query(Task).count()
        logger.info(f"Después de limpieza: {users_count} usuarios, {tasks_count} tareas")
        
    except Exception as e:
        logger.error(f"Error en setup/teardown: {str(e)}")
        raise
    finally:
        session.close()
        logger.debug("Sesión cerrada")

class TestNL2SQLIntegration:
    @pytest.fixture(autouse=True)
    def setup(self, test_db):
        logger.info("Iniciando setup de prueba individual")
        self.db = test_db
        self.agent = NL2SQLAgent(database=test_db)
        logger.debug("Agente NL2SQL creado")

    @pytest.mark.asyncio
    async def test_create_task(self):
        """Prueba la creación de una nueva tarea a través del lenguaje natural"""
        logger.info("Iniciando test_create_task")
        query = "Crea una tarea de hacer la compra"
        logger.debug(f"Query: {query}")
        
        result = await self.agent.process_natural_language(query)
        logger.debug(f"Resultado: {result}")
        
        session = self.db.get_session()
        task = session.query(Task).filter(Task.description.like('%compra%')).first()
        logger.info(f"Tarea creada: {task.description if task else 'None'}")
        session.close()

        # assert that result does not contain error message
        assert "error" not in result, f"Error en resultado: {result}"
        assert task is not None, "La tarea no fue creada"
        assert task.status == "TODO", f"Estado incorrecto: {task.status}"

    @pytest.mark.asyncio
    async def test_list_tasks(self):
        """Prueba listar todas las tareas a través del lenguaje natural"""
        logger.info("Iniciando test_list_tasks")
        query = "Muestra todas las tareas"
        logger.debug(f"Query: {query}")
        
        result = await self.agent.process_natural_language(query)
        logger.debug(f"Resultado: {result}")
        
        assert "Comprar leche" in result, "Tarea 'Comprar leche' no encontrada"
        assert "Llamar al médico" in result, "Tarea 'Llamar al médico' no encontrada"
        assert "Enviar informe" in result, "Tarea 'Enviar informe' no encontrada"

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
