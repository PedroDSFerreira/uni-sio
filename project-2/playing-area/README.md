# Playing area

<br>

## Description

The playing area is where all users connect. It serves as a secure playing field, where information is signed with a keypair and then exchanged. All users can request a log containing this information, under the format `sequence, timestamp, hash(prev_entry), text, signature`.

Before the game starts, all [players](https://github.com/detiuaveiro/assignment-2---bingo-8/tree/main/player) must be granted access through means of valid authentication, otherwise they are not accepted into the game.

<br>

## How to run

    $ cd playing-area/
    $ python playing_area.py