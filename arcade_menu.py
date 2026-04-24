import pygame
import sys
import random
import math
import database 
import pong, starship, russian_roulette, pacman, tetris, snakey
import compute_core, axiom_realm, market_matrix, optimize_engine, stochastic_space

pygame.init()
pygame.mixer.init()
database.init_db() 

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hijoe's Arcade")

# Colors
BG_COLOR, TEXT_COLOR = (15, 15, 25), (255, 255, 255)
BTN_COLOR, HOVER_COLOR = (45, 45, 85), (100, 100, 255)
EXIT_COLOR, EXIT_HOVER = (150, 40, 40), (220, 60, 60)
TITLE_COLOR, EDU_COLOR = (0, 255, 200), (40, 80, 60)
EDU_HOVER, GOLD = (80, 160, 120), (255, 215, 0)
WHITE = (255, 255, 255)

title_font = pygame.font.Font(None, 90)
font = pygame.font.Font(None, 60) 
btn_font = pygame.font.Font(None, 38)
small_font = pygame.font.Font(None, 30)

is_muted = False
click_sound = None
try:
    pygame.mixer.music.load("bg_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except: pass
try:
    click_sound = pygame.mixer.Sound("click.mp3")
    click_sound.set_volume(0.7)
except: pass

particles = []
for _ in range(120):
    particles.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(1.0, 3.0), random.randint(2, 4)])

sprite_x, anim_state, frame_count = -150, 1, 0

class Button:
    def __init__(self, x, y, width, height, text, default_color, hover_color, font=btn_font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text, self.default_color, self.hover_color = text, default_color, hover_color
        self.current_color, self.is_hovered, self.font = default_color, False, font
    def draw(self, surface):
        shadow = self.rect.copy(); shadow.y += 4
        pygame.draw.rect(surface, (5, 5, 10), shadow, border_radius=12)
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=12)
        t_surf = self.font.render(self.text, True, TEXT_COLOR)
        surface.blit(t_surf, t_surf.get_rect(center=self.rect.center))
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.is_hovered else self.default_color

btn_w, btn_h, center_x, gap_x = 450, 55, WIDTH // 2, 30
main_buttons = []
retro_games = ["Pong", "Starship", "Russian Roulette", "Pacman", "Tetris", "Snakey"]
edu_games = ["Compute Core (Comp Math)", "Axiom Realm (Pure Math)", "Market Matrix (Fin Math)", "Optimize Engine (O.R.)", "Stochastic Space (Stats)"]

start_y = 160
y_gap = 65 

left_height = (len(retro_games) - 1) * y_gap + btn_h
right_height = (len(edu_games) - 1) * y_gap + btn_h
right_y_offset = (left_height - right_height) // 2 

for i, n in enumerate(retro_games): 
    main_buttons.append(Button(center_x-btn_w-gap_x, start_y+(i*y_gap), btn_w, btn_h, n, BTN_COLOR, HOVER_COLOR))
for i, n in enumerate(edu_games): 
    main_buttons.append(Button(center_x+gap_x, start_y + right_y_offset + (i*y_gap), btn_w, btn_h, n, EDU_COLOR, EDU_HOVER))

exit_btn = Button(center_x - 100, HEIGHT - 140, 200, 50, "EXIT ARCADE", EXIT_COLOR, EXIT_HOVER, small_font)
mute_btn = Button(30, HEIGHT - 140, 120, 50, "MUTE", EXIT_COLOR, EXIT_HOVER, small_font)

sel_1p = Button(center_x - 150, 300, 300, 70, "1 Player", BTN_COLOR, HOVER_COLOR)
sel_2p = Button(center_x - 150, 400, 300, 70, "2 Players Battle", BTN_COLOR, HOVER_COLOR)
back_btn = Button(center_x - 100, 550, 200, 50, "BACK", EXIT_COLOR, EXIT_HOVER, small_font)
pts_5 = Button(center_x - 150, 250, 300, 60, "First to 5", BTN_COLOR, HOVER_COLOR)
pts_10 = Button(center_x - 150, 330, 300, 60, "First to 10", BTN_COLOR, HOVER_COLOR)
pts_inf = Button(center_x - 150, 410, 300, 60, "Infinity", BTN_COLOR, HOVER_COLOR)
cont_btn = Button(center_x - 150, HEIGHT - 120, 300, 50, "CONTINUE TO MENU", BTN_COLOR, HOVER_COLOR, small_font)

