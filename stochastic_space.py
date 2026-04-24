import pygame
import random
import math

class SS_Button:
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

def start_game(screen, is_muted):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    
    if not is_muted: pygame.mixer.music.pause()
    edu_music = None
    try:
        edu_music = pygame.mixer.Sound("bg_music.mp3") 
        edu_music.set_volume(0.3)
        if not is_muted: edu_music.play(loops=-1)
    except FileNotFoundError: pass

    # Colors
    BG_COLOR = (5, 10, 20)
    WHITE = (255, 255, 255)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    RED = (255, 50, 50)
    GREEN = (50, 255, 100)
    GRAY = (100, 100, 100)
    GOLD = (255, 215, 0)
    
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 35)
    huge_font = pygame.font.Font(None, 100)

    # UI Setup
    start_btn = SS_Button(WIDTH//2 - 200, HEIGHT - 110, 400, 70, "Begin Sampling !", CYAN, WHITE, font)

    # Game Variables
    game_state = "INSTRUCTIONS"
    score = 0
    lives = 3
    
    # Statistical Variables
    target_mean = 50.0
    margin_of_error = 10.0 
    sample_sum = 0.0
    sample_count = 0
    current_mean = 50.0
    
    # Entities
    player_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT - 100, 100, 20)
    data_points = []
    fall_speed = 6.0 
    spawn_timer = 0

    def spawn_data():
        val = random.randint(10, 90)
        is_outlier = random.random() < 0.15 # 15% outlier chance
        if is_outlier:
            val = random.choice([5, 95]) 
        
        x_pos = random.randint(50, WIDTH - 50)
        data_points.append({
            "rect": pygame.Rect(x_pos, -50, 40, 40),
            "val": val,
            "outlier": is_outlier
        })

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if edu_music: edu_music.stop()
                    if not is_muted: pygame.mixer.music.unpause()
                    return score
                if event.key == pygame.K_r and game_state == "GAME_OVER":
                    game_state = "INSTRUCTIONS"
                    score, lives, sample_count, sample_sum, current_mean = 0, 3, 0, 0.0, 50.0
                    margin_of_error = 10.0
                    fall_speed = 6.0
                    data_points.clear()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "INSTRUCTIONS" and start_btn.is_hovered:
                    game_state = "PLAYING"

        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_rect.left > 0:
                player_rect.x -= 12
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_rect.right < WIDTH:
                player_rect.x += 12

            # DYNAMIC DIFFICULTY: Faster scaling
            spawn_interval = max(10, 40 - (sample_count // 4) * 2)
            
            spawn_timer += 1
            if spawn_timer > spawn_interval:
                spawn_data()
                spawn_timer = 0
            
            current_speed = fall_speed + (sample_count // 15)

            for d in data_points[:]:
                d["rect"].y += current_speed
                
                if player_rect.colliderect(d["rect"]):
                    sample_count += 1
                    sample_sum += d["val"]
                    current_mean = sample_sum / sample_count
                    
                    if d["outlier"]:
                        margin_of_error = max(2.0, margin_of_error - 1.5) 
                    score += 10
                    data_points.remove(d)
                
                elif d["rect"].top > HEIGHT:
                    data_points.remove(d)

            if sample_count > 3:
                if abs(current_mean - target_mean) > margin_of_error:
                    lives -= 1
                    sample_sum = target_mean * sample_count
                    current_mean = target_mean
                    if lives <= 0: game_state = "GAME_OVER"

        # --- DRAWING ---
        screen.fill(BG_COLOR)
        
        if game_state == "INSTRUCTIONS":
            title_surf = huge_font.render("STOCHASTIC SPACE", True, MAGENTA)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 100)))
            
            # ---> UPDATED RULES WITH EXPLICIT STRATEGY <---
            rules = [
                "Objective: Maintain a Sample Mean of 50.0",
                "1. Keep your Mean inside the [SAFE ZONE] at the bottom.",
                "2. TO KEEP SIGNIFICANCE: Balance your catches!",
                "   -> If Mean drifts RIGHT (high), catch LOW numbers to pull it left.",
                "   -> If Mean drifts LEFT (low), catch HIGH numbers to pull it right.",
                "3. ⚠ HARD MODE: Outliers (5 or 95) are hidden! READ the numbers.",
                "   Catching an outlier shrinks your safe zone permanently!",
                "",
                "Failure to maintain significance costs 1 LIFE.",
                "Controls: [A/D] or [ARROW KEYS]"
            ]
            
            for i, line in enumerate(rules):
                if i in [2, 3, 4]:
                    color = GOLD
                elif i in [5, 6]:
                    color = RED
                else:
                    color = WHITE
                
                line_surf = small_font.render(line, True, color)
                screen.blit(line_surf, line_surf.get_rect(center=(WIDTH//2, 190 + (i * 36))))
                
            start_btn.check_hover(mouse_pos)
            start_btn.draw(screen)

        elif game_state == "PLAYING" or game_state == "GAME_OVER":
            # Confidence Interval (Safe Zone)
            safe_left = WIDTH//2 - (margin_of_error * 10)
            safe_right = WIDTH//2 + (margin_of_error * 10)
            pygame.draw.rect(screen, (20, 30, 50), (safe_left, HEIGHT-150, safe_right - safe_left, 100))
            pygame.draw.line(screen, GREEN, (safe_left, HEIGHT-150), (safe_left, HEIGHT-50), 3)
            pygame.draw.line(screen, GREEN, (safe_right, HEIGHT-150), (safe_right, HEIGHT-50), 3)
            
            # Mean Marker
            mean_x = WIDTH//2 + (current_mean - target_mean) * 10
            pygame.draw.polygon(screen, WHITE, [(mean_x, HEIGHT-160), (mean_x-10, HEIGHT-185), (mean_x+10, HEIGHT-185)])
            mean_label = small_font.render(f"Mean: {current_mean:.1f}", True, WHITE)
            screen.blit(mean_label, (mean_x - mean_label.get_width()//2, HEIGHT-215))

            for d in data_points:
                pygame.draw.circle(screen, WHITE, d["rect"].center, 20)
                val_surf = small_font.render(str(d["val"]), True, BG_COLOR)
                screen.blit(val_surf, (d["rect"].centerx - val_surf.get_width()//2, d["rect"].centery - val_surf.get_height()//2))

            pygame.draw.rect(screen, MAGENTA, player_rect, border_radius=10)
            
            # UI
            score_surf = small_font.render(f"SAMPLES (n): {sample_count} | SCORE: {score}", True, WHITE)
            zone_surf = small_font.render(f"CONFIDENCE: ±{margin_of_error:.1f}", True, GREEN)
            screen.blit(score_surf, (20, 20))
            screen.blit(zone_surf, (20, 60))
            for i in range(lives):
                pygame.draw.circle(screen, RED, (WIDTH - 120 + (i * 40), 40), 12)

            if game_state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(220); overlay.fill((0,0,0))
                screen.blit(overlay, (0,0))
                go_surf = huge_font.render("INSIGNIFICANT RESULT", True, RED)
                final_surf = font.render(f"Final Score: {score}", True, WHITE)
                restart_surf = small_font.render("Press [R] to Resample or [ESC] for Menu", True, GRAY)
                screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 100))
                screen.blit(final_surf, (WIDTH//2 - final_surf.get_width()//2, HEIGHT//2 + 20))
                screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 90))

        pygame.display.flip()
        clock.tick(60)