import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///task_manager.db')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Task States
class TaskStatus:
    TODO = 'TODO'
    BLOCKED = 'BLOCKED'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'

    @classmethod
    def to_spanish(cls, status):
        return {
            cls.TODO: 'Pendiente',
            cls.BLOCKED: 'Bloqueada',
            cls.IN_PROGRESS: 'En Progreso',
            cls.DONE: 'Completada'
        }.get(status, status) 