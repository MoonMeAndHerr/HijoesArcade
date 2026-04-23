import pygame
import random

def start_game(screen, is_muted):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    
    # Audio
    if not is_muted: pygame.mixer.music.pause()
    edu_music = None
    try:
        edu_music = pygame.mixer.Sound("bg_music.mp3") 
        edu_music.set_volume(0.3)
        if not is_muted: edu_music.play(loops=-1)
    except FileNotFoundError: pass

    # Colors (Added WHITE!)
    BG_COLOR = (15, 10, 25)
    ORB_COLOR = (200, 100, 255)
    TRUE_COLOR = (0, 255, 150)
    FALSE_COLOR = (255, 50, 100)
    WALL_COLOR = (50, 40, 80)
    TEXT_COLOR = (255, 255, 255)
    WHITE = (255, 255, 255)
    
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 35)
    math_font = pygame.font.Font(None, 55)

    # Pure Math Statements 
    QUESTIONS = [
        {"q": "There are infinitely many prime numbers.", "ans": True},
        {"q": "Every continuous function is differentiable.", "ans": False},
        {"q": "The set of real numbers is countable.", "ans": False},
        {"q": "e^(iπ) + 1 = 0", "ans": True},
        {"q": "The empty set is a subset of every set.", "ans": True},
        {"q": "A matrix with determinant 0 is invertible.", "ans": False},
        {"q": "The intersection of two open sets is always open.", "ans": True},
        {"q": "The union of infinitely many closed sets is always closed.", "ans": False},
        {"q": "Every integer can be written as the sum of 4 squares.", "ans": True},
        {"q": "π (Pi) is a rational number.", "ans": False},
        {"q": "All vector spaces have a basis.", "ans": True},
        {"q": "1 is a prime number.", "ans": False}
    ]

    # Player Setup
    orb_x = 150
    orb_y = HEIGHT // 2
    orb_radius = 20
    orb_speed = 8
    
    # Game Variables
    score = 0
    lives = 3
    game_over = False
    wall_speed = 6.0
    
    # Wall Setup
    wall_x = WIDTH
    wall_width = 40
    current_q = random.choice(QUESTIONS)
    
    # Particle trail for the orb
    trail = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if edu_music: edu_music.stop()
                    if not is_muted: pygame.mixer.music.unpause()
                    return score
                if event.key == pygame.K_r and game_over:
                    score, lives, game_over, wall_speed = 0, 3, False, 6.0
                    wall_x = WIDTH
                    current_q = random.choice(QUESTIONS)
                    trail.clear()

        keys = pygame.key.get_pressed()
        
        if not game_over:
            # Move Orb (Up and Down only)
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and orb_y - orb_radius > 0:
                orb_y -= orb_speed
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and orb_y + orb_radius < HEIGHT:
                orb_y += orb_speed
                
            # Add to particle trail
            trail.append((orb_x, orb_y))
            if len(trail) > 15: trail.pop(0)

            # Move Wall
            wall_x -= wall_speed
            
            # Check if wall passes the orb
            if wall_x < orb_x and wall_x + wall_speed >= orb_x:
                chose_true = orb_y < HEIGHT // 2
                
                if chose_true == current_q["ans"]:
                    score += 10
                    wall_speed += 0.2 
                else:
                    lives -= 1
                    
                wall_x = WIDTH
                current_q = random.choice(QUESTIONS)
                
                if lives <= 0:
                    game_over = True

        # Drawing
        screen.fill(BG_COLOR)
        
        pygame.draw.line(screen, (40, 30, 60), (0, HEIGHT//2), (WIDTH, HEIGHT//2), 2)
        
        if not game_over:
            # Top Gate (TRUE)
            pygame.draw.rect(screen, TRUE_COLOR, (wall_x, 0, wall_width, HEIGHT//2), 3)
            pygame.draw.rect(screen, (0, 100, 50), (wall_x, 0, wall_width, HEIGHT//2))
            
            # Bottom Gate (FALSE)
            pygame.draw.rect(screen, FALSE_COLOR, (wall_x, HEIGHT//2, wall_width, HEIGHT//2), 3)
            pygame.draw.rect(screen, (100, 0, 0), (wall_x, HEIGHT//2, wall_width, HEIGHT//2))

            t_label = small_font.render("TRUE", True, TRUE_COLOR)
            f_label = small_font.render("FALSE", True, FALSE_COLOR)
            screen.blit(t_label, (wall_x - 10, HEIGHT // 4))
            screen.blit(f_label, (wall_x - 15, HEIGHT * 3 // 4))

            q_surf = math_font.render(current_q["q"], True, TEXT_COLOR)
            text_bg = pygame.Rect(WIDTH//2 - q_surf.get_width()//2 - 20, 80, q_surf.get_width() + 40, q_surf.get_height() + 20)
            pygame.draw.rect(screen, BG_COLOR, text_bg)
            pygame.draw.rect(screen, ORB_COLOR, text_bg, 2, border_radius=10)
            screen.blit(q_surf, (WIDTH//2 - q_surf.get_width()//2, 90))

            # Draw Trail
            for i, pos in enumerate(trail):
                alpha = int(255 * (i / len(trail)))
                radius = int(orb_radius * (i / len(trail)))
                trail_color = (
                    min(255, BG_COLOR[0] + (ORB_COLOR[0] - BG_COLOR[0]) * alpha // 255),
                    min(255, BG_COLOR[1] + (ORB_COLOR[1] - BG_COLOR[1]) * alpha // 255),
                    min(255, BG_COLOR[2] + (ORB_COLOR[2] - BG_COLOR[2]) * alpha // 255),
                )
                pygame.draw.circle(screen, trail_color, pos, max(1, radius))

            # Draw Orb
            pygame.draw.circle(screen, ORB_COLOR, (orb_x, orb_y), orb_radius)
            pygame.draw.circle(screen, WHITE, (orb_x, orb_y), orb_radius - 5)
            
            if score == 0:
                tut = small_font.render("Fly UP for TRUE, DOWN for FALSE", True, (150, 150, 150))
                screen.blit(tut, (10, HEIGHT - 40))

        # Draw UI
        score_surf = small_font.render(f"THEOREMS PROVEN: {score}", True, WHITE)
        screen.blit(score_surf, (20, 20))
        for i in range(lives):
            pygame.draw.circle(screen, ORB_COLOR, (WIDTH - 120 + (i * 40), 30), 12)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(200); overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            go_surf = pygame.font.Font(None, 120).render("LOGIC FAILED", True, FALSE_COLOR)
            score_res = font.render(f"Theorems Proven: {score}", True, ORB_COLOR)
            restart_surf = small_font.render("Press [R] to Retry or [ESC] for Main System", True, WHITE)
            screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 100))
            screen.blit(score_res, (WIDTH//2 - score_res.get_width()//2, HEIGHT//2 + 10))
            screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 80))

        pygame.display.flip()
        clock.tick(60)