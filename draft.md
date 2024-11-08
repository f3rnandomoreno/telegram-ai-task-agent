**Agente de Tareas IA para Telegram**

**Descripción General**

Esta aplicación es un bot de Telegram que actúa como un gestor de tareas inteligente, permitiendo a los usuarios crear, asignar y gestionar tareas mediante lenguaje natural. El bot utiliza inteligencia artificial para interpretar los comandos de los usuarios y convertirlos en operaciones sobre una base de datos. Utiliza gpt-4o-mini como modelo.

**Funcionalidades Principales**

1. **Gestión de Tareas**

   - Crear nuevas tareas
   - Asignar tareas a usuarios
   - Modificar el estado de las tareas
   - Eliminar tareas
   - Consultar tareas existentes

2. **Estados de Tareas**

   Las tareas pueden estar en los siguientes estados:

   - Pendiente (TODO)
   - Bloqueada (BLOCKED)
   - En Progreso (IN_PROGRESS)
   - Completada (DONE)

3. **Interacción mediante Lenguaje Natural**

   Los usuarios pueden interactuar con el bot usando comandos en lenguaje natural como:

   - "Crea una tarea de hacer la compra"
   - "Ver todas las tareas"
   - "Asigname la tarea 6"
   - "Asigna la tarea 6 a Fernando"
   - "Pon la tarea 3 en progreso"
   - "Elimina la tarea 3"

**Arquitectura**

**Base de Datos**

La aplicación utiliza dos tablas principales:

- **tasks**: Almacena las tareas con sus propiedades

  - id
  - description
  - assignee
  - status
  - created_at
  - updated_at

- **users**: Almacena información de los usuarios
  - id
  - email
  - userId
  - chatId
  - userName
  - firstName
  - lastName
  - created_at
  - updated_at

**Componentes Principales**

1. **Agentes IA**

   - **NL2SQLAgent**: Convierte el lenguaje natural a consultas SQL
   - **ManagerAgent**: Gestiona las respuestas y la interacción con el usuario

2. **Servicios**
   - **MessageService**: Maneja el envío de mensajes a través de Telegram
   - **TaskService**: Gestiona las operaciones con tareas
   - **WelcomeService**: Maneja los mensajes de bienvenida

**Sistema de Prompts**

1. **Prompt NL2SQL**

   Este prompt es crucial para la conversión de lenguaje natural a SQL. Sus características principales son:

   - Interpreta instrucciones en lenguaje natural
   - Genera consultas SQL válidas y seguras
   - Maneja la creación de tareas sin asignación por defecto
   - Permite modificaciones de tareas independientemente del asignado
   - Previene inyecciones SQL

2. **Prompt del Manager**

   Este prompt gestiona la forma en que el bot responde a los usuarios:

   - Personaliza las respuestas usando el nombre del usuario
   - Formatea las tareas de manera consistente:

     _Tarea [ID]_: [Descripción] - _[Estado]_ - _[Asignada a]_ - _Actualizado el [Fecha]_

   - Traduce los estados a español (TODO → Pendiente, etc.)
   - Incluye fechas de actualización cuando están disponibles
   - Enriquece las respuestas con emojis

**Características Especiales**

- No mantiene memoria de chat (stateless)
- Soporta formato MarkdownV2 para mensajes
- Manejo de caracteres especiales en mensajes
- Inicialización automática de variables de entorno (.env)

**Limitaciones**

- No hay memoria de conversación entre mensajes
- Las tareas solo pueden tener un estado a la vez
- No hay sistema de prioridades para las tareas

**Seguridad**

**Validación de Usuarios**

- Sistema de autenticación basado en el repositorio UserRepository
- Validación de usuarios mediante:
  - ID único de Telegram (userId)
  - Email registrado en la base de datos
  - ChatId específico de la conversación
- Solo los usuarios registrados en la base de datos pueden interactuar con el bot
- La tabla users mantiene la correlación entre los datos de Telegram y los usuarios autorizados

**Protección de Datos**

- Prevención de inyección SQL mediante el uso de JdbcTemplate y consultas parametrizadas
- Manejo seguro de credenciales mediante variables de entorno (.env)
- Validación de entrada de usuarios antes de procesar cualquier comando
- Uso de tipos de datos específicos y restricciones a nivel de base de datos (unique constraints)

**Restricciones de Acceso**

- Los usuarios solo pueden ver y gestionar tareas si están registrados
- La modificación de tareas requiere que el usuario esté autenticado
- Cada operación verifica los permisos del usuario antes de ejecutarse

** Implementations hints **

- natural language to sql
  from langchain import OpenAI
  from langchain.chains import SQLDatabaseChain
  from langchain.sql_database import SQLDatabase

# Configura el modelo de lenguaje

llm = OpenAI(temperature=0)

# Conecta a la base de datos

db = SQLDatabase.from_uri("sqlite:///path_to_your_db.db")

# Crea la cadena de base de datos SQL

db_chain = SQLDatabaseChain(llm=llm, database=db)

# Ejecuta una consulta en lenguaje natural

db_chain.run("Muestra todas las entradas en la tabla de empleados.")
