import pygame
import math
from maze import OFFSET_X, OFFSET_Y, CELL_SIZE

# Color Palette for Robot Visuals
ROBOT_COLOR = (52, 152, 219)     # Electric Blue Body
HEADING_COLOR = (241, 196, 15)   # Gold Direction Pointer
GLOW_COLOR = (41, 128, 185, 100) # Semi-transparent accent glow

class Robot:
    def __init__(self, start_row=0, start_col=0, max_energy=100.0):
        # 1. Spatial & Grid State
        self.row = start_row
        self.col = start_col
        self.heading = 'S'  # Default facing South ('N', 'E', 'S', 'W')
        
        # Smooth interpolation coordinates (for smooth movement animations)
        self.pixel_x = OFFSET_X + self.col * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = OFFSET_Y + self.row * CELL_SIZE + CELL_SIZE // 2

        # 2. Navigation State
        self.path = []            # List of (row, col) tuples to follow
        self.target_idx = 0       # Current target index along path
        self.is_moving = False
        
        # 3. Energy State
        self.max_energy = max_energy
        self.energy_remaining = max_energy
        self.energy_consumed = 0.0

        # Energy Parameters
        self.MOVE_COST = 1.0     # Energy per step straight
        self.TURN_COST = 0.5     # Additional energy penalty per 90-degree turn

    def reset(self, start_row=0, start_col=0):
        """Resets robot state back to starting conditions."""
        self.row = start_row
        self.col = start_col
        self.heading = 'S'
        self.pixel_x = OFFSET_X + self.col * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = OFFSET_Y + self.row * CELL_SIZE + CELL_SIZE // 2
        self.path = []
        self.target_idx = 0
        self.is_moving = False
        self.energy_remaining = self.max_energy
        self.energy_consumed = 0.0

    def set_path(self, path):
        """Assigns a planned path (list of Cell objects or (r, c) tuples) to follow."""
        if not path:
            return
        
        # Convert path items to (row, col) tuples if Cell objects are passed
        self.path = [(c.row, c.col) if hasattr(c, 'row') else c for c in path]
        self.target_idx = 0
        self.is_moving = True

    def _determine_direction(self, from_cell, to_cell):
        """Determines compass direction between two adjacent grid cells."""
        dr = to_cell[0] - from_cell[0]
        dc = to_cell[1] - from_cell[1]
        
        if dr == -1: return 'N'
        if dr == 1:  return 'S'
        if dc == 1:  return 'E'
        if dc == -1: return 'W'
        return self.heading

    def update(self, speed=0.15):
        """
        Behavioral update loop: handles smooth geometric translation 
        and updates energy consumption along path.
        """
        if not self.is_moving or self.target_idx >= len(self.path):
            self.is_moving = False
            return

        target_row, target_col = self.path[self.target_idx]
        target_px = OFFSET_X + target_col * CELL_SIZE + CELL_SIZE // 2
        target_py = OFFSET_Y + target_row * CELL_SIZE + CELL_SIZE // 2

        # Check turn penalties when stepping into a new cell target
        if (self.row, self.col) != (target_row, target_col):
            new_dir = self._determine_direction((self.row, self.col), (target_row, target_col))
            if new_dir != self.heading:
                # Add turning energy cost penalty
                self.energy_consumed += self.TURN_COST
                self.energy_remaining = max(0.0, self.energy_remaining - self.TURN_COST)
                self.heading = new_dir
            
            # Add linear movement energy cost
            self.energy_consumed += self.MOVE_COST
            self.energy_remaining = max(0.0, self.energy_remaining - self.MOVE_COST)

        # Smooth position interpolation (lerp) toward target pixel position
        self.pixel_x += (target_px - self.pixel_x) * speed
        self.pixel_y += (target_py - self.pixel_y) * speed

        # Snap to cell once close enough and target next cell on path
        if math.hypot(target_px - self.pixel_x, target_py - self.pixel_y) < 2.0:
            self.pixel_x = target_px
            self.pixel_y = target_py
            self.row = target_row
            self.col = target_col
            self.target_idx += 1

            if self.target_idx >= len(self.path):
                self.is_moving = False

    def draw(self, surface):
        """Renders the robot as an oriented geometric triangle."""
        radius = CELL_SIZE * 0.35

        # Define direction angles in radians for geometric rotation
        angles = {'N': -math.pi/2, 'E': 0, 'S': math.pi/2, 'W': math.pi}
        angle = angles.get(self.heading, 0)

        # Calculate triangle vertices (Nose, Left Wing, Right Wing)
        nose = (
            self.pixel_x + radius * math.cos(angle),
            self.pixel_y + radius * math.sin(angle)
        )
        left_wing = (
            self.pixel_x + radius * math.cos(angle + 2.5),
            self.pixel_y + radius * math.sin(angle + 2.5)
        )
        right_wing = (
            self.pixel_x + radius * math.cos(angle - 2.5),
            self.pixel_y + radius * math.sin(angle - 2.5)
        )

        # Draw outer orientation border
        pygame.draw.polygon(surface, HEADING_COLOR, [nose, left_wing, right_wing], width=2)
        # Draw main robot body
        pygame.draw.polygon(surface, ROBOT_COLOR, [nose, left_wing, right_wing])
        # Center core marker
        pygame.draw.circle(surface, (255, 255, 255), (int(self.pixel_x), int(self.pixel_y)), 3)