# Miniplatform
A 2D platform game written in Python.
Inspired by [Eloquent JavaScript](https://eloquentjavascript.net/16_game.html)

## Features

### Game mechanics
- Press `Left`/`Right` arrow keys to move sides. Press `Up` to jump.
- Collect all coins to complete the level. Complete all the levels to win the game.
- Don't touch lava, or else you'll die and will start the level all over again.
- Press `z` to _stop time_. Pay attention to the power bar at the top left.
- Shake a leg! The game gets reset. _Once time's up, you'll start the whole game all over again!_ 

### Extra features
- A window re-sizes automatically to fit a screen size.
- _The game saves current progress_. After re-launching you go back to where you stopped.

## Preview

### Time stop
![preview](previews/time_stop.gif)

### Time's up. Game reset.
![preview](previews/reset.gif)

## How to run
running via `uv`:
```bash
uv run miniplatform
```
