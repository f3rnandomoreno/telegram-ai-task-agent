from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import OpenAI
from config.settings import OPENAI_API_KEY
from utils.database import Database
from langchain.prompts import PromptTemplate

class NL2SQLAgent:
    def __init__(self, database:None):
        self.llm = OpenAI(temperature=0, api_key=OPENAI_API_KEY, model="gtp-4o-mini")
        self.db = Database()
        self.sql_database = SQLDatabase(database.engine) if database else SQLDatabase(self.db.engine)

        # Define un prompt personalizado o permite que se use el predeterminado
        prompt = PromptTemplate.from_template("Translate the following query to SQL: {query}")

        # Inicializa SQLDatabaseChain pasando el LLM, la base de datos y el prompt
        self.db_chain = SQLDatabaseChain.from_llm(
            llm=self.llm,
            db=self.sql_database,
            prompt=prompt,  # Usa el prompt personalizado, opcional
            verbose=True    # Activa modo detallado (opcional)
        )

    async def process_natural_language(self, text: str) -> str:
        try:
            result = await self.db_chain.arun(text)
            return result
        except Exception as e:
            return f"Error processing natural language: {str(e)}"
