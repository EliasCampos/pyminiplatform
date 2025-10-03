# Overview

This is a 2D platformer game built with Pygame, replicating the miniplatform game originally written in C++ with SFML. The game features player movement, platforming mechanics, collectible coins that accelerate time, animated lava hazards, and a time-stop ability. The implementation uses the exact level layouts and color scheme from the original repository.

# User Preferences

Preferred communication style: Simple, everyday language.

# Game Features

## Core Mechanics
- **Player Movement**: Move left/right with arrow keys, jump with Up arrow
- **Gravity & Physics**: Realistic gravity with tile-based collision detection
- **Multiple Levels**: Two complete levels from the original game with automatic progression
- **Camera System**: Smooth camera that follows the player through large levels

## Special Abilities
- **Time Stop**: Press Z to freeze the world for 5 seconds while the player continues moving
  - 10-second cooldown after each use
  - Visual color-shift effect when time is stopping/starting
  - Freezes coin animations and lava movement
- **Coin Collection**: Collect yellow coins to increase game speed
  - Each coin adds 10 points and increases time multiplier by 0.1x
  - Time acceleration affects player movement speed and gravity
  - Coins have animated floating effect
  - Collecting all coins advances to next level

## Hazards
- **Static Lava**: Red blocks marked with '+' that reset the level on contact
- **Animated Lava**: Moving lava blocks ('v', '|', '=') that bounce vertically or horizontally
- **Level Reset**: Touching any lava restarts the current level

## HUD
- Score counter
- Game time tracker
- Speed multiplier display (shows time acceleration)
- Current level indicator
- Time stop status (active, cooldown, or ready)
- Control instructions at bottom of screen

# System Architecture

## Game Engine
- **Framework**: Pygame for rendering, input handling, and game loop management
- **Rationale**: Pygame provides a Python-native solution matching the SFML functionality of the original C++ version

## Level System
- **Format**: ASCII-based tile maps matching the original C++ implementation
- **Characters**: 
  - `#` = walls/platforms (dark gray, RGB: 60, 60, 60)
  - `+` = static lava (red, RGB: 255, 100, 100)
  - `v`, `|`, `=` = animated lava (vertical or horizontal movement)
  - `o` = coins
  - `@` = player starting position
  - `.` = empty space
- **Tile Size**: 20x20 pixels per block
- **Camera**: Centered on player with smooth scrolling

## Physics System
- **Approach**: Frame-based physics with velocity and acceleration
- **Gravity**: Constant acceleration applied each frame
- **Friction**: Horizontal velocity decay for smooth movement
- **Time Scaling**: Multiplier system affects velocity and gravity calculations
  - Coins increase the multiplier to speed up gameplay
  - Time stop freezes world time while allowing player to move normally
- **Collision Detection**: Tile-based collision checking for walls and platforms

## Input System
- **Method**: Direct keyboard polling using pygame.key.get_pressed()
- **Controls**: 
  - Movement: Left/Right arrow keys
  - Jump: Up arrow (only when grounded)
  - Time Stop: Z key
- **Rationale**: Immediate input response for precise platforming control

## Rendering
- **Display**: 800x600 window at 60 FPS
- **Graphics**: Block-based rendering with exact colors from original game
- **Color Scheme**: 
  - Background: White (255, 255, 255)
  - Walls: Dark gray (60, 60, 60)
  - Lava: Red (255, 100, 100)
  - Player: Blue (100, 100, 255)
  - Coins: Gold (255, 215, 0)
- **Effects**: Time-stop color transition effect on walls and lava
- **HUD**: Real-time display of all game statistics and ability status

## Game State Management
- **Player State**: Position, velocity, ground detection, camera offset tracked per-frame
- **Coin State**: Position, collection status, animation offset
- **Lava State**: Position, animation type (vertical/horizontal), animation offset
- **Time State**: Game time, time multiplier, time stop active/cooldown timers
- **Level State**: Current level index, automatic progression on completion
- **Rationale**: Clean state management matching original game structure

# External Dependencies

## Core Framework
- **Pygame**: Primary game development library (v2.6.1+)
  - Window management
  - 2D rendering
  - Input handling
  - Game loop timing

## Python Standard Library
- **sys**: Application lifecycle management
- **math**: Trigonometric functions for animations

## Runtime Requirements
- Python 3.11
- Pygame 2.6.1 or higher
- No external APIs or services
- Local single-player experience

# Controls

- **Arrow Keys**: Move player left/right and jump
- **Z**: Activate time stop (5-second duration, 10-second cooldown)

# Recent Changes

**October 3, 2025**: Updated to match original repository exactly
- Implemented exact level layouts from the original C++ source code (2 levels)
- Applied exact color scheme: white background, dark gray walls, red lava
- Added camera system that follows player through large levels
- Implemented animated lava hazards with vertical and horizontal movement
- Added level progression system (advance to next level when all coins collected)
- Added level reset on lava contact
- Implemented time-stop visual color transition effect
- Used tile-based collision detection matching original 20x20 block size
