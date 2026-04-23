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
    BG_COLOR = (10, 20, 15)
    CORE_COLOR = (0, 255, 150)
    BLOCK_COLOR = (40, 80, 60)
    TEXT_COLOR = (255, 255, 255)
    LANE_COLOR = (20, 40, 30)
    WHITE = (255, 255, 255) 
    
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    math_font = pygame.font.Font(None, 70)

    # Computational Math Question Bank
    QUESTIONS = [
        {"q": "Root of x^2 - 16 = 0 (x > 0)", "c": "4", "w1": "8", "w2": "2"},
        {"q": "Derivative of x^3 at x = 2", "c": "12", "w1": "6", "w2": "8"},
        {"q": "Det of Matrix [[3, 1], [0, 2]]", "c": "6", "w1": "5", "w2": "3"},
        {"q": "Binary 1010 in Decimal", "c": "10", "w1": "12", "w2": "8"},
        {"q": "Integral of 2x dx from 0 to 2", "c": "4", "w1": "2", "w2": "8"},
        {"q": "Value of 5! (Factorial)", "c": "120", "w1": "60", "w2": "24"},
        {"q": "Log base 2 of 8", "c": "3", "w1": "4", "w2": "16"},
        {"q": "Next in sequence: 1, 1, 2, 3, 5, ?", "c": "8", "w1": "7", "w2": "9"},
        {"q": "Root of f(x) = 2x - 10", "c": "5", "w1": "-5", "w2": "10"},
        {"q": "Hexadecimal 'A' in Decimal", "c": "10", "w1": "11", "w2": "16"}
    ]

    # Lanes setup (3 Lanes)
    lane_width = 250
    lane_x = [WIDTH//2 - lane_width*1.5, WIDTH//2 - lane_width//2, WIDTH//2 + lane_width//2]
    
    # Player Setup
    current_lane = 1 
    core_rect = pygame.Rect(lane_x[current_lane] + 25, HEIGHT - 100, 200, 40)
    
    # Game Variables
    score = 0
    lives = 3
    game_over = False
    fall_speed = 4.0
    
    # Block Setup
    blocks = []
    current_q = None
    
    def generate_question():
        nonlocal current_q, blocks, fall_speed
        current_q = random.choice(QUESTIONS)
        answers = [current_q["c"], current_q["w1"], current_q["w2"]]
        random.shuffle(answers)
        
        blocks = []
        for i in range(3):
            blocks.append({
                "rect": pygame.Rect(lane_x[i] + 25, -100, 200, 100),
                "text": answers[i],
                "is_correct": answers[i] == current_q["c"]
            })
        fall_speed += 0.2 

    generate_question()

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
                    score, lives, game_over, fall_speed = 0, 3, False, 4.0
                    generate_question()
                    
                if not game_over:
                    if event.key in [pygame.K_LEFT, pygame.K_a] and current_lane > 0:
                        current_lane -= 1
                    if event.key in [pygame.K_RIGHT, pygame.K_d] and current_lane < 2:
                        current_lane += 1
                        
        core_rect.x = lane_x[current_lane] + 25

        if not game_over:
            # Move blocks down
            for b in blocks:
                b["rect"].y += fall_speed
                
                # Collision Check
                if core_rect.colliderect(b["rect"]):
                    if b["is_correct"]:
                        score += 10
                    else:
                        lives -= 1
                    generate_question()
                    break 
                    
                # Missed Check 
                elif b["rect"].top > HEIGHT:
                    lives -= 1
                    generate_question()
                    break

            if lives <= 0:
                game_over = True

        # Drawing
        screen.fill(BG_COLOR)
        
        # Draw Lanes
        for lx in lane_x:
            pygame.draw.rect(screen, LANE_COLOR, (lx, 0, lane_width, HEIGHT))
            pygame.draw.line(screen, (50, 90, 70), (lx, 0), (lx, HEIGHT), 2)
        pygame.draw.line(screen, (50, 90, 70), (lane_x[-1]+lane_width, 0), (lane_x[-1]+lane_width, HEIGHT), 2)

        if not game_over:
            # Draw Question
            q_surf = math_font.render(current_q["q"], True, (255, 255, 100))
            screen.blit(q_surf, (WIDTH//2 - q_surf.get_width()//2, 50))
            
            # Draw Blocks
            for b in blocks:
                pygame.draw.rect(screen, BLOCK_COLOR, b["rect"], border_radius=10)
                pygame.draw.rect(screen, CORE_COLOR, b["rect"], 3, border_radius=10)
                t_surf = font.render(b["text"], True, TEXT_COLOR)
                screen.blit(t_surf, (b["rect"].centerx - t_surf.get_width()//2, b["rect"].centery - t_surf.get_height()//2))

            # Draw Core (Player)
            pygame.draw.rect(screen, CORE_COLOR, core_rect, border_radius=20)
            pygame.draw.rect(screen, WHITE, core_rect.inflate(-10, -10), 2, border_radius=15)
            
        # Draw UI
        score_surf = small_font.render(f"DATA MINED: {score}", True, WHITE)
        screen.blit(score_surf, (20, 20))
        for i in range(lives):
            pygame.draw.circle(screen, CORE_COLOR, (WIDTH - 120 + (i * 40), 30), 15)

        # Game Over Screen
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(200); overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            go_surf = pygame.font.Font(None, 120).render("SYSTEM FAILURE", True, (255, 50, 50))
            score_res = font.render(f"Final Data Mined: {score}", True, CORE_COLOR)
            restart_surf = small_font.render("Press [R] to Reboot or [ESC] for Main System", True, WHITE)
            screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 100))
            screen.blit(score_res, (WIDTH//2 - score_res.get_width()//2, HEIGHT//2 + 10))
            screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 80))

        pygame.display.flip()
        clock.tick(60)