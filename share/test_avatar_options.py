"""Review-only checks for the Lv3–Lv7 avatar candidate gallery."""

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from avatar_options import ARCHIVED_AVATAR_OPTIONS, AVATAR_OPTIONS, candidates  # noqa: E402


def _ink(candidate):
    return sum(not char.isspace() for row in candidate["art"] for char in row)


def main():
    assert set(AVATAR_OPTIONS) == {3, 4, 5, 6, 7}
    assert set(ARCHIVED_AVATAR_OPTIONS) == set(AVATAR_OPTIONS)
    for level, options in AVATAR_OPTIONS.items():
        assert len(options) >= 3
        assert len({option["id"] for option in options}) == len(options)
        for option in options:
            assert len(option["art"]) >= 5, (level, option["id"])
            assert max(len(row) for row in option["art"]) >= 8, (level, option["id"])
            assert _ink(option) >= 20, (level, option["id"])
            assert all("\x1b" not in row for row in option["art"])
    assert sum(1 for _level, _option in candidates()) == 15
    env = dict(os.environ, NO_COLOR="1", TERM="dumb")
    demo = subprocess.run([sys.executable, str(HERE / "avatar_options.py")],
                          capture_output=True, text=True, check=True, env=env)
    assert demo.stdout.count("complete candidates shown") == 1
    assert "15 complete candidates shown; no avatar was selected." in demo.stdout
    for level in AVATAR_OPTIONS:
        assert demo.stdout.count("Lv%d ·" % level) == 3
    print("test_avatar_options: all passed")


if __name__ == "__main__":
    main()
