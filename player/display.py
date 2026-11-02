"""128x64 SSD1306 OLED on SPI1: the local dashboard.

Layout:
    PLAY            vol 45%
    -----------------------
    Al Jolson
    Avalon (1920)
"""

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

from . import state

WIDTH = 128
HEIGHT = 64


class Display:
    def __init__(self, spi_names, reset_name, dc_name, cs_name):
        clock, mosi, miso = (getattr(board, name) for name in spi_names)
        self.spi = busio.SPI(clock, mosi, miso)
        self.reset = digitalio.DigitalInOut(getattr(board, reset_name))
        self.dc = digitalio.DigitalInOut(getattr(board, dc_name))
        # This OLED has no physical CS pin; the library still wants one.
        self.cs = digitalio.DigitalInOut(getattr(board, cs_name))

        self.oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, self.spi, self.dc, self.reset, self.cs)
        self.font = ImageFont.load_default()
        self._last_frame = None

        self.clear()

    # ---------- helpers ----------
    def _text_width(self, draw, text):
        return draw.textlength(text, font=self.font)

    def _fit(self, draw, text, width=WIDTH):
        """Shorten text with '..' until it fits on one line."""
        if self._text_width(draw, text) <= width:
            return text
        while text and self._text_width(draw, text + "..") > width:
            text = text[:-1]
        return text + ".."

    # ---------- drawing ----------
    def show(self, status, volume, artist="", title=""):
        """Draw a full frame. Only sends it to the OLED when something changed."""
        if status == state.STANDBY:
            frame_key = (status,)   # standby screen does not depend on the rest
        else:
            frame_key = (status, volume, artist, title)
        if frame_key == self._last_frame:
            return
        self._last_frame = frame_key

        image = Image.new("1", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(image)

        if status == state.STANDBY:
            draw.text((34, 22), "STANDBY", font=self.font, fill=255)
            draw.text((52, 38), "Zzz", font=self.font, fill=255)
        else:
            # Status line with volume on the right.
            draw.text((0, 0), status, font=self.font, fill=255)
            vol_text = f"vol {volume}%"
            draw.text((WIDTH - self._text_width(draw, vol_text), 0), vol_text, font=self.font, fill=255)
            draw.line((0, 12, WIDTH, 12), fill=255)

            draw.text((0, 14), self._fit(draw, artist), font=self.font, fill=255)
            draw.text((0, 26), self._fit(draw, title), font=self.font, fill=255)

        self.oled.image(image)
        self.oled.show()
        self.last_image = image   # kept for debugging / screenshots

    def clear(self):
        self.oled.fill(0)
        self.oled.show()
        self._last_frame = None

    def close(self):
        self.clear()
