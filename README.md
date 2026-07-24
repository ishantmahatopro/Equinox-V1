# Equinox V1

Equinox V1 is my custom full size (108 key) wireless mechanical keybaord, its built around a **Adafruit Feather nRF52840 Express**.

so basicaly i wanted a full size board that could go fully wireles over bluetooth but still work as a normal wired keyboard when i need it too, and i really didnt want to just buy some kit and screw it togther.. i wanted to actualy understand how the whole thing works like the matrix the diodes the I2C gpio expanders the battery the little screen ALL of it, so i designed the entire thing from scratch in kicad and fusion 360 which took forever lol

![Equinox V1 full 3D model](Images/Screenshot%202026-07-02%20211919.png)

## why i made this

im 17 and i basicaly live on my keyboard, school work,coding, everything.. so i figured if im gonna be typing on somthing like 8 hours a day it might aswell be somthing i built myself and actualy understand top to bottom right

main goals i set for myself :

- design a full size PCB in kicad (108 keys, numpad + nav cluster included)
- make it **wireless** (BLE) off a lipo battery,, but keep usb-c as a backup incase
- drive a huge key matrix off only 2 I2C pins using the MCP23017 expanders
- add a little 1.9" LCD that runs a animated cherry blossom scene, just becuase i thought it looked cool
- keep the whole thing actualy manufacturable (real production files not just a pretty render)
- learn the full pipline : schematic -> pcb -> 3d model -> printed case -> firmware

honestly the wireless part was the scaryest bit and it took me alot of trys to get the matrix scaning right over the expanders,, but it works now so im happy

## project status

this repo has the complete hardware design + manufacturing outputs. its basicaly done as a "V1", theres definately stuff i would change for a V2 but everything here is real and usable

whats included :

- kicad project, schematic and pcb
- full 3d cad (fusion 360 + `.step` export)
- printable case parts (`.stl`) and a plate dxf
- production files (bom, positions, designators, ipc netlist, gerber zip)
- kmk firmware for the nrf52840

current hardware summary :

| | |
|---|---|
| Layout | full size, 108 keys (main block + nav + numpad) |
| Controller | Adafruit Feather nRF52840 Express |
| Connectivity | bluetooth LE **and** usb-c (Fn+Esc toggles at runtime) |
| Matrix | 21 columns x 6 rows, scaned through 2x MCP23017 I2C expanders |
| Diodes | 1N4148W, one per switch (COL2ROW) |
| Battery | 500mAh 1S lipo, with charge / low battery status leds |
| Display | Waveshare 1.9" ST7789 IPS lcd (animated cherry blossom scene) |
| Stabilizers | Durock Clear screw-in V2 (6.25u space + 2u / 2.25u / 2.75u) |
| Switches | Akko V3 Penguin Pro |
| Keycaps | Plum Blossom cherry profile shine-through PBT |
| Case | 3d printed (Hack Club PrintLegion) |
| PCB | fabbed at JLCPCB |

the keycaps are pink plum blossom shine through and the lcd runs a pink cherry blossom animation so the whole "Equinox" theme kinda just came togther around that,, wasnt even fully planned tbh

## images

### full 3d model
![Assembled 3D model with switches](Images/Screenshot%202026-07-02%20211919.png)

### indicator leds (caps / num / charging)
![Close up of the status LED indicators](Images/Screenshot%202026-07-02%20213116.png)

### pcb
![Equinox V1 PCB routing](Images/Screenshot%202026-07-02%20214339.png)

### schematic / wiring
the matrix, both gpio expanders, the mcu, usb-c, esd protection, stabs and display are all on one sheet..

![Equinox V1 schematic](Images/Screenshot%202026-07-02%20214315.png)

### other screenshots
some more views of the case and plate from fusion

![Case tray](Images/Screenshot%202026-07-02%20201928.png)
![Case side profile](Images/Screenshot%202026-07-02%20203534.png)
![Switch plate cutouts](Images/Screenshot%202026-07-02%20211927.png)
![Top plate frame](Images/Screenshot%202026-07-02%20211938.png)
![Bottom case](Images/Screenshot%202026-07-02%20212027.png)

