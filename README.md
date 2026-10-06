A transmission problem on the app so not usable, I'm currently working on it

# launcher-to-termux
play beta test

requires having termux-x11
install : 

pkg install x11-repo -y && apt update
pkg install dpkg pkg-config build-essential python libx11 libxext libxrandr sdl2 sdl2-image sdl2-mixer sdl2-ttf freetype fontconfig xorgproto termux-x11-nightly -y


pip install setuptools wheel
pip install pygame --no-binary :all: --no-build-isolation

font = pygame.font.Font(None, 36)


DISPLAY=:0 python ~/launcher-to-termux/launcher.py.

or 

termux-x11 :0 &
export DISPLAY=:0
cd ~/launcher-to-termux
python launcher.py


start serveur python -m http.server 8080     


