import pygame
import random

class SnakeButton:
    def __init__(self, x, y, w, h, text, color, hover_color, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = font

    def draw(self, surface):
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (5, 5, 10), shadow_rect, border_radius=8) 
        
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

class Snake:
    def __init__(self, start_x, start_y, bounds, color, is_p2=False):
        self.bounds = bounds
        self.color = color
        self.is_p2 = is_p2
        self.dead = False
        self.grow = False
        self.score = 0
        
        self.body = [(start_x, start_y), (start_x-1, start_y), (start_x-2, start_y)]
        self.dx, self.dy = 1, 0
        
        if is_p2:
            self.body = [(start_x, start_y), (start_x+1, start_y), (start_x+2, start_y)]
            self.dx, self.dy = -1, 0
            
        self.next_dx, self.next_dy = self.dx, self.dy

    def move(self):
        if self.dead: return
        
        self.dx, self.dy = self.next_dx, self.next_dy
        head_x, head_y = self.body[0]
        new_x, new_y = head_x + self.dx, head_y + self.dy

        min_c, max_c, min_r, max_r = self.bounds
        if new_x >= max_c: new_x = min_c
        elif new_x < min_c: new_x = max_c - 1
        if new_y >= max_r: new_y = min_r
        elif new_y < min_r: new_y = max_r - 1

        self.body.insert(0, (new_x, new_y))
        if self.grow: self.grow = False
        else: self.body.pop()

    def check_self_collision(self):
        if not self.dead and self.body[0] in self.body[1:]:
            self.dead = True

    def trigger_hard_mode_swap(self):
        self.body.reverse() 
        if len(self.body) >= 2:
            hx, hy = self.body[0]
            nx, ny = self.body[1]
            dx, dy = hx - nx, hy - ny
            if dx > 1: dx = -1
            elif dx < -1: dx = 1
            if dy > 1: dy = -1
            elif dy < -1: dy = 1
            if dx == 0 and dy == 0: dx = 1
            self.dx, self.dy = dx, dy
            self.next_dx, self.next_dy = dx, dy
        else:
            self.dx, self.dy = -self.dx, -self.dy
            self.next_dx, self.next_dy = self.dx, self.dy

class Apple:
    def __init__(self, bounds, snake1, snake2=None):
        self.bounds = bounds
        self.pos = (0,0)
        self.respawn(snake1, snake2)

    def respawn(self, s1, s2=None):
        min_c, max_c, min_r, max_r = self.bounds
        while True:
            x, y = random.randint(min_c, max_c - 1), random.randint(min_r, max_r - 1)
            if (x, y) not in s1.body:
                if s2 is None or (x, y) not in s2.body:
                    self.pos = (x, y)
                    break