## repo file checklist

important files in this repo :

- `PCB/Equinox V1.kicad_pro`
- `PCB/Equinox V1.kicad_sch`
- `PCB/Equinox V1.kicad_pcb`
- `CAD/Full Equinox V1/Equinox V1.step`
- `CAD/Printing Files/`  -> `Plate.stl`, `Top Plate.stl`, `Bottom.stl`, `Bottom Lifter.stl`, `Bottom Lifter Screw.stl`
- `Firmware/code.py`
- `Production/bom.csv`
- `Production/positions.csv`
- `Production/designators.csv`
- `Production/netlist.ipc`
- `Production/Equinox_V1.zip`  (gerbers)
- `bom.csv`
- `PDFs/Equinox V1.pdf`  (schematic print)

## cad

designed in **fusion 360**.. theres a `.step` export right next to it if you just want the geometry. all the print ready parts are in `CAD/Printing Files/`

## firmware note

firmware is **KMK** running on **circuitpython**, its all in one file :

- `Firmware/code.py`

it has the real nrf52840 feather pin map, both MCP23017 adresses (`0x20` and `0x21`), the full 108 key layout maped from my layout photo, the lock/battery led logic and the cherry blossom lcd animation. all the periferal code is wraped in try/except so if a display or a led pin is wrong it still lets you type it just skips that part

to flash it : double tap RESET on the feather, drop the circuitpython `.uf2`, then copy `code.py` plus the `kmk/` folder and the required `lib/` drivers (`adafruit_mcp230xx`, `adafruit_bus_device`, `adafruit_ble`, `adafruit_st7789`, `adafruit_display_text`) onto the `CIRCUITPY` drive

by defalt it boots as **usb** (easyest for first bring up) and **Fn+Esc** switches over to bluetooth. if you want it wireless first just swap `hid_type` and `secondary_hid_type` at the bottom of `code.py`

## bom (summary)

full bom is in `bom.csv`. prices are what i actualy payed (usd)

