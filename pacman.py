import pygame
import random
import math

# Added p1_name and p2_name parameters
def start_pacman(screen, is_muted, players, p1_name="Player 1", p2_name="Player 2"):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    
    # Silence arcade background music and play Pacman music
    if not is_muted:
        pygame.mixer.music.pause()
        
    pacman_music = None
    try:
        pacman_music = pygame.mixer.Sound("pacman_bg.mp3")
        pacman_music.set_volume(0.4)
        if not is_muted:
            pacman_music.play(loops=-1)
    except FileNotFoundError:
        pass

    # Colors
    BG_COLOR = (5, 5, 10)
    WALL_COLOR = (20, 50, 150)
    DOT_COLOR = (255, 200, 150)
    POWER_COLOR = (255, 255, 255)
    P1_COLOR = (255, 255, 0)   
    P2_COLOR = (0, 255, 0)     
    GHOST_COLORS = [(255, 0, 0), (255, 150, 200), (0, 255, 255), (255, 150, 0)] 
    SCARED_COLOR = (50, 100, 255)
    
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 35)
    tiny_font = pygame.font.Font(None, 22) # Added for the name tags above the characters

    # Level Designs 
    HALF_MAPS = [
        # Level 1
        [
            "WWWWWWWWWWWWWWWW",
            "W..O..........WW",
            "W.WWWW.WWWWWW.WW",
            "W.WWWW.WWWWWW.WW",
            "W...............",
            "W.WWWW.WW.WWWWWW",
            "W......WW......W",
            "WWWWWW.WWWWWWW W",
            "WWWWWW.WW       ", 
            "WWWWWW.WW WWWW  ", 
            "W.....    W     ", 
            "WWWWWW.WW WWWWWW",
            "W..............W",
            "W.WWWW.WWWWWWW.W",
            "W..O.W.........W",
            "WWWW.W.WW.WWWWWW",
            "W......WW......W",
            "WWWWWWWWWWWWWWWW"
        ],
        # Level 2 
        [
            "WWWWWWWWWWWWWWWW",
            "W..O.W........WW",
            "W.WW.W.WWWWWW.WW",
            "W.WW.W.W......WW",
            "W.WW...W.WWWWWWW",
            "W.WWWW.W.......W",
            "W......WWWWWWW.W",
            "WWWWWW.WWWWWWW W", 
            "WWWWWW.WW       ", 
            "WWWWWW.WW WWWW  ", 
            "W.....    W     ", 
            "WWWWWW.WW WWWWWW",
            "W......WW......W",
            "W.WWWWWWWWWWWW.W",
            "W..O.....WWWWW.W",
            "WWWWWWWW.W.....W",
            "W........W.WWWWW",
            "WWWWWWWWWWWWWWWW"
        ],
        # Level 3 
        [
            "WWWWWWWWWWWWWWWW",
            "W..O.....W....WW",
            "W.WWWWWW.W.WWW.W",
            "W.W......W.W...W",
            "W.W.WWWWWW.W.WWW",
            "W.W......W.W...W",
            "W.WWWWWW.W.WWW.W",
            "WWWWWW.WWWWWWW W", 
            "WWWWWW.WW       ", 
            "WWWWWW.WW WWWW  ", 
            "W.....    W     ", 
            "WWWWWW.WW WWWWWW",
            "W.W......W.W...W",
            "W.W.WWWWWW.W.W.W",
            "W.W........W.W.W",
            "W.WWWWWWWWWW.W.W",
            "W..O.........W.W",
            "WWWWWWWWWWWWWWWW"
        ],
        # Level 4 
        [
            "WWWWWWWWWWWWWWWW",
            "W..O.W....W...WW",
            "W.WW.W.WW.W.WW.W",
            "W.WW.W.WW.W.WW.W",
            "W..............W",
            "W.WW.W.WW.W.WW.W",
            "W.WW.W.WW.W.WW.W",
            "WWWWWW.WWWWWWW W", 
            "WWWWWW.WW       ", 
            "WWWWWW.WW WWWW  ", 
            "W.....    W     ", 
            "WWWWWW.WW WWWWWW",
            "W..............W",
            "W.WW.W.WW.W.WW.W",
            "W.WW.W.WW.W.WW.W",
            "W.WW.W.WW.W.WW.W",
            "W..O.W....W....W",
            "WWWWWWWWWWWWWWWW"
        ],
        # Level 5
        [
            "WWWWWWWWWWWWWWWW",
            "W..O..........WW",
            "W.WWWWWWWWWWWW.W",
            "W.W..........W.W",
            "W.W.WWWWWWWW.W.W",
            "W.W.W......W.W.W",
            "W.W.W.WWWW.W.W.W",
            "WWWWWW.WWWWWWW W", 
            "WWWWWW.WW       ", 
            "WWWWWW.WW WWWW  ", 
            "W.....    W     ", 
            "WWWWWW.WW WWWWWW",
            "W.W.W.WWWW.W.W.W",
            "W.W.W......W.W.W",
            "W.W.WWWWWWWW.W.W",
            "W.W..........W.W",
            "W.WWWWWWWWWWWW.W",
            "WWWWWWWWWWWWWWWW"
        ]
    ]
    TILE_SIZE = 40
    
    def build_level(level_idx):
        layout = [h + h[::-1] for h in HALF_MAPS[level_idx]]
        walls, dots, powers = [], [], []
        for row_idx, row in enumerate(layout):
            for col_idx, tile in enumerate(row):
                x, y = col_idx * TILE_SIZE, row_idx * TILE_SIZE
                if tile == "W": walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == ".": dots.append(pygame.Rect(x + 15, y + 15, 10, 10))
                elif tile == "O": powers.append(pygame.Rect(x + 10, y + 10, 20, 20))
        return walls, dots, powers

    # Drawing functions
    def draw_pacman(surface, color, rect, direction, frame):
        center = rect.center
        radius = rect.width // 2
        pygame.draw.circle(surface, color, center, radius)
        
        if (frame // 8) % 2 == 0 and direction != (0, 0):
            angles = { (1,0): (45, 315), (-1,0): (225, 135), (0,1): (135, 45), (0,-1): (315, 225) }
            start_a, end_a = angles.get(direction, (45, 315))
            p1 = (center[0] + radius * math.cos(math.radians(start_a)), center[1] - radius * math.sin(math.radians(start_a)))
            p2 = (center[0] + radius * math.cos(math.radians(end_a)), center[1] - radius * math.sin(math.radians(end_a)))
            pygame.draw.polygon(surface, BG_COLOR, [center, p1, p2])

    def draw_ghost(surface, color, rect, state):
        if state == "DEAD": 
            pygame.draw.circle(surface, (255,255,255), (rect.left+10, rect.top+12), 5)
            pygame.draw.circle(surface, (255,255,255), (rect.right-10, rect.top+12), 5)
            pygame.draw.circle(surface, (0,0,255), (rect.left+10, rect.top+12), 2)
            pygame.draw.circle(surface, (0,0,255), (rect.right-10, rect.top+12), 2)
            return
            
        c = SCARED_COLOR if state == "SCARED" else color
        pygame.draw.circle(surface, c, (rect.centerx, rect.centery), rect.width//2)
        pygame.draw.rect(surface, c, (rect.left, rect.centery, rect.width, rect.height//2))
        r = rect.width // 6
        pygame.draw.circle(surface, c, (rect.left + r, rect.bottom), r)
        pygame.draw.circle(surface, c, (rect.centerx, rect.bottom), r)
        pygame.draw.circle(surface, c, (rect.right - r, rect.bottom), r)
        
        if state != "SCARED":
            pygame.draw.circle(surface, (255,255,255), (rect.left+10, rect.top+12), 4)
            pygame.draw.circle(surface, (255,255,255), (rect.right-10, rect.top+12), 4)

    # Game State Setup
    current_level = 1
    max_level = 5
    score = 0
    
    # Independent Lives
    p1_lives = 3
    p2_lives = 3 if players == 2 else 0
    
    game_over = False
    game_won = False
    frame_count = 0
    scared_timer = 0
    
    walls, dots, powers = build_level(0)
    
    p1_rect = pygame.Rect(1 * TILE_SIZE + 5, 1 * TILE_SIZE + 5, 30, 30)
    p2_rect = pygame.Rect(30 * TILE_SIZE + 5, 1 * TILE_SIZE + 5, 30, 30) if players == 2 else None
    p1_dir, p2_dir = (0,0), (0,0)
    p_speed = 5
    
    ghosts = []
    def spawn_ghosts(level):
        nonlocal ghosts
        ghosts = []
        num_ghosts = 3 + level 
        for i in range(num_ghosts):
            rect = pygame.Rect((14 + i%4) * TILE_SIZE + 5, 8 * TILE_SIZE + 5, 30, 30)
            ghosts.append({
                "id": i,
                "rect": rect,
                "dir": random.choice([(1,0), (-1,0), (0,1), (0,-1)]),
                "color": GHOST_COLORS[i % len(GHOST_COLORS)],
                "state": "NORMAL", 
                "dead_timer": 0
            })
    spawn_ghosts(current_level)

    def move_entity(rect, dx, dy, speed):
        rect.x += dx * speed
        for wall in walls:
            if rect.colliderect(wall):
                if dx > 0: rect.right = wall.left
                if dx < 0: rect.left = wall.right
                
        rect.y += dy * speed
        for wall in walls:
            if rect.colliderect(wall):
                if dy > 0: rect.bottom = wall.top
                if dy < 0: rect.top = wall.bottom

    running = True
    while running:
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pacman_music: pacman_music.stop()
                    if not is_muted: pygame.mixer.music.unpause()
                    return score
                if event.key == pygame.K_r and (game_over or game_won):
                    current_level, score, game_over, game_won, frame_count = 1, 0, False, False, 0
                    p1_lives = 3
                    p2_lives = 3 if players == 2 else 0
                    walls, dots, powers = build_level(0)
                    spawn_ghosts(current_level)
                    p1_rect.topleft = (1 * TILE_SIZE + 5, 1 * TILE_SIZE + 5)
                    if players == 2: p2_rect.topleft = (30 * TILE_SIZE + 5, 1 * TILE_SIZE + 5)

        keys = pygame.key.get_pressed()
        
        if not game_over and not game_won:
            # Player 1 Movement
            if p1_lives > 0:
                dx1, dy1 = 0, 0
                if keys[pygame.K_w]: dy1 = -1; p1_dir = (0,-1)
                elif keys[pygame.K_s]: dy1 = 1; p1_dir = (0,1)
                elif keys[pygame.K_a]: dx1 = -1; p1_dir = (-1,0)
                elif keys[pygame.K_d]: dx1 = 1; p1_dir = (1,0)
                move_entity(p1_rect, dx1, dy1, p_speed)
            
            # Player 2 Movement
            if players == 2 and p2_lives > 0:
                dx2, dy2 = 0, 0
                if keys[pygame.K_UP]: dy2 = -1; p2_dir = (0,-1)
                elif keys[pygame.K_DOWN]: dy2 = 1; p2_dir = (0,1)
                elif keys[pygame.K_LEFT]: dx2 = -1; p2_dir = (-1,0)
                elif keys[pygame.K_RIGHT]: dx2 = 1; p2_dir = (1,0)
                move_entity(p2_rect, dx2, dy2, p_speed)

            # Scared Timer
            if scared_timer > 0:
                scared_timer -= 1
                if scared_timer == 0:
                    for g in ghosts:
                        if g["state"] == "SCARED": g["state"] = "NORMAL"

            # Eating Dots & Powers
            for dot in dots[:]:
                if (p1_lives > 0 and p1_rect.colliderect(dot)) or (players == 2 and p2_lives > 0 and p2_rect.colliderect(dot)):
                    dots.remove(dot)
                    score += 10
            
            for p_pellet in powers[:]:
                if (p1_lives > 0 and p1_rect.colliderect(p_pellet)) or (players == 2 and p2_lives > 0 and p2_rect.colliderect(p_pellet)):
                    powers.remove(p_pellet)
                    score += 50
                    scared_timer = 600 
                    for g in ghosts:
                        if g["state"] == "NORMAL": g["state"] = "SCARED"

            # Level Up
            if len(dots) == 0 and len(powers) == 0:
                current_level += 1
                if current_level > max_level:
                    game_won = True
                else:
                    walls, dots, powers = build_level(current_level - 1)
                    spawn_ghosts(current_level)
                    if p1_lives > 0: p1_rect.topleft = (1 * TILE_SIZE + 5, 1 * TILE_SIZE + 5)
                    if players == 2 and p2_lives > 0: p2_rect.topleft = (30 * TILE_SIZE + 5, 1 * TILE_SIZE + 5)
                    scared_timer = 0

            # Ghost Movement & AI
            ghost_base_speed = 3 + (current_level - 1) * 0.5
            
            for g in ghosts:
                if g["state"] == "DEAD":
                    g["dead_timer"] -= 1
                    if g["dead_timer"] <= 0:
                        g["state"] = "NORMAL"
                        g["rect"].topleft = ((14 + g["id"]%4) * TILE_SIZE + 5, 8 * TILE_SIZE + 5) 
                    continue 
                    
                speed = ghost_base_speed * 0.6 if g["state"] == "SCARED" else ghost_base_speed
                old_x, old_y = g["rect"].x, g["rect"].y
                move_entity(g["rect"], g["dir"][0], g["dir"][1], speed)
                
                # Cornering AI
                if g["rect"].x == old_x and g["rect"].y == old_y:
                    directions = [(1,0), (-1,0), (0,1), (0,-1)]
                    if g["dir"] in directions: directions.remove(g["dir"]) 
                    
                    reverse_dir = (g["dir"][0] * -1, g["dir"][1] * -1)
                    if reverse_dir in directions: directions.remove(reverse_dir) 
                    
                    if len(directions) > 0:
                        g["dir"] = random.choice(directions)
                    else:
                        g["dir"] = reverse_dir
                    
                # Collision with Player 1
                if p1_lives > 0 and g["rect"].colliderect(p1_rect):
                    if g["state"] == "SCARED":
                        g["state"] = "DEAD"
                        g["dead_timer"] = 300 
                        score += 200
                    elif g["state"] == "NORMAL":
                        p1_lives -= 1
                        if p1_lives > 0:
                            p1_rect.topleft = (1 * TILE_SIZE + 5, 1 * TILE_SIZE + 5)

                # Collision with Player 2
                if players == 2 and p2_lives > 0 and g["rect"].colliderect(p2_rect):
                    if g["state"] == "SCARED":
                        g["state"] = "DEAD"
                        g["dead_timer"] = 300 
                        score += 200
                    elif g["state"] == "NORMAL":
                        p2_lives -= 1
                        if p2_lives > 0:
                            p2_rect.topleft = (30 * TILE_SIZE + 5, 1 * TILE_SIZE + 5)

            # Check Total Game Over
            if p1_lives <= 0 and (players == 1 or p2_lives <= 0):
                game_over = True

        # Drawing
        screen.fill(BG_COLOR)
        
        for wall in walls:
            pygame.draw.rect(screen, WALL_COLOR, wall, border_radius=4)
            pygame.draw.rect(screen, (50, 100, 200), wall.inflate(-10, -10), 1, border_radius=2)
            
        for dot in dots: pygame.draw.ellipse(screen, DOT_COLOR, dot)
        for p in powers: pygame.draw.ellipse(screen, POWER_COLOR, p) 
            
        if not game_over and not game_won:
            if p1_lives > 0:
                draw_pacman(screen, P1_COLOR, p1_rect, p1_dir, frame_count)
            if players == 2 and p2_lives > 0:
                draw_pacman(screen, P2_COLOR, p2_rect, p2_dir, frame_count)
                
            for g in ghosts:
                draw_ghost(screen, g["color"], g["rect"], g["state"])
                
        # UI
        score_surf = font.render(f"SCORE: {score}", True, (255, 255, 255))
        level_surf = font.render(f"LEVEL {current_level}/5", True, (255, 255, 255))
        
        screen.blit(score_surf, (20, HEIGHT - 75))
        screen.blit(level_surf, (WIDTH // 2 - level_surf.get_width()//2, HEIGHT - 60))
        
        # P1 Lives
        for i in range(p1_lives):
            pygame.draw.circle(screen, P1_COLOR, (35 + (i * 40), HEIGHT - 30), 15)
            
        # P2 Lives
        if players == 2:
            for i in range(p2_lives):
                pygame.draw.circle(screen, P2_COLOR, (WIDTH - 150 + (i * 40), HEIGHT - 30), 15)

        # --- CONTROLS vs NAMES LOGIC ---
        if not (game_over or game_won):
            if frame_count <= 300:
                if p1_lives > 0:
                    tut1 = tiny_font.render("[W][A][S][D]", True, (150, 150, 150))
                    screen.blit(tut1, (p1_rect.centerx - tut1.get_width()//2, p1_rect.top - 20))
                if players == 2 and p2_lives > 0:
                    tut2 = tiny_font.render("[ARROWS]", True, (150, 150, 150))
                    screen.blit(tut2, (p2_rect.centerx - tut2.get_width()//2, p2_rect.top - 20))
            else:
                if p1_lives > 0:
                    n1 = tiny_font.render(p1_name.upper(), True, P1_COLOR)
                    screen.blit(n1, (p1_rect.centerx - n1.get_width()//2, p1_rect.top - 20))
                if players == 2 and p2_lives > 0:
                    n2 = tiny_font.render(p2_name.upper(), True, P2_COLOR)
                    screen.blit(n2, (p2_rect.centerx - n2.get_width()//2, p2_rect.top - 20))

        if game_over or game_won:
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(150); overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            
            title_text = "VICTORY!" if game_won else "GAME OVER"
            title_color = P1_COLOR if game_won else (255, 50, 50)
            go_surf = pygame.font.Font(None, 120).render(title_text, True, title_color)
            restart_surf = small_font.render("Press [R] to Restart or [ESC] for Menu", True, (255, 255, 255))
            
            screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 60))
            screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 50))

        pygame.display.flip()
        clock.tick(60)