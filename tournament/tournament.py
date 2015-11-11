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
    query = """ SELECT * FROM player_standings """
    c.execute(query)
    players = c.fetchall()
    db.close()

    return players


def reportMatch(player_one, player_two=None, outcome='win'):
    """Records the outcome of a single match between two players.

    Args:
      player_one: the id number of the player one
      player_two: the id number of the player two
      outcome: the outcome of the match (win or draw)

    If the outcome is a draw neither player_one nor player_two
    have won. In case of a win, make sure that
        player_one = the winner's player id
        player_two = the loser's player id

    For a free win ('bye') supply only player_one,
    but not player_two nor outcome"""

    if player_one == player_two:
        raise Exception("""Both players have the same id.
            Please provide two different players""")

    db = connect()
    c = db.cursor()
    if player_two is None:
        # Free win situation, no loser
        query = """ INSERT INTO matches (player_one, match_outcome)
                    VALUES (%s, 'win'); """
        c.execute(query, (player_one, ))

        # Mark player as free win receiver
        query_assign_bye = """ UPDATE players
                               SET free_win = true
                               WHERE players.id = %s """
        c.execute(query_assign_bye, (player_one, ))
    else:
        # Regular match outcome, two players, either win or loss.
        query = """ INSERT INTO matches (player_one, player_two, match_outcome)
                VALUES (%s, %s, %s); """
        c.execute(query, (player_one, player_two, outcome))

    db.commit()
    db.close()


def getRandomPlayer():
    """Returns a randomly chosen player's id
    of a player who hasn't received a free win ('bye') yet"""
    db = connect()
    c = db.cursor()
    query = """ SELECT id
                FROM players
                WHERE free_win = false
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

    If an uneven number of players registered, a random player will be
    assigned a free win ('bye')

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db = connect()
    c = db.cursor()

    # Check to see if even or uneven number of players exist
    if countPlayers() % 2 == 1:
        # Uneven number of players, choose random player for free win ('bye')
        logging.debug("Uneven number of players")
        logging.debug("Choose random player for free win ('bye')")
        logging.debug("Selecting random player from database")
        random_player = getRandomPlayer()

        # Give randomly chosen player the free win ('bye')
        logging.debug("Random player id: " + str(random_player))
        logging.debug("Giving selected random player a free win ('bye')")
        reportMatch(random_player)

        # Get players excl. free win ('bye') player ordered by player wins
        logging.debug("Get players excl. free win ('bye') player")
        query = """ SELECT id, name FROM player_standings
                    WHERE player_standings.id != %s """
        c.execute(query, (random_player, ))
        players = c.fetchall()

    else:
        # Even number of players, getting players
        logging.debug("Even number of players, getting players")
        db = connect()
        c = db.cursor()
        query = """SELECT id, name FROM player_standings;"""
        c.execute(query)
        players = c.fetchall()

    db.close

    # Create Swiss pairs
    logging.debug("Creating Swiss pairs")
    pairs = list()
    for i in range(0, len(players), 2):
        pairs.append((players[i][0], players[i][1],
                      players[i+1][0], players[i+1][1]))

    return pairs


def selectByePlayers():
    """Returns a list of players who have received a free win ('bye') """
    db = connect()
    c = db.cursor()

    query = """ SELECT id, name, free_win
                FROM players
                WHERE free_win = true; """
    c.execute(query)
    result = c.fetchall()

    db.close

    return result
