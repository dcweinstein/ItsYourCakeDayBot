import praw
import sqlite3
import datetime
import time
import botInfo

#### FINAL VARIABLES ####

USERAGENT = "/u/dvdwnstn Cakeday notifier bot"
# Bot login information
USERNAME = botInfo.sU
PASSWORD = botInfo.sP
# Time (in seconds) paused between messages so as to not it Reddit API's messaging limit
WAIT = 600


# Connects to database holding usernames and cakedays
print("Opening Database")
sql = sqlite3.connect("sql.db")
cur = sql.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS cakedays(author TEXT, cakeday TEXT, year INTEGER, messaged INTEGER)")
sql.commit()

# Logs into reddit as bot 
print("Logging in to Reddit as " + USERNAME)
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)

def main():
	curDay = getCurDate()
	users = getCakedayUsers(curDay)

	for user in users:
		if(user[3] == 0):
			print "It's " + user[0] + "'s cakeday! Messaging now."
			message(user[0], user[2])

	resetMessageStatuses()

# Retrieves current date 
def getCurDate():
	date = str(datetime.date.today())
	curDay = date[5:]
	return curDay

# Gets users with cakeday on given day
def getCakedayUsers(day):
	cur.execute("SELECT * FROM cakedays WHERE cakeday = ?", [day])
	users = cur.fetchall()
	return users

# Creates cakeday message reminding user it is their cakeday and attaches
# to the user's newest comment. It then marks
# that user as messaged in the database
def message(user, createdYear):
	curYear = getCurYear()
	years = curYear - createdYear
	message = "IT'S YOUR CAKEDAY!\n\n\nHappy Cakeday " + user + ".\n\nYou've been a redditor for " + str(years) + " years.\n\nI hope all of your wildest dreams come true today.\n\n\nSincerely,\n\nItsYourCakeDayBot"
	if years > 0:
		# gets user and then gets most recent comment from that user
		redditor = r.get_redditor(user)
		comments = redditor.get_comments(limit=1)
		for comment in comments:
			comment.reply(message)
			time.sleep(WAIT)

	cur.execute("UPDATE cakedays SET messaged = ? WHERE author = ?", (1, user))
	sql.commit()
# Returns current year
def getCurYear():
	date = str(datetime.date.today())
	curYear = int(date[:4])
	return curYear

# If there are users in the database that are marked as messaged, but their
# cakeday is not today this function resets the messaged column to 0.
# This would be the case the day after a person's cakeday if they were messaged
# the day before
def resetMessageStatuses():
	curDay = getCurDate()
	cur.execute("SELECT * FROM cakedays WHERE cakeday != ? AND messaged = ?", (curDay, 1))
	users = cur.fetchall()

	for user in users:
		cur.execute("UPDATE cakedays SET messaged = ? WHERE author = ?", (0, user[0]))
		sql.commit()
while True:
	main()	