current_state = "MAIN_MENU" 
target_game, temp_players = "", 1
p1_name, p2_name, active_input = "", "", 1

pending_game = ""
pending_score = 0
hs_name = ""
sb_message = ""

clock = pygame.time.Clock() 

def check_score_return(game_id, score_returned):
    global current_state, pending_game, pending_score, hs_name, sb_message
    if score_returned is not None:
        
        # --> ADDED: Unpacks the tuple from Snakey so we have 2 distinct scoreboards <--
        if isinstance(score_returned, tuple):
            pending_game = score_returned[0]
            pending_score = score_returned[1]
        else:
            pending_game = game_id.upper()
            pending_score = score_returned
            
        if database.is_high_score(pending_game, pending_score):
            current_state = "NEW_HIGH_SCORE"
            hs_name = ""
        else:
            current_state = "SCOREBOARD"
            sb_message = "SORRY, YOU DIDN'T MAKE IT INTO THE SCOREBOARD"
    else:
        current_state = "MAIN_MENU"

running = True
while running:
    frame_count += 1
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.KEYDOWN and current_state == "NEW_HIGH_SCORE":
            if event.key == pygame.K_RETURN and hs_name.strip() != "":
                database.add_score(pending_game, hs_name.strip(), pending_score)
                current_state = "SCOREBOARD"
                sb_message = "SCORE SAVED! YOU MADE THE TOP 10!"
            elif event.key == pygame.K_BACKSPACE:
                hs_name = hs_name[:-1]
            else:
                if len(hs_name) < 12: hs_name += event.unicode
                
        elif event.type == pygame.KEYDOWN and current_state == "NAME_INPUT":
            if event.key == pygame.K_RETURN:
                if active_input == 1: active_input = 2
                else: 
                    if p1_name == "": p1_name = "Player 1"
                    if p2_name == "": p2_name = "Player 2"
                    
                    if target_game == "Pong": current_state = "PONG_POINTS"
                    else:
                        if target_game == "Starship": check_score_return("STARSHIP", starship.start_starship(screen, is_muted, 2, p1_name, p2_name))
                        elif target_game == "Russian Roulette": russian_roulette.start_roulette(screen, is_muted, 2, p1_name, p2_name); current_state = "MAIN_MENU"
                        elif target_game == "Pacman": check_score_return("PACMAN", pacman.start_pacman(screen, is_muted, 2, p1_name, p2_name))
                        elif target_game == "Tetris": check_score_return("TETRIS", tetris.start_tetris(screen, is_muted, 2, p1_name, p2_name))
                        elif target_game == "Snakey": check_score_return("SNAKEY", snakey.start_snakey(screen, is_muted, 2, p1_name, p2_name))
                        current_state = "MAIN_MENU"
                        
            elif event.key == pygame.K_BACKSPACE:
                if active_input == 1: p1_name = p1_name[:-1]
                else: p2_name = p2_name[:-1]
            elif event.key == pygame.K_TAB: active_input = 2 if active_input == 1 else 1
            elif event.key == pygame.K_ESCAPE: current_state = f"{target_game.upper()}_SELECT"
            else:
                if len(p1_name if active_input == 1 else p2_name) < 10:
                    if active_input == 1: p1_name += event.unicode
                    else: p2_name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if click_sound and not is_muted: click_sound.play()

            if mute_btn.is_hovered:
                is_muted = not is_muted
                if is_muted: pygame.mixer.music.pause()
                else: pygame.mixer.music.unpause()

            if current_state == "MAIN_MENU":
                if exit_btn.is_hovered: running = False
                for b in main_buttons:
                    if b.is_hovered:
                        target_game = b.text.split(" (")[0]
                        if target_game in retro_games: current_state = f"{target_game.upper()}_SELECT"
                        elif target_game == "Compute Core": check_score_return("COMPUTE CORE", compute_core.start_game(screen, is_muted))
                        elif target_game == "Axiom Realm": check_score_return("AXIOM REALM", axiom_realm.start_game(screen, is_muted))
                        elif target_game == "Market Matrix": check_score_return("MARKET MATRIX", market_matrix.start_game(screen, is_muted))
                        elif target_game == "Optimize Engine": check_score_return("OPTIMIZE ENGINE", optimize_engine.start_game(screen, is_muted))
                        elif target_game == "Stochastic Space": check_score_return("STOCHASTIC SPACE", stochastic_space.start_game(screen, is_muted))

            elif "_SELECT" in current_state:
                if back_btn.is_hovered: current_state = "MAIN_MENU"
                elif sel_1p.is_hovered:
                    temp_players, p1_name, p2_name = 1, "Player 1", "AI"
                    if target_game == "Pong": current_state = "PONG_POINTS"
                    else:
                        if target_game == "Starship": check_score_return("STARSHIP", starship.start_starship(screen, is_muted, 1, p1_name, p2_name))
                        elif target_game == "Russian Roulette": russian_roulette.start_roulette(screen, is_muted, 1, p1_name, p2_name); current_state = "MAIN_MENU"
                        elif target_game == "Pacman": check_score_return("PACMAN", pacman.start_pacman(screen, is_muted, 1, p1_name, p2_name))
                        elif target_game == "Tetris": check_score_return("TETRIS", tetris.start_tetris(screen, is_muted, 1, p1_name, p2_name))
                        elif target_game == "Snakey": check_score_return("SNAKEY", snakey.start_snakey(screen, is_muted, 1, p1_name, p2_name))
                elif sel_2p.is_hovered:
                    temp_players, p1_name, p2_name, active_input = 2, "", "", 1
                    current_state = "NAME_INPUT"

            elif current_state == "PONG_POINTS":
                if back_btn.is_hovered: current_state = "NAME_INPUT" if temp_players == 2 else "PONG_SELECT"
                elif pts_5.is_hovered: pong.start_pong(screen, is_muted, temp_players, 5, p1_name, p2_name); current_state = "MAIN_MENU"
                elif pts_10.is_hovered: pong.start_pong(screen, is_muted, temp_players, 10, p1_name, p2_name); current_state = "MAIN_MENU"
                elif pts_inf.is_hovered: pong.start_pong(screen, is_muted, temp_players, 0, p1_name, p2_name); current_state = "MAIN_MENU"
                
            elif current_state == "SCOREBOARD":
                if cont_btn.is_hovered: current_state = "MAIN_MENU"

    # --- BACKGROUND DRAWING ---
    screen.fill(BG_COLOR)
    for p in particles:
        p[1] += p[2] 
        p[0] += math.sin(frame_count * 0.02 + p[2]) * 0.5 
        if p[1] > HEIGHT: p[1], p[0] = -10, random.randint(0, WIDTH)
        pygame.draw.circle(screen, (0, 150, 200), (int(p[0]), int(p[1])), p[3] + 2)
        pygame.draw.circle(screen, (200, 255, 255), (int(p[0]), int(p[1])), p[3])
    
    # --- FOREGROUND UI DRAWING ---
    if current_state == "MAIN_MENU":
        title_surf = title_font.render("HIJOE'S ARCADE", True, TITLE_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, 60)))
        screen.blit(small_font.render("RETRO CLASSICS", True, (150, 150, 150)), (center_x-btn_w-gap_x, 135))
        screen.blit(small_font.render("EDUCATIONAL MODULES", True, (150, 150, 150)), (center_x+gap_x, 135))
        for b in main_buttons: b.check_hover(mouse_pos); b.draw(screen)
        exit_btn.check_hover(mouse_pos); exit_btn.draw(screen)
        mute_btn.check_hover(mouse_pos); mute_btn.draw(screen)
        
    elif current_state == "NAME_INPUT":
        title_surf = title_font.render("ENTER PLAYER NAMES", True, TITLE_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, 100)))
        for i, (n, act) in enumerate([(p1_name, 1), (p2_name, 2)]):
            c = HOVER_COLOR if active_input == act else BTN_COLOR
            pygame.draw.rect(screen, c, (center_x-250, 250+(i*100), 500, 60), border_radius=10)
            display_text = f"P{act}: {n}"
            if active_input == act and pygame.time.get_ticks() % 1000 < 500: display_text += "|"
            screen.blit(btn_font.render(display_text, True, TEXT_COLOR), (center_x-230, 265+(i*100)))
        screen.blit(small_font.render("Type name, press ENTER to advance", True, (150, 150, 150)), (center_x-180, 480))
        
    elif "_SELECT" in current_state or current_state == "PONG_POINTS":
        title_surf = title_font.render(target_game.upper(), True, TITLE_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, 150)))
        if "POINTS" in current_state:
            for b in [pts_5, pts_10, pts_inf, back_btn]: b.check_hover(mouse_pos); b.draw(screen)
        else:
            for b in [sel_1p, sel_2p, back_btn]: b.check_hover(mouse_pos); b.draw(screen)

    elif current_state == "NEW_HIGH_SCORE":
        title_surf = title_font.render("NEW HIGH SCORE!", True, GOLD)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, 150)))
        score_surf = font.render(f"SCORE ACHIEVED: {pending_score}", True, WHITE)
        screen.blit(score_surf, score_surf.get_rect(center=(center_x, 250)))
        
        pygame.draw.rect(screen, HOVER_COLOR, (center_x-250, 350, 500, 60), border_radius=10)
        display_text = f"NAME: {hs_name}"
        if pygame.time.get_ticks() % 1000 < 500: display_text += "|"
        screen.blit(btn_font.render(display_text, True, TEXT_COLOR), (center_x-230, 365))
        screen.blit(small_font.render("Type your name and press ENTER to save to the Hall of Fame", True, (150, 150, 150)), (center_x-320, 450))

    elif current_state == "SCOREBOARD":
        title_surf = title_font.render(f"{pending_game} TOP 10", True, GOLD)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, 80)))
        
        if sb_message:
            msg_color = GOLD if "SAVED" in sb_message else (255, 100, 100)
            msg_surf = small_font.render(sb_message, True, msg_color)
            screen.blit(msg_surf, msg_surf.get_rect(center=(center_x, 140)))
            
        top_10 = database.get_top_10(pending_game)
        for i, (name, s) in enumerate(top_10):
            color = WHITE if i > 2 else (GOLD if i==0 else ((192,192,192) if i==1 else (205, 127, 50)))
            screen.blit(btn_font.render(f"{i+1}.", True, color), (center_x - 300, 180 + i*40))
            screen.blit(btn_font.render(name, True, color), (center_x - 200, 180 + i*40))
            screen.blit(btn_font.render(str(s), True, color), (center_x + 150, 180 + i*40))
            
        cont_btn.check_hover(mouse_pos); cont_btn.draw(screen)

    # --- BOTTOM SCREEN ANIMATION PARADE ---
    if current_state in ["MAIN_MENU", "_SELECT", "NAME_INPUT"]:
        ground_y = HEIGHT - 30
        if anim_state == 1:
            sprite_x += 4
            c_x = sprite_x - 120
            pygame.draw.circle(screen, (255, 150, 0), (int(c_x), ground_y - 10), 15)
            pygame.draw.rect(screen, (255, 150, 0), (int(c_x) - 15, ground_y - 10, 30, 15))
            pygame.draw.circle(screen, (255, 255, 255), (int(c_x) - 5, ground_y - 15), 5)
            pygame.draw.circle(screen, (255, 255, 255), (int(c_x) + 7, ground_y - 15), 5)
            pygame.draw.circle(screen, (0, 0, 255), (int(c_x) - 3, ground_y - 15), 2)
            pygame.draw.circle(screen, (0, 0, 255), (int(c_x) + 9, ground_y - 15), 2)
            b_x = sprite_x - 60
            pygame.draw.circle(screen, (255, 0, 0), (int(b_x), ground_y - 10), 15)
            pygame.draw.rect(screen, (255, 0, 0), (int(b_x) - 15, ground_y - 10, 30, 15))
            pygame.draw.circle(screen, (255, 255, 255), (int(b_x) - 5, ground_y - 15), 5)
            pygame.draw.circle(screen, (255, 255, 255), (int(b_x) + 7, ground_y - 15), 5)
            pygame.draw.circle(screen, (0, 0, 255), (int(b_x) - 3, ground_y - 15), 2)
            pygame.draw.circle(screen, (0, 0, 255), (int(b_x) + 9, ground_y - 15), 2)
            mouth_angle = abs(math.sin(frame_count * 0.15)) * 40
            pygame.draw.circle(screen, (255, 255, 0), (int(sprite_x), ground_y - 10), 20)
            p1, p2, p3 = (int(sprite_x), ground_y - 10), (int(sprite_x) + 25, ground_y - 10 - int(25 * math.tan(math.radians(mouth_angle)))), (int(sprite_x) + 25, ground_y - 10 + int(25 * math.tan(math.radians(mouth_angle))))
            pygame.draw.polygon(screen, BG_COLOR, [p1, p2, p3])
            if sprite_x > WIDTH + 300: anim_state, sprite_x = 2, WIDTH + 150
        elif anim_state == 2:
            sprite_x -= 5
            a_x, s_x = sprite_x - 150, sprite_x
            pygame.draw.rect(screen, (200, 50, 50), (int(a_x), ground_y - 30, 30, 30), border_radius=6)
            pygame.draw.polygon(screen, (0, 200, 255), [(int(s_x)-20, ground_y-15), (int(s_x)+20, ground_y-30), (int(s_x)+20, ground_y)])
            if (frame_count // 8) % 2 == 0: pygame.draw.line(screen, (255, 215, 0), (int(s_x)-20, ground_y-15), (int(a_x)+30, ground_y-15), 3)
            if sprite_x < -300: anim_state, sprite_x = 3, -150
        elif anim_state == 3:
            sprite_x += 3
            i_x = sprite_x
            for i in range(4): pygame.draw.rect(screen, (0, 255, 255), (int(i_x) + i*20, ground_y - 20, 20, 20)); pygame.draw.rect(screen, (0, 0, 0), (int(i_x) + i*20, ground_y - 20, 20, 20), 2)
            o_x = sprite_x - 100
            for i in range(2):
                for j in range(2): pygame.draw.rect(screen, (255, 255, 0), (int(o_x) + i*20, ground_y - 40 + j*20, 20, 20)); pygame.draw.rect(screen, (0, 0, 0), (int(o_x) + i*20, ground_y - 40 + j*20, 20, 20), 2)
            t_x = sprite_x - 220
            for dx, dy in [(0, 0), (-20, 0), (20, 0), (0, -20)]: pygame.draw.rect(screen, (128, 0, 128), (int(t_x) + dx, ground_y - 20 + dy, 20, 20)); pygame.draw.rect(screen, (0, 0, 0), (int(t_x) + dx, ground_y - 20 + dy, 20, 20), 2)
            if sprite_x > WIDTH + 300: anim_state, sprite_x = 4, WIDTH + 150
        elif anim_state == 4:
            sprite_x -= 4
            p1_x, p2_x = sprite_x, sprite_x - 150
            ball_x, ball_y = sprite_x - 75 + math.sin(frame_count * 0.1) * 70, ground_y - 15
            pygame.draw.rect(screen, (255, 255, 255), (int(p2_x), ground_y - 30, 10, 30))
            pygame.draw.rect(screen, (0, 255, 255), (int(p1_x), ground_y - 30, 10, 30))
            pygame.draw.circle(screen, (255, 255, 255), (int(ball_x), int(ball_y)), 6)
            if sprite_x < -300: anim_state, sprite_x = 5, -150
        elif anim_state == 5:
            sprite_x += 3
            c_x, c_y = int(sprite_x), ground_y - 25
            pygame.draw.circle(screen, (100, 100, 100), (c_x, c_y), 25); pygame.draw.circle(screen, (60, 60, 60), (c_x, c_y), 25, 3)
            for i in range(6):
                angle = math.radians(frame_count * 4 + i * 60)
                cham_x, cham_y = c_x + int(math.cos(angle) * 14), c_y + int(math.sin(angle) * 14)
                pygame.draw.circle(screen, (255, 50, 50) if i == 0 else (30, 30, 30), (cham_x, cham_y), 6)
            pygame.draw.circle(screen, (40, 40, 40), (c_x, c_y), 4)
            if sprite_x > WIDTH + 300: anim_state, sprite_x = 1, -150

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()