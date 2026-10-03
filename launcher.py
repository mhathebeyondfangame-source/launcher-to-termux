import sys
import os
import subprocess
import zipfile
import threading
import pygame

# --- Auto-installation des dépendances Python standards ---
try:
    import requests
except ImportError:
    print("Installation automatique de requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# Initialisation de Pygame
pygame.init()

# --- Configuration de la fenêtre ---
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ma Bibliothèque de Jeux - Termux Launcher")
clock = pygame.time.Clock()

# --- Configuration du Serveur et Dossiers ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = "http://192.168.1.202:8080"
GAMES_DIR = os.path.join(SCRIPT_DIR, "installed_games")

if not os.path.exists(GAMES_DIR):
    os.makedirs(GAMES_DIR)

# --- Détection et Unzip automatique du fichier icon.zip ---
def extract_and_get_icon_dir():
    target_dir = os.path.join(SCRIPT_DIR, "icon")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Liste des emplacements possibles pour icon.zip
    possible_zips = [
        os.path.join(SCRIPT_DIR, "icon.zip"),
        "/sdcard/Download/icon.zip",
        "/sdcard/icon.zip",
        os.path.join(os.path.expanduser("~"), "Desktop", "icon.zip")
    ]

    for zip_path in possible_zips:
        if os.path.exists(zip_path):
            try:
                print(f"Extraction de {zip_path} vers {target_dir}...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                print("Extraction terminée avec succès !")
                break
            except Exception as e:
                print(f"Erreur lors de l'extraction de icon.zip : {e}")

    return target_dir

ICON_DIR = extract_and_get_icon_dir()

# --- Couleurs ---
COLOR_BG = (10, 10, 25)
COLOR_SIDEBAR_BG = (5, 5, 18)
COLOR_CARD_BG = (20, 20, 45)
COLOR_BORDER = (40, 60, 180)
COLOR_TEXT_NORMAL = (180, 190, 210)
COLOR_TEXT_ACTIVE = (255, 255, 255)
COLOR_SELECTION = (30, 80, 220)
COLOR_PURPLE_BTN = (100, 30, 220)
COLOR_PURPLE_HOVER = (130, 50, 250)
COLOR_GREEN_BTN = (30, 180, 80)
COLOR_GREEN_HOVER = (50, 210, 100)
COLOR_RED_BTN = (180, 40, 40)
COLOR_RED_HOVER = (220, 60, 60)
COLOR_DARK_BOX = (25, 20, 55, 220)

# --- Polices ---
font_item = pygame.font.SysFont(None, 22)
font_title = pygame.font.SysFont(None, 36)
font_btn = pygame.font.SysFont(None, 24)
font_info = pygame.font.SysFont(None, 18)

# --- Liste des jeux ---
GAMES = [
    {
        "id": "gta6",
        "title": "Grand Theft Auto VI",
        "filename": "gta6",
        "zip_name": "gta6.zip",
        "exec_cmd": "bash ./installed_games/gta6/start.sh",
        "info": "Bienvenue à Vice City ! Grand Theft Auto VI vous plonge dans le monde ouvert le plus vaste."
    },
    {
        "id": "miside",
        "title": "MiSide",
        "filename": "miside",
        "zip_name": "miside.zip",
        "exec_cmd": "bash ./installed_games/miside/start.sh",
        "info": "MiSide est un jeu d'aventure psychologique et d'horreur."
    },
    {
        "id": "mhur",
        "title": "My Hero Ultra Rumble",
        "filename": "mhur",
        "zip_name": "mhur.zip",
        "exec_cmd": "bash ./installed_games/mhur/start.sh",
        "info": "Choisissez votre personnage préféré et battez-vous en équipe."
    },
    {
        "id": "cp",
        "title": "Cyberpunk 2077",
        "filename": "cp",
        "zip_name": "cp.zip",
        "exec_cmd": "bash ./installed_games/cp/start.sh",
        "info": "Incarnez V, un mercenaire hors-la-loi à la recherche d'un implant unique dans la mégapole de Night City."
    },
    {
        "id": "sa2",
        "title": "Sonic Adventure 2",
        "filename": "sa2",
        "zip_name": "sa2.zip",
        "exec_cmd": "bash ./installed_games/sa2/start.sh",
        "info": "Rejoignez Sonic et ses amis dans une course contre la montre pour sauver le monde."
    },
    {
        "id": "gh",
        "title": "Grey Hack",
        "filename": "gh",
        "zip_name": "gh.zip",
        "exec_cmd": "bash ./installed_games/gh/start.sh",
        "info": "Un jeu de simulation de piratage informatique massivement multijoueur."
    }
]

# Suivi de l'état des jeux
install_status = {game["id"]: "idle" for game in GAMES}

for game in GAMES:
    game_path = os.path.join(GAMES_DIR, game["id"])
    if os.path.exists(game_path):
        install_status[game["id"]] = "installed"

# --- Chargement des images ---
def load_game_images():
    images = {}
    extensions = ('.jpg', '.jpeg', '.png', '.webp')
    
    all_files = []
    if os.path.exists(ICON_DIR):
        for root, _, files in os.walk(ICON_DIR):
            for f in files:
                all_files.append(os.path.join(root, f))

    for game in GAMES:
        found_path = None
        target_name = game["filename"].lower().replace(" ", "")

        for filepath in all_files:
            fname = os.path.splitext(os.path.basename(filepath))[0].lower().replace(" ", "")
            ext = os.path.splitext(filepath)[1].lower()
            if (fname == target_name or fname == game["id"].lower()) and ext in extensions:
                found_path = filepath
                break

        if found_path:
            try:
                images[game["id"]] = pygame.image.load(found_path).convert_alpha()
            except Exception as e:
                print(f"Erreur de chargement pour {game['id']}: {e}")
                images[game["id"]] = None
        else:
            images[game["id"]] = None

    return images

game_images = load_game_images()

# --- Creation d'une image par defaut si manquante ---
def create_placeholder_image(width, height, text):
    surf = pygame.Surface((width, height))
    surf.fill((30, 40, 80))
    pygame.draw.rect(surf, COLOR_BORDER, (0, 0, width, height), 2)
    
    # Rendu du titre centre
    words = text.split(' ')
    y_offset = height // 3
    for word in words:
        txt_surf = font_btn.render(word, True, COLOR_TEXT_ACTIVE)
        surf.blit(txt_surf, ((width - txt_surf.get_width()) // 2, y_offset))
        y_offset += txt_surf.get_height() + 5
    return surf

# --- Redimensionnement sans déformer ---
def scale_aspect_ratio(image, target_width, target_height):
    img_width, img_height = image.get_size()
    ratio = min(target_width / img_width, target_height / img_height)
    new_w, new_h = max(1, int(img_width * ratio)), max(1, int(img_height * ratio))
    return pygame.transform.smoothscale(image, (new_w, new_h)), new_w, new_h

# --- Téléchargement et Installation ---
def download_and_install_game(game):
    game_id = game["id"]
    install_status[game_id] = "downloading"
    
    url = f"{SERVER_URL}/{game['zip_name']}"
    zip_dest = os.path.join(GAMES_DIR, game["zip_name"])
    extract_folder = os.path.join(GAMES_DIR, game_id)

    try:
        print(f"Téléchargement depuis {url}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(zip_dest, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Extraction vers {extract_folder}...")
            with zipfile.ZipFile(zip_dest, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
            
            os.remove(zip_dest)
            install_status[game_id] = "installed"
            print(f"{game['title']} installé avec succès !")
        else:
            print(f"Erreur HTTP : {response.status_code}")
            install_status[game_id] = "idle"
    except Exception as e:
        print(f"Erreur lors de l'installation : {e}")
        install_status[game_id] = "idle"

# --- Lancement du Jeu ---
def launch_game(game):
    subprocess.Popen(game["exec_cmd"], shell=True)

# --- Désinstallation ---
def uninstall_game(game):
    game_id = game["id"]
    game_folder = os.path.join(GAMES_DIR, game_id)
    if os.path.exists(game_folder):
        import shutil
        shutil.rmtree(game_folder)
    install_status[game_id] = "idle"

# --- Layout ---
SIDEBAR_WIDTH = 260
ITEM_HEIGHT = 50
GRID_X = SIDEBAR_WIDTH + 20
GRID_Y = 20
COLS = 3
CARD_MARGIN = 20
available_width = WIDTH - SIDEBAR_WIDTH - (CARD_MARGIN * (COLS + 1))
CARD_WIDTH = available_width // COLS
CARD_HEIGHT = int(CARD_WIDTH * 1.35)

selected_index = 0
current_view = "library"

def render_multiline_text(surface, text, x, y, max_width, font, color):
    words = text.split(' ')
    lines, current_line = [], ""
    for word in words:
        if font.size(current_line + word + " ")[0] < max_width:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    for i, line in enumerate(lines):
        surface.blit(font.render(line, True, color), (x, y + i * 26))

# --- Boucle Principale ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_view == "library":
                if mouse_pos[0] < SIDEBAR_WIDTH:
                    index = mouse_pos[1] // ITEM_HEIGHT
                    if 0 <= index < len(GAMES):
                        selected_index = index
                        current_view = "detail"
                else:
                    for i, game in enumerate(GAMES):
                        row, col = i // COLS, i % COLS
                        cx = GRID_X + col * (CARD_WIDTH + CARD_MARGIN)
                        cy = GRID_Y + row * (CARD_HEIGHT + CARD_MARGIN)
                        if pygame.Rect(cx, cy, CARD_WIDTH, CARD_HEIGHT).collidepoint(mouse_pos):
                            selected_index = i
                            current_view = "detail"

            elif current_view == "detail":
                game = GAMES[selected_index]
                status = install_status[game["id"]]

                if pygame.Rect(30, 20, 120, 40).collidepoint(mouse_pos):
                    current_view = "library"

                btn_action_rect = pygame.Rect(80, 370, 240, 120)
                if btn_action_rect.collidepoint(mouse_pos):
                    if status == "idle":
                        threading.Thread(target=download_and_install_game, args=(game,), daemon=True).start()
                    elif status == "installed":
                        launch_game(game)

                btn_uninst_rect = pygame.Rect(880, 310, 320, 80)
                if btn_uninst_rect.collidepoint(mouse_pos) and status == "installed":
                    uninstall_game(game)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                current_view = "library"

    # ==================== VUE 1 : BIBLIOTHÈQUE ====================
    if current_view == "library":
        screen.fill(COLOR_BG)
        pygame.draw.rect(screen, COLOR_SIDEBAR_BG, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(screen, COLOR_BORDER, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)

        for i, game in enumerate(GAMES):
            item_rect = pygame.Rect(0, i * ITEM_HEIGHT, SIDEBAR_WIDTH, ITEM_HEIGHT)
            color = COLOR_SELECTION if i == selected_index else ((20, 35, 70) if item_rect.collidepoint(mouse_pos) else COLOR_SIDEBAR_BG)
            pygame.draw.rect(screen, color, item_rect)
            screen.blit(font_item.render(game["title"], True, COLOR_TEXT_ACTIVE if i == selected_index else COLOR_TEXT_NORMAL), (15, i * ITEM_HEIGHT + 12))

        for i, game in enumerate(GAMES):
            row, col = i // COLS, i % COLS
            cx = GRID_X + col * (CARD_WIDTH + CARD_MARGIN)
            cy = GRID_Y + row * (CARD_HEIGHT + CARD_MARGIN)
            card_rect = pygame.Rect(cx, cy, CARD_WIDTH, CARD_HEIGHT)

            pygame.draw.rect(screen, COLOR_CARD_BG, card_rect)
            img = game_images.get(game["id"])
            if img:
                screen.blit(pygame.transform.smoothscale(img, (CARD_WIDTH, CARD_HEIGHT)), (cx, cy))
            else:
                placeholder = create_placeholder_image(CARD_WIDTH, CARD_HEIGHT, game["title"])
                screen.blit(placeholder, (cx, cy))
            
            border_color = (100, 160, 255) if i == selected_index else COLOR_BORDER
            pygame.draw.rect(screen, border_color, card_rect, 4 if i == selected_index or card_rect.collidepoint(mouse_pos) else 1)

    # ==================== VUE 2 : DÉTAIL DU JEU ====================
    elif current_view == "detail":
        screen.fill(COLOR_BG)
        game = GAMES[selected_index]
        status = install_status[game["id"]]
        img = game_images.get(game["id"])

        if img:
            scaled_img, new_w, new_h = scale_aspect_ratio(img, WIDTH, HEIGHT)
            screen.blit(scaled_img, ((WIDTH - new_w) // 2, (HEIGHT - new_h) // 2))
        else:
            placeholder = create_placeholder_image(WIDTH, HEIGHT, game["title"])
            screen.blit(placeholder, (0, 0))

        dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((10, 10, 25, 160))
        screen.blit(dark_overlay, (0, 0))

        btn_back = pygame.Rect(30, 20, 120, 40)
        pygame.draw.rect(screen, COLOR_PURPLE_HOVER if btn_back.collidepoint(mouse_pos) else COLOR_PURPLE_BTN, btn_back, border_radius=6)
        screen.blit(font_btn.render("← Retour", True, COLOR_TEXT_ACTIVE), (42, 26))

        screen.blit(font_title.render(game["title"], True, COLOR_TEXT_ACTIVE), (80, 300))

        btn_action = pygame.Rect(80, 370, 240, 120)
        if status == "idle":
            btn_color = COLOR_PURPLE_HOVER if btn_action.collidepoint(mouse_pos) else COLOR_PURPLE_BTN
            lbl = "Installer"
        elif status == "downloading":
            btn_color = (80, 80, 80)
            lbl = "En cours..."
        elif status == "installed":
            btn_color = COLOR_GREEN_HOVER if btn_action.collidepoint(mouse_pos) else COLOR_GREEN_BTN
            lbl = "JOUER"

        pygame.draw.rect(screen, btn_color, btn_action, border_radius=8)
        screen.blit(font_title.render(lbl, True, COLOR_TEXT_ACTIVE), (100, 410))

        if status == "installed":
            btn_uninst = pygame.Rect(880, 310, 320, 80)
            un_color = COLOR_RED_HOVER if btn_uninst.collidepoint(mouse_pos) else COLOR_RED_BTN
            pygame.draw.rect(screen, un_color, btn_uninst, border_radius=8)
            screen.blit(font_title.render("Désinstaller", True, COLOR_TEXT_ACTIVE), (940, 330))

        info_rect = pygame.Rect(880, 410, 320, 250)
        info_surface = pygame.Surface((320, 250), pygame.SRCALPHA)
        info_surface.fill(COLOR_DARK_BOX)
        screen.blit(info_surface, (880, 410))
        pygame.draw.rect(screen, COLOR_PURPLE_BTN, info_rect, 2, border_radius=8)
        screen.blit(font_btn.render("Info sur le jeu", True, COLOR_TEXT_ACTIVE), (900, 425))
        render_multiline_text(screen, game["info"], 900, 470, 280, font_info, COLOR_TEXT_NORMAL)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()