import pygame
import random

class OE_Button:
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
    BG_COLOR = (10, 10, 25)
    LANE_COLOR = (20, 20, 45)
    HIGHLIGHT = (0, 200, 255)
    WHITE = (255, 255, 255)
    RED = (220, 50, 50)
    GREEN = (50, 220, 50)
    GOLD = (255, 215, 0)
    
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 35)
    huge_font = pygame.font.Font(None, 100)

    # UI Setup
    start_btn = OE_Button(WIDTH//2 - 200, HEIGHT - 150, 400, 70, "Start Optimization !", GREEN, (100, 255, 100), font)

    # Game Variables
    game_state = "INSTRUCTIONS" 
    score = 0
    lives = 3
    level = 1
    
    lane_count = 4
    lane_width = WIDTH // lane_count
    current_lane = 1 # 0 to 3
    
    # Path Data
    nodes = []
    constraint = "MIN" # MIN or MAX
    fall_speed = 4.0
    
    def generate_row():
        nonlocal nodes, constraint
        constraint = random.choice(["MIN", "MAX"])
        new_nodes = []
        
        # Level difficulty scaling
        for i in range(lane_count):
            if level < 3:
                val = random.randint(1, 20)
                display = str(val)
            else:
                # Mental Math constraints
                a, b = random.randint(1, 10), random.randint(1, 10)
                op = random.choice(["+", "-"])
                val = a + b if op == "+" else a - b
                display = f"{a}{op}{b}"
            
            new_nodes.append({"val": val, "text": display, "rect": pygame.Rect(i * lane_width + 20, -100, lane_width - 40, 80)})
        nodes = new_nodes

    generate_row()

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
                    score, lives, level, fall_speed = 0, 3, 1, 4.0
                    generate_row()
                    
                if game_state == "PLAYING":
                    if event.key in [pygame.K_LEFT, pygame.K_a] and current_lane > 0:
                        current_lane -= 1
                    if event.key in [pygame.K_RIGHT, pygame.K_d] and current_lane < 3:
                        current_lane += 1
                        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "INSTRUCTIONS" and start_btn.is_hovered:
                    game_state = "PLAYING"

        if game_state == "PLAYING":
            # Move Nodes
            for n in nodes:
                n["rect"].y += fall_speed
            
            # Check Collision
            player_rect = pygame.Rect(current_lane * lane_width + 20, HEIGHT - 120, lane_width - 40, 60)
            if any(player_rect.colliderect(n["rect"]) for n in nodes):
                # Did they hit the right one?
                values = [n["val"] for n in nodes]
                target_val = min(values) if constraint == "MIN" else max(values)
                
                # Check the value of the node in the current lane
                if nodes[current_lane]["val"] == target_val:
                    score += 10
                    if score % 50 == 0:
                        level += 1
                        fall_speed += 0.5
                else:
                    lives -= 1
                
                if lives <= 0:
                    game_state = "GAME_OVER"
                else:
                    generate_row()

            # Missed Check
            if nodes[0]["rect"].top > HEIGHT:
                lives -= 1
                if lives <= 0: game_state = "GAME_OVER"
                else: generate_row()

        # --- DRAWING ---
        screen.fill(BG_COLOR)
        
        if game_state == "INSTRUCTIONS":
            title_surf = huge_font.render("OPTIMIZE ENGINE", True, HIGHLIGHT)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 120)))
            
            rules = [
                "Objective: Find the Optimal Path through the network.",
                "1. Look at the CONSTRAINT at the top (MIN or MAX).",
                "2. Move your unit to the lane with the matching value.",
                "3. Watch out: Higher levels use arithmetic expressions!",
                "",
                "Wrong path or missing a node costs 1 LIFE.",
                "Use [LEFT/RIGHT] or [A/D] to move."
            ]
            
            for i, line in enumerate(rules):
                line_surf = small_font.render(line, True, WHITE if i < 4 else GOLD)
                screen.blit(line_surf, line_surf.get_rect(center=(WIDTH//2, 250 + (i * 45))))
                
            start_btn.check_hover(mouse_pos)
            start_btn.draw(screen)

        elif game_state == "PLAYING" or game_state == "GAME_OVER":
            # Draw Lanes
            for i in range(lane_count):
                color = (30, 30, 60) if i == current_lane else LANE_COLOR
                pygame.draw.rect(screen, color, (i * lane_width, 0, lane_width, HEIGHT))
                pygame.draw.line(screen, (50, 50, 100), (i * lane_width, 0), (i * lane_width, HEIGHT), 2)

            # Draw Constraint Header
            header_color = RED if constraint == "MIN" else GREEN
            header_label = "CONSTRAINT: MINIMIZE COST" if constraint == "MIN" else "CONSTRAINT: MAXIMIZE THROUGHPUT"
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 100))
            pygame.draw.line(screen, header_color, (0, 100), (WIDTH, 100), 4)
            h_surf = font.render(header_label, True, header_color)
            screen.blit(h_surf, (WIDTH//2 - h_surf.get_width()//2, 25))

            # Draw Nodes
            for n in nodes:
                pygame.draw.rect(screen, (40, 40, 80), n["rect"], border_radius=10)
                pygame.draw.rect(screen, HIGHLIGHT, n["rect"], 2, border_radius=10)
                t_surf = font.render(n["text"], True, WHITE)
                screen.blit(t_surf, (n["rect"].centerx - t_surf.get_width()//2, n["rect"].centery - t_surf.get_height()//2))

            # Draw Player Unit
            p_rect = pygame.Rect(current_lane * lane_width + 20, HEIGHT - 120, lane_width - 40, 60)
            pygame.draw.rect(screen, HIGHLIGHT, p_rect, border_radius=15)
            pygame.draw.rect(screen, WHITE, p_rect.inflate(-10, -10), 2, border_radius=10)
            
            # UI
            score_surf = small_font.render(f"EFFICIENCY: {score}", True, WHITE)
            level_surf = small_font.render(f"LEVEL: {level}", True, GOLD)
            screen.blit(score_surf, (20, 120))
            screen.blit(level_surf, (WIDTH - 150, 120))
            for i in range(lives):
                pygame.draw.circle(screen, RED, (WIDTH // 2 - 40 + (i * 40), 130), 12)

            if game_state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(220); overlay.fill((0,0,0))
                screen.blit(overlay, (0,0))
                go_surf = huge_font.render("OPTIMIZATION FAILED", True, RED)
                final_surf = font.render(f"Final Efficiency: {score}", True, WHITE)
                restart_surf = small_font.render("Press [R] to Reboot or [ESC] for Menu", True, (150, 150, 150))
                screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 100))
                screen.blit(final_surf, (WIDTH//2 - final_surf.get_width()//2, HEIGHT//2 + 20))
                screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 90))

        pygame.display.flip()
        clock.tick(60)