# ChainReaction: A Python online multiplayer

This game is inspired by the original game Chain Reaction by Buddy-Matt Entertainment
([Play Store](https://play.google.com/store/apps/details?id=com.BuddyMattEnt.ChainReaction))
and its missing online multiplayer mode.<br/>
Chain Reaction is a combinatorial game in which "orbs" are placed in cells with the goal
of capturing all the orbs on the board. This version of the game allows a theoretically
unlimited number of players and board sizes.

## Rules:

Taken from [brilliant.org](https://brilliant.org/wiki/chain-reaction-game/), which describes the rule
for a game with two players (red and green).

1. The gameplay takes place in an m×n board. The most commonly used size of the board is 9×6.
2. For each cell in the board, we define a critical mass. The critical mass is equal to the number
of orthogonally adjacent cells. That would be 4 for usual cells, 3 for cells in the edge and 2 for
cells in the corner.
3. All cells are initially empty. The Red and the Green player take turns to place "orbs" of their
corresponding colors. The Red player can only place an (red) orb in an empty cell or a cell which
already contains one or more red orbs. When two or more orbs are placed in the same cell, they
stack up.
4. When a cell is loaded with a number of orbs equal to its critical mass, the stack immediately
explodes. As a result of the explosion, to each of the orthogonally adjacent cells, an orb is
added and the initial cell looses as many orbs as its critical mass. The explosions might result
in overloading of an adjacent cell and the chain reaction of explosion continues until every
cell is stable.
5. When a red cell explodes and there are green cells around, the green cells are converted to red
and the other rules of explosions still follow. The same rule is applicable for other colors.
6. The winner is the one who eliminates every other player's orbs.

# How to play

In the following sections you will find further information on installing and playing the game.
You will also find some information about the configuration file and the log files.

## Installation

This game is written in Python (3.8.10) and requires the following third-party packages:<br/>
`pygame, numpy, tkinter, matplotlib (and pytest)`<br/>
which can be installed with pip as follows:<br/>
`pip install pygame numpy tk matplotlib`

It is recommended to convert the .py files into executable .exe files, which allows for
easier distribution as these executable files are self-contained, i.e. do not require a
Python installation. The executable files can be created e.g. with
[PyInstaller](https://pyinstaller.org/en/stable/). PyInstaller can be install using:<br/>
`pip install pyinstaller` <br/>
After installing the required Python packages and PyInstaller, the two executable files
can be created as follows:<br/>
`pyinstaller --onefile client.py` <br/>
`pyinstaller --onefile server.py` <br/>
The executable files are located in the created "dist" folder.
> [!NOTE]
> Running these files can/will cause Windows Defender to issue a warning due to missing
> certificates and the way PyInstaller (and other such packagers) create the executables.

Alternatively, the client.py and server.py files can also be executed directly with an
existing Python installation.

## How to start

The multiplayer concept is based on a server-client model. It is therefore necessary to
start a server and a client separately.<br/>
For a direct connection via the Internet, port forwarding (of a TCP port) may be required
on the server side. For ease of use, tools such as [RadminVPN](https://www.radmin-vpn.com/),
[Hamachi](https://vpn.net/) etc. can be used to create a VPN that enables local multiplayer
and thus avoids the need for port forwarding.

### Server

1. Start server.py/.exe.
2. The following window is displayed:<br/>
![Server GUI](/images/server_gui.png)
    - Number of players: Defines the number of players who can play.
    - Board tiles width/height: Defines the size of the game board (m×n).
    - IP/Port: IP/Port at which the server can be reached and to which the clients must connect.
    (Is filled in automatically, but may be incorrect.)
3. Press "Continue" to start the server. If successful, the output is "Waiting for players ...".
 (remains open for 100 seconds)
4. The game is started when the specified number of players have joined.

### Client

1. Start client.py/.exe.
2. The following window is displayed:<br/>
![Client GUI](/images/client_gui.png)
    - Nickname: Your nickname in the game.
    - IP/Port: IP/Port of the server you want to connect to.
    - Spectator: Allows you to observe the game without playing yourself. (Allows you to join
     even after starting a game.)
3. Press "Continue" to join the server. If successful, the output will be
 "Waiting for players ..." or an immediate joining.
4. The game will start when the specified number of players have joined.
5. "Next:" shows the player whose turn it is.
6. The "Undo" button can be pressed by any player to undo the last move.
7. Enjoy the game!

Further information:
- Each player/spectator can leave the game at any time without affecting the play of others.
- "Round:" shows the current round.
- "Total:" shows the total number of orbs in the game (equals the number of rounds).
- The bar chart shows the current percentage (size) of orbs owned by each player and the
 number of orbs owned (number before the nickname).
- The game can be resized.
- The initial player order is determined at random.
- The name of the window is your nickname.

Gameplay example:
![Gameplay example](/images/gameplay.png)

## Restart

After finishing a game, a new game can be started immediately. The required entries are filled
in with the values from the last game, but can be changed if desired. If no changes are required,
press "Continue" to wait until all players are reconnected and a new game is started.

At the end of the game, players receive some additional statistics. Firstly, the winner is named.
Secondly, two diagrams are displayed (see image below). The dotted lines correspond to the maximum number of orbs
per round. The top graph shows the number of orbs per player, while the bottom graph shows the
percentage that each player has.<br/>
As these diagrams were created with matplotlib, they are interactive. The cross can be used to
move within the diagrams, while the magnifying glass enables zooming. The building resets the
diagrams. You can save the diagrams by pressing on the disk.

![Restart GUI](/images/restart_gui.png)

## Config

To simplify the start process and avoid unnecessary repetitions, many attributes can be saved in
a configuration file. The first time the game is started, a file called "chain_reaction.ini" is
created. The [DEFAULT] section shows the default settings and can be changed without consequences.

[CLIENT] section:
- fps_limit: Limits the amount of game loops calculated per second.
- box_min_size: Minimum size in pixels that the boxes may have.
- box_line_width: Size of the dividing lines between the boxes in pixels.
- board_color: Background color in RGB format (R,G,B).
- player_colors: List of player colors in RGB format. If the list is "too short", the colors are repeated.
- nickname: Nickname, can be set as "None" to be a free input field.
- ip: IP of the server to which a connection is to be established.
- port: Port of the server to which a connection is to be established.
- be_player: "True" for joining as a player, "False" for joining as a spectator.



[SERVER] section:
- reaction_time_step: Time in seconds between the individual steps of the "chain reaction".
- player_number: Number of players per game, "None" to be a free input field.
- gameboard_height: Number of cells vertically, "None" to be a free input field.
- gameboard_width: Number of cells horizontally, "None" to be a free input field.
- ip: IP address at which the server can be reached, "None" to fill in automatically (may be incorrect).
- port: Port via which the server will be accessible.

## Logging

When the game is started for the first time, a "logs" folder is created. The logs for the server
(server.log.jsonl) and for the client (client.log.jsonl) are created here. The logs contain detailed
information about the game and its progress. If problems or crashes occur, they should contain enough
information to fix the problem. Please make sure that you can send the logs on request.
> [!CAUTION]
> These logs contain "sensitive" information such as nicknames and IPs. Please make sure that you
> censor them manually if you want to share log files.


# Further resources

This section contains some additional resources and all the links mentioned above.
- Original Chain Reaction by Buddy-Matt Entertainment for android: https://play.google.com/store/apps/details?id=com.BuddyMattEnt.ChainReaction&amp;hl=en
- Game rules and additional informations provided by brilliant.org: https://brilliant.org/wiki/chain-reaction-game/
- ChainReactionAI written in Python: https://github.com/Agnishom/ChainReactionAI
- Chain Reaction game created using HTML & Javascript: https://github.com/nitish712/Chain-Reaction
- Chain Reaction game created in Java using Swing and AWT: https://github.com/realspal/ChainReaction
- PyInstaller Manual: https://pyinstaller.org/en/stable/
- RadminVPN: https://www.radmin-vpn.com/
- Hamachi by LogMeIn: https://vpn.net/
