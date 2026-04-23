import pygame
import random

def start_tetris(screen, is_muted, players, p1_name="Player 1", p2_name="Player 2"):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    
    if not is_muted: pygame.mixer.music.pause()
        
    tetris_music = None
    try:
        tetris_music = pygame.mixer.Sound("tetris_bg.wav")
        tetris_music.set_volume(0.4)
        if not is_muted: tetris_music.play(loops=-1)
    except FileNotFoundError: pass

    # Colors
    BG_COLOR = (10, 10, 20)
    GRID_COLOR = (40, 40, 60)
    WHITE = (255, 255, 255)
    GARBAGE_COLOR = (100, 100, 100)
    
    font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 30)

    # Tetromino Shapes
    SHAPES = [
        [(-1,0), (0,0), (1,0), (2,0)],  # I (Cyan)
        [(-1,-1), (-1,0), (0,0), (1,0)],# J (Blue)
        [(1,-1), (-1,0), (0,0), (1,0)], # L (Orange)
        [(0,0), (1,0), (0,1), (1,1)],   # O (Yellow)
        [(0,-1), (1,-1), (-1,0), (0,0)],# S (Green)
        [(0,-1), (-1,0), (0,0), (1,0)], # T (Purple)
        [(-1,-1), (0,-1), (0,0), (1,0)] # Z (Red)
    ]
    COLORS = [
        (0, 255, 255), (0, 0, 255), (255, 165, 0), 
        (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
    ]

    class TetrisBoard:
        def __init__(self, offset_x, offset_y, title):
            self.cols, self.rows = 10, 20
            self.cell_size = 28 
            self.offset_x = offset_x
            self.offset_y = offset_y
            self.title = title
            self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
            self.score = 0
            self.game_over = False
            self.fall_time = 0
            self.fall_speed = 500 # ms
            
            # Tracking the NEXT piece
            self.next_idx = random.randint(0, 6)
            self.spawn_piece()

        def spawn_piece(self):
            # Take the piece from the 'next' queue, then generate a new one
            idx = self.next_idx
            self.piece = [list(pos) for pos in SHAPES[idx]]
            self.piece_color = COLORS[idx]
            self.piece_x, self.piece_y = 4, 1
            
            self.next_idx = random.randint(0, 6) # Queue up the next block
            
            if not self.is_valid(self.piece_x, self.piece_y, self.piece):
                self.game_over = True

        def is_valid(self, px, py, shape):
            for dx, dy in shape:
                x, y = px + dx, py + dy
                if x < 0 or x >= self.cols or y >= self.rows: return False
                if y >= 0 and self.grid[y][x] is not None: return False
            return True

        def rotate(self):
            if self.piece_color == COLORS[3]: return # O-shape doesn't rotate
            new_shape = [[-dy, dx] for dx, dy in self.piece]
            if self.is_valid(self.piece_x, self.piece_y, new_shape):
                self.piece = new_shape

        def move(self, dx, dy):
            if self.is_valid(self.piece_x + dx, self.piece_y + dy, self.piece):
                self.piece_x += dx
                self.piece_y += dy
                return True
            return False

        def hard_drop(self):
            while self.move(0, 1): pass
            return self.lock_piece()

        def lock_piece(self):
            for dx, dy in self.piece:
                if self.piece_y + dy >= 0:
                    self.grid[self.piece_y + dy][self.piece_x + dx] = self.piece_color
            return self.clear_lines()

        def clear_lines(self):
            lines_cleared = 0
            new_grid = [row for row in self.grid if any(cell is None for cell in row)]
            lines_cleared = self.rows - len(new_grid)
            for _ in range(lines_cleared):
                new_grid.insert(0, [None for _ in range(self.cols)])
            self.grid = new_grid
            
            if lines_cleared == 1: self.score += 100
            elif lines_cleared == 2: self.score += 300
            elif lines_cleared == 3: self.score += 500
            elif lines_cleared == 4: self.score += 800
            
            self.spawn_piece()
            return lines_cleared

        def add_garbage(self, lines):
            if lines <= 0: return
            for _ in range(lines):
                self.grid.pop(0) 
                hole = random.randint(0, self.cols - 1)
                new_row = [GARBAGE_COLOR if i != hole else None for i in range(self.cols)]
                self.grid.append(new_row)

        def draw(self, surface):
            # Draw Title & Score
            t_surf = font.render(self.title, True, WHITE)
            s_surf = small_font.render(f"SCORE: {self.score}", True, WHITE)
            surface.blit(t_surf, (self.offset_x, self.offset_y - 75))
            surface.blit(s_surf, (self.offset_x, self.offset_y - 35))

            # Draw Board Background
            board_w = self.cols * self.cell_size
            board_h = self.rows * self.cell_size
            board_rect = pygame.Rect(self.offset_x, self.offset_y, board_w, board_h)
            pygame.draw.rect(surface, (5, 5, 10), board_rect)
            pygame.draw.rect(surface, GRID_COLOR, board_rect, 2)

            # Draw NEXT Block Window
            next_box_x = self.offset_x + board_w + 15
            next_box_y = self.offset_y
            next_surf = small_font.render("NEXT", True, WHITE)
            surface.blit(next_surf, (next_box_x, next_box_y))
            pygame.draw.rect(surface, GRID_COLOR, (next_box_x, next_box_y + 30, 90, 90), 2)
            
            # Render the next shape in the box
            next_shape = SHAPES[self.next_idx]
            next_color = COLORS[self.next_idx]
            for dx, dy in next_shape:
                nx = next_box_x + 45 + dx * self.cell_size - (self.cell_size//2 if self.next_idx != 3 else self.cell_size)
                ny = next_box_y + 70 + dy * self.cell_size - (self.cell_size//2 if self.next_idx != 3 else self.cell_size)
                rect = pygame.Rect(nx, ny, self.cell_size, self.cell_size)
                pygame.draw.rect(surface, next_color, rect)
                pygame.draw.rect(surface, (0,0,0), rect, 1)

            # Draw Locked Blocks
            for y in range(self.rows):
                for x in range(self.cols):
                    if self.grid[y][x]:
                        rect = pygame.Rect(self.offset_x + x*self.cell_size, self.offset_y + y*self.cell_size, self.cell_size, self.cell_size)
                        pygame.draw.rect(surface, self.grid[y][x], rect)
                        pygame.draw.rect(surface, (0,0,0), rect, 1)

            # Draw Falling Piece
            if not self.game_over:
                for dx, dy in self.piece:
                    x, y = self.piece_x + dx, self.piece_y + dy
                    if y >= 0:
                        rect = pygame.Rect(self.offset_x + x*self.cell_size, self.offset_y + y*self.cell_size, self.cell_size, self.cell_size)
                        pygame.draw.rect(surface, self.piece_color, rect)
                        pygame.draw.rect(surface, (0,0,0), rect, 1)
                        
            if self.game_over:
                go_surf = font.render("DEAD", True, (255, 50, 50))
                surface.blit(go_surf, (self.offset_x + board_w//2 - go_surf.get_width()//2, self.offset_y + board_h//2))

    # Initialize Boards with Custom Names
    if players == 1:
        board1 = TetrisBoard(WIDTH//2 - 140, 90, p1_name.upper())
        boards = [board1]
    else:
        board1 = TetrisBoard(WIDTH//4 - 140, 90, p1_name.upper())
        board2 = TetrisBoard(WIDTH*3//4 - 140, 90, p2_name.upper())
        boards = [board1, board2]

    frame_count = 0
    running = True
    while running:
        dt = clock.tick(60)
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if tetris_music: tetris_music.stop()
                    if not is_muted: pygame.mixer.music.unpause()
                    return max(b.score for b in boards) 
                    
                if not board1.game_over:
                    if event.key == pygame.K_a: board1.move(-1, 0)
                    elif event.key == pygame.K_d: board1.move(1, 0)
                    elif event.key == pygame.K_w: board1.rotate()
                    elif event.key == pygame.K_SPACE:
                        lines = board1.hard_drop()
                        if players == 2 and lines >= 2:
                            garbage = 1 if lines == 2 else (2 if lines == 3 else 4)
                            board2.add_garbage(garbage)

                if players == 2 and not board2.game_over:
                    if event.key == pygame.K_LEFT: board2.move(-1, 0)
                    elif event.key == pygame.K_RIGHT: board2.move(1, 0)
                    elif event.key == pygame.K_UP: board2.rotate()
                    elif event.key == pygame.K_RETURN: 
                        lines = board2.hard_drop()
                        if lines >= 2:
                            garbage = 1 if lines == 2 else (2 if lines == 3 else 4)
                            board1.add_garbage(garbage)

        keys = pygame.key.get_pressed()
        if not board1.game_over and keys[pygame.K_s] and frame_count % 3 == 0: board1.move(0, 1)
        if players == 2 and not board2.game_over and keys[pygame.K_DOWN] and frame_count % 3 == 0: board2.move(0, 1)

        # Gravity Fall
        for b in boards:
            if not b.game_over:
                b.fall_time += dt
                if b.fall_time >= b.fall_speed:
                    b.fall_time = 0
                    if not b.move(0, 1):
                        lines = b.lock_piece()
                        if players == 2 and lines >= 2:
                            garbage = 1 if lines == 2 else (2 if lines == 3 else 4)
                            target = board2 if b == board1 else board1
                            target.add_garbage(garbage)

        screen.fill(BG_COLOR)
        for b in boards: b.draw(screen)

        # Tutorial Overlay (Fades out after 5 seconds!)
        if frame_count <= 300:
            tut1 = small_font.render("[W/A/S/D] MOVE  [SPACE] DROP", True, GARBAGE_COLOR)
            screen.blit(tut1, (board1.offset_x - 10, board1.offset_y + board1.rows * board1.cell_size + 15))
            if players == 2:
                tut2 = small_font.render("[ARROWS] MOVE  [ENTER] DROP", True, GARBAGE_COLOR)
                screen.blit(tut2, (board2.offset_x - 10, board2.offset_y + board2.rows * board2.cell_size + 15))

        if all(b.game_over for b in boards):
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(150); overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            
            go_surf = pygame.font.Font(None, 120).render("GAME OVER", True, (255, 50, 50))
            esc_surf = small_font.render("Press [ESC] to return to Menu", True, WHITE)
            screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 60))
            screen.blit(esc_surf, (WIDTH//2 - esc_surf.get_width()//2, HEIGHT//2 + 50))

        pygame.display.flip()