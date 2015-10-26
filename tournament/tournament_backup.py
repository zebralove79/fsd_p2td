#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
import logging
import psycopg2


# Set logging level 
# to logging.DEBUG during debugging,
# to logging.ERROR in production.
logging.basicConfig(level=logging.ERROR,
                    format=' %(asctime)s - %(levelname)s - %(message)s')


def connect():
    """Connect to the PostgreSQL database.
       Returns a database connection."""

    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    query = "DELETE FROM matches;"
    c.execute(query)
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    query = "DELETE FROM players;"
    c.execute(query)
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    query = """ SELECT count(players.id) AS num
                FROM players; """
    c.execute(query)
    count = c.fetchone()[0]
    db.close()

    return count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player. (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    query = "INSERT INTO players (name) VALUES (%s)"
    c.execute(query, (name,))
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    query = """ SELECT players.id, players.name, wins, matches
                FROM players, player_matches, player_wins
                WHERE player_matches.id = player_wins.id
                      and players.id = player_matches.id
                ORDER BY wins DESC; """
    c.execute(query)
    players = c.fetchall()
    db.close()

    return players


def reportMatch(winner, loser=None, outcome='win'):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      outcome: the outcome of the match (win or draw)
    """
    if winner == loser:
        raise Exception("""Winner and loser have same id.
            Winner must be a different player (id) than loser""")

    db = connect()
    c = db.cursor()
    if loser is None:
        query = """ INSERT INTO matches (player_one, match_outcome)
                VALUES (%s, %s); """
        c.execute(query, (winner, outcome))
    else:
        query = """ INSERT INTO matches (player_one, player_two, match_outcome)
                VALUES (%s, %s, %s); """
        c.execute(query, (winner, loser, outcome))

    db.commit()
    db.close()


def getAllPlayerWins():
    """Returns a list of tuples each of which contains (id, name, wins)
        id: the id of the player
        name: the name of the player
        wins: number of matches won by player"""
    db = connect()
    c = db.cursor()
    query = """SELECT players.id, players.name, wins
               FROM players, player_wins
               WHERE players.id = player_wins.id
               ORDER BY wins DESC;"""
    c.execute(query)
    results = c.fetchall()
    db.close()

    return results


def countMatches():
    """Returns the total number of matches played"""
    db = connect()
    c = db.cursor()
    query = 'SELECT count(id) FROM matches'
    c.execute(query)
    count = c.fetchone()[0]
    db.close

    return count


def getRandomPlayer():
    """Returns a randomly chosen player's id"""
    db = connect()
    c = db.cursor()
    query = """ SELECT id
                FROM players
                ORDER BY random()
                LIMIT 1; """
    c.execute(query)
    player = c.fetchone()[0]
    db.close

    return player


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    result = list()
    db = connect()
    c = db.cursor()

    # Check to see if even or uneven number of players exist
    if countPlayers() % 2 == 1:
        # Uneven number of players, choose random player for free win ('bye')
        logging.debug("Uneven number of players")
        logging.debug("Choose random player for free win ('bye')")

        # Give random player a free win ('bye')
        logging.debug("Selecting random player from database")
        random_player = getRandomPlayer()
        logging.debug("Random player id: " + str(random_player))
        logging.debug("Giving selected random player a free win ('bye')")
        reportMatch(random_player)

        # Get players excl. free win ('bye') player ordered by player wins
        logging.debug("Get players excl. free win ('bye') player")
        query = """ SELECT player_wins.id, players.name
                    FROM player_wins, players
                    WHERE player_wins.id = players.id
                          and players.id != %s
                    ORDER BY player_wins.wins """
        c.execute(query, (random_player, ))
        players = c.fetchall()

    else:
        # Even number of players, getting players
        logging.debug("Even number of players, getting players")
        db = connect()
        c = db.cursor()
        query = """ SELECT player_wins.id, players.name
                    FROM player_wins, players
                    WHERE player_wins.id = players.id
                    ORDER BY player_wins.wins """
        c.execute(query)
        players = c.fetchall()

    db.close

    # Create swiss pairs
    logging.debug("Creating swiss pairs")
    pairs = list()
    for i in range(0, len(players), 2):
        pairs.append((players[i][0], players[i][1],
                      players[i+1][0], players[i+1][1]))

    return pairs
