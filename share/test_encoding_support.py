#!/usr/bin/env python3
"""File-encoding round trip proof, not proportional-layout acceptance."""
import shutil
import subprocess
import tempfile
from pathlib import Path

text = "　⌒ヽ\n　ヽ_ノ\nﾆ二ニ\n"
for encoding in ("shift_jis", "cp932"):
    original = text.encode(encoding, errors="strict")
    for editor in ("vim", "nvim"):
        exe = shutil.which(editor)
        if not exe:
            print("SKIP %s: not installed" % editor)
            continue
        with tempfile.TemporaryDirectory(prefix="vim-daily-encoding-") as tmp:
            path = Path(tmp) / "art.txt"
            path.write_bytes(original)
            # Load from bytes with an explicit file encoding. The in-memory
            # buffer remains Unicode; writing must preserve the source bytes.
            enc = "sjis" if encoding == "shift_jis" else "cp932"
            edit = "edit ++enc=%s %s" % (enc, path)
            verify = "if &fileencoding !=# '%s' | cquit 9 | endif" % enc
            run = subprocess.run([exe, "-u", "NONE", "-i", "NONE", "-n", "-es",
                                  "-c", "set encoding=utf-8", "-c", edit,
                                  "-c", verify, "-c", "write", "-c", "qa!"],
                                 capture_output=True, timeout=10)
            assert run.returncode == 0, (editor, encoding, run.stderr)
            assert path.read_bytes() == original, (editor, encoding, "bytes changed")
        print("PASS %s: %s file read/write byte round trip" % (editor, encoding))
try:
    "🔥".encode("shift_jis", errors="strict")
except UnicodeEncodeError:
    pass
else:
    raise AssertionError("unrepresentable glyph did not fail strict export")
print("PASS unsupported Shift-JIS glyph rejects strict export; no proportional rendering claim")
