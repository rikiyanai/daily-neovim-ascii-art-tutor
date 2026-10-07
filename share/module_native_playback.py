"""Native-font module reward playback; canonical frames remain text.

The caller supplies a precise transport context. This module never changes
terminal configuration or grades art. Every frame requires an actual bound
Kitty acknowledgement; protocol fixtures are labelled as such by the tests.
"""
import hashlib
import os
import secrets
import sys
import time
from io import BytesIO

from PIL import Image

import sjis_authoring as native
import sjis_terminal as terminal


def play(motion, *, sender=None, output=None, wait=None):
    sender = sender or terminal.transmit_png
    output = output or sys.stdout
    wait = wait or time.sleep
    frames = motion["frames"]
    if len(frames) < 8:
        raise ValueError("A complete module animation needs at least eight frames.")
    metrics = native.load_font_metrics(
        os.environ.get("VIM_DAILY_SAITAMAAR_FONT") or native.DEFAULT_FONT_PATH)
    authored_interval = motion.get("interval", 0.2)
    interval = (1 / float(authored_interval["fps"]) if isinstance(authored_interval, dict)
                else float(authored_interval))
    if not 0 < interval <= 2:
        raise ValueError("Invalid authored playback interval.")
    # Equal code-point row widths do not imply equal proportional advances.
    # Keep one pixel canvas and one origin across the complete sequence.
    rasters = [native.render_text("\n".join(frame) + "\n", metrics) for frame in frames]
    width = max(raster.width_px for raster in rasters)
    height = max(raster.height_px for raster in rasters)
    print("MODULE REWARD · %s · %d native-font frames · not learner output" % (
        motion.get("title", "proportional animation"), len(frames)), file=output)
    print("Credit: " + motion["credit"], file=output)
    image_id = secrets.randbelow(2**30 - 1) + 1
    def delete_image():
        packet = "\x1b_Ga=d,d=i,i=%d;\x1b\\" % image_id
        if os.environ.get("TMUX"):
            packet = "\x1bPtmux;" + packet.replace("\x1b", "\x1b\x1b") + "\x1b\\"
        output.write(packet)
    receipts = []
    output.write("\x1b[s")
    try:
        for index, raster in enumerate(rasters):
            canvas = Image.new("L", (width, height), 0)
            canvas.paste(Image.frombytes("L", (raster.width_px, raster.height_px), raster.pixels), (0, 0))
            encoded = BytesIO()
            canvas.save(encoded, format="PNG", optimize=False, compress_level=9)
            delete_image()
            output.write("\x1b[u")
            output.flush()
            png = encoded.getvalue()
            receipt = sender(png, image_id)
            if (receipt.get("image_id") != image_id or receipt.get("terminal_reply") != "OK"
                    or receipt.get("png_sha256") != hashlib.sha256(png).hexdigest()):
                raise RuntimeError("Native animation ACK does not bind its current frame.")
            held_at = time.monotonic()
            wait(interval)
            receipts.append(dict(receipt, frame_index=index,
                                 canonical_text_sha256=raster.text_sha256,
                                 authored_hold_seconds=interval,
                                 elapsed_hold_seconds=time.monotonic() - held_at))
    finally:
        delete_image()
        output.write("\x1b[u\n")
        output.flush()
    return {"frames": receipts, "font_sha256": metrics.font_sha256,
            "font_size_px": metrics.font_size_px, "line_pitch_px": metrics.line_pitch_px,
            "canvas_px": [width, height], "origin_px": [0, 0],
            "operator_visual_acceptance": "unverified"}
