# Project 2 - Tournament Database

This repository contains course work for the Udacity course Full Stack Web Developer. It is for the second assignment, the database schema and the code needed to implement a Swiss-system tournament.

Schema and code can deal with only one tournament at a time, but allow for draws and an uneven number of players.

The skeleton code was provided by Udacity, the rest of the code written by [Moritz Hellwig](http://blog.zebralove79.com).

## Table of contents

* [Quick start](#quick-start)
* [Unit tests](#unit-tests)
* [Requirements](#requirements)
* [Acknowledgements](#acknowledgements)
* [Resources used](#resources-used)

## Quick start

### Without vagrant
* Clone the repo: `git clone https://github.com/zebralove79/fsp2_td/`
* Run PostgreSQL and execute: `\i tournament.sql` (Warning: This will drop the tournament database if it already exists, which could lead to data loss.)
* Your tournament database should now be set up

### With vagrant
* Clone the repo: `git clone https://github.com/zebralove79/fsp2_td/`
* Set up and run the vagrant machine: `vagrant up`
* Connect to the vagrant machine: `vagrant ssh`
* In the vagrant machine: cd /vagrant/tournament
* Run PostgreSQL and execute: `\i tournament.sql` (Warning: This will drop the tournament database if it already exists, which could lead to data loss.)
* Your tournament database should now be set up

## Unit tests
You can run unit tests to check if everything is working. Be warned, however, because the tests will wipe your current tournament database, which could lead to data loss. It will also leave some test data in the database which you may want to remove.

You can run the tests with: `python tournament_test.sql'

## Requirements

* Python 2.7
* PostgreSQL 9.3.9

### Additional requirements, if you want to use the vagrant machine:
* VirtualBox
* Vagrant

## Acknowledgements

Special thanks to
* Udacity, for offering the course and the skeleton code
* R., for non-technical support

## Resources used
* Wizards of the Coast Swiss-style tournament description: http://www.wizards.com/dci/downloads/swiss_pairings.pdf
* PostgreSQL 9.3 documentation: http://www.postgresql.org/docs/9.3/static/