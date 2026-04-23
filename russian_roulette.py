import pygame
import random

class RR_Button:
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
        pygame.draw.rect(surface, (10, 5, 5), shadow_rect, border_radius=8) 
        
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

# Added p1_name and p2_name parameters here
def start_roulette(screen, is_muted, players, p1_name="Player 1", p2_name="Player 2"):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    
    # Silence arcade background music for suspense
    if not is_muted:
        pygame.mixer.music.pause()
        
    # Load SFX and Game Over Music
    blank_sfx, bang_sfx, game_over_music = None, None, None
    try:
        blank_sfx = pygame.mixer.Sound("blank.wav")
        bang_sfx = pygame.mixer.Sound("gunshot.wav")
        game_over_music = pygame.mixer.Sound("game_over.wav")
        game_over_music.set_volume(0.6) # Slightly lower volume so it's not deafening
    except FileNotFoundError:
        print("Warning: Missing audio files (blank.wav, gunshot.wav, or game_over.wav). Playing in silence.")

    # Colors & Fonts
    BG_COLOR = (15, 10, 10) 
    WHITE = (255, 255, 255)
    GRAY = (150, 150, 150)
    RED = (200, 30, 30)
    DARK_RED = (120, 20, 20)
    GOLD = (255, 215, 0)
    
    title_font = pygame.font.Font(None, 100)
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 35)
    
    # UI Elements (Dynamically updated)
    btn_4 = RR_Button(WIDTH//2 - 250, HEIGHT//2, 120, 80, "4", DARK_RED, RED, font)
    btn_6 = RR_Button(WIDTH//2 - 60, HEIGHT//2, 120, 80, "6", DARK_RED, RED, font)
    btn_8 = RR_Button(WIDTH//2 + 130, HEIGHT//2, 120, 80, "8", DARK_RED, RED, font)
    
    heads_btn = RR_Button(WIDTH//2 - 200, HEIGHT//2, 150, 80, "HEADS", GRAY, WHITE, font)
    tails_btn = RR_Button(WIDTH//2 + 50, HEIGHT//2, 150, 80, "TAILS", GRAY, WHITE, font)
    
    do_or_die_btn = RR_Button(WIDTH//2 - 150, HEIGHT - 150, 300, 70, "DO OR DIE", RED, (255, 50, 50), font)
    
    shoot_self_btn = RR_Button(WIDTH//2 - 220, HEIGHT - 200, 200, 80, "SHOOT SELF", GRAY, WHITE, small_font)
    shoot_enemy_btn = RR_Button(WIDTH//2 + 20, HEIGHT - 200, 200, 80, "SHOOT ENEMY", DARK_RED, RED, small_font)
    
    # Game Variables
    game_state = "CHAMBER_SELECT" 
    max_chambers = 6
    bullet_chamber = 1
    current_chamber = 1
    current_turn = 1 
    toss_result = ""
    coin_message = ""
    frame_count = 0 # Added for the 5-second instruction overlay
    
    message = ""
    winner = ""
    ai_timer = 0
    ai_is_thinking = False
    
    def fire_gun(target):
        nonlocal current_chamber, current_turn, game_state, message, winner, ai_is_thinking
        
        is_bullet = (current_chamber == bullet_chamber)
        
        # Determine who is shooting and who is the enemy using the custom names
        shooter_name = p1_name if current_turn == 1 else (p2_name if players == 2 else "AI")
        enemy_name = (p2_name if players == 2 else "AI") if current_turn == 1 else p1_name
        
        if is_bullet:
            if bang_sfx and not is_muted: bang_sfx.play()
            if target == "SELF":
                message = f"BANG! {shooter_name} shot themselves!" if shooter_name != "AI" else "BANG! AI shot itself!"
                winner = f"{enemy_name} Wins!"
            else:
                message = f"BANG! {shooter_name} shot the enemy!" if shooter_name != "AI" else "BANG! AI shot you!"
                winner = f"{shooter_name} Wins!"
            
            game_state = "GAME_OVER"
            
            # Start the infinite looping Game Over song!
            if game_over_music and not is_muted:
                game_over_music.play(loops=-1) 

        else:
            if blank_sfx and not is_muted: blank_sfx.play()
            if target == "SELF":
                message = "*Click* ... Empty. You get another turn."
                current_chamber += 1
            else:
                message = "*Click* ... Empty. Turn passed."
                current_chamber += 1
                current_turn = 2 if current_turn == 1 else 1 
                
        ai_is_thinking = False
    
    running = True
    while running:
        frame_count += 1
        mouse_pos = pygame.mouse.get_pos()
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Stop the game over music if it's currently playing
                    if game_over_music:
                        game_over_music.stop()
                    # Restore main menu music!
                    if not is_muted:
                        pygame.mixer.music.unpause() 
                    return 
                    
                if event.key == pygame.K_r and game_state == "GAME_OVER":
                    # Stop the game over music so we can play in silence again
                    if game_over_music:
                        game_over_music.stop()
                    game_state = "CHAMBER_SELECT" 
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                if game_state == "CHAMBER_SELECT":
                    if btn_4.is_hovered: max_chambers = 4; game_state = "COIN_TOSS"
                    if btn_6.is_hovered: max_chambers = 6; game_state = "COIN_TOSS"
                    if btn_8.is_hovered: max_chambers = 8; game_state = "COIN_TOSS"
                    
                elif game_state == "COIN_TOSS":
                    if heads_btn.is_hovered or tails_btn.is_hovered:
                        choice = "HEADS" if heads_btn.is_hovered else "TAILS"
                        toss_result = random.choice(["HEADS", "TAILS"])
                        
                        if choice == toss_result:
                            coin_message = f"Coin landed {toss_result}! {p1_name} Wins toss. Enemy starts."
                            current_turn = 2
                        else:
                            coin_message = f"Coin landed {toss_result}! {p1_name} Loses toss. {p1_name} starts."
                            current_turn = 1
                            
                        bullet_chamber = random.randint(1, max_chambers)
                        current_chamber = 1
                        game_state = "RULES"
                        
                elif game_state == "RULES":
                    if do_or_die_btn.is_hovered:
                        game_state = "PLAYING"
                        message = "Make your choice."
                        frame_count = 0 # Reset frame count so the control instruction shows up
                        
                elif game_state == "PLAYING" and not ai_is_thinking:
                    if shoot_self_btn.is_hovered:
                        fire_gun("SELF")
                    elif shoot_enemy_btn.is_hovered:
                        fire_gun("ENEMY")
                        
        # 2. AI Logic
        if game_state == "PLAYING" and players == 1 and current_turn == 2:
            if not ai_is_thinking:
                ai_is_thinking = True
                ai_timer = pygame.time.get_ticks()
                message = "AI is deciding who to shoot..."
            else:
                if pygame.time.get_ticks() - ai_timer > 2000: 
                    chambers_left = max_chambers - current_chamber + 1
                    if chambers_left == 1:
                        ai_choice = "ENEMY"
                    else:
                        ai_choice = random.choice(["SELF", "ENEMY"])
                    fire_gun(ai_choice)

        # 3. Drawing
        screen.fill(BG_COLOR)
        
        if game_state == "CHAMBER_SELECT":
            title_surf = title_font.render("SELECT CHAMBER SIZE", True, RED)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 200)))
            
            for btn in [btn_4, btn_6, btn_8]:
                btn.check_hover(mouse_pos)
                btn.draw(screen)
                
        elif game_state == "COIN_TOSS":
            # Swapped out hardcoded "PLAYER 1" for dynamic name
            title_surf = title_font.render(f"{p1_name.upper()}: CALL THE COIN", True, GOLD)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 200)))
            
            sub_surf = small_font.render("Winner of the toss forces the enemy to go first.", True, GRAY)
            screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH//2, 280)))
            
            heads_btn.check_hover(mouse_pos)
            tails_btn.check_hover(mouse_pos)
            heads_btn.draw(screen)
            tails_btn.draw(screen)
            
        elif game_state == "RULES":
            title_surf = title_font.render("THE RULES", True, RED)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 100)))
            
            rules = [
                coin_message,
                "",
                f"1 Revolver. {max_chambers} Chambers. 1 Bullet.",
                "Shoot Yourself: If blank, YOU GET ANOTHER TURN.",
                "Shoot Enemy: If blank, YOUR TURN IS OVER.",
                "If it bangs... you die."
            ]
            
            for i, line in enumerate(rules):
                color = GOLD if i == 0 else (WHITE if i > 1 else GRAY)
                line_surf = font.render(line, True, color) if i == 0 else small_font.render(line, True, color)
                screen.blit(line_surf, line_surf.get_rect(center=(WIDTH//2, 200 + (i * 45))))
                
            do_or_die_btn.check_hover(mouse_pos)
            do_or_die_btn.draw(screen)
            
        elif game_state == "PLAYING":
            # Dynamic Turn Text
            turn_name = p1_name if current_turn == 1 else (p2_name if players == 2 else "AI")
            turn_surf = title_font.render(f"{turn_name.upper()}'S TURN", True, WHITE)
            screen.blit(turn_surf, turn_surf.get_rect(center=(WIDTH//2, 150)))
            
            start_x = WIDTH//2 - ((max_chambers * 50) // 2)
            for i in range(max_chambers):
                chamber_color = RED if i < (current_chamber - 1) else GRAY
                pygame.draw.circle(screen, chamber_color, (start_x + (i * 50), 300), 15)
                
            msg_surf = font.render(message, True, GOLD)
            screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH//2, 400)))
            
            ctrl_surf = small_font.render("[USE MOUSE TO CLICK OPTIONS]", True, GRAY)
            screen.blit(ctrl_surf, ctrl_surf.get_rect(center=(WIDTH//2, HEIGHT - 100)))
            
            if not (players == 1 and current_turn == 2):
                shoot_self_btn.check_hover(mouse_pos)
                shoot_enemy_btn.check_hover(mouse_pos)
                shoot_self_btn.draw(screen)
                shoot_enemy_btn.draw(screen)
                
        elif game_state == "GAME_OVER":
            go_surf = title_font.render(message, True, RED)
            win_surf = font.render(winner, True, GOLD)
            restart_surf = small_font.render("Press [R] to Play Again or [ESC] for Menu", True, GRAY)
            
            screen.blit(go_surf, go_surf.get_rect(center=(WIDTH//2, 250)))
            screen.blit(win_surf, win_surf.get_rect(center=(WIDTH//2, 350)))
            screen.blit(restart_surf, restart_surf.get_rect(center=(WIDTH//2, 500)))

        esc_surf = small_font.render("Press ESC to return to menu", True, (80, 80, 80))
        screen.blit(esc_surf, (WIDTH//2 - esc_surf.get_width()//2, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)