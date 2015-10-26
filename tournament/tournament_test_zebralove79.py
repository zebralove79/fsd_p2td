from tournament import *
import string
import random
import time                                                

#deleteMatches()
#deletePlayers()

#http://www.laurivan.com/braindump-use-a-decorator-to-time-your-python-function/
def timeit(method):
 
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
 
        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result
 
    return timed


@timeit
def createBulkPlayers():
	N = 10
	for index in range(0,100):
		# http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
		name = ''.join(random.choice(string.ascii_uppercase) for _ in range(N))
		# print name
		registerPlayer(name)


@timeit
def getPairs():
	return swissPairings()
	#for entry in swissPairings():
	#	reportMatch(entry[0], entry[2])

# getPairs()

#for each entry in getAllPlayerWins():
#	print entry

@timeit
def getPairs2():
	db = connect()
	c = db.cursor()
	query = """SELECT player_wins.id, players.name
				FROM player_wins, players where player_wins.id = players.id"""
	c.execute(query)
	players = c.fetchall()
	pairs = list()#
	print len(players)
	for player in range(0,countPlayers(),2):
		pairs.append((players[player][0],
			players[player][1],
			players[player+1][0],
			players[player+1][1]))

	#print pairs
	return pairs

#createBulkPlayers()
#print "SQL Pairing: "
#getPairs()
#print "Python Pariring: "
#getPairs2()

print swissPairings()