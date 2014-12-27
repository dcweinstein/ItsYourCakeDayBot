import praw
import sqlite3
import urllib
import re
import botInfo

#### FINAL VARIABLES ####

USERAGENT = "/u/dvdwnstn Cakeday fetcher bot"
# Bot login information
USERNAME = botInfo.gU
PASSWORD = botInfo.gP
# Subreddit to fetch comment author information from
SUBREDDIT = "all"
# Comments fetched when looking to get author information
MAXPOSTS = 100


# Creates databse if not already created and connects
print("Opening Database")
sql = sqlite3.connect("sql.db")
cur = sql.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS cakedays(author TEXT, cakeday TEXT, year INTEGER, messaged INTEGER)")
sql.commit()

# Logs into reddit as bot 
print("Logging in to Reddit as " + USERNAME)
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)

# Fetchs newest comments in SUBREDDIT and pulls author for each comment
def fetchAuthors():
	subreddit = r.get_subreddit(SUBREDDIT)
	comments = subreddit.get_comments(limit=MAXPOSTS)
	for comment in comments:
		try:
			cAuthor = comment.author.name
			checkAuthor(cAuthor)
		except AttributeError:
			pass

# Checks if author's cakeday is already stored in the DB
def checkAuthor(author):
	cur.execute("SELECT * FROM cakedays WHERE author=?", [author])
	if not cur.fetchone():
		getCakeDay(author)

# Get's cakeday for author by requesting 'www.reddit.com/u/*author*'
def getCakeDay(author):
	# Regex for time tag html that contains the cakeday information
	# This tag is more regular than the regex suggests, but there
	# is only one time tag on the page so this will suffice
	timeTag = re.compile('<time title=.{0,31} datetime=.{0,27}')
	# Request user page for author
	sock = urllib.urlopen("http://www.reddit.com/u/" + author)
	cakedayTag = timeTag.findall(sock.read())
	sock.close()

	# Splits whole tag at datetime and stores the section containing
	# the date in cakeday
	if len(cakedayTag) > 0:
		cakeday = cakedayTag[0].split('datetime=')[1]
		storeUser(author, cakeday)	

# Adds users cakeday to DB and sets messaged to zero 
# (The message attribute is changed on the user's cakeday
# once a message has been sent to the user and reset at the
# end of the day or bot's run cycle)
def storeUser(author, date):
	year = int(date[1:5]) 
	month = date[6:8]
	day = date[9:11]
	cakeday = month + '-' + day

	print("Storing user " + author + "'s cakeday into DB")
	try:
		cur.execute("INSERT INTO cakedays(author, cakeday, year, messaged) VALUES(?, ?, ?, ?)", (author, cakeday, year, 0))
		sql.commit()
	except sqlite3.Error, e:
		print "Error %s:" % e.args[0]

while True:
	fetchAuthors()


