import os
import discord
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time
from pytz import timezone, utc
from discord.ext import commands
import sqlite3
from sqlite3 import Error


TOKEN = os.environ['TOKEN']
GUILD = 'Bot Testing Server'

months = {
	"jan" : 1,
	'feb' : 2,
	'mar' : 3,
	'apr' : 4,
	'may' : 5,
	'jun' : 6,
	'jul' : 7,
	'aug' : 8,
	'sep' : 9,
	'oct' : 10,
	'nov' : 11,
	'dec' : 12
}


def get_pst_time():
    date_format='%m_%d_%Y_%H_%M_%S_%Z'
    date = datetime.now(tz=utc)
    pstDateTime = date.astimezone(timezone('US/Pacific'))
    return pstDateTime

result = get_pst_time()
# result = time.strftime("%H,%M,%S" , result)

print(result.strftime(""))




sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS date (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    member_id integer NOT NULL,
                                    date text NOT NULL
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

def create_date(conn, date):
    """
    Create a new date
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO date(name,member_id,date)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, date)
    conn.commit()
    return cur.lastrowid

client = discord.Client()

# @client.event
# async def sendmess():
# 	channel = client.get_channel(859836665811697676)
# 	await channel.send('hello')

def select_all_date(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM date")

    rows = cur.fetchall()

    for row in rows:
        print(row)



def delete_all_date(conn):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM date'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def update_date(conn, task):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE date
              SET date = ? 
              WHERE member_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

print('\n')
conn = create_connection()
# delete_all_date(conn)

def get_ids():
	cur = conn.cursor()
	cur.execute("SELECT member_id FROM date")
	rows = cur.fetchall()

	ids = []

	for row in rows:
		for one in row:
			ids.append(one)

	return ids


@client.event
async def on_ready():
  for guild in client.guilds:
    if guild.name == GUILD:
      break

client.run(TOKEN)

# sendmess()
bot = commands.Bot(command_prefix='!bb-')

@bot.command(name='hello' , help = 'I need some too!')
async def setBirthday(ctx , month: str , date: int) :
	month = month.lower()
	await ctx.send('hello!')
	await ctx.send(ctx.author.id)
	create_table(conn,sql_create_tasks_table)
	author = str(ctx.author)
	id  = ctx.author.id
	date_now = datetime.now()
	try:
		x = str(datetime(int(date_now.strftime('%Y')),months[month],int(date)))
	except ValueError:
		await ctx.send('Error in parsing date. Check the entered values.')
		return
	print(x)
	if id in get_ids() :
		update_date(conn , (x , id))
		await ctx.send('Ok ' + author + '! entry updated.')
	else:
		newdate = (author,id,x)
		create_date(conn,newdate)
		await ctx.send('Ok ' + author + '! entry added.')
	select_all_date(conn)


# async def notifyBirthday():
# 	channel = bot.get_channel(859836665811697676)
# 	await channel.send('hello')

# def notify():
# 	print('hello')
# 	notifyBirthday()
	
# scheduler = BackgroundScheduler()
# scheduler.add_job(notify, 'cron', second=1)
# scheduler.start()


bot.run(TOKEN)
