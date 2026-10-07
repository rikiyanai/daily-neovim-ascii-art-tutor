"""Strict Shift_JIS authoring and true-advance preview backend.

This module is deliberately independent of the tutor runtime and of any one
preview surface.  It owns the evidence boundary for proportional text art:

* :func:`import_artifact` and :func:`export_artifact` use an explicit,
  strict encoding and preserve the bytes, code points, and every whitespace
  character.  No encoding detection, replacement, or newline translation is
  performed.
* :func:`load_font_metrics` reads the declared Saitamaar font with
  ``fontTools``.  The file hash is measured at load time.  A missing font or
  missing dependency is an actionable error, never a monospace fallback.
* :func:`render_text` uses Pillow for a deterministic raster while placing
  each glyph at the fontTools advance lattice.  :func:`compare_text_art`
  reports transcription equality separately from visual equality and reports
  a changed-pixel bounding box.
* :func:`make_join_contract` and :func:`evaluate_join_contract` require
  explicit anchors in native font units.  A terminal-width match cannot pass
  a contract whose native advance is misregistered.
* :func:`build_preview_receipt` binds the preview to the source byte hash,
  source text hash, target text hash, yours text hash, font hash, size, and
  line pitch.  :func:`gate_submission` rejects stale or non-preview receipts;
  it does not claim artist intent or operator visual acceptance.
* :func:`build_preview_payload` is a browser-neutral JSON payload.  The
  optional :func:`serve_preview` adapter serves the new ``sjis_preview.*``
  files from a token-protected ``127.0.0.1`` loopback server only.

The public API is intentionally small::

    before = import_artifact(path, encoding="utf-8")
    target = import_artifact(target_path, encoding="utf-8")
    metrics = load_font_metrics()  # Saitamaar, 16 px, 17 px pitch
    comparison = compare_text_art(before.text, yours, target.text, metrics)
    contract = make_join_contract(target.text, metrics, anchors)
    joins = evaluate_join_contract(yours, target.text, metrics, contract)
    receipt = build_preview_receipt(before, yours, target.text, metrics,
                                    comparison, joins)
    decision = gate_submission(receipt, before, yours, target.text, metrics)

``decision`` contains only evidence-level fields.  ``operator_visual_acceptance``
remains ``required`` unless a human-owned integration records that decision.

The module contains no corpus admission logic and does not open AA-004 or
new-admission records.  M10 authored strings are supplied by the caller.
"""

from __future__ import annotations

import base64
import codecs
import hashlib
import http.server
from io import BytesIO
import json
import os
from pathlib import Path
import secrets
import socketserver
import tempfile
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Optional, Sequence
from urllib.parse import parse_qs, urlsplit

try:  # Optional imports are checked again at the point of use.
    from fontTools.ttLib import TTFont  # type: ignore
except Exception:  # pragma: no cover - exercised through dependency tests
    TTFont = None  # type: ignore

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
except Exception:  # pragma: no cover - exercised through dependency tests
    Image = ImageDraw = ImageFont = None  # type: ignore


DEFAULT_FONT_PATH = Path(
    "/Users/r/Projects/ascii-art-archive/collections/aahub/Saitamaar.ttf"
)
DEFAULT_FONT_SIZE_PX = 16
DEFAULT_LINE_PITCH_PX = 17
SUPPORTED_ENCODINGS = ("utf-8", "shift_jis", "cp932")
_ENCODING_ALIASES = {
    "utf8": "utf-8",
    "utf-8": "utf-8",
    "shiftjis": "shift_jis",
    "shift_jis": "shift_jis",
    "sjis": "shift_jis",
    "cp932": "cp932",
    "ms932": "cp932",
    "windows-31j": "cp932",
}


class AuthoringError(Exception):
    """Base class for strict authoring failures."""


class EncodingPolicyError(AuthoringError):
    """The caller omitted or selected an unsupported encoding."""


class UnsupportedGlyphError(AuthoringError):
    """A code point is not representable by the selected encoding or font."""


class DependencyMissingError(AuthoringError):
    """A required renderer/metrics dependency is not installed."""


class FontUnavailableError(AuthoringError):
    """The declared font path is absent or cannot be read."""


class ExportExistsError(AuthoringError):
    """An export would overwrite an existing path without explicit consent."""


class ReceiptError(AuthoringError):
    """A receipt is stale, incomplete, or bound to different evidence."""


