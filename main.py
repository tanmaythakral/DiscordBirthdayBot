import os
import discord
from datetime import datetime
import threading
import schedule
import time
import asyncio
from pytz import timezone, utc
from discord.ext import tasks, commands
import sqlite3
from sqlite3 import Error
from dhooks import Webhook

conn = None
hook = Webhook(
    "https://discord.com/api/webhooks/905344366502105088/19IIPjnyk3HT_xOTc8VHGvQV5SB7wfRVAgVmR-XjF-2w7baVNx3CiD9p08g0TAAAKAVX")
TOKEN = os.environ['TOKEN']
GUILD = 'Bot Testing Server'

months = {
    "jan": 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}


def get_pst_time():
    date_format = '%m_%d_%Y_%H_%M_%S_%Z'
    date = datetime.now(tz=utc)
    pstDateTime = date.astimezone(timezone('US/Pacific'))
    return pstDateTime


result = get_pst_time()
print(result)
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
    return rows


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

conn = create_connection()
print('\n')


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


def getupcoming():
    entries = select_all_date(conn)
    i = 0
    upcoming = []
    for entry in entries:
        date_time_obj = datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S')
        day = result.strftime('%d')
        month = result.strftime('%m')
        if (month == date_time_obj.strftime('%m')):
            if (day <= date_time_obj.strftime('%d')):
                x = [day, month, entry[1]]
                upcoming.append(x)
    return upcoming


bot = commands.Bot(command_prefix='!bb-')


@bot.command(name='set', help='set your birthday')
async def setBirthdaycommand(ctx, month: str, date: int):
    

    month = month.lower()
    await ctx.send('hello!')
    await ctx.send(ctx.author.id)
    create_table(conn, sql_create_tasks_table)
    author = str(ctx.author)
    id = ctx.author.id
    date_now = datetime.now()
    try:
        x = str(datetime(int(date_now.strftime('%Y')), months[month], int(date)))
    except ValueError:
        await ctx.send('Error in parsing date. Check the entered values.')
        return
    print(x)
    if id in get_ids():
        update_date(conn, (x, id))
        await ctx.send('Ok ' + author + '! entry updated.')
    else:
        newdate = (author, id, x)
        create_date(conn, newdate)
        await ctx.send('Ok ' + author + '! entry added.')
    select_all_date(conn)


@bot.command(name='upcoming', help="get upcoming birthdays")
async def getupcomingcommand(ctx):
    upcoming = (getupcoming())
    print(upcoming)
    channel = bot.get_channel(id=905310969205514283)
    await channel.send("hello")
    await ctx.send(upcoming)


def checkAllBds():
    conn = create_connection()
    entries = select_all_date(conn)
    for entry in entries:
        date_time_obj = datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S')
        day = result.strftime('%d')
        month = result.strftime('%m')
        if (month == date_time_obj.strftime('%m')):
            if (day == date_time_obj.strftime('%d')):
                hook.send("Happy Birthday <@{}>".format(entry[2]))
    conn.close()


def background(f):
    '''
    a threading decorator
    use @background above the function you want to run in the background
    '''

    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()

    return backgrnd_func


@background
def doStuff():
    schedule.every(10).seconds.do(checkAllBds)

    while True:
        schedule.run_pending()
        time.sleep(.001)


doStuff()
# hook.send("hello <@531484670114791435>")
bot.run(TOKEN)




