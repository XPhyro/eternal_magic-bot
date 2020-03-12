import win32com.client as comclt
import autoit
import time
import win32gui
import re
import keyboard


class WindowMgr:
    def __init__(self):
        self._handle = None

    def find_window(self, class_name, window_name=None):
        self._handle = win32gui.FindWindow(class_name, window_name)

    def foreground_window(self):
        self._handle = win32gui.GetForegroundWindow()

    def _window_enum_callback(self, hwnd, wildcard):
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        win32gui.SetForegroundWindow(self._handle)

    @property
    def handle(self):
        return self._handle


def initialise():
    game_window = WindowMgr()
    game_window.find_window_wildcard(gameWildcard)

    if game_window.handle is None:
        print("\nUhm, would you, maybe, like to start the game first? "
              "Like I'm a bot made for Eternal Magic, you know that right?")
        while game_window.handle is None:
            game_window.find_window_wildcard(gameWildcard)
            time.sleep(0.5)
        print("Oh it seems you finally started the game, I\'ll give you another chance then.\n")
        print("Press {} again.".format(initiateShortcut))
        keyboard.wait(initiateShortcut)

    update()


def update():
    game_window = WindowMgr()
    game_window.find_window_wildcard(gameWildcard)
    quest_pos = autoit.mouse_get_pos()

    print(quest_pos)
    print(game_window.handle)
    print("\nHold {} to stop.".format(stopShortcut))

    while True:
        try:
            prev_mouse_pos = autoit.mouse_get_pos()
            prev_foreground_window = WindowMgr()
            prev_foreground_window.foreground_window()
            game_window.set_foreground()

            time.sleep(0.040)

            autoit.mouse_click("left", quest_pos[0], quest_pos[1], 1, 0)

            prev_foreground_window.set_foreground()
            autoit.mouse_move(prev_mouse_pos[0], prev_mouse_pos[1], 0)

            for i in range(clickInterval):
                if keyboard.is_pressed(stopShortcut):
                    return
                time.sleep(1)
        except:
            continue


# wsh = comclt.Dispatch("WScript.Shell")
# wsh.AppActivate("Eternal Magic")
# wsh.SendKeys("{ENTER}")

gameWildcard = "Eternal Magic -Andromeda"
initiateShortcut = "shift+ctrl+alt+s"
stopShortcut = "alt+shift+d"
clickInterval = 45  # Must be a positive integer

print("Press {} to initiate.".format(initiateShortcut))
keyboard.wait(initiateShortcut)
initialise()
