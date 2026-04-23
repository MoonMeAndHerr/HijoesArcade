import sqlite3
import os

DB_FILE = "arcade_scores.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
                    game_name TEXT,
                    player_name TEXT,
                    score INTEGER
                 )''')
    
    # Check if empty, then preset top 10 for the scorable games
    c.execute("SELECT COUNT(*) FROM scores")
    if c.fetchone()[0] == 0:
        # Your custom names list!
        names = ["Jay", "Yand", "Kay", "Noh", "Randy", "Meran", "snz", "b#sting0#", "102AM", "Amedin"]
        
        # Realistic, handcrafted descending scores for each game
        realistic_scores = {
            "STARSHIP": [142, 115, 98, 85, 76, 62, 54, 45, 38, 29],
            "PACMAN": [4250, 3800, 3120, 2750, 2100, 1850, 1420, 1150, 980, 850],
            "TETRIS": [12500, 10200, 8800, 7500, 6100, 5300, 4200, 3100, 2500, 1800],
            "MARKET MATRIX": [17540, 16200, 15850, 15200, 14800, 13500, 12100, 11500, 10800, 10100],
            "COMPUTE CORE": [350, 310, 285, 250, 215, 180, 155, 130, 110, 95],
            "AXIOM REALM": [120, 105, 94, 85, 76, 68, 55, 48, 41, 32],
            "OPTIMIZE ENGINE": [450, 410, 375, 340, 315, 280, 255, 220, 195, 160],
            "STOCHASTIC SPACE": [850, 780, 710, 650, 590, 530, 460, 410, 350, 290]
        }
        
        preset_data = []
        for game, scores in realistic_scores.items():
            for i in range(10):
                preset_data.append((game, names[i], scores[i]))
                
        c.executemany("INSERT INTO scores (game_name, player_name, score) VALUES (?, ?, ?)", preset_data)
    
    conn.commit()
    conn.close()

def get_top_10(game_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT player_name, score FROM scores WHERE game_name=? ORDER BY score DESC LIMIT 10", (game_name,))
    results = c.fetchall()
    conn.close()
    return results

def is_high_score(game_name, score):
    top_10 = get_top_10(game_name)
    if len(top_10) < 10: return True
    return score > top_10[-1][1]

def add_score(game_name, player_name, score):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO scores (game_name, player_name, score) VALUES (?, ?, ?)", (game_name, player_name, score))
    conn.commit()
    conn.close()