# =====================================================================
#  code.py  -  KMK firmware : full-size (108-key) wireless/wired keyboard
#
#  Board : Adafruit Feather nRF52840 Express  (CircuitPython)
#  Matrix: 2x MCP23017 I2C expanders
#            U1 @ 0x20  ->  Col0 .. Col15
#            U2 @ 0x21  ->  Col16 .. Col20  +  Row0 .. Row5
#  Layout: standard full-size, columns = 14 main + 3 nav + 4 numpad = 21
#  Diodes: COL2ROW
#  Extras: Caps/Num LEDs, battery LEDs, animated cherry-blossom LCD
#  Link  : USB + BLE  (Fn+Esc toggles between them at runtime)
# =====================================================================
#
#  COPY ONTO CIRCUITPY:
#    /code.py                      <- this file
#    /kmk/                         <- the 'kmk' folder from the KMK repo
#    /lib/adafruit_mcp230xx/       <- MCP23017 driver
#    /lib/adafruit_bus_device/     <- dependency of the MCP driver
#    /lib/adafruit_ble/            <- required for Bluetooth HID
#    /lib/adafruit_st7789.mpy      <- LCD driver   (optional: display)
#    /lib/adafruit_display_text/   <- status text  (optional: display)
#    (vectorio + random are built into CircuitPython)
#
#  FLASH: double-tap RESET -> FTHR840BOOT appears -> drop the CP .uf2 ->
#         CIRCUITPY appears -> copy this file + the folders above.
# =====================================================================

import board
import busio
import digitalio
import analogio

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.scanners.digitalio import MatrixScanner
from kmk.hid import HIDModes
from kmk.modules.layers import Layers
from kmk.modules import Module

from adafruit_mcp230xx.mcp23017 import MCP23017


# ---------------------------------------------------------------------
#  1.  PIN MAP  (these are the REAL nRF52840 Feather names from the board)
# ---------------------------------------------------------------------
#  Wire each peripheral to these exact pads. All of them are broken out on
#  your board's silk. If you soldered an LED/display line to a DIFFERENT
#  pad, just change its name here to match.

# ST7789 LCD (SPI). CLK/DIN must be the hardware-SPI pins.
LCD_CLK = board.SCK          # LCD "CLK"
LCD_DIN = board.MOSI         # LCD "DIN"  (board silk "MO")
LCD_CS  = board.A0           # LCD "CS"
LCD_DC  = board.D6           # LCD "DC"
LCD_RST = board.D9           # LCD "RST"
LCD_BL  = board.A1           # LCD "BL"

# Indicator LEDs:  GPIO -> 1k -> LED anode ; cathode -> GND  (active HIGH)
LED_CAPS     = board.D10
LED_NUM      = board.D11
LED_BAT_LOW  = board.D12
LED_BAT_GOOD = board.D13

# Battery sense (internal 2:1 divider on the Feather)
try:
    BATTERY_PIN = board.VOLTAGE_MONITOR
except AttributeError:
    BATTERY_PIN = board.A6


# ---------------------------------------------------------------------
#  2.  I2C  +  the two MCP23017 expanders
# ---------------------------------------------------------------------
i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)

mcp1 = MCP23017(i2c, address=0x20)   # U1 : columns 0..15
mcp2 = MCP23017(i2c, address=0x21)   # U2 : columns 16..20 + rows 0..5

# get_pin(n): n = 0..7 -> GPA0..GPA7 ,  n = 8..15 -> GPB0..GPB7
col_pins = [
    mcp1.get_pin(0),  mcp1.get_pin(1),  mcp1.get_pin(2),  mcp1.get_pin(3),   # Col0-3   U1 GPA0-3
    mcp1.get_pin(4),  mcp1.get_pin(5),  mcp1.get_pin(6),  mcp1.get_pin(7),   # Col4-7   U1 GPA4-7
    mcp1.get_pin(8),  mcp1.get_pin(9),  mcp1.get_pin(10), mcp1.get_pin(11),  # Col8-11  U1 GPB0-3
    mcp1.get_pin(12), mcp1.get_pin(13), mcp1.get_pin(14), mcp1.get_pin(15),  # Col12-15 U1 GPB4-7
    mcp2.get_pin(0),  mcp2.get_pin(1),  mcp2.get_pin(2),  mcp2.get_pin(3),   # Col16-19 U2 GPA0-3
    mcp2.get_pin(4),                                                          # Col20    U2 GPA4
]
row_pins = [
    mcp2.get_pin(8),  mcp2.get_pin(9),  mcp2.get_pin(10),                     # Row0-2  U2 GPB0-2
    mcp2.get_pin(11), mcp2.get_pin(12), mcp2.get_pin(13),                     # Row3-5  U2 GPB3-5
]
COLS = len(col_pins)   # 21
ROWS = len(row_pins)   # 6


