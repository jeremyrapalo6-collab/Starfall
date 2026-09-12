# Starfall Hackpad - KMK / CircuitPython
# XIAO RP2040 | 9-key matrix | EC11 encoder | 0.91in SSD1306 OLED

import board
import busio

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.media_keys import MediaKeys
from kmk.extensions import Extension

keyboard = KMKKeyboard()
layers = Layers()
encoder = EncoderHandler()
keyboard.modules = [layers, encoder]
keyboard.extensions.append(MediaKeys())

# PCB pinout
keyboard.col_pins = (board.D0, board.D1, board.D2)
keyboard.row_pins = (board.D3, board.D6, board.D7)
keyboard.diode_orientation = DiodeOrientation.ROW2COL

# EC11 rotation. The switch/push function is not wired as a separate input.
encoder.pins = ((board.D8, board.D9, None, False),)

# Persistent mode keys. The bottom-right key cycles modes because each layer
# maps that same physical key to the next default layer.
TO_EVERYDAY = KC.DF(0)
TO_GAMING = KC.DF(1)
TO_CODING = KC.DF(2)

# Common shortcuts
COPY = KC.LCTL(KC.C)
PASTE = KC.LCTL(KC.V)
CUT = KC.LCTL(KC.X)
UNDO = KC.LCTL(KC.Z)
REDO = KC.LCTL(KC.Y)
SELECT_ALL = KC.LCTL(KC.A)
SCREENSHOT = KC.LGUI(KC.LSFT(KC.S))

# VS Code / Python shortcuts
RUN_NO_DEBUG = KC.LCTL(KC.F5)
DEBUG = KC.F5
FORMAT = KC.LSFT(KC.LALT(KC.F))
COMMENT = KC.LCTL(KC.SLSH)
TERMINAL = KC.LCTL(KC.GRAVE)
SPLIT_EDITOR = KC.LCTL(KC.BSLS)
COMMAND_PALETTE = KC.LCTL(KC.LSFT(KC.P))
QUICK_OPEN = KC.LCTL(KC.P)

# Matrix order is row-major: row1 col1..3, row2 col1..3, row3 col1..3.
keyboard.keymap = [
    # Everyday
    [
        COPY, PASTE, CUT,
        UNDO, REDO, SELECT_ALL,
        SCREENSHOT, KC.MPLY, TO_GAMING,
    ],
    # Gaming
    [
        KC.N1, KC.N2, KC.N3,
        KC.Q, KC.E, KC.R,
        KC.LSFT, KC.SPC, TO_CODING,
    ],
    # Coding
    [
        RUN_NO_DEBUG, DEBUG, FORMAT,
        COMMENT, TERMINAL, SPLIT_EDITOR,
        COMMAND_PALETTE, QUICK_OPEN, TO_EVERYDAY,
    ],
]

# Encoder: left/right/click for each layer. Click is unused.
encoder.map = [
    ((KC.VOLD, KC.VOLU, KC.NO),),
    ((KC.VOLD, KC.VOLU, KC.NO),),
    ((KC.LCTL(KC.PGUP), KC.LCTL(KC.PGDN), KC.NO),),
]

# OLED is optional at runtime: keyboard still works if its library/display is absent.
try:
    import adafruit_ssd1306

    class StarfallOLED(Extension):
        def __init__(self):
            self.display = None
            self.last_layer = None
            try:
                i2c = busio.I2C(board.D5, board.D4)  # SCL, SDA
                self.display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3C)
                self.display.fill(0)
                self.display.show()
            except Exception as exc:
                print('OLED disabled:', exc)
                self.display = None

        def during_bootup(self, keyboard):
            self._update(keyboard)

        def before_matrix_scan(self, keyboard):
            pass

        def on_runtime_enable(self, keyboard):
            pass

        def on_runtime_disable(self, keyboard):
            pass

        def after_matrix_scan(self, keyboard):
            self._update(keyboard)

        def before_hid_send(self, keyboard):
            pass

        def after_hid_send(self, keyboard):
            pass

        def on_powersave_enable(self, keyboard):
            pass

        def on_powersave_disable(self, keyboard):
            self._update(keyboard, force=True)

        def _update(self, keyboard, force=False):
            if self.display is None:
                return
            try:
                layer = keyboard.active_layers[0]
            except Exception:
                layer = 0
            if not force and layer == self.last_layer:
                return
            self.last_layer = layer
            names = ('EVERYDAY', 'GAMING', 'CODING')
            name = names[layer] if 0 <= layer < len(names) else 'STARFALL'
            self.display.fill(0)
            self.display.text('STARFALL', 0, 0, 1)
            self.display.text(name, 0, 13, 1)
            self.display.text('MODE  %d/3' % (layer + 1), 68, 22, 1)
            self.display.show()

    keyboard.extensions.append(StarfallOLED())
except ImportError as exc:
    print('OLED library missing:', exc)

if __name__ == '__main__':
    keyboard.go()
