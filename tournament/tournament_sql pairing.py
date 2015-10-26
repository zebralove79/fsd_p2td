#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
import logging
import psycopg2

logging.basicConfig(level=logging.DEBUG,
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
    query = """ SELECT count(*) AS num
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
    results = c.fetchall()
    db.close()

    return results


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


def selectRandomPlayer():
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


def swissPairings(pairing='Python'):
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

        # Selecting random player from database
        logging.debug("Selecting random player from database")
        random_player = getRandomPlayer()
        logging.debug("Random player id: " + str(player))

        # Giving selected random player a free win ('bye')
        logging.debug("Giving selected random player a free win ('bye')")
        reportMatch(random_player)

        # Get swiss pairings excl. free win ('bye') player
        logging.debug("Get swiss pairings excl. free win ('bye') player")
        if pairing == 'SQL':
            query = """ SELECT odd.id, odd.name, even.id, even.name
                        FROM (
                            SELECT players.id, players.name,
                                   row_number() OVER () AS row
                            FROM (
                                SELECT id, row_number() OVER () AS row
                                FROM player_wins
                                WHERE id != %s)
                                AS even_table, players
                            WHERE mod(even_table.row,2) = 0
                                  and even_table.id = players.id)
                            AS even
                        INNER JOIN (
                            SELECT players.id, players.name,
                                   row_number() OVER () AS row
                            FROM (
                                SELECT id, row_number() OVER ()
                                AS row
                                FROM player_wins
                                WHERE id != %s)
                                AS odd_table, players
                            WHERE mod(odd_table.row,2) = 1
                                  and odd_table.id = players.id)
                            AS odd
                        ON odd.row = even.row; """
            c.execute(query, (random_player_id, random_player_id))

        else:
            query = """ SELECT player_wins.id, players.name
                        FROM player_wins, players 
                        WHERE player_wins.id = players.id 
                              and player_id != %s """
            c.execute(query, (random_player_id))

        result = c.fetchall()

        # Commit changes (free win) to database,
        # after swiss pairing was successful
        logging.debug("Commit free win ('bye') to database")
        db.commit()

    else:
        # Even number of players, getting swiss pairs
        logging.debug("Even number of players, getting swiss pairs")
        db = connect()
        c = db.cursor()
        query = """ SELECT odd.id, odd.name, even.id, even.name
                    FROM (
                        SELECT players.id, players.name,
                               row_number() OVER () AS row
                        FROM (
                            SELECT id, row_number() OVER () AS row
                            FROM player_wins)
                            AS even_table, players
                        WHERE mod(even_table.row,2) = 0
                              and even_table.id = players.id)
                        AS even
                    INNER JOIN (
                        SELECT players.id, players.name,
                               row_number() OVER () AS row
                        FROM (
                            SELECT id, row_number() OVER () AS row
                            FROM player_wins)
                            AS odd_table, players
                        WHERE mod(odd_table.row,2) = 1
                              and odd_table.id = players.id)
                        AS odd
                    ON odd.row = even.row;"""
        c.execute(query)
        result = c.fetchall()

    # Return swiss pairing results
    db.close
    return result
