import pytest
import asyncio
from agents.nl2sql_agent import NL2SQLAgent
from utils.database import Database
from models.task import Task
from models.user import User
import os

class TestNL2SQLIntegration:
    @classmethod
    def setup_class(cls):
        """Setup test database and create tables"""
        # Use a test database
        os.environ['DATABASE_URL'] = 'sqlite:///test_task_manager.db'
        cls.db = Database()
        cls.db.create_tables()
        cls.agent = NL2SQLAgent()

    def setup_method(self):
        """Setup test data before each test"""
        session = self.db.get_session()
        
        # Create test user
        test_user = User(
            email="test@example.com",
            userId="123456",
            chatId="789012",
            userName="testuser",
            firstName="Test",
            lastName="User"
        )
        session.add(test_user)
        
        # Create some test tasks
        tasks = [
            Task(description="Comprar leche", status="TODO"),
            Task(description="Llamar al médico", status="IN_PROGRESS"),
            Task(description="Enviar informe", status="DONE")
        ]
        session.add_all(tasks)
        session.commit()
        session.close()

    def teardown_method(self):
        """Clean up after each test"""
        session = self.db.get_session()
        session.query(Task).delete()
        session.query(User).delete()
        session.commit()
        session.close()

    @classmethod
    def teardown_class(cls):
        """Clean up after all tests"""
        if os.path.exists('test_task_manager.db'):
            os.remove('test_task_manager.db')

    @pytest.mark.asyncio
    async def test_create_task(self):
        """Test creating a new task through natural language"""
        query = "Crea una tarea de hacer la compra"
        result = await self.agent.process_natural_language(query)
        
        session = self.db.get_session()
        task = session.query(Task).filter(Task.description.like('%compra%')).first()
        session.close()

        assert task is not None
        assert task.status == "TODO"

    @pytest.mark.asyncio
    async def test_list_tasks(self):
        """Test listing all tasks through natural language"""
        query = "Muestra todas las tareas"
        result = await self.agent.process_natural_language(query)
        
        assert "Comprar leche" in result
        assert "Llamar al médico" in result
        assert "Enviar informe" in result

    @pytest.mark.asyncio
    async def test_update_task_status(self):
        """Test updating task status through natural language"""
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
        """Test assigning a task to a user through natural language"""
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
        """Test deleting a task through natural language"""
        session = self.db.get_session()
        task = session.query(Task).filter_by(description="Comprar leche").first()
        task_id = task.id
        session.close()

        query = f"Elimina la tarea {task_id}"
        result = await self.agent.process_natural_language(query)

        session = self.db.get_session()
        deleted_task = session.query(Task).filter_by(id=task_id).first()
        session.close()

        assert deleted_task is None 