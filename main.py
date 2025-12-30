# ==========================================
# Tetris game (pygame)
#
# Author: Nika Falaleeva
# GitHub: https://github.com/nikanikoo
#
# Description:
# Tetris game implemented in Python Pygame.
# Includes scoring, levels, next piece preview and restart.
#
# License: MIT
# ==========================================

import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Grid configuration
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50

# Window size
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + 2 * GRID_X_OFFSET + 200
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 2 * GRID_Y_OFFSET

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# Tetromino shapes (5x5 matrices)
TETROMINOES = {
    'I': [['.....',
           '..#..',
           '..#..',
           '..#..',
           '..#..'],
          ['.....',
           '.....',
           '####.',
           '.....',
           '.....']],
    
    'O': [['.....',
           '.....',
           '.##..',
           '.##..',
           '.....']],
    
    'T': [['.....',
           '.....',
           '.#...',
           '###..',
           '.....'],
          ['.....',
           '.....',
           '.#...',
           '.##..',
           '.#...'],
          ['.....',
           '.....',
           '.....',
           '###..',
           '.#...'],
          ['.....',
           '.....',
           '.#...',
           '##...',
           '.#...']],
    
    'S': [['.....',
           '.....',
           '.##..',
           '##...',
           '.....'],
          ['.....',
           '.....',
           '.#...',
           '.##..',
           '..#..']],
    
    'Z': [['.....',
           '.....',
           '##...',
           '.##..',
           '.....'],
          ['.....',
           '.....',
           '..#..',
           '.##..',
           '.#...']],
    
    'J': [['.....',
           '.....',
           '.#...',
           '.#...',
           '##...'],
          ['.....',
           '.....',
           '.....',
           '#....',
           '###..'],
          ['.....',
           '.....',
           '.##..',
           '.#...',
           '.#...'],
          ['.....',
           '.....',
           '.....',
           '###..',
           '..#..']],
    
    'L': [['.....',
           '.....',
           '.#...',
           '.#...',
           '.##..'],
          ['.....',
           '.....',
           '.....',
           '###..',
           '#....'],
          ['.....',
           '.....',
           '##...',
           '.#...',
           '.#...'],
          ['.....',
           '.....',
           '.....',
           '..#..',
           '###..']]
}

# Color for each tetromino type
TETROMINO_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

