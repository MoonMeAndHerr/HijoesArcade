import pygame
import random

def start_starship(screen, is_muted, players, p1_name="P1", p2_name="P2"):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    
    # Colors
    WHITE = (255, 255, 255)
    P1_C = (0, 200, 255)
    P2_C = (50, 255, 50)
    STAR = (255, 215, 0)
    AST = (200, 50, 50)
    BG_COLOR = (10, 10, 25)
    
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 35)
    tiny_font = pygame.font.Font(None, 25)
    
    def reset_game():
        p1 = pygame.Rect(WIDTH//3, HEIGHT - 100, 30, 40)
        p2 = pygame.Rect(2*WIDTH//3, HEIGHT - 100, 30, 40) if players == 2 else None
        return p1, p2, [], [], 0, 3, (3 if players == 2 else 0), False, 5.0, 45

    p1, p2, stars, asts, score, l1, l2, game_over, spd, rate = reset_game()
    frame_count = 0

    running = True
    while running:
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return score # Back to menu
                if event.key == pygame.K_r and game_over:
                    p1, p2, stars, asts, score, l1, l2, game_over, spd, rate = reset_game()
                    frame_count = 0

        if not game_over:
            keys = pygame.key.get_pressed()
            
            # 1. Player 1 Movement
            if l1 > 0:
                if keys[pygame.K_w] and p1.top > 0: p1.y -= 9
                if keys[pygame.K_s] and p1.bottom < HEIGHT: p1.y += 9
                if keys[pygame.K_a] and p1.left > 0: p1.x -= 9
                if keys[pygame.K_d] and p1.right < WIDTH: p1.x += 9
                
            # 2. Player 2 Movement
            if players == 2 and l2 > 0:
                if keys[pygame.K_UP] and p2.top > 0: p2.y -= 9
                if keys[pygame.K_DOWN] and p2.bottom < HEIGHT: p2.y += 9
                if keys[pygame.K_LEFT] and p2.left > 0: p2.x -= 9
                if keys[pygame.K_RIGHT] and p2.right < WIDTH: p2.x += 9

            # 3. Spawn Entities
            if frame_count % max(15, rate - (score // 5) * 2) == 0:
                asts.append(pygame.Rect(random.randint(0, WIDTH - 50), -50, 45, 45))
            if frame_count % 40 == 0:
                stars.append(pygame.Rect(random.randint(0, WIDTH - 25), -25, 25, 25))

            # 4. Update Entities & Collisions
            cur_spd = spd + (score // 10) 
            
            for s in stars[:]:
                s.y += cur_spd - 1
                if s.top > HEIGHT: 
                    stars.remove(s)
                elif (l1 > 0 and p1.colliderect(s)) or (players == 2 and l2 > 0 and p2.colliderect(s)):
                    stars.remove(s)
                    score += 1
                    
            for a in asts[:]:
                a.y += cur_spd
                if a.top > HEIGHT: 
                    asts.remove(a)
                elif l1 > 0 and p1.colliderect(a): 
                    asts.remove(a)
                    l1 -= 1
                elif players == 2 and l2 > 0 and p2.colliderect(a): 
                    asts.remove(a)
                    l2 -= 1
                    
            # 5. Check Game Over
            if l1 <= 0 and (players == 1 or l2 <= 0): 
                game_over = True

        # --- DRAWING ---
        screen.fill(BG_COLOR)
        
        for s in stars: 
            pygame.draw.circle(screen, STAR, s.center, 12)
        for a in asts: 
            pygame.draw.rect(screen, AST, a, border_radius=8)
            
        if not game_over:
            if l1 > 0: 
                pygame.draw.polygon(screen, P1_C, [(p1.centerx, p1.top), (p1.left, p1.bottom), (p1.right, p1.bottom)])
            if players == 2 and l2 > 0: 
                pygame.draw.polygon(screen, P2_C, [(p2.centerx, p2.top), (p2.left, p2.bottom), (p2.right, p2.bottom)])

        # Draw UI
        score_surf = font.render(f"TEAM SCORE: {score}", True, WHITE)
        screen.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, 20))
        
        l1_surf = small_font.render(f"{p1_name.upper()}: {l1}", True, P1_C)
        screen.blit(l1_surf, (20, 20))
        
        if players == 2:
            l2_surf = small_font.render(f"{p2_name.upper()}: {l2}", True, P2_C)
            screen.blit(l2_surf, (WIDTH - l2_surf.get_width() - 20, 20))

        # --- CONTROLS vs NAMES LOGIC ---
        if frame_count <= 300 and not game_over:
            if l1 > 0:
                p1_ctrl = tiny_font.render("[WASD] MOVE", True, (150, 150, 150))
                screen.blit(p1_ctrl, (p1.centerx - p1_ctrl.get_width()//2, p1.top - 25))
            if players == 2 and l2 > 0:
                p2_ctrl = tiny_font.render("[ARROWS] MOVE", True, (150, 150, 150))
                screen.blit(p2_ctrl, (p2.centerx - p2_ctrl.get_width()//2, p2.top - 25))
        elif not game_over:
            if l1 > 0:
                p1_n_surf = tiny_font.render(p1_name.upper(), True, P1_C)
                screen.blit(p1_n_surf, (p1.centerx - p1_n_surf.get_width()//2, p1.top - 25))
            if players == 2 and l2 > 0:
                p2_n_surf = tiny_font.render(p2_name.upper(), True, P2_C)
                screen.blit(p2_n_surf, (p2.centerx - p2_n_surf.get_width()//2, p2.top - 25))

        # Game Over View
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            
            # ---> FIX: Cumulative Score Display instead of Mission Failed!
            go_surf = font.render(f"FINAL SCORE: {score}", True, STAR)
            restart_surf = small_font.render("Press [R] to Play Again or [ESC] for Menu", True, WHITE)
            screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 50))

        pygame.display.flip()
        clock.tick(60)