class JoinContractError(AuthoringError):
    """A declared native-coordinate join contract is malformed."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    try:
        data = text.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise UnsupportedGlyphError(
            "Text contains a surrogate or other non-UTF-8 code point at "
            f"index {exc.start}; preserve the original bytes instead of "
            "repairing the text."
        ) from exc
    return _sha256(data)


def _canonical_encoding(encoding: str) -> str:
    if not isinstance(encoding, str) or not encoding.strip():
        raise EncodingPolicyError(
            "An explicit encoding is required; choose utf-8, shift_jis, or cp932."
        )
    key = encoding.strip().lower().replace(" ", "")
    canonical = _ENCODING_ALIASES.get(key)
    if canonical is None:
        raise EncodingPolicyError(
            f"Unsupported encoding {encoding!r}; use exactly one of "
            "utf-8, shift_jis, or cp932. Encoding detection is disabled."
        )
    # Make a codec lookup part of the contract, rather than trusting an alias.
    codecs.lookup(canonical)
    return canonical


def _encode_strict(text: str, encoding: str) -> bytes:
    canonical = _canonical_encoding(encoding)
    try:
        return text.encode(canonical, errors="strict")
    except UnicodeEncodeError as exc:
        cp = ord(text[exc.start]) if exc.start < len(text) else None
        detail = f"U+{cp:04X}" if cp is not None else "unknown code point"
        raise UnsupportedGlyphError(
            f"{canonical} cannot encode {detail} at text index {exc.start}; "
            "export was refused without replacement or loss recovery."
        ) from exc


def _decode_strict(data: bytes, encoding: str) -> str:
    canonical = _canonical_encoding(encoding)
    try:
        return data.decode(canonical, errors="strict")
    except UnicodeDecodeError as exc:
        raise EncodingPolicyError(
            f"{canonical} rejected source bytes at offset {exc.start}; "
            "import was refused without detection or replacement."
        ) from exc


@dataclass(frozen=True)
class TextArtifact:
    """Decoded text plus immutable source-byte provenance."""

    text: str
    encoding: str
    source_bytes: bytes
    byte_sha256: str
    text_sha256: str
    source_path: Optional[str] = None

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        encoding: str,
        source_path: Optional[os.PathLike[str] | str] = None,
        expected_sha256: Optional[str] = None,
    ) -> "TextArtifact":
        raw = bytes(data)
        byte_hash = _sha256(raw)
        if expected_sha256 is not None and byte_hash != expected_sha256:
            raise ReceiptError(
                f"Source byte hash mismatch: expected {expected_sha256}, "
                f"got {byte_hash}; source provenance is not trusted."
            )
        text = _decode_strict(raw, encoding)
        canonical = _canonical_encoding(encoding)
        return cls(
            text=text,
            encoding=canonical,
            source_bytes=raw,
            byte_sha256=byte_hash,
            text_sha256=_sha256_text(text),
            source_path=str(Path(source_path).resolve()) if source_path else None,
        )

    def encode(self, encoding: str) -> bytes:
        """Encode this artifact strictly; the source bytes remain unchanged."""
        canonical = _canonical_encoding(encoding)
        if canonical == self.encoding:
            # CP932 has valid duplicate byte spellings for some codepoints.
            # A decode/encode cycle can canonicalize them despite strict mode.
            # Re-exporting the unchanged source codec must preserve its bytes.
            if (_sha256(self.source_bytes) != self.byte_sha256
                    or _decode_strict(self.source_bytes, canonical) != self.text
                    or _sha256_text(self.text) != self.text_sha256):
                raise ReceiptError("Artifact provenance is inconsistent; same-codec export refused.")
            return self.source_bytes
        return _encode_strict(self.text, canonical)


def import_artifact(
    path: os.PathLike[str] | str,
    *,
    encoding: str,
    expected_sha256: Optional[str] = None,
) -> TextArtifact:
    """Read a path as raw bytes and decode it with the explicit codec."""

    source = Path(path)
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise AuthoringError(f"Cannot read source artifact {source}: {exc}") from exc
    return TextArtifact.from_bytes(
        raw,
        encoding=encoding,
        source_path=source,
        expected_sha256=expected_sha256,
    )


def artifact_from_text(text: str, *, encoding: str) -> TextArtifact:
    """Create an artifact through the same strict byte encoder as export."""

    raw = _encode_strict(text, encoding)
    return TextArtifact.from_bytes(raw, encoding=encoding)


@dataclass(frozen=True)
class ExportReceipt:
    output_path: str
    encoding: str
    output_byte_sha256: str
    source_byte_sha256: str
    source_text_sha256: str
    overwritten: bool
    atomic: bool = True


def export_artifact(
    artifact: TextArtifact,
    destination: os.PathLike[str] | str,
    *,
    encoding: str,
    overwrite: bool = False,
) -> ExportReceipt:
    """Atomically export an artifact without implicit replacement.

    ``overwrite=True`` is the explicit authorization required for replacing a
    destination.  A no-overwrite export uses an atomic hard-link claim after
    the temporary file is fsynced, so a concurrent writer cannot win silently.
    """

    canonical = _canonical_encoding(encoding)
    payload = artifact.encode(canonical)
    destination_path = Path(destination)
    if not destination_path.parent.exists():
        raise AuthoringError(
            f"Export directory does not exist: {destination_path.parent}; "
            "create it explicitly before exporting."
        )
    temp_name: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=str(destination_path.parent),
            prefix=f".{destination_path.name}.sjis-",
            delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if overwrite:
            os.replace(temp_name, destination_path)
            temp_name = None
        else:
            try:
                os.link(temp_name, destination_path)
            except FileExistsError as exc:
                raise ExportExistsError(
                    f"Refusing to overwrite existing export {destination_path}; "
                    "pass overwrite=True explicitly."
                ) from exc
            finally:
                try:
                    os.unlink(temp_name)
                except FileNotFoundError:
                    pass
            temp_name = None
        try:
            directory_fd = os.open(destination_path.parent, os.O_RDONLY)
        except OSError:
            directory_fd = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
    return ExportReceipt(
        output_path=str(destination_path.resolve()),
        encoding=canonical,
        output_byte_sha256=_sha256(payload),
        source_byte_sha256=artifact.byte_sha256,
        source_text_sha256=artifact.text_sha256,
        overwritten=overwrite,
    )


@dataclass(frozen=True)
class GlyphMetric:
    codepoint: int
    glyph_name: str
    advance_units: int
    advance_px: float
    has_ink: Optional[bool] = None


@dataclass(frozen=True)
class FontMetrics:
    """Measured native font metrics; no fallback values are inferred."""

    font_path: str
    font_sha256: str
    units_per_em: int
    font_size_px: int
    line_pitch_px: int
    _cmap: Mapping[int, str] = field(repr=False, compare=False)
    _advances: Mapping[str, int] = field(repr=False, compare=False)

    @classmethod
    def load(
        cls,
        font_path: os.PathLike[str] | str = DEFAULT_FONT_PATH,
        *,
        font_size_px: int = DEFAULT_FONT_SIZE_PX,
        line_pitch_px: int = DEFAULT_LINE_PITCH_PX,
    ) -> "FontMetrics":
        if TTFont is None:
            raise DependencyMissingError(
                "fontTools is required for native advance metrics. Install "
                "fonttools in the approved workspace environment; no fallback "
                "metrics are permitted."
            )
        path = Path(font_path)
        if not path.is_file():
            raise FontUnavailableError(
                f"Declared Saitamaar font is unavailable at {path}. "
                "Provide the exact local font path; monospace fallback is disabled."
            )
        if not isinstance(font_size_px, int) or font_size_px <= 0:
            raise FontUnavailableError("font_size_px must be a positive integer.")
        if not isinstance(line_pitch_px, int) or line_pitch_px <= 0:
            raise FontUnavailableError("line_pitch_px must be a positive integer.")
        try:
            raw = path.read_bytes()
            font = TTFont(BytesIO(raw), lazy=False)
            units = int(font["head"].unitsPerEm)
            cmap = dict(font.getBestCmap() or {})
            hmtx = font["hmtx"].metrics
            advances = {name: int(values[0]) for name, values in hmtx.items()}
            font.close()
        except Exception as exc:
            raise FontUnavailableError(f"Cannot measure font {path}: {exc}") from exc
        if units <= 0:
            raise FontUnavailableError(f"Font {path} has invalid unitsPerEm={units}.")
        return cls(
            font_path=str(path.resolve()),
            font_sha256=_sha256(raw),
            units_per_em=units,
            font_size_px=font_size_px,
            line_pitch_px=line_pitch_px,
            _cmap=cmap,
            _advances=advances,
        )

    @property
    def lattice_px_per_unit(self) -> float:
        return self.font_size_px / self.units_per_em

    def glyph_metric(self, char: str) -> GlyphMetric:
        if len(char) != 1:
            raise ValueError("glyph_metric accepts one code point")
        codepoint = ord(char)
        glyph_name = self._cmap.get(codepoint)
        if glyph_name is None:
            raise UnsupportedGlyphError(
                f"Saitamaar does not contain U+{codepoint:04X} at the requested "
                "text position; rasterization is refused."
            )
        try:
            advance_units = self._advances[glyph_name]
        except KeyError as exc:
            raise FontUnavailableError(
                f"Font cmap points U+{codepoint:04X} to missing hmtx glyph "
                f"{glyph_name!r}; font metrics are incomplete."
            ) from exc
        return GlyphMetric(
            codepoint=codepoint,
            glyph_name=glyph_name,
            advance_units=advance_units,
            advance_px=advance_units * self.lattice_px_per_unit,
        )

    def validate_text(self, text: str) -> None:
        """Reject unsupported visible code points without changing the text."""

        for index, char in enumerate(text):
            if char == "\n":
                continue
            if char == "\r":
                # CRLF is accepted as a line terminator for rendering.  The
                # imported/exported source still contains the original CR.
                if index + 1 < len(text) and text[index + 1] == "\n":
                    continue
                raise UnsupportedGlyphError(
                    f"Lone carriage return at text index {index} has no declared "
                    "Saitamaar placement; preserve it in bytes but do not render it."
                )
            self.glyph_metric(char)

    def receipt(self) -> dict[str, Any]:
        return {
            "font_path": self.font_path,
            "font_sha256": self.font_sha256,
            "units_per_em": self.units_per_em,
            "font_size_px": self.font_size_px,
            "line_pitch_px": self.line_pitch_px,
            "lattice_px_per_unit": self.lattice_px_per_unit,
        }


@dataclass(frozen=True)
class GlyphPlacement:
    row: int
    column: int
    char: str
    x_units: int
    x_px: float
    y_px: int
    advance_units: int
    advance_px: float
    ink_bbox: Optional[tuple[float, float, float, float]]


@dataclass(frozen=True)
class RasterResult:
    width_px: int
    height_px: int
    pixels: bytes
    png_bytes: bytes
    pixel_sha256: str
    text_sha256: str
    font_sha256: str
    font_size_px: int
    line_pitch_px: int
    placements: tuple[GlyphPlacement, ...]

    def placement(self, row: int, column: int) -> GlyphPlacement:
        for item in self.placements:
            if item.row == row and item.column == column:
                return item
        raise JoinContractError(f"No rendered glyph at row={row}, column={column}.")


def _require_pillow() -> None:
    if Image is None or ImageDraw is None or ImageFont is None:
        raise DependencyMissingError(
            "Pillow is required for the native raster preview. Install Pillow "
            "in the approved workspace environment; no terminal or monospace "
            "fallback is permitted."
        )


def _line_entries(text: str) -> Iterable[tuple[int, int, str]]:
    """Yield (row, column, char) while retaining source code-point indexes."""

    row = 0
    column = 0
    for index, char in enumerate(text):
        if char == "\n":
            row += 1
            column = 0
            continue
        if char == "\r":
            if index + 1 < len(text) and text[index + 1] == "\n":
                continue
            raise UnsupportedGlyphError(
                f"Lone carriage return at text index {index} cannot be rasterized."
            )
        yield row, column, char
        column += 1


def _png_bytes(width: int, height: int, pixels: bytes) -> bytes:
    _require_pillow()
    image = Image.frombytes("L", (width, height), pixels)
    from io import BytesIO

    output = BytesIO()
    image.save(output, format="PNG", optimize=False, compress_level=9)
    return output.getvalue()


def render_text(text: str, metrics: FontMetrics) -> RasterResult:
    """Render text at measured advances using the declared native font.

    The source string is never normalised.  CRLF is treated as a line break
    only for the raster; the artifact used for export retains both code points.
    """

    _require_pillow()
    metrics.validate_text(text)
    try:
        raw_font = Path(metrics.font_path).read_bytes()
        if _sha256(raw_font) != metrics.font_sha256:
            raise FontUnavailableError("Measured font changed on disk; preview refused.")
        font = ImageFont.truetype(BytesIO(raw_font), metrics.font_size_px)
    except Exception as exc:
        raise FontUnavailableError(
            f"Pillow cannot load the measured font {metrics.font_path}: {exc}"
        ) from exc

    entries = list(_line_entries(text))
    placements: list[GlyphPlacement] = []
    current_units: dict[int, int] = {}
    max_width_px = 0
    max_row = 0
    for row, column, char in entries:
        x_units = current_units.get(row, 0)
        metric = metrics.glyph_metric(char)
        x_px = x_units * metrics.lattice_px_per_unit
        y_px = row * metrics.line_pitch_px
        bbox = font.getbbox(char)
        ink_bbox: Optional[tuple[float, float, float, float]]
        if bbox[2] > bbox[0] and bbox[3] > bbox[1]:
            ink_bbox = (
                x_px + bbox[0],
                y_px + bbox[1],
                x_px + bbox[2],
                y_px + bbox[3],
            )
        else:
            ink_bbox = None
        placements.append(
            GlyphPlacement(
                row=row,
                column=column,
                char=char,
                x_units=x_units,
                x_px=x_px,
                y_px=y_px,
                advance_units=metric.advance_units,
                advance_px=metric.advance_px,
                ink_bbox=ink_bbox,
            )
        )
        current_units[row] = x_units + metric.advance_units
        max_width_px = max(
            max_width_px,
            int(round(current_units[row] * metrics.lattice_px_per_unit)),
        )
        max_row = max(max_row, row)
    width = max(1, max_width_px)
    height = max(metrics.line_pitch_px, (max_row + 1) * metrics.line_pitch_px)
    image = Image.new("L", (width, height), color=0)
    draw = ImageDraw.Draw(image)
    for item in placements:
        draw.text(
            (int(round(item.x_px)), item.y_px),
            item.char,
            font=font,
            fill=255,
        )
    pixels = image.tobytes()
    return RasterResult(
        width_px=width,
        height_px=height,
        pixels=pixels,
        png_bytes=_png_bytes(width, height, pixels),
        pixel_sha256=_sha256(pixels),
        text_sha256=_sha256_text(text),
        font_sha256=metrics.font_sha256,
        font_size_px=metrics.font_size_px,
        line_pitch_px=metrics.line_pitch_px,
        placements=tuple(placements),
    )


@dataclass(frozen=True)
class RasterComparison:
    visual_equal: bool
    changed_pixel_count: int
    changed_bbox: Optional[tuple[int, int, int, int]]
    width_px: int
    height_px: int
    diff_png_bytes: bytes
    diff_pixel_sha256: str


def compare_rasters(before: RasterResult, after: RasterResult) -> RasterComparison:
    """Compare the union of raster extents, including deletion-only tails."""

    _require_pillow()
    width = max(before.width_px, after.width_px)
    height = max(before.height_px, after.height_px)
    changed = bytearray(width * height)
    changed_count = 0
    x0 = y0 = None
    x1 = y1 = None
    for y in range(height):
        for x in range(width):
            old = before.pixels[y * before.width_px + x] if (
                x < before.width_px and y < before.height_px
            ) else 0
            new = after.pixels[y * after.width_px + x] if (
                x < after.width_px and y < after.height_px
            ) else 0
            if old != new:
                changed[y * width + x] = 255
                changed_count += 1
                x0 = x if x0 is None else min(x0, x)
                y0 = y if y0 is None else min(y0, y)
                x1 = x + 1 if x1 is None else max(x1, x + 1)
                y1 = y + 1 if y1 is None else max(y1, y + 1)
    diff = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    rgba = bytearray(width * height * 4)
    for index, value in enumerate(changed):
        if value:
            offset = index * 4
            rgba[offset : offset + 4] = bytes((255, 40, 40, 255))
    diff = Image.frombytes("RGBA", (width, height), bytes(rgba))
    from io import BytesIO

    output = BytesIO()
    diff.save(output, format="PNG", optimize=False, compress_level=9)
    diff_png = output.getvalue()
    return RasterComparison(
        visual_equal=changed_count == 0,
        changed_pixel_count=changed_count,
        changed_bbox=(x0, y0, x1, y1) if x0 is not None else None,
        width_px=width,
        height_px=height,
        diff_png_bytes=diff_png,
        diff_pixel_sha256=_sha256(bytes(changed)),
    )


@dataclass(frozen=True)
class TextArtComparison:
    text_equal: bool
    before_text_sha256: str
    after_text_sha256: str
    target_text_sha256: str
    before_raster: RasterResult
    after_raster: RasterResult
    target_raster: RasterResult
    yours_vs_target: RasterComparison
    transcription_changed_codepoints: int


def _codepoint_difference_count(left: str, right: str) -> int:
    limit = max(len(left), len(right))
    return sum(
        (left[index] if index < len(left) else None)
        != (right[index] if index < len(right) else None)
        for index in range(limit)
    )


def compare_text_art(
    before_text: str,
    yours_text: str,
    target_text: str,
    metrics: FontMetrics,
) -> TextArtComparison:
    """Return independent transcription, raster, and pixel-diff evidence."""

    before_raster = render_text(before_text, metrics)
    after_raster = render_text(yours_text, metrics)
    target_raster = render_text(target_text, metrics)
    return TextArtComparison(
        text_equal=yours_text == target_text,
        before_text_sha256=_sha256_text(before_text),
        after_text_sha256=_sha256_text(yours_text),
        target_text_sha256=_sha256_text(target_text),
        before_raster=before_raster,
        after_raster=after_raster,
        target_raster=target_raster,
        yours_vs_target=compare_rasters(after_raster, target_raster),
        transcription_changed_codepoints=_codepoint_difference_count(
            yours_text, target_text
        ),
    )


@dataclass(frozen=True)
class JoinAnchor:
    """A human-declared join point measured in native font units and pixels."""

    name: str
    row: int
    column: int
    expected_x_units: int
    expected_y_px: int
    tolerance_units: int = 0
    tolerance_y_px: int = 0
    require_ink: bool = False


@dataclass(frozen=True)
class JoinContract:
    target_text_sha256: str
    font_sha256: str
    font_size_px: int
    line_pitch_px: int
    anchors: tuple[JoinAnchor, ...]
    contract_sha256: str


def _contract_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return _sha256(encoded)


def make_join_contract(
    target_text: str,
    metrics: FontMetrics,
    anchors: Sequence[JoinAnchor],
) -> JoinContract:
    """Create a target/font-bound native-coordinate join contract."""

    target = render_text(target_text, metrics)
    if not anchors:
        raise JoinContractError(
            "A proportional join contract must declare at least one anchor; "
            "text equality alone is not visual acceptance."
        )
    for anchor in anchors:
        try:
            placement = target.placement(anchor.row, anchor.column)
        except JoinContractError as exc:
            raise JoinContractError(
                f"Anchor {anchor.name!r} does not identify a target glyph: {exc}"
            ) from exc
        expected_x_px = anchor.expected_x_units * metrics.lattice_px_per_unit
        if abs(placement.x_px - expected_x_px) > 1e-9:
            raise JoinContractError(
                f"Anchor {anchor.name!r} expected x_units={anchor.expected_x_units}, "
                f"but target renders at {placement.x_units}."
            )
        if anchor.expected_y_px != placement.y_px:
            raise JoinContractError(
                f"Anchor {anchor.name!r} expected y_px={anchor.expected_y_px}, "
                f"but target renders at {placement.y_px}."
            )
    payload = {
        "target_text_sha256": _sha256_text(target_text),
        "font_sha256": metrics.font_sha256,
        "font_size_px": metrics.font_size_px,
        "line_pitch_px": metrics.line_pitch_px,
        "anchors": [asdict(anchor) for anchor in anchors],
    }
    return JoinContract(
        target_text_sha256=payload["target_text_sha256"],
        font_sha256=metrics.font_sha256,
        font_size_px=metrics.font_size_px,
        line_pitch_px=metrics.line_pitch_px,
        anchors=tuple(anchors),
        contract_sha256=_contract_digest(payload),
    )


def anchor_from_target(
    target_text: str,
    metrics: FontMetrics,
    *,
    name: str,
    row: int,
    column: int,
    tolerance_units: int = 0,
    tolerance_y_px: int = 0,
    require_ink: bool = False,
) -> JoinAnchor:
    """Declare one anchor from a measured TARGET glyph position.

    The caller still chooses the semantic join and its tolerance.  This helper
    only records the target's measured native coordinates; it does not infer
    that the join is artistically correct.
    """

    placement = render_text(target_text, metrics).placement(row, column)
    return JoinAnchor(
        name=name,
        row=row,
        column=column,
        expected_x_units=placement.x_units,
        expected_y_px=placement.y_px,
        tolerance_units=tolerance_units,
        tolerance_y_px=tolerance_y_px,
        require_ink=require_ink,
    )


@dataclass(frozen=True)
class JoinMeasurement:
    name: str
    passed: bool
    expected_x_units: int
    actual_x_units: int
    delta_x_units: int
    expected_y_px: int
    actual_y_px: int
    delta_y_px: int
    actual_ink: bool


@dataclass(frozen=True)
class JoinEvaluation:
    passed: bool
    contract_sha256: str
    basis: str
    measurements: tuple[JoinMeasurement, ...]
    failures: tuple[str, ...]


def evaluate_join_contract(
    yours_text: str,
    target_text: str,
    metrics: FontMetrics,
    contract: JoinContract,
) -> JoinEvaluation:
    """Measure declared anchors; never infer artist intent from text/schema."""

    if contract.target_text_sha256 != _sha256_text(target_text):
        raise JoinContractError(
            "Join contract target hash does not match the supplied target text."
        )
    if contract.font_sha256 != metrics.font_sha256:
        raise JoinContractError("Join contract font hash does not match measured font.")
    if (contract.font_size_px != metrics.font_size_px
            or contract.line_pitch_px != metrics.line_pitch_px):
        raise JoinContractError("Join contract size or line pitch does not match preview metrics.")
    yours = render_text(yours_text, metrics)
    measurements: list[JoinMeasurement] = []
    failures: list[str] = []
    for anchor in contract.anchors:
        try:
            placement = yours.placement(anchor.row, anchor.column)
        except JoinContractError as exc:
            failures.append(f"{anchor.name}: {exc}")
            continue
        actual_ink = placement.ink_bbox is not None
        dx = placement.x_units - anchor.expected_x_units
        dy = placement.y_px - anchor.expected_y_px
        passed = (
            abs(dx) <= anchor.tolerance_units
            and abs(dy) <= anchor.tolerance_y_px
            and (actual_ink or not anchor.require_ink)
        )
        measurements.append(
            JoinMeasurement(
                name=anchor.name,
                passed=passed,
                expected_x_units=anchor.expected_x_units,
                actual_x_units=placement.x_units,
                delta_x_units=dx,
                expected_y_px=anchor.expected_y_px,
                actual_y_px=placement.y_px,
                delta_y_px=dy,
                actual_ink=actual_ink,
            )
        )
        if not passed:
            failures.append(
                f"{anchor.name}: native join delta x={dx} units, y={dy} px, "
                f"ink={actual_ink}; tolerance x={anchor.tolerance_units}, "
                f"y={anchor.tolerance_y_px}."
            )
    return JoinEvaluation(
        passed=not failures and len(measurements) == len(contract.anchors),
        contract_sha256=contract.contract_sha256,
        basis="declared-native-font-advance-anchors",
        measurements=tuple(measurements),
        failures=tuple(failures),
    )


@dataclass(frozen=True)
class PreviewReceipt:
    schema: str
    source_byte_sha256: str
    source_text_sha256: str
    yours_text_sha256: str
    target_text_sha256: str
    font_sha256: str
    font_size_px: int
    line_pitch_px: int
    before_pixel_sha256: str
    yours_pixel_sha256: str
    target_pixel_sha256: str
    diff_pixel_sha256: str
    text_equal: bool
    visual_equal: bool
    changed_pixel_count: int
    changed_bbox: Optional[tuple[int, int, int, int]]
    preview_rendered: bool
    join_contract_sha256: Optional[str]
    join_passed: bool
    created_at_utc: str

    def matches(
        self,
        source: TextArtifact,
        yours_text: str,
        target_text: str,
        metrics: FontMetrics,
    ) -> bool:
        return (
            self.preview_rendered
            and self.source_byte_sha256 == source.byte_sha256
            and self.source_text_sha256 == source.text_sha256
            and self.yours_text_sha256 == _sha256_text(yours_text)
            and self.target_text_sha256 == _sha256_text(target_text)
            and self.font_sha256 == metrics.font_sha256
            and self.font_size_px == metrics.font_size_px
            and self.line_pitch_px == metrics.line_pitch_px
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_preview_receipt(
    source: TextArtifact,
    yours_text: str,
    target_text: str,
    metrics: FontMetrics,
    comparison: TextArtComparison,
    join_evaluation: Optional[JoinEvaluation] = None,
    *,
    preview_rendered: bool = True,
) -> PreviewReceipt:
    """Create an evidence receipt bound to all preview inputs."""

    if comparison.target_text_sha256 != _sha256_text(target_text):
        raise ReceiptError("Comparison target hash does not match target text.")
    if comparison.before_text_sha256 != source.text_sha256:
        raise ReceiptError("Comparison BEFORE hash does not match source artifact.")
    if comparison.after_text_sha256 != _sha256_text(yours_text):
        raise ReceiptError("Comparison YOURS hash does not match yours text.")
    for raster in (comparison.before_raster, comparison.after_raster,
                   comparison.target_raster):
        if (raster.font_sha256 != metrics.font_sha256
                or raster.font_size_px != metrics.font_size_px
                or raster.line_pitch_px != metrics.line_pitch_px):
            raise ReceiptError("Comparison raster uses different font metrics.")
    return PreviewReceipt(
        schema="sjis-authoring-preview/v1",
        source_byte_sha256=source.byte_sha256,
        source_text_sha256=source.text_sha256,
        yours_text_sha256=_sha256_text(yours_text),
        target_text_sha256=_sha256_text(target_text),
        font_sha256=metrics.font_sha256,
        font_size_px=metrics.font_size_px,
        line_pitch_px=metrics.line_pitch_px,
        before_pixel_sha256=comparison.before_raster.pixel_sha256,
        yours_pixel_sha256=comparison.after_raster.pixel_sha256,
        target_pixel_sha256=comparison.target_raster.pixel_sha256,
        diff_pixel_sha256=comparison.yours_vs_target.diff_pixel_sha256,
        text_equal=comparison.text_equal,
        visual_equal=comparison.yours_vs_target.visual_equal,
        changed_pixel_count=comparison.yours_vs_target.changed_pixel_count,
        changed_bbox=comparison.yours_vs_target.changed_bbox,
        preview_rendered=preview_rendered,
        join_contract_sha256=(
            join_evaluation.contract_sha256 if join_evaluation else None
        ),
        join_passed=bool(join_evaluation and join_evaluation.passed),
        created_at_utc=datetime.now(timezone.utc).isoformat(),
    )


@dataclass(frozen=True)
class SubmissionGate:
    fresh_receipt: bool
    preview_present: bool
    transcription_equal: bool
    visual_equal: bool
    join_contract_passed: bool
    transcription_ready: bool
    visual_review_ready: bool
    operator_visual_acceptance: str
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def gate_submission(
    receipt: PreviewReceipt,
    source: TextArtifact,
    yours_text: str,
    target_text: str,
    metrics: FontMetrics,
) -> SubmissionGate:
    """Reject stale/no-preview evidence without claiming artist-intent acceptance."""

    fresh = receipt.matches(source, yours_text, target_text, metrics)
    reasons: list[str] = []
    if not receipt.preview_rendered:
        reasons.append("No native preview was rendered; transcription cannot be credited.")
    if not fresh:
        reasons.append("Preview receipt is stale or bound to different source/font/target hashes.")
    if not receipt.text_equal:
        reasons.append("YOURS does not exactly match TARGET code points.")
    if not receipt.visual_equal:
        reasons.append("YOURS and TARGET differ in native-font raster pixels.")
    if receipt.join_contract_sha256 is None:
        reasons.append("No explicit native-coordinate join contract was supplied.")
    elif not receipt.join_passed:
        reasons.append("Declared native-coordinate join anchors are misregistered.")
    return SubmissionGate(
        fresh_receipt=fresh,
        preview_present=receipt.preview_rendered,
        transcription_equal=receipt.text_equal,
        visual_equal=receipt.visual_equal,
        join_contract_passed=receipt.join_passed,
        transcription_ready=fresh and receipt.preview_rendered and receipt.text_equal,
        visual_review_ready=(
            fresh and receipt.preview_rendered and receipt.join_passed
        ),
        operator_visual_acceptance="required",
        reasons=tuple(reasons),
    )


def _data_url(mime: str, payload: bytes) -> str:
    return f"data:{mime};base64," + base64.b64encode(payload).decode("ascii")


def build_preview_payload(
    source: TextArtifact,
    yours_text: str,
    target_text: str,
    metrics: FontMetrics,
    *,
    join_contract: Optional[JoinContract] = None,
) -> dict[str, Any]:
    """Build BEFORE/YOURS/TARGET raw text plus native raster and gating data."""

    comparison = compare_text_art(source.text, yours_text, target_text, metrics)
    joins = (
        evaluate_join_contract(yours_text, target_text, metrics, join_contract)
        if join_contract is not None
        else None
    )
    receipt = build_preview_receipt(source, yours_text, target_text, metrics, comparison, joins)
    gate = gate_submission(receipt, source, yours_text, target_text, metrics)

    def panel(raster: RasterResult, text: str) -> dict[str, Any]:
        return {
            "text": text,
            "text_sha256": _sha256_text(text),
            "png_data_url": _data_url("image/png", raster.png_bytes),
            "width_px": raster.width_px,
            "height_px": raster.height_px,
            "pixel_sha256": raster.pixel_sha256,
            "placements": [asdict(item) for item in raster.placements],
        }

    return {
        "schema": "sjis-authoring-preview/v1",
        "font": metrics.receipt(),
        "source": {
            "path": source.source_path,
            "encoding": source.encoding,
            "byte_sha256": source.byte_sha256,
            "text_sha256": source.text_sha256,
        },
        "before": panel(comparison.before_raster, source.text),
        "yours": panel(comparison.after_raster, yours_text),
        "target": panel(comparison.target_raster, target_text),
        "difference": {
            "png_data_url": _data_url("image/png", comparison.yours_vs_target.diff_png_bytes),
            "visual_equal": comparison.yours_vs_target.visual_equal,
            "changed_pixel_count": comparison.yours_vs_target.changed_pixel_count,
            "changed_bbox": comparison.yours_vs_target.changed_bbox,
            "width_px": comparison.yours_vs_target.width_px,
            "height_px": comparison.yours_vs_target.height_px,
        },
        "receipt": receipt.as_dict(),
        "join_evaluation": joins and asdict(joins),
        "gate": gate.as_dict(),
    }


def build_final_receipt(
    source: TextArtifact,
    yours_text: str,
    target_text: str,
    metrics: FontMetrics,
    *,
    join_contract: Optional[JoinContract] = None,
) -> dict[str, Any]:
    """Return a compact structured receipt for the root integration hook."""

    payload = build_preview_payload(
        source, yours_text, target_text, metrics, join_contract=join_contract
    )
    return {
        "kind": "sjis-authoring-backend-final-receipt",
        "backend_schema": "sjis-authoring-preview/v1",
        "font_sha256": metrics.font_sha256,
        "source_byte_sha256": source.byte_sha256,
        "target_text_sha256": payload["receipt"]["target_text_sha256"],
        "receipt": payload["receipt"],
        "gate": payload["gate"],
        "limitations": [
            "Native raster equality is not artist-intent acceptance.",
            "Operator visual acceptance remains required.",
            "No corpus admission or AA-004 record was opened by this backend.",
        ],
    }


class _PreviewRequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "sjis-preview/1"

    def _authorized(self) -> bool:
        server = self.server  # type: ignore[attr-defined]
        query = parse_qs(urlsplit(self.path).query)
        return secrets.compare_digest(
            query.get("token", [""])[0], server.preview_token  # type: ignore[attr-defined]
        )

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        parsed = urlsplit(self.path)
        if parsed.path == "/font.ttf":
            if not self._authorized():
                self._send(403, "text/plain; charset=utf-8", b"forbidden")
                return
            font = self.server.preview_payload["font"]
            raw = Path(font["font_path"]).read_bytes()
            if _sha256(raw) != font["font_sha256"]:
                self._send(409, "text/plain; charset=utf-8", b"font changed")
                return
            self._send(200, "font/ttf", raw)
            return
        if parsed.path == "/api/preview":
            if not self._authorized():
                self._send(403, "text/plain; charset=utf-8", b"forbidden")
                return
            body = json.dumps(
                self.server.preview_payload,  # type: ignore[attr-defined]
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", body)
            return
        if parsed.path == "/" or parsed.path == "/sjis_preview.html":
            if not self._authorized():
                self._send(403, "text/plain; charset=utf-8", b"forbidden")
                return
            body = Path(__file__).with_name("sjis_preview.html").read_bytes()
            self._send(200, "text/html; charset=utf-8", body)
            return
        if parsed.path in {"/sjis_preview.js", "/sjis_preview.css"}:
            body = Path(__file__).with_name(parsed.path.lstrip("/")).read_bytes()
            content_type = (
                "application/javascript; charset=utf-8"
                if parsed.path.endswith(".js")
                else "text/css; charset=utf-8"
            )
            self._send(200, content_type, body)
            return
        self._send(404, "text/plain; charset=utf-8", b"not found")

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if urlsplit(self.path).path != "/api/seen":
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return
        if not self._authorized():
            self._send(403, "text/plain; charset=utf-8", b"forbidden")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError("invalid acknowledgement size")
            acknowledged = json.loads(self.rfile.read(length))
        except (ValueError, TypeError):
            self._send(400, "text/plain; charset=utf-8", b"invalid acknowledgement")
            return
        current = _preview_identity(self.server.preview_payload)
        if acknowledged != current:
            self._send(409, "text/plain; charset=utf-8", b"stale preview")
            return
        self.server.preview_seen = {
            "identity": current,
            "displayed_at_utc": datetime.now(timezone.utc).isoformat(),
            "basis": "browser-font-and-four-native-images-loaded",
        }
        self._send(200, "application/json", b'{"displayed":true}')

    def log_message(self, format: str, *args: Any) -> None:
        return


class PreviewServer:
    """Token-protected loopback preview server owned by the caller."""

    def __init__(self, server: socketserver.TCPServer, thread: threading.Thread, token: str):
        self._server = server
        self._thread = thread
        self.token = token
        host, port = server.server_address[:2]
        self.url = f"http://{host}:{port}/?token={token}"

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)

    def update(self, payload: Mapping[str, Any]) -> None:
        """Replace the in-memory payload for an editor-driven live refresh."""

        self._server.preview_payload = dict(payload)  # type: ignore[attr-defined]

    def displayed_receipt(self) -> Optional[dict[str, Any]]:
        """Return the browser display receipt only for the current inputs.

        Rendering a payload or fetching JSON does not establish display. This
        receipt is automated browser evidence, not a human artistic decision.
        """
        seen = self._server.preview_seen
        if seen and seen["identity"] == _preview_identity(self._server.preview_payload):
            return dict(seen)
        return None

    def __enter__(self) -> "PreviewServer":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()


def serve_preview(
    payload: Mapping[str, Any],
    *,
    host: str = "127.0.0.1",
    port: int = 0,
) -> PreviewServer:
    """Serve a payload locally; no cloud upload or automatic browser action occurs."""

    if host != "127.0.0.1":
        raise AuthoringError("Preview server is local-only and must bind 127.0.0.1.")
    token = secrets.token_urlsafe(24)

    class _Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = False

    server = _Server((host, port), _PreviewRequestHandler)
    server.daemon_threads = True
    server.preview_token = token  # type: ignore[attr-defined]
    server.preview_payload = dict(payload)  # type: ignore[attr-defined]
    server.preview_seen = None
    thread = threading.Thread(target=server.serve_forever, name="sjis-preview", daemon=True)
    thread.start()
    return PreviewServer(server, thread, token)


def _preview_identity(payload: Mapping[str, Any]) -> dict[str, Any]:
    receipt = payload["receipt"]
    return {key: receipt[key] for key in (
        "source_byte_sha256", "source_text_sha256", "yours_text_sha256",
        "target_text_sha256", "font_sha256", "font_size_px", "line_pitch_px",
        "before_pixel_sha256", "yours_pixel_sha256", "target_pixel_sha256",
        "diff_pixel_sha256", "join_contract_sha256",
    )}


__all__ = [
    "AuthoringError",
    "DependencyMissingError",
    "EncodingPolicyError",
    "ExportExistsError",
    "FontMetrics",
    "FontUnavailableError",
    "GlyphMetric",
    "GlyphPlacement",
    "JoinAnchor",
    "JoinContract",
    "JoinContractError",
    "JoinEvaluation",
    "JoinMeasurement",
    "PreviewReceipt",
    "PreviewServer",
    "RasterComparison",
    "RasterResult",
    "ReceiptError",
    "SubmissionGate",
    "TextArtifact",
    "TextArtComparison",
    "artifact_from_text",
    "anchor_from_target",
    "build_final_receipt",
    "build_preview_payload",
    "build_preview_receipt",
    "compare_rasters",
    "compare_text_art",
    "evaluate_join_contract",
    "export_artifact",
    "gate_submission",
    "import_artifact",
    "load_font_metrics",
    "make_join_contract",
    "render_text",
    "serve_preview",
]


def load_font_metrics(
    font_path: os.PathLike[str] | str = DEFAULT_FONT_PATH,
    *,
    font_size_px: int = DEFAULT_FONT_SIZE_PX,
    line_pitch_px: int = DEFAULT_LINE_PITCH_PX,
) -> FontMetrics:
    """Public convenience wrapper for :meth:`FontMetrics.load`."""

    return FontMetrics.load(
        font_path,
        font_size_px=font_size_px,
        line_pitch_px=line_pitch_px,
    )