class Tetromino:
    """Represents a falling tetromino piece"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.color = TETROMINO_COLORS[self.shape]
        self.rotation = 0
    
    def get_rotated_shape(self):
        """Return the current rotated shape"""
        return TETROMINOES[self.shape][self.rotation % len(TETROMINOES[self.shape])]
    
    def get_cells(self):
        """Return all occupied grid cells of the piece"""
        cells = []
        shape = self.get_rotated_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    cells.append((self.x + j, self.y + i))
        return cells

class TetrisGame:
    """Main Tetris game class"""
    def __init__(self):
        # Game grid
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        # Pieces
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()

        # Game state
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.game_over = False
        
        # Window and UI
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
    def get_new_piece(self):
        """Create a new tetromino at the top of the grid"""
        return Tetromino(GRID_WIDTH // 2 - 2, 0)
    
    def is_valid_position(self, piece, dx=0, dy=0, rotation=None):
        """Check if a piece position is valid"""
        if rotation is None:
            rotation = piece.rotation
        
        old_rotation = piece.rotation
        piece.rotation = rotation
        
        for x, y in piece.get_cells():
            x += dx
            y += dy
            
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                piece.rotation = old_rotation
                return False
            
            if y >= 0 and self.grid[y][x] != BLACK:
                piece.rotation = old_rotation
                return False
        
        piece.rotation = old_rotation
        return True
    
    def place_piece(self, piece):
        """Lock the piece into the grid"""
        for x, y in piece.get_cells():
            if y >= 0:
                self.grid[y][x] = piece.color
    
    def clear_lines(self):
        """Clear completed lines and update score"""
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell != BLACK for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        
        lines_cleared = len(lines_to_clear)
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += lines_cleared * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)
    
    def update(self, dt):
        """Update game logic"""
        if self.game_over:
            return
        
        self.fall_time += dt
        
        if self.fall_time >= self.fall_speed:
            if self.is_valid_position(self.current_piece, dy=1):
                self.current_piece.y += 1
            else:
                self.place_piece(self.current_piece)
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self.get_new_piece()
                
                if not self.is_valid_position(self.current_piece):
                    self.game_over = True
            
            self.fall_time = 0
    
    def move_piece(self, dx):
        """Move piece left or right"""
        if self.is_valid_position(self.current_piece, dx=dx):
            self.current_piece.x += dx
    
    def rotate_piece(self):
        """Rotate the current piece"""
        new_rotation = (self.current_piece.rotation + 1) % len(TETROMINOES[self.current_piece.shape])
        if self.is_valid_position(self.current_piece, rotation=new_rotation):
            self.current_piece.rotation = new_rotation
    
    def drop_piece(self):
        """Instantly drop the piece down"""
        while self.is_valid_position(self.current_piece, dy=1):
            self.current_piece.y += 1
    
    def draw_grid(self):
        """Draw the game grid"""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    GRID_X_OFFSET + x * CELL_SIZE,
                    GRID_Y_OFFSET + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen, self.grid[y][x], rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_piece(self, piece, offset_x=0, offset_y=0):
        """Draw a tetromino on the screen"""
        for x, y in piece.get_cells():
            if y >= 0:
                rect = pygame.Rect(
                    GRID_X_OFFSET + (x + offset_x) * CELL_SIZE,
                    GRID_Y_OFFSET + (y + offset_y) * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen, piece.color, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_next_piece(self):
        """Draw the next piece preview"""
        next_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        next_y = GRID_Y_OFFSET + 50
        
        text = self.font.render("Next:", True, WHITE)
        self.screen.blit(text, (next_x, next_y - 30))
        
        shape = self.next_piece.get_rotated_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell == '#':
                    rect = pygame.Rect(
                        next_x + j * 20,
                        next_y + i * 20,
                        20,
                        20
                    )
                    pygame.draw.rect(self.screen, self.next_piece.color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_info(self):
        """Draw score, level, lines, and controls"""
        info_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
        info_y = GRID_Y_OFFSET + 200
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        
        self.screen.blit(score_text, (info_x, info_y))
        self.screen.blit(level_text, (info_x, info_y + 40))
        self.screen.blit(lines_text, (info_x, info_y + 80))
        
        # Controls
        controls = [
            "Controls:",
            "A/D - move left/right",
            "S - soft drop",
            "W - rotate",
            "Space - hard drop",
            "R - restart" ]
        
        for i, text in enumerate(controls):
            color = WHITE if i == 0 else GRAY
            control_text = pygame.font.Font(None, 24).render(text, True, color)
            self.screen.blit(control_text, (info_x, info_y + 140 + i * 25))
    
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = pygame.font.Font(None, 72).render("GAME OVER", True, WHITE)
        score_text = self.font.render(f"Final score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)
        
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500
        self.game_over = False
    
    def run(self):
        """Main game loop"""
        while True:
            dt = self.clock.tick(60)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.move_piece(-1)
                    elif event.key == pygame.K_d:
                        self.move_piece(1)
                    elif event.key == pygame.K_s:
                        if self.is_valid_position(self.current_piece, dy=1):
                            self.current_piece.y += 1
                    elif event.key == pygame.K_w:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.drop_piece()
                    elif event.key == pygame.K_r:
                        self.reset_game()
            
            # Update game logic
            self.update(dt)
            
            # Drawing
            self.screen.fill(BLACK)
            self.draw_grid()
            
            if not self.game_over:
                self.draw_piece(self.current_piece)
            
            self.draw_next_piece()
            self.draw_info()
            
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()