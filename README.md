# Boulder Puzzle

## Information

------

### Description

This is a relatively small game, designed with the intention of showcasing programming knowledge while also being
infinitely repeatable. Originally designed in Java, the program works fairly well in Python, utilizing the PyQt5 render
library. However, due to Python's slower computation speed, certain settings were tweaked
for better performance.

### How it works

With the goal of being infinitely playable, the levels/boards must be procedurally generated. As such,
multiple algorithms are used in the creation of a level. A board is randomly generated, and an algorithm
attempts to evaluate the validity of the level - if it is solvable. Depending on the parameters passed in,
a board may be constantly regenerated or enhanced to increase the "difficulty" of a level.

Depending on preset size and difficulty, some boards may be trivial while others may be challenging.
As a result, generation on higher difficulties may take substantially longer to create.

Multithreading is used (though possibly not very effectively/safely due to python libraries) to create
levels while a player is playing the game, attempting to minimize the waiting period.

### Gameplay

The game itself was inspired by Pokémon Ruby, Sapphire and Emerald - Seafloor Cavern Puzzle,
where the player must push boulders to reach the end of the level. However, the player can only
push one boulder at a time, therefore certain paths cannot reach the end.

Due to the use of actual buttons, only the WASD keys can be used to move the player(represented by
the red square). Reaching the end of the level (marked in green) gives the player another board.

"Points" act as lives, and using certain lifelines reduces the points. Solving puzzles quickly and
efficiently gives bonus points. If the player runs out of points, they lose.

## Notes

------

### Issues

* At times the algorithm used to determine if a board is solvable may fail, creating either an impossible board or
  empty board
* As a result of the Qt library, concurrency issues may occur at times

### Future Improvements

* Algorithm could potentially be improved to run in faster time and space, but
  solving the puzzle can be quite complex
* Currently, the frame is redrawn multiple times a second (20 fps), but this could possibly
  be improved in the future by only redrawing it on update
* Qt Buttons are hidden by simply appearing transparent. This could potentially be further improved
* The procedural generation algorithm could be improved further, possibly counting "player movement" as part of the
  difficulty assessment.
* Menus and Visuals could be improved, allowing users to directly customize grid size and difficulty
