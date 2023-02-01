# Player

<br>

## Description

After a successful authentication and authorization in the playing area, the players generate their own card, have it protected through digital signature and other mechanisms that prevent cheating. Any cheating involves disqualification.

To prevent any cheating at all, the users blindly shuffle the deck. This makes it impossible to know beforehand which one will be used to play, even for the player itself, as the caller signs the actual deck afterwards.

As with any user, players can also audit events by requesting the log from the [playing area](https://github.com/detiuaveiro/assignment-2---bingo-8/tree/main/playing-area) and check the winner(s).

<br>

## How to run

    $ cd player/
    $ python player.py