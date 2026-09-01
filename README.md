# Energy-Aware Robot Navigation

A 2D simulator for mobile robot path planning and energy-aware navigation.

The robot navigates randomly generated mazes while comparing classic pathfinding algorithms. The long-term goal is to minimize energy consumption through smarter planning and (eventually) reinforcement learning.

---

## Features

### Current
- Random maze generation using **Prim's algorithm**
- Start and goal positions
- **Breadth-First Search (BFS)**
- **A\*** pathfinding
- **Micromouse-style Flood Fill** exploration (partial information)
- Smooth robot movement and animation
- 2D visualization with Pygame
- Maze reset and regeneration

### Planned
- [ ] Distance and turn metrics
- [ ] Energy consumption model
- [ ] Energy-aware path planning
- [ ] Reinforcement learning for energy-aware navigation

---

## Technologies
- Python 3.8+
- Pygame
- Git / GitHub

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Neoth-nik/energy_aware_robot_navigation.git
   cd energy_aware_robot_navigation