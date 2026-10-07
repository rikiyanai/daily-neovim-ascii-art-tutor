#!/usr/bin/env python3
"""Review-only gallery of original level 3–7 avatar candidates.

This is deliberately a separate demo.  It does not import or mutate the live
``dashboard_theme.AVATARS`` ladder, and it has no selection command: the
operator can compare complete candidates before a later, explicit choice.

Run ``python3 share/avatar_options.py`` for every candidate or pass
``--level 5`` for one level.  Output is selectable text; colour is applied only
to labels, never to the art rows.
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import ui_style as UI  # noqa: E402


# Archived v1 candidates remain here as provenance.  They were never selected
# for the live ladder; keeping them makes the review history reproducible.
ARCHIVED_AVATAR_OPTIONS = {
    3: (
        {"id": "v1-lv3-quiet-spark", "name": "Quiet spark", "art": ("  o  ", " /|\\ ", " / \\ ")},
        {"id": "v1-lv3-ruler", "name": "Ruler", "art": ("  .  ", " _|_ ", "  |  ")},
        {"id": "v1-lv3-scout", "name": "Scout", "art": ("  o> ", " /|  ", " / \\ ")},
    ),
    4: (
        {"id": "v1-lv4-frame", "name": "Frame", "art": ("+---+", "|o  |", "+-+-+")},
        {"id": "v1-lv4-window", "name": "Window", "art": (" .-. ", "/|_|\\", "  |  ")},
        {"id": "v1-lv4-bracket", "name": "Bracket", "art": (" [o] ", "  |  ", " / \\ ")},
    ),
    5: (
        {"id": "v1-lv5-studio", "name": "Studio", "art": ("+---+", "| o |", "|/ \\|", "+---+")},
        {"id": "v1-lv5-bridge", "name": "Bridge", "art": ("  o  ", " /|\\ ", "_/ \\_")},
        {"id": "v1-lv5-crest", "name": "Crest", "art": (" _o_ ", "/ | \\", "  /\\ ")},
    ),
    6: (
        {"id": "v1-lv6-arch", "name": "Arch", "art": ("  /\\  ", " /oo\\ ", "  ||  ", " /  \\ ")},
        {"id": "v1-lv6-signal", "name": "Signal", "art": (" .--. ", "( o  )", " /||\\ ", "  /\\  ")},
        {"id": "v1-lv6-vector", "name": "Vector", "art": ("  o-> ", " /|== ", " / \\  ")},
    ),
    7: (
        {"id": "v1-lv7-orbit", "name": "Orbit", "art": ("  .-.  ", " (o o) ", " /|_|\\ ", "  / \\  ")},
        {"id": "v1-lv7-pivot", "name": "Pivot", "art": ("  o  ", " /|> ", "< |  ", " / \\ ")},
        {"id": "v1-lv7-standard", "name": "Standard", "art": (" __o__ ", "  /|  ", " / \\  ")},
    ),
}

# Whole candidates, not fragments.  These v2 silhouettes are deliberately
# larger than the archived stick figures so each level can be judged for shape,
# negative space, and visual weight in the review-only demo.
AVATAR_OPTIONS = {
    3: (
        {"id": "lv3-spark-forge", "name": "Spark forge", "art": (
            "    .-^-.", "  .'  o  '.", " /  .---.  \\", "|  /|   |\\  |",
            " \\_/  |  \\_/", "    /   \\" )},
        {"id": "lv3-trail-scout", "name": "Trail scout", "art": (
            "     /\\", "  __/  \\__", " /  .--.  \\", "|  (o  )  |",
            " \\  /||\\  /", "  \\/_||_\\/" )},
        {"id": "lv3-workbench", "name": "Workbench", "art": (
            "  .--------.", " /  .--.    \\", "|  | oo |    |", "|  |_==_|  __|",
            " \\______/  /", "    /\\___/" )},
    ),
    4: (
        {"id": "lv4-frame-architect", "name": "Frame architect", "art": (
            "+----------+", "|  .----.  |", "| /  oo  \\ |", "| | /||\\ | |",
            "|  \\_||_/  |", "+----\\/----+", "     /\\" )},
        {"id": "lv4-window-keeper", "name": "Window keeper", "art": (
            "    .------.", " .-'  .-.   '-.", "/    (o o)     \\", "|     \\_/      |",
            "\\   /|_|\\     /", " '-./___\\_.-'" )},
        {"id": "lv4-bracket-sentinel", "name": "Bracket sentinel", "art": (
            "  [========]  ", "  |  .--.  |  ", "  | ( oo ) |  ", "  |  /||\\  |  ",
            "  |_/____\\_|  ", "      ||      ", "     /  \\" )},
    ),
    5: (
        {"id": "lv5-studio-master", "name": "Studio master", "art": (
            "   +-------+   ", "  /| .---. |\\  ", " / |( o o )| \\", "|  | \\_-_/ |  |",
            "|  | /| |\\ |  |", "\\__|/_|_|_\\|__/" )},
        {"id": "lv5-bridge-builder", "name": "Bridge builder", "art": (
            "      .-.      ", "  .--( o )--.  ", " /  __/|\\__  \\", "|  /  / \\  \\  |",
            "|_/__/___\\__\\_|", "   /_/   \\_\\" )},
        {"id": "lv5-crest-bearer", "name": "Crest bearer", "art": (
            "   ___o___   ", "  /  /|\\  \\", " /  / | \\  \\", "|  /  |  \\  |",
            "|_/___|___\\_|", "    / \\" )},
    ),
    6: (
        {"id": "lv6-arch-weaver", "name": "Arch weaver", "art": (
            "      .-^^^^-.      ", "   .-'  .--.  '-.   ", "  /    ( oo )    \\",
            " |      \\__/      | ", " |   .--/||\\--.   | ", "  \\_/__/ || \\__\\_/  ",
            "      /__||__\\      " )},
        {"id": "lv6-signal-caller", "name": "Signal caller", "art": (
            "      .----.      ", "  .--'  o   '--.  ", " /   .-|||-.    \\",
            "|   /  |||  \\    |", " \\_/___|||___\\_ / ", "      /   \\      " )},
        {"id": "lv6-vector-runner", "name": "Vector runner", "art": (
            "  .--------->  ", " /   .--.      \\", "|  _( oo )_     |",
            "| /  /||\\  \\===>|", " \\_/ || \\_/    /", "    /__\\" )},
    ),
    7: (
        {"id": "lv7-orbit-keeper", "name": "Orbit keeper", "art": (
            "       .-====-.       ", "    .-'  .--.  '-.    ", "  .'   _( oo )_   '.  ",
            " /    /  /||\\  \\    \\", "|    /__/ || \\__\\    |", " \\      /__\\      / " )},
        {"id": "lv7-pivot-captain", "name": "Pivot captain", "art": (
            "    .------.      ", " .-'   o    '-.   ", "/    /||\\      \\",
            "|   /_||_\\  ==> |", "\\      ||      /  ", " '-.___||___.-'  ", "       /  \\" )},
        {"id": "lv7-standard-bearer", "name": "Standard bearer", "art": (
            "   ___________   ", "  /  .---.    \\", " /  ( o o )    \\",
            "|    \\_-_/  ---|->", "|   /|   |\\    | ", "\\__/ |___| \\__ / ", "     /   \\" )},
    ),
}


# The first large review used framed humanoid silhouettes. Preserve that whole
# pass, but offer animals with distinct contours rather than border-enlarged
# stick figures. All new drawings below are original tutor review art.
ARCHIVED_FRAMED_AVATAR_OPTIONS = AVATAR_OPTIONS
AVATAR_OPTIONS = {
    3: (
        {"id": "lv3-frog", "name": "Pond frog", "art": (
            "   .-.   .-.", "  ( o )_( o )", " .'         '.",
            "(   ._____.   )", " '._       _.'", "  /_/'---'\\_\\")},
        {"id": "lv3-moth", "name": "Lantern moth", "art": (
            "     \\   /", " .---.(o).---.", "(  .-. | .-.  )",
            " \\(__)/|\\(__)/", "  '.  / \\  .'", "    ''   ''")},
        {"id": "lv3-snail", "name": "Shell scout", "art": (
            "       .----.", "     .' .--. '.", "    (  (  )  )  o o",
            "     \\  '--' /   \\|", "  .---'----'----. |", " (_______________)' ")},
    ),
    4: (
        {"id": "lv4-owl", "name": "Moon owl", "art": (
            "   /\\     /\\", "  /  '---'  \\", " ( (o) V (o) )",
            " |  .----- . |", " \\ / V V V\\ /", "  '._V_V_V_.'", "    /_V_V_\\")},
        {"id": "lv4-crab", "name": "Tide keeper", "art": (
            "  .-.       .-.", " (   ) o o (   )", "  \\_/\\| |/\\_/",
            "   / .---. \\", " _/ (_____) \\_", "/__/'     '\\__\\")},
        {"id": "lv4-hedgehog", "name": "Bristle keeper", "art": (
            "      /\\/\\/\\", "   /\\/       \\/\\", " /\\  .---.      \\/\\",
            "(   /     \\    o  )", " \\_/       '----. /", "    /_/      /_/''")},
    ),
    5: (
        {"id": "lv5-fox", "name": "Copper fox", "art": (
            "  /\\        /\\", " /  \\______/  \\", "(   \\ o  o /   )",
            " \\   '.V.'   /", "  '.   V   .'", "   /'-----'\\", "  /__     __\\")},
        {"id": "lv5-tortoise", "name": "Pattern keeper", "art": (
            "      .------.", "   .-' /\\ /\\ '-.", "  / __/  V  \\__ \\",
            " (  \\  /\\  /   )--(o)", "  '._\\/__\\/___.'", "    /_/    \\_\\")},
        {"id": "lv5-ray", "name": "Gliding ray", "art": (
            "        .-.", "   .---(o o)---.", " .'    \\_/     '.",
            "(  .--.   .--.   )", " '._   \\ /   _.'", "    '---V---'", "        |", "        '")},
    ),
    6: (
        {"id": "lv6-dragon", "name": "Contour dragon", "art": (
            "       /\\     /\\", "  .---/  \\___/  \\", " /   /    ( o  o )",
            "(   /  /\\  \\_V_/", " \\_/__/  \\  /  |", "    /  /\\  \\ |  |",
            "   /__/  \\__\\/__/", "             /_/")},
        {"id": "lv6-seahorse", "name": "Wave caller", "art": (
            "       .--.", "   .--( o  '--.", "  / /\\ '.___.'",
            " ( (  \\   \\", "  \\ \\  )   )", "   \\_\\/   /", "     (  .-'", "      '--'")},
        {"id": "lv6-stag", "name": "Branch keeper", "art": (
            "  \\_/\\     /\\_/", "   \\  \\   /  /", "    \\  'V'  /",
            "     ( o o )", "      \\ V /", "      /'--'\\", "   .-'      '-.", "  /___/  \\___\\")},
    ),
    7: (
        {"id": "lv7-phoenix", "name": "Ember phoenix", "art": (
            "   .--.       .--.", "  / /\\\\  .  //\\ \\", " / /  \\ (o) /  \\ \\",
            "( / /\\ ' V ' /\\ \\ )", " \\_/  \\  |  /  \\_/", "    \\   /|\\   /",
            "     '._/ | \\_.'", "        / V \\", "       /_ V _\\")},
        {"id": "lv7-whale", "name": "Deep navigator", "art": (
            "        .  .", "         \\/", "    .----------.", " .-'            '-.",
            "(  o   .______.     )   /\\", " \\    '------'    /___/  \\",
            "  '.___      ____/    \\  /", "      /_____/          \\/")},
        {"id": "lv7-octopus", "name": "Eightfold keeper", "art": (
            "       .------.", "     .'        '.", "    (  o      o  )",
            "     \\   __   /", "   .--'--'  '--'--.", "  / /\\ /\\  /\\ /\\ \\",
            " (_(  V  )__(  V  )_)", "    \\__/    \\__/")},
    ),
}


def candidates(level=None):
    """Yield review candidates in stable level/order sequence."""

    levels = (level,) if level is not None else sorted(AVATAR_OPTIONS)
    for current in levels:
        for candidate in AVATAR_OPTIONS[current]:
            yield current, candidate


def _label(role, text):
    prefix = UI.ansi(role)
    return prefix + text + (UI.RESET if prefix else "")


def main(argv=None):
    parser = argparse.ArgumentParser(description="review original Lv3–Lv7 avatar candidates")
    parser.add_argument("--level", type=int, choices=sorted(AVATAR_OPTIONS),
                        help="show only one level (there is no selection action)")
    args = parser.parse_args(argv)
    print(_label("heading", "AVATAR OPTIONS · REVIEW ONLY"))
    print(_label("meta", "Live dashboard_theme.AVATARS is unchanged; compare candidates and decide later."))
    print()
    selected = list(candidates(args.level))
    for level, candidate in selected:
        print(_label("new", "Lv%d · %s · %s" % (level, candidate["id"], candidate["name"])))
        print("\n".join(candidate["art"]))
        print()
    print(_label("meta", "%d complete candidates shown; no avatar was selected." % len(selected)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
