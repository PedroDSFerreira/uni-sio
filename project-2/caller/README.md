# Caller

<br>

## Description

The caller is the game host and the user whose sequence number is 0. This entity is in charge of disqualifying the [players](https://github.com/detiuaveiro/assignment-2---bingo-8/tree/main/player) that cheat and abort the game if there is any problem that compromises the correct continuity of the game. It is also in the caller's hands to shuffle the numbers from the deck (each one encrypted with a symmetric key), signing it and posting to the [playing area](https://github.com/detiuaveiro/assignment-2---bingo-8/tree/main/playing-area) and to announce the winner(s).

<br>

## How to run

    $ cd caller/
    $ python caller.py