#!/usr/bin/env python3
"""Verify the local-only excerpt register against source bytes and curriculum use."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "share" / "audits" / "STONE_STORY_LOCAL_PROVENANCE.md"
STONE_ROOT = Path("/Users/r/Downloads/stone-story-consolidated")
AAHUB_ROOT = Path("/Users/r/Downloads/aahub-consolidated")


text = AUDIT.read_text(encoding="utf-8")
set_rows = re.findall(
    r"^\| `(official-[^`]+)` \| `([^`]+)` \| `([0-9a-f]{64})` \|$",
    text,
    re.MULTILINE,
)
assert len(set_rows) == 21, len(set_rows)

registered = set()
for relative_dir, names_text, expected in set_rows:
    names = names_text.split(", ")
    digest = hashlib.sha256()
    for name in names:
        source = STONE_ROOT / relative_dir / name
        assert source.is_file(), source
        file_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        digest.update(f"{name}\t{file_digest}\n".encode())
    assert digest.hexdigest() == expected, relative_dir
    registered.add(relative_dir)

aahub_rows = re.findall(
    r"^\| `(bakuhatsu-kemuri/[^`]+)` \| `([0-9a-f]{64})` \| M10\.06",
    text,
    re.MULTILINE,
)
assert len(aahub_rows) == 2, len(aahub_rows)
for relative_file, expected in aahub_rows:
    source = AAHUB_ROOT / relative_file
    assert source.is_file(), source
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, relative_file

curriculum = json.loads(
    (ROOT / "share" / "curriculum-v2.json").read_text(encoding="utf-8")
)
external_sources = set()
transfer_cards = []
for card in curriculum["cards"]:
    if card.get("kind") == "transfer":
        transfer_cards.append(card)
    for row in (card, *card.get("review_variants", []), *card.get("variants", [])):
        source = row.get("source", "")
        if source.startswith("official-"):
            external_sources.add(source.split(" ", 1)[0])
        elif source.startswith("AAHub"):
            external_sources.add("AAHub")

assert external_sources - registered == {"AAHub"}, sorted(external_sources - registered)
assert len(transfer_cards) == 20, len(transfer_cards)
for card in transfer_cards:
    assert len(card.get("variants", [])) >= 2, card["id"]
    for variant in card["variants"]:
        source = variant.get("source", "")
        assert source.startswith("official-") or source.startswith("AAHub"), (
            card["id"], source
        )
# VD-60/VD-61: publication confirmed by the operator on condition of credit.
assert "**Publication (updated 2026-09-29, VD-60):**" in text
assert "Gabriel Santos" in text and "aahub.org/mlt/a60392576bd5eefca3ed22d55606b85f" in text
art = json.loads((ROOT / "share" / "art.json").read_text(encoding="utf-8"))["art"]
assert all(entry.get("credit") and entry["redistribution"] == "cleared" for entry in art.values())
readme = (ROOT / "README.md").read_text(encoding="utf-8")
for name in ("Gabriel Santos", "AAHub", "Joan G. Stark"):
    assert name in readme, name
assert "not archive ingestion" in text
print(
    "PASS local provenance: %d Stone Story source sets, %d AAHub files, "
    "%d curriculum source families, %d/20 source-backed transfers; "
    "published with credit (VD-60, VD-61)"
    % (len(set_rows), len(aahub_rows), len(external_sources), len(transfer_cards))
)