def start_snakey(screen, is_muted, players, p1_name="P1", p2_name="P2"):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    
    bg_music = None
    try:
        bg_music = pygame.mixer.Sound("bg_music.mp3") 
        bg_music.set_volume(0.3)
        if not is_muted: bg_music.play(loops=-1)
    except FileNotFoundError: pass

    BG_COLOR, WHITE, CYAN, GREEN, RED, GRAY, GOLD = (15, 20, 15), (255, 255, 255), (0, 255, 255), (50, 255, 100), (255, 50, 50), (100, 100, 100), (255, 215, 0)
    
    title_font = pygame.font.Font(None, 90)
    font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 30)

    # ---> CHANGED: Reduced ROWS from 20 to 18 to give text room to breathe <---
    CELL_SIZE, COLS, ROWS, OFFSET_X, OFFSET_Y = 30, 40, 18, 40, 100
    FULL_BOUNDS, INDEP_P1_BOUNDS, INDEP_P2_BOUNDS = (0, 40, 0, 18), (0, 19, 0, 18), (21, 40, 0, 18)

    game_state = "MODE_SELECT" if players == 2 else "DIFFICULTY_SELECT"
    play_mode, difficulty = "RUMBLE", "NORMAL"
    
    btn_indep = SnakeButton(WIDTH//2 - 250, HEIGHT//2 - 50, 500, 70, "INDEPENDENT (Split Screen)", (0, 120, 120), CYAN, font)
    btn_rumble = SnakeButton(WIDTH//2 - 250, HEIGHT//2 + 50, 500, 70, "ROYAL RUMBLE (1 Arena)", (150, 20, 20), RED, font)
    btn_norm = SnakeButton(WIDTH//2 - 250, HEIGHT//2 - 50, 500, 70, "NORMAL (Classic Snake)", (20, 120, 50), GREEN, font)
    btn_hard = SnakeButton(WIDTH//2 - 250, HEIGHT//2 + 50, 500, 70, "HARD MODE (Swap on Eat!)", (150, 20, 20), RED, font)
    
    p1, p2, apple1, apple2 = None, None, None, None
    frame_count, move_timer = 0, 0
    winner_text = ""

    def setup_game():
        nonlocal p1, p2, apple1, apple2, frame_count
        frame_count = 0
        if players == 1:
            p1, apple1 = Snake(20, 10, FULL_BOUNDS, CYAN), Apple(FULL_BOUNDS, Snake(20, 10, FULL_BOUNDS, CYAN))
        else:
            if play_mode == "INDEPENDENT":
                p1, p2 = Snake(5, 10, INDEP_P1_BOUNDS, CYAN), Snake(35, 10, INDEP_P2_BOUNDS, GREEN, is_p2=True)
                apple1, apple2 = Apple(INDEP_P1_BOUNDS, p1), Apple(INDEP_P2_BOUNDS, p2)
            else:
                p1, p2 = Snake(10, 10, FULL_BOUNDS, CYAN), Snake(30, 10, FULL_BOUNDS, GREEN, is_p2=True)
                apple1 = Apple(FULL_BOUNDS, p1, p2)

    running = True
    while running:
        frame_count += 1
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if p2: return (f"SNAKEY ({difficulty})", max(p1.score, p2.score))
                    return (f"SNAKEY ({difficulty})", p1.score if p1 else 0)
                    
                if event.key == pygame.K_r and game_state == "GAME_OVER":
                    setup_game(); game_state = "PLAYING"
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "MODE_SELECT":
                    if btn_indep.is_hovered: play_mode = "INDEPENDENT"; game_state = "DIFFICULTY_SELECT"
                    if btn_rumble.is_hovered: play_mode = "RUMBLE"; game_state = "DIFFICULTY_SELECT"
                elif game_state == "DIFFICULTY_SELECT":
                    if btn_norm.is_hovered: difficulty = "NORMAL"; setup_game(); game_state = "PLAYING"
                    if btn_hard.is_hovered: difficulty = "HARD"; setup_game(); game_state = "PLAYING"

        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            
            if p1 and not p1.dead:
                if (keys[pygame.K_w] or keys[pygame.K_UP] if players==1 else keys[pygame.K_w]) and p1.dy == 0: p1.next_dx, p1.next_dy = 0, -1
                elif (keys[pygame.K_s] or keys[pygame.K_DOWN] if players==1 else keys[pygame.K_s]) and p1.dy == 0: p1.next_dx, p1.next_dy = 0, 1
                elif (keys[pygame.K_a] or keys[pygame.K_LEFT] if players==1 else keys[pygame.K_a]) and p1.dx == 0: p1.next_dx, p1.next_dy = -1, 0
                elif (keys[pygame.K_d] or keys[pygame.K_RIGHT] if players==1 else keys[pygame.K_d]) and p1.dx == 0: p1.next_dx, p1.next_dy = 1, 0
                
            if p2 and not p2.dead:
                if keys[pygame.K_UP] and p2.dy == 0: p2.next_dx, p2.next_dy = 0, -1
                elif keys[pygame.K_DOWN] and p2.dy == 0: p2.next_dx, p2.next_dy = 0, 1
                elif keys[pygame.K_LEFT] and p2.dx == 0: p2.next_dx, p2.next_dy = -1, 0
                elif keys[pygame.K_RIGHT] and p2.dx == 0: p2.next_dx, p2.next_dy = 1, 0

            move_timer += 1
            if move_timer >= 5: 
                move_timer = 0
                if p1: p1.move()
                if p2: p2.move()

                if p1 and not p1.dead and p1.body[0] == apple1.pos:
                    p1.grow = True; p1.score += 100
                    if difficulty == "HARD": p1.trigger_hard_mode_swap()
                    apple1.respawn(p1, p2)
                
                if play_mode == "INDEPENDENT" and p2 and not p2.dead and p2.body[0] == apple2.pos:
                    p2.grow = True; p2.score += 100
                    if difficulty == "HARD": p2.trigger_hard_mode_swap()
                    apple2.respawn(p2, p1)
                    
                elif play_mode == "RUMBLE" and p2 and not p2.dead and p2.body[0] == apple1.pos:
                    p2.grow = True; p2.score += 100
                    if difficulty == "HARD": p2.trigger_hard_mode_swap()
                    apple1.respawn(p1, p2)

                if p1: p1.check_self_collision()
                if p2: p2.check_self_collision()
                
                if play_mode == "RUMBLE" and p2 and not p1.dead and not p2.dead:
                    if p1.body[0] in p2.body: p1.dead = True
                    if p2.body[0] in p1.body: p2.dead = True

                if players == 1 and p1.dead:
                    game_state = "GAME_OVER"; winner_text = "YOU DIED!"
                elif players == 2:
                    if play_mode == "INDEPENDENT":
                        if p1.dead and p2.dead:
                            game_state = "GAME_OVER"; winner_text = f"{p1_name.upper()} WINS!" if p1.score > p2.score else f"{p2_name.upper()} WINS!"
                    elif play_mode == "RUMBLE":
                        if p1.dead and p2.dead: game_state = "GAME_OVER"; winner_text = "DOUBLE K.O.!"
                        elif p1.dead: game_state = "GAME_OVER"; winner_text = f"{p2_name.upper()} WINS THE RUMBLE!"
                        elif p2.dead: game_state = "GAME_OVER"; winner_text = f"{p1_name.upper()} WINS THE RUMBLE!"

        # --- DRAWING ---
        screen.fill(BG_COLOR)
        
        if game_state in ["MODE_SELECT", "DIFFICULTY_SELECT"]:
            title_surf = title_font.render("SNAKEY", True, GREEN)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 150)))
            
            if game_state == "MODE_SELECT":
                screen.blit(font.render("SELECT ARENA", True, GOLD), (WIDTH//2 - 140, 220))
                btn_indep.check_hover(mouse_pos); btn_indep.draw(screen)
                btn_rumble.check_hover(mouse_pos); btn_rumble.draw(screen)
            else:
                screen.blit(font.render("SELECT DIFFICULTY", True, GOLD), (WIDTH//2 - 180, 220))
                btn_norm.check_hover(mouse_pos); btn_norm.draw(screen)
                btn_hard.check_hover(mouse_pos); btn_hard.draw(screen)

        elif game_state in ["PLAYING", "GAME_OVER"]:
            pygame.draw.rect(screen, (30, 40, 30), (OFFSET_X, OFFSET_Y, COLS*CELL_SIZE, ROWS*CELL_SIZE))
            pygame.draw.rect(screen, GRAY, (OFFSET_X, OFFSET_Y, COLS*CELL_SIZE, ROWS*CELL_SIZE), 2)
            
            if play_mode == "INDEPENDENT":
                pygame.draw.line(screen, GRAY, (OFFSET_X + 20*CELL_SIZE, OFFSET_Y), (OFFSET_X + 20*CELL_SIZE, OFFSET_Y + ROWS*CELL_SIZE), 4)

            if frame_count <= 300 and game_state == "PLAYING":
                p1_ctrl = font.render("[W A S D] TO MOVE", True, CYAN)
                p2_ctrl = font.render("[ARROWS] TO MOVE", True, GREEN)
                
                if play_mode == "INDEPENDENT":
                    screen.blit(p1_ctrl, (OFFSET_X + (COLS//4)*CELL_SIZE - p1_ctrl.get_width()//2, OFFSET_Y + (ROWS//2)*CELL_SIZE))
                    if p2: screen.blit(p2_ctrl, (OFFSET_X + (COLS*3//4)*CELL_SIZE - p2_ctrl.get_width()//2, OFFSET_Y + (ROWS//2)*CELL_SIZE))
                else: 
                    ctrl_x = WIDTH//2 - p1_ctrl.get_width()//2 if players == 1 else WIDTH//2 - 150
                    if players == 1:
                        screen.blit(p1_ctrl, (ctrl_x, OFFSET_Y + (ROWS//2)*CELL_SIZE))
                    else:
                        screen.blit(p1_ctrl, (WIDTH//2 - p1_ctrl.get_width()//2, OFFSET_Y + (ROWS//2)*CELL_SIZE - 40))
                        screen.blit(p2_ctrl, (WIDTH//2 - p2_ctrl.get_width()//2, OFFSET_Y + (ROWS//2)*CELL_SIZE + 40))

            if apple1: pygame.draw.circle(screen, RED, (OFFSET_X + apple1.pos[0]*CELL_SIZE + 15, OFFSET_Y + apple1.pos[1]*CELL_SIZE + 15), 12)
            if play_mode == "INDEPENDENT" and apple2: pygame.draw.circle(screen, RED, (OFFSET_X + apple2.pos[0]*CELL_SIZE + 15, OFFSET_Y + apple2.pos[1]*CELL_SIZE + 15), 12)

            for snake in [p1, p2]:
                if snake and not snake.dead:
                    for i, (c, r) in enumerate(snake.body):
                        color = WHITE if i == 0 else snake.color 
                        pygame.draw.rect(screen, color, (OFFSET_X + c*CELL_SIZE + 1, OFFSET_Y + r*CELL_SIZE + 1, 28, 28), border_radius=4)
                        
            mode_str = "HARD MODE" if difficulty == "HARD" else "NORMAL MODE"
            screen.blit(small_font.render(mode_str, True, RED if difficulty=="HARD" else GREEN), (WIDTH//2 - 80, 20))
            
            p1_score = small_font.render(f"{p1_name.upper()}: {p1.score}", True, CYAN)
            screen.blit(p1_score, (OFFSET_X, 60))
            if p2:
                p2_score = small_font.render(f"{p2_name.upper()}: {p2.score}", True, GREEN)
                screen.blit(p2_score, (WIDTH - OFFSET_X - p2_score.get_width(), 60))

            if game_state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(200); overlay.fill((0,0,0)); screen.blit(overlay, (0,0))
                go_surf = title_font.render(winner_text, True, GOLD)
                rest_surf = small_font.render("Press [R] to Retry or [ESC] for Menu", True, WHITE)
                screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 50))
                screen.blit(rest_surf, (WIDTH//2 - rest_surf.get_width()//2, HEIGHT//2 + 50))

        if game_state not in ["GAME_OVER"]:
            esc_surf = small_font.render("Press ESC to return to menu", True, (80, 80, 80))
            screen.blit(esc_surf, (WIDTH//2 - esc_surf.get_width()//2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)