# ---------------------------------------------------------------------
#  3.  Keyboard + matrix scanner
# ---------------------------------------------------------------------
#  Diodes are COL2ROW. If keys don't register / everything ghosts, change
#  COL2ROW to ROW2COL and re-test.
keyboard = KMKKeyboard()
keyboard.matrix = MatrixScanner(
    cols=col_pins,
    rows=row_pins,
    diode_orientation=DiodeOrientation.COL2ROW,
)


# ---------------------------------------------------------------------
#  4.  KEYMAP  (full-size, mapped from your layout photo)
# ---------------------------------------------------------------------
#  Row-major: index = Row*21 + Col.  Columns are:
#     0..13  = main typing block        (14 wide)
#     14..16 = nav cluster (Ins/Home... / arrows)
#     17..20 = numpad
#  If a key prints wrong, only THAT row/col is mismatched to your wiring;
#  swap it here. Empty intersections are KC.NO.
_______ = KC.TRNS
XXXXXXX = KC.NO

_L0 = [
    # Row0 : Esc  F1-F12            | Print Scroll Pause | Cal Mute Vol- Vol+
    KC.ESC,  KC.F1,  KC.F2,  KC.F3,  KC.F4,  KC.F5,  KC.F6,  KC.F7,  KC.F8,  KC.F9,  KC.F10, KC.F11, KC.F12, XXXXXXX, KC.PSCR, KC.SLCK, KC.PAUS, XXXXXXX, KC.MUTE, KC.VOLD, KC.VOLU,
    #                                                          ^Col17 "Cal": set to KC.CALCULATOR if your KMK build has it
    # Row1 : ` 1-0 - = Bksp        | Ins Home PgUp     | Num  /  *  -
    KC.GRV,  KC.N1,  KC.N2,  KC.N3,  KC.N4,  KC.N5,  KC.N6,  KC.N7,  KC.N8,  KC.N9,  KC.N0,  KC.MINS, KC.EQL, KC.BSPC, KC.INS,  KC.HOME, KC.PGUP, KC.NLCK, KC.PSLS, KC.PAST, KC.PMNS,
    # Row2 : Tab Q-P [ ] \         | Del End  PgDn     | 7  8  9  +
    KC.TAB,  KC.Q,   KC.W,   KC.E,   KC.R,   KC.T,   KC.Y,   KC.U,   KC.I,   KC.O,   KC.P,   KC.LBRC, KC.RBRC, KC.BSLS, KC.DEL,  KC.END,  KC.PGDN, KC.P7,   KC.P8,   KC.P9,   KC.PPLS,
    # Row3 : Caps A-L ; ' Enter    |  (none)           | 4  5  6
    KC.CAPS, KC.A,   KC.S,   KC.D,   KC.F,   KC.G,   KC.H,   KC.J,   KC.K,   KC.L,   KC.SCLN, KC.QUOT, KC.ENT,  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, KC.P4,   KC.P5,   KC.P6,   XXXXXXX,
    # Row4 : LShift Z-/ RShift     |     Up            | 1  2  3  KPEnter
    KC.LSFT, KC.Z,   KC.X,   KC.C,   KC.V,   KC.B,   KC.N,   KC.M,   KC.COMM, KC.DOT, KC.SLSH, KC.RSFT, XXXXXXX, XXXXXXX, XXXXXXX, KC.UP,   XXXXXXX, KC.P1,   KC.P2,   KC.P3,   KC.PENT,
    # Row5 : Ctrl Win Alt Space Alt Fn Ctrl | Left Down Right | 0  .
    KC.LCTL, KC.LGUI, KC.LALT, XXXXXXX, XXXXXXX, KC.SPC, XXXXXXX, XXXXXXX, XXXXXXX, KC.RALT, KC.MO(1), KC.RCTL, XXXXXXX, XXXXXXX, KC.LEFT, KC.DOWN, KC.RIGHT, KC.P0, XXXXXXX, KC.PDOT, XXXXXXX,
]

