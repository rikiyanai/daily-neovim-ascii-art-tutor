"""Headed local browser proof fixture, isolated from real learner state.

Run this script, open its printed token-protected URL in a real browser, then
send ``edit`` to change YOURS to TARGET and ``submit`` after the page displays
the new raster. The final assertion requires an actual browser callback.
This proves the display transport, not operator artistic acceptance.
"""
import json
from pathlib import Path
import tempfile

from sjis_tutor import TutorPreview, art_text


def main():
    before = ["　　⌒?", "　（　　）", "　　ヽ_ノ"]
    target = ["　　⌒ヽ", "　（　　）", "　　ヽ_ノ"]
    with tempfile.TemporaryDirectory(prefix="vim-daily-native-browser-") as folder:
        path = Path(folder) / "art.txt"
        path.write_text(art_text(before), encoding="utf-8")
        with TutorPreview(path, target, open_browser=False) as session:
            assert not session.final_receipt(display_timeout=0)["ready"]
            print(json.dumps({"url": session.url, "fixture_path": str(path)}), flush=True)
            for command in iter(input, "submit"):
                if command == "edit":
                    path.write_text(art_text(target), encoding="utf-8")
                    session.refresh()
                    assert not session.server.displayed_receipt()
                    print("TARGET written; old display acknowledgement is stale.", flush=True)
            final = session.final_receipt()
            assert final["ready"], final["reasons"]
            print(json.dumps(final, ensure_ascii=False), flush=True)
            print("test_sjis_browser: real native font/four-image display and changed-art submission passed", flush=True)


if __name__ == "__main__":
    main()
