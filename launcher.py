import pygame
import requests
import zipfile
import threading
import os

# --- CONFIGURATION ---
PC_IP = "192.168.1.18"  # Remplace par l'IP de ton PC si besoin
PC_PORT = "8080"
BASE_URL = f"http://{PC_IP}:{PC_PORT}"

# Initialisation de Pygame
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Termux Game Launcher")

# Couleurs
BG_COLOR = (24, 25, 38)
PANEL_BG = (30, 32, 48)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (96, 90, 230)
GREEN_COLOR = (46, 204, 113)
GRAY_COLOR = (120, 120, 120)
RED_COLOR = (231, 76, 60)

# Polices
font_title = pygame.font.SysFont("sans-serif", 28, bold=True)
font_text = pygame.font.SysFont("sans-serif", 18)
font_desc = pygame.font.SysFont("sans-serif", 14)

# Base de données des jeux
GAMES = {
    "miside": {
        "title": "MiSide",
        "zip_url": f"{BASE_URL}/miside.zip",
        "folder_name": "miside",
        "desc": "Un jeu d'aventure psychologique captivant.",
        "poster_color": (150, 50, 100)
    },
    "sa2": {
        "title": "Sonic Adventure 2",
        "zip_url": f"{BASE_URL}/sa2.zip",
        "folder_name": "sa2",
        "desc": "Rejoignez Sonic et ses amis dans une course contre la montre.",
        "poster_color": (50, 100, 180)
    }
}

selected_game_key = "sa2"
install_status = {}      # État: "idle", "downloading", "extracting", "error", "popup_error"
download_progress = {}   # Pourcentage (0 à 100)

for key in GAMES:
    install_status[key] = "idle"
    download_progress[key] = 0

def check_game_installed(game_key):
    folder = GAMES[game_key]["folder_name"]
    return os.path.exists(f"installed_games/{folder}")

def download_and_extract(game_key):
    global install_status, download_progress
    game = GAMES[game_key]
    install_status[game_key] = "downloading"
    download_progress[game_key] = 0

    zip_filename = f"{game['folder_name']}.zip"
    extract_folder = f"installed_games/{game['folder_name']}"

    try:
        os.makedirs("installed_games", exist_ok=True)
        response = requests.get(game["zip_url"], stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        # Téléchargement par morceaux avec calcul du %
        with open(zip_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        download_progress[game_key] = int((downloaded_size / total_size) * 100)

        # Phase d'extraction
        install_status[game_key] = "extracting"
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        # Nettoyage du fichier ZIP temporaire
        if os.path.exists(zip_filename):
            os.remove(zip_filename)

        install_status[game_key] = "idle"
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        install_status[game_key] = "error"

# Boucle principale Pygame
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BG_COLOR)

    # 1. Barre latérale (Liste des jeux)
    sidebar_rect = pygame.Rect(0, 0, 250, HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, sidebar_rect)

    y_offset = 20
    for key, game in GAMES.items():
        is_selected = (key == selected_game_key)
        btn_rect = pygame.Rect(10, y_offset, 230, 50)

        if is_selected:
            pygame.draw.rect(screen, ACCENT_COLOR, btn_rect, border_radius=8)
        
        text_surf = font_text.render(game["title"], True, TEXT_COLOR)
        screen.blit(text_surf, (btn_rect.x + 15, btn_rect.y + 15))

        y_offset += 60

    # 2. Zone de détails du jeu
    game = GAMES[selected_game_key]
    is_installed = check_game_installed(selected_game_key)
    status = install_status[selected_game_key]

    # Poster
    poster_rect = pygame.Rect(280, 50, 300, 450)
    pygame.draw.rect(screen, game["poster_color"], poster_rect, border_radius=12)
    poster_title = font_title.render(game["title"], True, TEXT_COLOR)
    screen.blit(poster_title, (poster_rect.x + 20, poster_rect.y + 20))

    # Titre & Description
    title_surf = font_title.render(game["title"], True, TEXT_COLOR)
    screen.blit(title_surf, (610, 50))

    desc_box = pygame.Rect(610, 100, 350, 150)
    pygame.draw.rect(screen, PANEL_BG, desc_box, border_radius=8)
    
    desc_surf = font_desc.render(game["desc"], True, TEXT_COLOR)
    screen.blit(desc_surf, (desc_box.x + 15, desc_box.y + 15))

    # Bouton d'action (Télécharger / Jouer)
    action_btn = pygame.Rect(610, 270, 220, 50)

    if status == "downloading":
        pygame.draw.rect(screen, GRAY_COLOR, action_btn, border_radius=8)
        pct = download_progress[selected_game_key]
        btn_text = font_text.render(f"En cours... {pct}%", True, TEXT_COLOR)
    elif status == "extracting":
        pygame.draw.rect(screen, GRAY_COLOR, action_btn, border_radius=8)
        btn_text = font_text.render("Extraction...", True, TEXT_COLOR)
    elif is_installed:
        pygame.draw.rect(screen, GREEN_COLOR, action_btn, border_radius=8)
        btn_text = font_text.render("JOUER", True, TEXT_COLOR)
    else:
        pygame.draw.rect(screen, ACCENT_COLOR, action_btn, border_radius=8)
        btn_text = font_text.render("Installer", True, TEXT_COLOR)

    screen.blit(btn_text, (action_btn.x + 15, action_btn.y + 15))

    # Message d'avertissement en cas de clic sur JOUER
    if status == "popup_error":
        err_box = pygame.Rect(610, 340, 350, 60)
        pygame.draw.rect(screen, RED_COLOR, err_box, border_radius=8)
        err_msg1 = font_desc.render("Désolé, mais Termux ne peut pas", True, TEXT_COLOR)
        err_msg2 = font_desc.render("se permettre cela.", True, TEXT_COLOR)
        screen.blit(err_msg1, (err_box.x + 10, err_box.y + 10))
        screen.blit(err_msg2, (err_box.x + 10, err_box.y + 32))

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Clic dans la liste de gauche
            y_offset = 20
            for key in GAMES:
                btn_rect = pygame.Rect(10, y_offset, 230, 50)
                if btn_rect.collidepoint(mx, my):
                    selected_game_key = key
                    if install_status[key] == "popup_error":
                        install_status[key] = "idle"
                y_offset += 60

            # Clic sur le bouton d'action
            if action_btn.collidepoint(mx, my):
                if is_installed:
                    # Affiche le message de refus
                    install_status[selected_game_key] = "popup_error"
                elif status == "idle":
                    # Démarre le téléchargement dans un thread séparé
                    thread = threading.Thread(target=download_and_extract, args=(selected_game_key,))
                    thread.start()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()