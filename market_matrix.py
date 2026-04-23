import pygame
import random
import math

class MM_Button:
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
    BG_COLOR = (10, 15, 20)
    GRID_COLOR = (20, 35, 45)
    PRICE_LINE = (0, 255, 200)
    LONG_COLOR = (0, 255, 100)
    SHORT_COLOR = (255, 50, 50)
    FLAT_COLOR = (150, 150, 150)
    WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)
    WARNING_COLOR = (255, 100, 0)
    
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 35)
    large_font = pygame.font.Font(None, 110)

    # UI Setup
    start_btn = MM_Button(WIDTH//2 - 200, HEIGHT - 150, 400, 70, "Start Buy/Sell !", LONG_COLOR, (50, 255, 150), font)

    # Game Variables
    game_state = "INSTRUCTIONS" 
    starting_capital = 10000.0
    target_capital = 15000.0
    capital = starting_capital
    position = 0 
    leverage = 60.0 
    spread_fee = 100.0 # Broker fee per trade!
    fee_flash_timer = 0
    
    # Time Variables
    max_frames = 3600 
    frame_count = 0
    game_won = False
    
    # News Event Variables
    news_timer = random.randint(300, 600) # Next news in 5-10 seconds
    news_triggering = False
    news_countdown = 0
    
    # Market Engine Variables
    time_t = 0.0
    current_price = HEIGHT // 2
    CHART_RIGHT = WIDTH - 200 
    price_history = [current_price] * CHART_RIGHT 
    
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
                    return int(capital)
                if event.key == pygame.K_r and game_state == "GAME_OVER":
                    game_state = "INSTRUCTIONS"
                    capital = starting_capital
                    frame_count = 0
                    game_won = False
                    time_t = 0.0
                    current_price = HEIGHT // 2
                    price_history = [current_price] * CHART_RIGHT
                    news_timer = random.randint(300, 600)
                    news_triggering = False
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "INSTRUCTIONS" and start_btn.is_hovered:
                    game_state = "PLAYING"

        keys = pygame.key.get_pressed()
        
        if game_state == "PLAYING":
            frame_count += 1
            
            # 1. Trading Input (With Spread Fees!)
            new_position = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]: new_position = 1
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]: new_position = -1
                
            if new_position != position:
                if new_position != 0: # Only charge when opening a trade, not closing to flat
                    capital -= spread_fee
                    fee_flash_timer = 30 # Show penalty for 30 frames
                position = new_position
                
            # 2. Market Generator (More jagged math)
            time_t += 0.03
            # Base trend + secondary wave + heavy random noise
            trend = math.sin(time_t) * 1.5 + math.cos(time_t * 0.5) * 2.5 + math.sin(time_t * 2.1) * 1.5
            noise = random.uniform(-3.5, 3.5)
            delta = trend + noise
            
            # 3. News Events (Flash Crashes)
            if not news_triggering:
                news_timer -= 1
                if news_timer <= 0:
                    news_triggering = True
                    news_countdown = 180 # 3 seconds warning
            else:
                news_countdown -= 1
                if news_countdown <= 0:
                    # MASSIVE SPIKE OR CRASH
                    delta += random.choice([-35, -25, 25, 35])
                    news_triggering = False
                    news_timer = random.randint(300, 600)
            
            # Keep price constrained
            if current_price + delta > HEIGHT - 100: delta = -abs(delta)
            if current_price + delta < 150: delta = abs(delta)
                
            current_price += delta
            
            price_history.pop(0)
            price_history.append(current_price)
            
            # 4. Calculate PnL
            price_movement = -delta 
            pnl_tick = position * price_movement * leverage
            capital += pnl_tick
            
            # 5. Check End Conditions
            if capital <= 0:
                capital = 0
                game_state = "GAME_OVER"
            elif frame_count >= max_frames:
                if capital >= target_capital:
                    game_won = True
                game_state = "GAME_OVER"

        # --- DRAWING ---
        screen.fill(BG_COLOR)
        
        if game_state == "INSTRUCTIONS":
            title_surf = large_font.render("MARKET MATRIX", True, PRICE_LINE)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 100)))
            
            rules = [
                f"Capital: ${starting_capital:,.0f}  |  Target: ${target_capital:,.0f}  |  Time: 60s",
                "",
                "[UP] = LONG (+ Profit when line goes UP)",
                "[DOWN] = SHORT (+ Profit when line goes DOWN)",
                "Release keys = FLAT (Close position)",
                "",
                "⚠ THE SPREAD: Every time you open a trade, you pay a $100 fee. Do not spam keys.",
                "⚠ VOLATILITY: Watch for High-Impact News warnings. The market will violently spike.",
                "Bankrupt ($0) = Immediate Game Over."
            ]
            
            for i, line in enumerate(rules):
                color = WHITE if i < 6 else WARNING_COLOR
                line_surf = small_font.render(line, True, color)
                screen.blit(line_surf, line_surf.get_rect(center=(WIDTH//2, 210 + (i * 35))))
                
            start_btn.check_hover(mouse_pos)
            start_btn.draw(screen)

        elif game_state == "PLAYING" or game_state == "GAME_OVER":
            for x in range(0, WIDTH, 50): pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, 50): pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

            pygame.draw.line(screen, GOLD, (0, HEIGHT//4), (WIDTH, HEIGHT//4), 1)

            points = [(x, price_history[x]) for x in range(CHART_RIGHT)]
            if len(points) >= 2:
                pygame.draw.lines(screen, PRICE_LINE, False, points, 3)
                
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 4 + 6
            pygame.draw.circle(screen, WHITE, (CHART_RIGHT, int(current_price)), max(3, int(pulse)))
            
            # Draw News Warning UI
            if news_triggering:
                warning_text = f"HIGH IMPACT NEWS IN: {math.ceil(news_countdown / 60)}s"
                warn_surf = font.render(warning_text, True, WARNING_COLOR)
                # Flash the background of the warning
                if (news_countdown // 10) % 2 == 0:
                    pygame.draw.rect(screen, SHORT_COLOR, (WIDTH//2 - warn_surf.get_width()//2 - 20, HEIGHT - 100, warn_surf.get_width() + 40, 60))
                screen.blit(warn_surf, (WIDTH//2 - warn_surf.get_width()//2, HEIGHT - 90))

            # UI Data Box
            ui_rect = pygame.Rect(10, 10, 450, 160)
            pygame.draw.rect(screen, (5, 5, 10), ui_rect, border_radius=10)
            pygame.draw.rect(screen, PRICE_LINE, ui_rect, 2, border_radius=10)
            
            cap_color = LONG_COLOR if capital >= starting_capital else SHORT_COLOR
            cap_surf = font.render(f"PORTFOLIO: ${capital:,.2f}", True, cap_color)
            target_surf = small_font.render(f"TARGET: ${target_capital:,.2f}", True, GOLD)
            
            if position == 1: pos_text, pos_color = "POSITION: LONG [+]", LONG_COLOR
            elif position == -1: pos_text, pos_color = "POSITION: SHORT [-]", SHORT_COLOR
            else: pos_text, pos_color = "POSITION: FLAT [ ]", FLAT_COLOR
                
            pos_surf = font.render(pos_text, True, pos_color)
            time_left = max(0, (max_frames - frame_count) // 60)
            time_surf = small_font.render(f"MARKET CLOSE IN: {time_left}s", True, WHITE)

            screen.blit(cap_surf, (25, 25))
            screen.blit(target_surf, (25, 75))
            screen.blit(pos_surf, (25, 115))
            screen.blit(time_surf, (WIDTH - 300, 30))
            
            # Show Fee Deduction visual
            if fee_flash_timer > 0:
                fee_flash_timer -= 1
                fee_surf = small_font.render("-$100 SPREAD", True, SHORT_COLOR)
                screen.blit(fee_surf, (ui_rect.right + 20, 25))

            if game_state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(200); overlay.fill((0,0,0))
                screen.blit(overlay, (0,0))
                
                if game_won: title_text, title_color = "PROFIT TARGET REACHED", LONG_COLOR
                else: title_text, title_color = "BANKRUPT" if capital <= 0 else "TARGET MISSED", SHORT_COLOR
                    
                go_surf = large_font.render(title_text, True, title_color)
                final_surf = font.render(f"Final Value: ${capital:,.2f}", True, WHITE)
                restart_surf = small_font.render("Press [R] to trade again or [ESC] for Menu", True, FLAT_COLOR)
                
                screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 100))
                screen.blit(final_surf, (WIDTH//2 - final_surf.get_width()//2, HEIGHT//2 + 20))
                screen.blit(restart_surf, (WIDTH//2 - restart_surf.get_width()//2, HEIGHT//2 + 90))

        esc_surf = small_font.render("Press ESC to return to menu", True, (80, 80, 80))
        screen.blit(esc_surf, (WIDTH//2 - esc_surf.get_width()//2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)