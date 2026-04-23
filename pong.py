import pygame
import random

def start_pong(screen, is_muted, players, max_points, p1_name="P1", p2_name="P2"):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    
    # Colors
    BG_COLOR = (10, 10, 30)
    WHITE = (255, 255, 255)
    CYAN = (0, 255, 255)
    GRAY = (120, 120, 120)
    
    # Fonts
    font = pygame.font.Font(None, 80)
    small_font = pygame.font.Font(None, 40)
    tiny_font = pygame.font.Font(None, 30)
    
    # Game Objects
    p_w, p_h = 15, 100
    p1 = pygame.Rect(30, HEIGHT//2 - p_h//2, p_w, p_h)
    p2 = pygame.Rect(WIDTH - 30 - p_w, HEIGHT//2 - p_h//2, p_w, p_h)
    ball = pygame.Rect(WIDTH//2 - 10, HEIGHT//2 - 10, 20, 20)
    
    ball_speed_x = 7 * random.choice((1, -1))
    ball_speed_y = 7 * random.choice((1, -1))
    p_speed = 8
    
    # State Variables
    score1, score2 = 0, 0
    frame_count = 0 
    game_over = False
    winner_text = ""

    # Prepare Limit Text
    limit_label = f"LIMIT: {max_points}" if max_points > 0 else "LIMIT: INFINITY"

    running = True
    while running:
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return # Back to menu
                if event.key == pygame.K_r and game_over:
                    score1, score2 = 0, 0
                    game_over = False
                    frame_count = 0
                    ball.center = (WIDTH//2, HEIGHT//2)
                    ball_speed_x = 7 * random.choice((1, -1))

        if not game_over:
            # 1. Player 1 Movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and p1.top > 0: p1.y -= p_speed
            if keys[pygame.K_s] and p1.bottom < HEIGHT: p1.y += p_speed
            
            # 2. Player 2 Movement (AI or Human)
            if players == 2:
                if keys[pygame.K_UP] and p2.top > 0: p2.y -= p_speed
                if keys[pygame.K_DOWN] and p2.bottom < HEIGHT: p2.y += p_speed
            else:
                # Simple AI Logic
                if p2.centery < ball.centery and p2.bottom < HEIGHT:
                    p2.y += p_speed - 1
                if p2.centery > ball.centery and p2.top > 0:
                    p2.y -= p_speed - 1

            # 3. Ball Physics
            ball.x += ball_speed_x
            ball.y += ball_speed_y
            
            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_speed_y *= -1
                
            if ball.colliderect(p1) or ball.colliderect(p2):
                ball_speed_x *= -1.08 # Gentle speed increase
                
            # 4. Scoring Logic
            if ball.left <= 0:
                score2 += 1
                ball.center = (WIDTH//2, HEIGHT//2)
                ball_speed_x = 7 * random.choice((1, -1))
            if ball.right >= WIDTH:
                score1 += 1
                ball.center = (WIDTH//2, HEIGHT//2)
                ball_speed_x = 7 * random.choice((1, -1))

            # 5. Check Win Condition
            if max_points > 0:
                if score1 >= max_points:
                    game_over = True
                    winner_text = f"{p1_name.upper()} WINS!"
                elif score2 >= max_points:
                    game_over = True
                    winner_text = f"{p2_name.upper()} WINS!" if players == 2 else "AI WINS!"

        # --- DRAWING ---
        screen.fill(BG_COLOR)
        
        # Draw Field Decor
        pygame.draw.aaline(screen, (40, 40, 60), (WIDTH//2, 0), (WIDTH//2, HEIGHT))
        
        # Draw Paddles & Ball
        pygame.draw.rect(screen, CYAN, p1)
        pygame.draw.rect(screen, WHITE, p2)
        pygame.draw.ellipse(screen, WHITE, ball)
        
        # Draw Scoreboard
        s1_surf = font.render(str(score1), True, WHITE)
        s2_surf = font.render(str(score2), True, WHITE)
        screen.blit(s1_surf, (WIDTH//2 - 120, 40))
        screen.blit(s2_surf, (WIDTH//2 + 60, 40))
        
        # Draw Win Limit Indicator (Below the scores)
        limit_surf = tiny_font.render(limit_label, True, GRAY)
        screen.blit(limit_surf, (WIDTH//2 - limit_surf.get_width()//2, 110))

        # --- CONTROLS vs NAMES LOGIC ---
        if frame_count <= 300 and not game_over:
            # Show controls for first 5 seconds
            p1_ctrl = small_font.render("[W][S] TO MOVE", True, GRAY)
            screen.blit(p1_ctrl, (p1.right + 20, p1.centery))
            
            if players == 2:
                p2_ctrl = small_font.render("[UP][DOWN] TO MOVE", True, GRAY)
                screen.blit(p2_ctrl, (p2.left - p2_ctrl.get_width() - 20, p2.centery))
            else:
                ai_ctrl = small_font.render("AI PADDLE", True, (60, 60, 80))
                screen.blit(ai_ctrl, (p2.left - ai_ctrl.get_width() - 20, p2.centery))
        elif not game_over:
            # Fade out controls and show names!
            p1_name_surf = tiny_font.render(p1_name.upper(), True, CYAN)
            screen.blit(p1_name_surf, (p1.centerx - p1_name_surf.get_width()//2, p1.top - 25))
            
            p2_name_surf = tiny_font.render(p2_name.upper(), True, WHITE)
            screen.blit(p2_name_surf, (p2.centerx - p2_name_surf.get_width()//2, p2.top - 25))

        # Game Over View
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            
            win_surf = font.render(winner_text, True, CYAN)
            restart_surf = small_font.render("Press [R] to Restart or [ESC] for Menu", True, WHITE)
            screen.blit(win_surf, (WIDTH//2 - win_surf.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 50))

        pygame.display.flip()
        clock.tick(60)