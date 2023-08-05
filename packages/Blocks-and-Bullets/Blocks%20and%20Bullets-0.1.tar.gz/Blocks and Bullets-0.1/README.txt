==================
Blocks and Bullets
==================

Blocks and Bullets is a simple game, which at the moment has little gameplay value. It is more an experiment on the components of a game.


Installation
============

Please ensure you are running Python 2.7 or better.
Ensure you have extracted the files from the .tar.gz file.

Run the standard command::

	python setup.py install

To do this, open terminal, cmd, or your nearest equivalent.
Navigate to the location of the extracted files.
Run the command above.

If you are running on Windows, and the above does not work, try::

	setup.py install

If you are running Ubuntu and the above does not work, add sudo to the start and see how it goes.

Game Setup
==========

Running the game should be done by running python command line and typing in::

	import BlocksandBullets

To start, simply enter the amount of players, from 2 to 15. Then, give each character their name of 1-25 characters that cannot be the same between characters, and a symbol, the 1 character that is their playing piece, and cannot be a hash, arrow including v or space.

It is recommended you resize the window to be slightly taller than default.


Controls
========

Type in each command then press enter.

WASD to move, E to reload, and SPACE to shoot.
8426 to move, 0 to reload, and 0 to shoot.
Alternatively type each command, eg "Up", "Reload", "Shoot".

Gameplay
========

Each player is allocated 10 hp and 10 bullets, as well as a spot on the edge of the 50x30 board, and enough room to move.

The board consists of blocks (#), players, and bullets (< v > ^).

Players take turns, either moving a spot, shooting a bullet, or reloading.

Players that shoot with no ammo will miss their turn, as will players walking into blocks, players, or the edge of the board.

Bullets move once per players' go, and so move faster relative to players the more players there are. For example, with two players, a bullet moves twice as fast as players, whereas with 15 players, bullets move 15 times as fast as players.

A bullet hitting a player will knock of 1 hp and be destroyed, bullets hitting a wall will destroy both the bullet and the wall, bullets colliding will be destroyed, and bullets two bullets hitting a wall at the same time will both be destroyed, as well as the wall.

A player with 0 hp will dissapear.

When 1 player remains they will be declared winner, but if none remain, the game will be declared a draw.

Known Bugs
==========

Report bugs to olligobber, at http://sirolligobbervii.zxq.net/
