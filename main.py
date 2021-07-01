import discord
import sqlite3
from sqlite3 import Error

TOKEN = 'ODU5ODM2ODUxMDk0NDIxNTQ1.YNyfeA.tXwSr7j25YVUgh0jNQdu-hAUFMY'
GUILD = 'Bot Testing Server'

sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    priority integer,
                                    status_id integer NOT NULL,
                                    project_id integer NOT NULL,
                                    begin_date text NOT NULL,
                                    end_date text NOT NULL,
                                    FOREIGN KEY (project_id) REFERENCES projects (id)
                                );"""

def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(r"database.db")
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


client = discord.Client()
conn = create_connection()

    # create tables
if conn is not None:
  # create projects table
  print("Im here")
  create_table(conn, sql_create_tasks_table)





@client.event
async def on_ready():
  for guild in client.guilds:
    if guild.name == GUILD:
      break

  print(
      f'{client.user} is connected to the following guild:\n'
      f'{guild.name}(id: {guild.id})'
    )
  members = '\n - '.join([member.name for member in guild.members])
  print(f'Guild Members:\n - {members}')
  print('Pow Pow! We on!')

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  if message.content.startswith('-hola'):
    await message.channel.send('hello!')

client.run(TOKEN)