# Layer 1 (Fn): transparent except the USB/BLE toggle on Fn+Esc.
_L1 = [_______] * (ROWS * COLS)
_L1[0] = KC.HID     # Fn + Esc  ->  switch USB <-> Bluetooth

keyboard.keymap = [_L0, _L1]


# ---------------------------------------------------------------------
#  5.  Modules: layers + status/animation module
# ---------------------------------------------------------------------
layers = Layers()


def _out(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.OUTPUT
    d.value = False
    return d


class StatusModule(Module):
    """Lock LEDs from host (USB), battery LEDs from the LiPo, and an
    animated cherry-blossom scene on the LCD. All peripheral code is
    guarded so a bad pin or missing display never stops typing."""

    def __init__(self):
        self._n = 0
        self._frame = 0
        self._hid = None

        # ---- LEDs ----
        self.led_caps = self.led_num = self.led_low = self.led_good = None
        try:
            self.led_caps = _out(LED_CAPS)
            self.led_num = _out(LED_NUM)
            self.led_low = _out(LED_BAT_LOW)
            self.led_good = _out(LED_BAT_GOOD)
        except Exception as e:      # noqa: BLE001
            print("LED init failed:", e)

        # ---- battery ADC ----
        self.batt = None
        try:
            self.batt = analogio.AnalogIn(BATTERY_PIN)
        except Exception as e:      # noqa: BLE001
            print("Battery init failed:", e)

        # ---- LCD scene ----
        self._display = None
        self._petals = []
        self._px = self._py = self._pvx = self._pvy = []
        self._W = self._H = 0
        self._lbl = None
        try:
            self._setup_scene()
        except Exception as e:      # noqa: BLE001
            print("LCD init failed:", e)

    # ---------- cherry-blossom scene ----------
    def _setup_scene(self):
        import displayio
        import vectorio
        import random
        import terminalio
        from adafruit_st7789 import ST7789
        from adafruit_display_text import label
        try:
            from fourwire import FourWire            # CircuitPython 9+
        except ImportError:
            from displayio import FourWire            # CircuitPython 8

        self._rand = random
        displayio.release_displays()
        spi = board.SPI()
        bus = FourWire(spi, command=LCD_DC, chip_select=LCD_CS,
                       reset=LCD_RST, baudrate=24_000_000)
        # 1.9" 170x320 panel in landscape. If the image is shifted/rotated
        # wrong, tweak rotation (0/90/180/270) and rowstart/colstart.
        # If it's garbled, lower baudrate (e.g. 12_000_000).
        disp = ST7789(bus, width=320, height=170,
                      rowstart=35, colstart=0, rotation=90)
        W, H = 320, 170
        self._W, self._H = W, H

        bl = digitalio.DigitalInOut(LCD_BL)
        bl.direction = digitalio.Direction.OUTPUT
        bl.value = True                               # backlight on

        def pal(color):
            p = displayio.Palette(1)
            p[0] = color
            return p

        sky = pal(0xFFF0F4)      # soft pink-white sky
        wood = pal(0x6B4A2B)     # trunk brown
        pink = pal(0xFF8FB4)     # blossom
        pink2 = pal(0xFFC2D6)    # blossom highlight
        petalc = pal(0xFFB0C6)   # falling petal

        root = displayio.Group()
        root.append(vectorio.Rectangle(pixel_shader=sky, width=W, height=H, x=0, y=0))

        # trunk + two branches (stylised, bottom-left)
        root.append(vectorio.Polygon(pixel_shader=wood, x=0, y=0, points=[
            (36, H), (46, H), (52, 74), (44, 62), (40, 62), (34, 76)]))
        root.append(vectorio.Polygon(pixel_shader=wood, x=0, y=0, points=[
            (44, 94), (98, 60), (102, 66), (46, 102)]))
        root.append(vectorio.Polygon(pixel_shader=wood, x=0, y=0, points=[
            (42, 110), (8, 86), (6, 92), (42, 118)]))

        # blossom canopy
        canopy = [(44, 56, 19), (68, 44, 15), (92, 56, 14),
                  (30, 62, 13), (80, 66, 13), (54, 40, 13),
                  (18, 76, 11), (100, 62, 11)]
        for (cx, cy, r) in canopy:
            root.append(vectorio.Circle(pixel_shader=pink, radius=r, x=cx, y=cy))
        for (cx, cy, r) in canopy[:4]:
            root.append(vectorio.Circle(pixel_shader=pink2, radius=max(3, r - 7),
                                        x=cx + 3, y=cy - 3))

        # falling petals
        N = 14
        self._px, self._py, self._pvx, self._pvy = [], [], [], []
        self._petals = []
        for _ in range(N):
            x = float(random.randint(0, W - 1))
            y = float(random.randint(-H, H - 1))
            c = vectorio.Circle(pixel_shader=petalc,
                                radius=random.randint(2, 4),
                                x=int(x), y=int(y))
            root.append(c)
            self._petals.append(c)
            self._px.append(x)
            self._py.append(y)
            self._pvy.append(random.uniform(0.7, 1.9))     # fall speed
            self._pvx.append(random.uniform(-0.7, 0.7))    # sideways drift

        # tiny status readout (delete these 2 lines for a pure scene)
        self._lbl = label.Label(terminalio.FONT, text="", color=0x9A5B72,
                                x=W - 96, y=10)
        root.append(self._lbl)

        disp.root_group = root
        self._display = disp

    def _animate(self):
        r = self._rand
        for i, c in enumerate(self._petals):
            self._py[i] += self._pvy[i]
            self._px[i] += self._pvx[i]
            if self._py[i] > self._H:                 # recycle at the top
                self._py[i] = -float(r.randint(0, 30))
                self._px[i] = float(r.randint(0, self._W - 1))
            c.x = int(self._px[i]) % self._W
            c.y = int(self._py[i])

    # ---------- HID lock-LED helper ----------
    def _get_hid(self):
        try:
            import usb_hid
            for d in usb_hid.devices:
                if d.usage_page == 0x01 and d.usage == 0x06:
                    return d
        except Exception:           # noqa: BLE001
            pass
        return None

    def _battery_volts(self):
        if not self.batt:
            return None
        return (self.batt.value / 65535) * 3.3 * 2

    # ================= KMK Module hooks =================
    def during_bootup(self, keyboard):
        self._hid = self._get_hid()

    def before_matrix_scan(self, keyboard):
        return

    def after_matrix_scan(self, keyboard):
        # step the animation a bit slower than the scan loop
        self._frame += 1
        if self._display is not None and (self._frame & 1) == 0:
            try:
                self._animate()
            except Exception:       # noqa: BLE001
                pass

    def process_key(self, keyboard, key, is_pressed, int_coord):
        return key

    def before_hid_send(self, keyboard):
        return

    def after_hid_send(self, keyboard):
        self._n += 1

        # lock LEDs (host reports these over USB; BLE usually does not)
        if self.led_caps and self._hid:
            try:
                report = self._hid.get_last_received_report()
                if report:
                    leds = report[0]
                    self.led_num.value = bool(leds & 0x01)    # Num Lock
                    self.led_caps.value = bool(leds & 0x02)   # Caps Lock
            except Exception:       # noqa: BLE001
                pass

        # battery LEDs + status text, throttled
        if self._n % 1500 == 0:
            v = self._battery_volts()
            if v is not None and self.led_low and self.led_good:
                self.led_low.value = v < 3.5
                self.led_good.value = v >= 3.7
            if self._lbl is not None:
                try:
                    txt = ""
                    try:
                        txt = "BLE " if keyboard.hid_type == HIDModes.BLE else "USB "
                    except Exception:   # noqa: BLE001
                        pass
                    if v is not None:
                        txt += "{:.2f}V".format(v)
                    self._lbl.text = txt
                except Exception:       # noqa: BLE001
                    pass

    def on_powersave_enable(self, keyboard):
        for led in (self.led_caps, self.led_num, self.led_low, self.led_good):
            if led:
                led.value = False

    def on_powersave_disable(self, keyboard):
        return

    def deinit(self, keyboard):
        return


keyboard.modules = [layers, StatusModule()]


# ---------------------------------------------------------------------
#  6.  Go!
# ---------------------------------------------------------------------
#  USB-primary here = plug in and type immediately (best for first bring-up).
#  Fn+Esc (KC.HID) switches to Bluetooth at runtime.
#  For a daily WIRELESS keyboard, swap these so BLE is primary:
#       hid_type=HIDModes.BLE, secondary_hid_type=HIDModes.USB
if __name__ == "__main__":
    keyboard.go(
        hid_type=HIDModes.USB,
        secondary_hid_type=HIDModes.BLE,
        ble_name="NRF Keyboard",
    )
