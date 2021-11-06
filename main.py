import os
from datetime import datetime
import threading
import schedule
import time
from pytz import timezone, utc
from discord.ext import commands
import sqlite3
from sqlite3 import Error
from discord import Game
from discord import Embed
import calendar



conn = None

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
    date = datetime.now(tz=utc)
    pstDateTime = date.astimezone(timezone('US/Pacific'))
    return pstDateTime


result = get_pst_time()
print(result)

print(result.strftime(""))

sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS dates (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    member_id integer NOT NULL,
                                    date text NOT NULL,
                                    wished text NOT NULL
                                );"""


def create_connection():
    try:
        c = sqlite3.connect(r"database.db")
        print(sqlite3.version)
        return c
    except Error as e:
        print(e)


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_date(conn, date):
    sql = ''' INSERT INTO dates(name,member_id,date,wished)
              VALUES(?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, date)
    conn.commit()
    return cur.lastrowid


def create_data(conn, date):
    sql = ''' INSERT INTO dates(name,member_id,date,wished)
              VALUES(?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, date)
    conn.commit()
    return cur.lastrowid


def select_all_date(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM dates ORDER BY date(date) ASC")

    rows = cur.fetchall()

    # for row in rows:
    #     print(row)
    return rows


def delete_all_date(conn):
    sql = 'DELETE FROM dates'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def update_date(conn, task):
    sql = ''' UPDATE dates
              SET date = ? 
              WHERE member_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

def delete_date(conn, task):
    sql = ''' DELETE FROM dates
              WHERE member_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

def update_wished(conn, task):
    sql = ''' UPDATE dates
              SET wished = ? 
              WHERE member_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

print('\n')


def get_ids():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT member_id FROM dates ORDER BY date(date) ASC")
    rows = cur.fetchall()

    ids = []

    for row in rows:
        for one in row:
            ids.append(one)

    return ids


def getupcoming():
    conn = create_connection()
    result = get_pst_time()
    entries = select_all_date(conn)
    print(entries)
    i = 0
    upcoming = []
    for entry in entries:
        if (i == 15):
            return upcoming
        date_time_obj = datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S')
        day = result.strftime('%d')
        month = result.strftime('%m')
        if (month == date_time_obj.strftime('%m')):
            if (day <= date_time_obj.strftime('%d')):
                x = [date_time_obj.strftime('%d'), month, entry[1]]
                upcoming.append(x)
                i=+1
    return upcoming


bot = commands.Bot(command_prefix='bb.')


@bot.command(name='set', help='set your birthday')
async def setBirthdaycommand(ctx, month: str, date: int):
    conn = create_connection()
    month = month.lower()
    create_table(conn, sql_create_tasks_table)
    author = str(ctx.author)
    id = ctx.author.id
    date_now = datetime.now()
    try:
        x = str(datetime(int(date_now.strftime('%Y')), months[month], int(date)))
    except ValueError:
        await ctx.send('Error in parsing date. Check the entered values.')
        return
    if id in get_ids():
        update_date(conn, (x, id))
        await ctx.send('Ok <@' + str(id) + '>! entry updated.')
    else:
        newdate = (author, id, x,"false")
        create_date(conn, newdate)
        await ctx.send('Ok <@' + str(id) + '>! entry added.')
    select_all_date(conn)


@bot.command(name="when" , help="get birthday of a user")
async def getBirthday(ctx,id: str):
    id = id[3:][:-1]
    conn = create_connection()
    entries = select_all_date(conn)
    for entry in entries:
        print(type(entry[2]))
        print(entry)
        date_time_obj = datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S')
        day = date_time_obj.strftime('%d')
        month = date_time_obj.strftime('%b')
        if str(entry[2])==id:
            desc = "`" + entry[1] + "`: " + month + "-" + day
            await ctx.send(embed=Embed(description=desc))
            conn.close()
            return

@bot.command(name="delete" , help="delete a birthday of a user")
async def deleteBirthday(ctx):
    conn = create_connection()
    entries = select_all_date(conn)
    print(type(ctx.author.id))
    for entry in entries:
        if entry[2]==ctx.author.id:
            delete_date(conn ,(ctx.author.id,))
            await ctx.send("Deleted!")

@bot.command(name='upcoming', help="get upcoming birthdays")
async def getupcomingcommand(ctx):
    str1 = ""
    upcoming = (getupcoming())
    for i in upcoming:
        x = "● `{}-{}`:  {}\n".format(calendar.month_abbr[int(i[1])], i[0], i[2])
        str1 += x
    await ctx.send("Upcoming birthdays:", embed=Embed(description=str1))


def checkAllBds():
    result = get_pst_time()
    conn = create_connection()
    entries = select_all_date(conn)
    for entry in entries:
        date_time_obj = datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S')
        day = result.strftime('%d')
        month = result.strftime('%m')
        if (entry[4] == "false"):
            if (month == date_time_obj.strftime('%m')):
                if (day == date_time_obj.strftime('%d')):
                    print("in")
                    channel = bot.get_channel("")
                    bot.loop.create_task(channel.send(embed=Embed(description="Happy birthday <@{}>! :cake:".format(entry[2]), color=0xdd4444)))
                    update_wished(conn, ("true", entry[2]))
    conn.close()

def settonotwished():
    result = get_pst_time()
    day = result.strftime('%d')
    month = result.strftime('%m')
    if (day == 1 and month == 1):
        conn = create_connection()
        entries = select_all_date(conn)
        for entry in entries:
            update_wished(conn, ("false", entry[2]))
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
def checkForBirthday():
    schedule.every().hour.do(checkAllBds)
    schedule.every().day.at("00:00").do(settonotwished)

    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name="bb.help"))

checkForBirthday()
bot.run(TOKEN)
