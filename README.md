# Pyco16

**Pyco16** is a personal 2D game framework built on top of **Pygame** and **ModernGL**. It’s a minimal, experimental framework intended for small-scale games and prototypes, inspired by fantasy console projects like PICO-8.  

This project is **not a finished engine**, it’s in **alpha**. The codebase is incomplete, some systems are broken or unfinished, and it is currently not suitable for production. That said, it offers a rich structure and interesting examples for learning about game architecture, rendering, and Python-based engine design.

---

## Features

Pyco16 provides a collection of subsystems and utilities designed for simple 2D games:

### Content Loader & Asset Pipeline
- Opinionated folder structure
- Automatic asset discovery and loading
- Texture and sound registration
- Centralized access to assets

### Game & Scene Architecture
- Game context abstraction
- Scene lifecycle system
- Scene stack and overlay support
- Deterministic update loop

### Savegame & Serialization
- Savegame system
- Structured state persistence
- Serialization utilities

### Tile & Tilemap System
- Tile-based world support
- Integration with LDtk
- Map loading and structured tile definitions
- Separation between data and rendering

### Entity System
- Base entity classes and Actor abstraction
- Collision handling
- CPU-side batch rendering
- Simple hierarchical structure
- Not ECS-based; designed for straightforward 2D games

### Event Bus
- Single-threaded event system
- Explicit publish/subscribe model
- Decouples gameplay systems

### Particles & VFX
- Particle system with presets
- Geometry helpers
- Supporting math primitives

### Input System
- Centralized input handling
- Structured access to key states

### Audio
- Sound loading and playback
- Integrated with the content pipeline

### Math & Geometry
- Custom math primitives
- Geometry classes for collision, rendering, and VFX

### Finite State Machine (FSM)
- Base FSM implementation
- Intended for entity logic and AI

### Rendering
- Uses ModernGL for GPU-accelerated rendering
- Explicit vertex buffers
- Shader programs
- Resolution scaling support
- Clear update/render separation  
Pygame is only used for windowing and input, sound, math and some other functionalities

---

## Design Intent

The project started as a minimal, low-resolution-friendly framework and has gradually expanded. The core design principles remain:

- **Low-resolution friendly**: ideal for retro-style or small-scope games  
- **Minimal abstraction overhead**: nothing is hidden or magical  
- **Clear architecture**: structured but not rigid  
- **Focused scope**: small 2D games rather than a general-purpose engine  

---

## Requirements

- numba
- numpy
- pygame-ce
- scipy
- moderngl


Install dependencies with:

```bash
pip install -r requirements.txt
```

## License

This project is MIT licensed. You can freely explore, learn from, or adapt it for your own experiments.