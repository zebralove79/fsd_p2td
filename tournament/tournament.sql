-- This file will set up a database for your Swiss-style tournament

-- How-to and important information
--   Run psql and execute this file with '\i tournament.sql'.
--   Warning: This will drop the tournament database if it already exists
--   which could cause data loss.
--   Requirements: PostgreSQL 9.3.9


-- ** Database creation **

-- Drop tournament database if it already exists
DROP DATABASE IF EXISTS tournament;

-- Create the tournament database and connect to it
CREATE DATABASE tournament;
\c tournament;


-- ** Table definitions **
-- Players
-- Create table to store players
--   id: id of player (primary key, type serial)
--	 name: name of player (type varchar(255))
CREATE TABLE players (
	id serial primary key,
	name varchar(255)
);

-- Matches
-- Create new type (enum) to describe match outcome
CREATE TYPE outcome AS ENUM ('win', 'draw');

-- Create table to store matches
--   id: id of match (primary key, type serial)
--	 player_one: id of player one (type integer, foreign key (player id))
--   player_two: id of player two (type integer, foreign key (player id))
--   match_outcome: the result of the match (type outcome)
-- If one of the players has won, set match_outcome to 'win',
-- make player_one the winner, player_two the loser.
-- In case of a tie, set match_outcome to 'draw',
-- which player is player_one, player_two is not relevant.    
CREATE TABLE matches (
	id serial primary key,
	player_one integer references players(id),
	player_two integer references players(id),
	match_outcome outcome
);


-- ** View definitions **
-- View to get the number of matches played per player
CREATE VIEW player_matches AS 
SELECT players.id, count(matches.id) AS matches 
FROM players 
LEFT JOIN matches 
ON players.id = matches.player_one 
   or players.id = matches.player_two 
GROUP BY players.id;

-- View to get the number of matches won per player
CREATE VIEW player_wins AS 
SELECT players.id, count(matches.player_one) AS wins 
FROM players 
LEFT JOIN matches 
ON players.id = matches.player_one 
   and matches.match_outcome = 'win' 
GROUP BY players.id;
