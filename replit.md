# Overview

This is a 2D platformer game built with Pygame, replicating the miniplatform game originally written in C++ with SFML. The game features player movement, platforming mechanics, collectible coins that accelerate time, and a time-stop ability.

# User Preferences

Preferred communication style: Simple, everyday language.

# Game Features

## Core Mechanics
- **Player Movement**: Move left/right with arrow keys or WASD, jump with Space or Up/W
- **Gravity & Physics**: Realistic gravity with collision detection on platforms
- **Platform Levels**: Multiple platforms creating a vertical platforming challenge

## Special Abilities
- **Time Stop**: Press Z to freeze the world for 5 seconds while the player continues moving
  - 10-second cooldown after each use
  - Visual indicator shows when ready or on cooldown
- **Coin Collection**: Collect yellow coins to increase game speed
  - Each coin adds 10 points and increases time multiplier by 0.1x
  - Time acceleration affects player movement speed and gravity
  - Coins have animated floating effect

## HUD
- Score counter
- Game time tracker
- Speed multiplier display (shows time acceleration)
- Time stop status (active, cooldown, or ready)
- Control instructions at bottom of screen

# System Architecture

## Game Engine
- **Framework**: Pygame for rendering, input handling, and game loop management
- **Rationale**: Pygame provides a Python-native solution matching the SFML functionality of the original C++ version

## Physics System
- **Approach**: Custom physics with delta-time-based movement
- **Gravity**: Constant acceleration (0.8 units/frame) applied each update
- **Time Scaling**: Multiplier system affects velocity and gravity calculations
  - Coins increase the multiplier to speed up gameplay
  - Time stop freezes world time while allowing player to move normally
- **Collision Detection**: Axis-separated (X then Y) rectangle-based collision with platforms

## Input System
- **Method**: Direct keyboard polling using pygame.key.get_pressed()
- **Controls**: 
  - Movement: Arrow keys or WASD
  - Jump: Space, Up, or W (only when grounded)
  - Time Stop: Z key
- **Rationale**: Immediate input response for precise platforming control

## Rendering
- **Display**: 800x600 window at 60 FPS
- **Graphics**: Simple geometric shapes for player, platforms, and coins
- **Color Scheme**: Sky blue background, green platforms, blue player, yellow coins
- **HUD**: Real-time display of score, timer, speed multiplier, and ability status

## Game State Management
- **Player State**: Position, velocity, ground detection tracked per-frame
- **Coin State**: Position, collection status, animation offset
- **Time State**: Game time, time multiplier, time stop active/cooldown timers
- **Rationale**: Simple state management appropriate for single-level platformer

# External Dependencies

## Core Framework
- **Pygame**: Primary game development library (v2.6.1+)
  - Window management
  - 2D rendering
  - Input handling
  - Game loop timing

## Python Standard Library
- **sys**: Application lifecycle management
- **random**: Coin animation offset randomization

## Runtime Requirements
- Python 3.11
- Pygame 2.6.1 or higher
- No external APIs or services
- Local single-player experience

# Controls

- **Arrow Keys / WASD**: Move player left and right
- **Space / Up / W**: Jump (when on ground)
- **Z**: Activate time stop (5-second duration, 10-second cooldown)

# Recent Changes

**October 3, 2025**: Complete implementation of miniplatform game in Python
- Created full game with player, platforms, coins, and special abilities
- Implemented time stop mechanic that freezes world while player moves
- Added time acceleration through coin collection that affects actual gameplay speed
- Built comprehensive HUD showing all game statistics and ability status
