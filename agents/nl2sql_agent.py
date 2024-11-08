from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.llms import OpenAI
from config.settings import OPENAI_API_KEY
from utils.database import Database

class NL2SQLAgent:
    def __init__(self):
        self.llm = OpenAI(temperature=0, api_key=OPENAI_API_KEY)
        self.db = Database()
        self.sql_database = SQLDatabase(self.db.engine)
        self.db_chain = SQLDatabaseChain.from_llm(llm=self.llm, database=self.sql_database)

    async def process_natural_language(self, text: str) -> str:
        try:
            result = await self.db_chain.arun(text)
            return result
        except Exception as e:
            return f"Error processing natural language: {str(e)}"