| # | Name | Purpose | Qty | Cost ($) | Distributor | Link |
|---|------|---------|-----|----------|-------------|------|
| 1 | 3D printed Case | keyboard case | 1 | 8 | Hack Club | [Buy](https://printlegion.hackclub.com) |
| 2 | PCB fabrication | the main board | 1 | 39.36 | JLCPCB | [Buy](https://cart.jlcpcb.com/shopcart/cart) |
| 3 | Plum Blossom Cherry Profile Top Shine-Through PBT Keycap Set V2 | keycaps to actualy type on | 1 | 28.35 | Curiosity Caps | [Buy](https://curiositycaps.in/products/plum-blossom-cherry-profile-shine-through-dye-sublimation-pbt-keycap-set) |
| 4 | Durock Clear Screw-In Stabilizers V2 | stabalizers to keep the big keys stable | 1 | 24.83 | Stackskb | [Buy](https://stackskb.com/store/durock-clear-screw-in-stabilizers-v2/?attribute_combination=7%2B1+Set&attribute_spacebar-size=6.25U) |
| 5 | Akko V3 Penguin Pro Switch (Pack of 45) | switches for the keys | 3(Already Have) | 47.22 | Stackskb | [Buy](https://stackskb.com/store/akko-penguin-pro-switch-pack-of-45/) |
| 6 | Adafruit Feather nRF52840 Express | microcontroler / the brains | 1 | 32.02 | Robu | [Buy](https://robu.in/product/adafruit-feather-nrf52840-express/) |
| 7 | WLY752530 3.7V 500mAh 1S LiPo Battery | battery | 1 | 2.74 | Robu | [Buy](https://robu.in/product/500mah-pcm-protected-micro-li-po-battery/) |
| 8 | 0805 X7R 100nF 50V ceramic capacitors | capacitors | 10 | 0.12 | Robu | [Buy](https://robu.in/product/tcc0805x7r104j500dt-cctc-smt-ceramic-capacitors-0805-x7r-104j100nf%c2%b15-0-rated-voltage50v-thickness0-85mmtape/) |
| 9 | Samsung 4.7uF 10V X7R 0805 capacitors | capacitors | 5 | 0.12 | Robu | [Buy](https://robu.in/product/cl21b475kpqvpne-samsung-cap-ceramic-4-7uf-10v-x7r-10-pad-smd-0805-125c-t-r-automotive-aec-q200/) |
| 10 | 1N4148W SOD-123 Diode | diode (1 per switch) | 216 | 1.59 | Robu | [Buy](https://robu.in/product/1n4148w-sod-123-1206-diodereel-of-3000/) |
| 11 | 3mm Green DIP LED | led | 15 | 0.12 | Robu | [Buy](https://robu.in/product/3mm-green-dip-led-pack-of-50/) |
| 12 | 3mm Red DIP LED | led | 15 | 0.14 | Robu | [Buy](https://robu.in/product/3mm-red-dip-led-pack-of-50/) |
| 13 | 16P Female Type-C SMD Connector | usb-c port | 2 | 0.8 | Robu | [Buy](https://robu.in/product/type-c-31-m-12-hroparts-5a-1-16p-female-type-c-smd-usb-connectors-rohs/) |
| 14 | XY308-2.54 3 Pin Screw Terminal Block | battery terminal | — | Free | Robu | — |
| 15 | JST SH 1x8P Right Angle Connector | display conection | 2 | 1.09 | Robu | [Buy](https://robu.in/product/sm08b-srss-tblfsn-jst-1x8p-8p-sh-tin-8-25%e2%84%8385%e2%84%83-1a-1-1mm-copper-alloy-surface-mount-smdp1mmsurface-mount%ef%bc%8cright-angle-wire-to-board-connector-rohs/) |
| 16 | Panasonic 4.7 kohm 0805 resistor | resistors (i2c pullups) | 11 | 0.11 | Robu | [Buy](https://robu.in/product/erj6enf4701v-panasonic-smd-chip-resistor-4-7-kohm-%c2%b1-1-125-mw-0805-2012-metric-thick-film-precision/) |
| 17 | Vishay 1 kohm 0805 resistor | resistors (led current limit) | 20 | 0.72 | Robu | [Buy](https://robu.in/product/crcw08051k00fkeahp-vishay-smd-chip-resistor-1-kohm-%c2%b1-1-500-mw-0805-2012-metric-thick-film-pulse-proof-high-power/) |
| 18 | Yageo 5.1 kohm 0805 resistor | resistors | 100 | 0.14 | Robu | [Buy](https://robu.in/product/rc0805jr-075k1l-yageo-smd-chip-resistor-5-1-kohm-%c2%b1-5-125-mw-0805-2012-metric-thick-film-general-purpose/) |
| 19 | MCP23017-E/SO I/O Expander (16-bit, I2C) | gpio expander | 4 | 8.78 | Robu | [Buy](https://robu.in/product/mcp23017-e-so-microchip-i-o-expander-16-bit-i2c-serial-1-8-v-5-5-v-soic-28-pins/) |
| 20 | USBLC6-2SC6 SOT-23-6 | esd / surge protection | 5 | 0.37 | Robu | [Buy](https://robu.in/product/usblc6-2sc6-ms-msksemi-4-5a-15v-150w-6v-5v-sot-23-6-esd-and-surge-protection-tvs-esd-rohs/) |
| 21 | Waveshare 1.9inch LCD Display Module (SPI, IPS) | the screen | 1 | 11.17 | Robu | [Buy](https://robu.in/product/waveshare-lcd-display-module-spi-interface-262k-colors/) |

**total bom cost : $160**

---

thanks for reading,, if you build one or have any questions feel free to open a issue. this was my first proper wireless board so its deffinately not perfect but i learnt a insane amount making it :)
