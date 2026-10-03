import sys
import os
import zipfile
import pygame

# Initialisation de Pygame
pygame.init()

# --- Configuration de la fenêtre ---
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ma Bibliothèque de Jeux - Style Steam")
clock = pygame.time.Clock()

# --- Détection automatique et gestion du fichier icon.zip / dossier icon ---
def setup_and_find_icon_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Emplacements possibles pour 'icon.zip'
    possible_zips = [
        os.path.join(script_dir, "icon.zip"),                            # Même dossier que le .py
        "/sdcard/Download/icon.zip",                                     # Téléchargements Android/Termux
        "/sdcard/icon.zip",                                              # Racine Android
        os.path.join(os.path.expanduser("~"), "Desktop", "icon.zip")     # Bureau PC
    ]
    
    # Emplacements possibles pour le dossier 'icon' extrait
    possible_dirs = [
        os.path.join(script_dir, "icon"),
        "/sdcard/Download/icon",
        "/sdcard/icon",
        os.path.join(os.path.expanduser("~"), "Desktop", "icon")
    ]

    # 1. Si le dossier existe déjà, on l'utilise directement
    for target_dir in possible_dirs:
        if os.path.exists(target_dir) and os.path.isdir(target_dir):
            print(f"Dossier 'icon' trouvé : {target_dir}")
            return target_dir

    # 2. Sinon, on cherche un 'icon.zip' pour l'extraire
    for zip_path in possible_zips:
        if os.path.exists(zip_path):
            extract_target = os.path.join(script_dir, "icon")
            print(f"Extraction de {zip_path} vers {extract_target}...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(script_dir)
                return extract_target
            except Exception as e:
                print(f"Erreur lors de l'extraction de {zip_path}: {e}")

    # Dossier par défaut
    return os.path.join(script_dir, "icon")

ICON_DIR = setup_and_find_icon_dir()

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
COLOR_DARK_BOX = (25, 20, 55, 220)

# --- Polices ---
font_path = pygame.font.match_font('arial') or pygame.font.match_font('sans-serif')
font_item = pygame.font.Font(font_path, 22)
font_title = pygame.font.Font(font_path, 36)
font_btn = pygame.font.Font(font_path, 24)
font_info = pygame.font.Font(font_path, 18)

# --- Liste des jeux avec descriptions ---
GAMES = [
    {
        "id": "gta6",
        "title": "grand thef auto vi",
        "filename": "gta 6",
        "info": "Bienvenue à Vice City ! Grand Theft Auto VI vous plonge dans le monde ouvert le plus vaste et immersif de la série."
    },
    {
        "id": "miside",
        "title": "miside",
        "filename": "miside",
        "info": "MiSide est un jeu d'aventure psychologique et d'horreur où la frontière entre réalité et jeu vidéo s'efface."
    },
    {
        "id": "mhur",
        "title": "my hero ultra rumbel",
        "filename": "mhur",
        "info": "Choisissez votre personnage préféré et battez-vous en équipe dans ce Battle Royale survolté !"
    },
    {
        "id": "cp",
        "title": "cyberpunk",
        "filename": "cp",
        "info": "Incarnez V, un mercenaire hors-la-loi à la recherche d'un implant unique dans la mégapole de Night City."
    },
    {
        "id": "sa2",
        "title": "sonic adventure 2",
        "filename": "sa2",
        "info": "Rejoignez Sonic et ses amis (ou Shadow et Eggman) dans une course contre la montre pour sauver ou conquérir le monde."
    },
    {
        "id": "gh",
        "title": "grey hack",
        "filename": "gh",
        "info": "Un jeu de simulation de piratage informatique massivement multijoueur basé sur des commandes réelles."
    }
]

# --- Chargement des images ---
def load_game_images():
    images = {}
    extensions = ['.jpg', '.jpeg', '.png', '.webp']
    
    for game in GAMES:
        found_path = None
        base_name = game["filename"]
        
        for ext in extensions:
            path = os.path.join(ICON_DIR, base_name + ext)
            if os.path.exists(path):
                found_path = path
                break
        
        if found_path:
            try:
                img = pygame.image.load(found_path).convert_alpha()
                images[game["id"]] = img
            except Exception as e:
                print(f"Erreur de chargement pour {found_path}: {e}")
                images[game["id"]] = None
        else:
            images[game["id"]] = None

    return images

game_images = load_game_images()

# --- Redimensionnement sans déformer (Garde le ratio) ---
def scale_aspect_ratio(image, target_width, target_height):
    img_width, img_height = image.get_size()
    ratio = min(target_width / img_width, target_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    scaled_img = pygame.transform.smoothscale(image, (new_width, new_height))
    return scaled_img, new_width, new_height

# --- Layout / Dimensions ---
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

# --- Texte multiligne ---
def render_multiline_text(surface, text, x, y, max_width, font, color):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines):
        txt_surf = font.render(line, True, color)
        surface.blit(txt_surf, (x, y + i * 26))

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
                        row = i // COLS
                        col = i % COLS
                        cx = GRID_X + col * (CARD_WIDTH + CARD_MARGIN)
                        cy = GRID_Y + row * (CARD_HEIGHT + CARD_MARGIN)
                        card_rect = pygame.Rect(cx, cy, CARD_WIDTH, CARD_HEIGHT)
                        if card_rect.collidepoint(mouse_pos):
                            selected_index = i
                            current_view = "detail"

            elif current_view == "detail":
                btn_back = pygame.Rect(30, 20, 120, 40)
                if btn_back.collidepoint(mouse_pos):
                    current_view = "library"

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                current_view = "library"
            elif current_view == "library":
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(GAMES)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(GAMES)
                elif event.key == pygame.K_RETURN:
                    current_view = "detail"

    # ==================== VUE 1 : BIBLIOTHÈQUE ====================
    if current_view == "library":
        screen.fill(COLOR_BG)

        # Barre latérale
        pygame.draw.rect(screen, COLOR_SIDEBAR_BG, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(screen, COLOR_BORDER, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)

        for i, game in enumerate(GAMES):
            item_rect = pygame.Rect(0, i * ITEM_HEIGHT, SIDEBAR_WIDTH, ITEM_HEIGHT)
            
            if i == selected_index:
                pygame.draw.rect(screen, COLOR_SELECTION, item_rect)
                text_color = COLOR_TEXT_ACTIVE
            elif item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (20, 35, 70), item_rect)
                text_color = COLOR_TEXT_ACTIVE
            else:
                text_color = COLOR_TEXT_NORMAL

            pygame.draw.line(screen, COLOR_BORDER, (0, (i + 1) * ITEM_HEIGHT), (SIDEBAR_WIDTH, (i + 1) * ITEM_HEIGHT), 1)

            title_surface = font_item.render(game["title"], True, text_color)
            screen.blit(title_surface, (15, i * ITEM_HEIGHT + 12))

        # Grille de cartes
        for i, game in enumerate(GAMES):
            row = i // COLS
            col = i % COLS
            
            cx = GRID_X + col * (CARD_WIDTH + CARD_MARGIN)
            cy = GRID_Y + row * (CARD_HEIGHT + CARD_MARGIN)
            card_rect = pygame.Rect(cx, cy, CARD_WIDTH, CARD_HEIGHT)

            is_selected = (i == selected_index)
            is_hovered = card_rect.collidepoint(mouse_pos)

            pygame.draw.rect(screen, COLOR_CARD_BG, card_rect)

            img = game_images.get(game["id"])
            if img:
                scaled_img = pygame.transform.smoothscale(img, (CARD_WIDTH, CARD_HEIGHT))
                screen.blit(scaled_img, (cx, cy))

            if is_selected or is_hovered:
                border_color = (100, 160, 255) if is_selected else COLOR_BORDER
                pygame.draw.rect(screen, border_color, card_rect, 4)
            else:
                pygame.draw.rect(screen, COLOR_BORDER, card_rect, 1)

    # ==================== VUE 2 : DÉTAIL DU JEU ====================
    elif current_view == "detail":
        screen.fill(COLOR_BG)

        game = GAMES[selected_index]
        img = game_images.get(game["id"])

        if img:
            scaled_img, new_w, new_h = scale_aspect_ratio(img, WIDTH, HEIGHT)
            pos_x = (WIDTH - new_w) // 2
            pos_y = (HEIGHT - new_h) // 2
            screen.blit(scaled_img, (pos_x, pos_y))

            dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark_overlay.fill((10, 10, 25, 140))
            screen.blit(dark_overlay, (0, 0))

        # Bouton Retour
        btn_back = pygame.Rect(30, 20, 120, 40)
        back_hover = btn_back.collidepoint(mouse_pos)
        pygame.draw.rect(screen, COLOR_PURPLE_HOVER if back_hover else COLOR_PURPLE_BTN, btn_back, border_radius=6)
        back_txt = font_btn.render("← Retour", True, COLOR_TEXT_ACTIVE)
        screen.blit(back_txt, (42, 26))

        # Nom du jeu
        title_surf = font_title.render(game["title"], True, COLOR_TEXT_ACTIVE)
        screen.blit(title_surf, (80, 300))

        # Bouton "installer"
        btn_install = pygame.Rect(80, 370, 240, 120)
        inst_hover = btn_install.collidepoint(mouse_pos)
        pygame.draw.rect(screen, COLOR_PURPLE_HOVER if inst_hover else COLOR_PURPLE_BTN, btn_install, border_radius=8)
        inst_txt = font_title.render("installer", True, COLOR_TEXT_ACTIVE)
        screen.blit(inst_txt, (120, 410))

        # Bouton "desinstaller"
        btn_uninstall = pygame.Rect(880, 310, 320, 80)
        uninst_hover = btn_uninstall.collidepoint(mouse_pos)
        pygame.draw.rect(screen, COLOR_PURPLE_HOVER if uninst_hover else COLOR_PURPLE_BTN, btn_uninstall, border_radius=8)
        uninst_txt = font_title.render("desinstaller", True, COLOR_TEXT_ACTIVE)
        screen.blit(uninst_txt, (940, 330))

        # Bloc "info sur le jeu choisi"
        info_rect = pygame.Rect(880, 410, 320, 250)
        info_surface = pygame.Surface((320, 250), pygame.SRCALPHA)
        info_surface.fill(COLOR_DARK_BOX)
        screen.blit(info_surface, (880, 410))
        pygame.draw.rect(screen, COLOR_PURPLE_BTN, info_rect, 2, border_radius=8)

        info_header = font_btn.render("info sur le jeu choisi", True, COLOR_TEXT_ACTIVE)
        screen.blit(info_header, (900, 425))
        
        render_multiline_text(screen, game["info"], 900, 470, 280, font_info, COLOR_TEXT_NORMAL)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()