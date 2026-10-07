# Proportional Shift_JIS authoring

The tutor keeps three results separate: exact transcription, native-font pixel
comparison, and measured target registration. None is an artist-intent verdict.
The operator must still judge the intended contour in the native preview.

## Japanese text, encoding and font spacing

Japanese can be typed and rendered in Ghostty and edited in terminal Neovim.
Shift_JIS is an encoding; it does not itself require proportional spacing.
Saitamaar supplies glyph shapes and per-glyph advances. At 16 px, the inspected
font advances `i` and `.` by 3 px, U+0020 by 5 px, U+3000 by 11 px, and `／` by
16 px. Those advances determine alignment in art authored for this font.
Neovim's normal terminal UI places text on a cell grid. Selecting Saitamaar
as a terminal font does not establish that its proportional advances are
preserved. The tutor therefore edits text in Neovim and displays a separate
native-font raster preview inside Ghostty. That is terminal graphics, not a
screenshot or a browser requirement, and not native proportional buffer
layout. Japanese glyph support and proportional layout are separate checks.

`sjis_authoring.py` owns strict bytes, measured advances, raster comparison and
the loopback page. `sjis_tutor.py` owns the working-file lifecycle and the
browser-display receipt. `sjis_terminal.py` owns the default Ghostty native-PNG
display and bound terminal acknowledgements. The implementation uses only the existing authored
M10 text. It does not import an AAHub corpus or grant new glyph admissions.

## Strict import and export

Install the repository normally to expose `vim-daily-sjis`. The installer pins
fontTools and Pillow in the existing managed runtime. It does not install a
font or change Neovim settings. The caller selects both codecs explicitly:

```sh
vim-daily-sjis import --source /absolute/source.sjis --source-encoding shift_jis --output /absolute/working.txt --output-encoding utf-8
vim-daily-sjis export --source /absolute/working.txt --source-encoding utf-8 --output /absolute/result.sjis --output-encoding shift_jis
```

The caller must supply an existing output directory. An existing destination
is refused unless the caller explicitly supplies `--overwrite`. Unsupported
bytes and unencodable glyphs are refused. The tools do not detect an encoding,
replace a character, trim spaces or translate newlines. Receipts name the
source and output byte hashes. U+0020 and U+3000 remain different codepoints.

CP932 contains some duplicate byte spellings. The backend preserves the exact
original bytes when an unchanged artifact is exported in its original codec.
Transcoding through a separate UTF-8 working file preserves codepoints, not
duplicate CP932 byte spellings. The output byte hash makes that distinction
visible; do not describe every transcode as byte-identical.

## Native preview

The default surface is terminal-native Kitty graphics, supported by Ghostty.
The tutor displays BEFORE, YOURS, TARGET and changed-pixel panels at native
dimensions before editing and again before awarding credit. Each PNG needs a
bound positive terminal response. A missing response, cancelled confirmation,
changed artifact or failed native comparison denies credit. Text remains
editable in Neovim; terminal-cell layout is not proportional alignment proof.
The preview temporarily enables graphics passthrough only on the exact tutor
pane when its inherited setting is off. It validates the TMUX socket, server,
session and TMUX_PANE ownership before changing anything. It restores the exact
prior explicit or inherited pane setting on success, cancellation and errors.
It never changes a global tmux option. Missing pane ownership fails visibly.
`test_sjis_ghostty_real.py` exercises all four production PNGs in
actual Ghostty, and `--tmux` repeats that transport through a new disposable
tmux server. Both passed on Ghostty 1.2.3. The isolated test verifies inherited
off before and after its temporary pane override and removes its server.
Popup children without TMUX_PANE fail closed; a passing exact-pane test does
not prove popup graphics support. The separate `--popup` run supplies verified
pane ownership but still times out without graphics acknowledgements on tmux
3.6a. Native previews are currently proved in normal panes, not popups.
The matching upstream [popup parser](https://github.com/tmux/tmux/blob/3.6a/popup.c#L735)
initializes its input context without a pane. Its
[DCS handler](https://github.com/tmux/tmux/blob/3.6a/input.c#L2430-L2431)
returns before reading passthrough options when no pane is present. This
explains the observed popup timeout; changing a global option is not a repair
for that source path.
`test_module_ghostty_real.py` also passes all eight canonical M10 frames
directly and with `--tmux`, including actual authored 1/6 s holds and exact
pane-setting restoration. These are transport runs, not reached lesson grades.
When the selected lesson needs native JIS graphics, the popup route now opens
a temporary normal tmux window inside Ghostty. The child keeps the scheduler,
daily cap and uncredited-practice route. Only the new window receives
`remain-on-exit off`; parent/global options stay unchanged. Nine routing
fixtures and isolated-server exit housekeeping pass. A private start barrier
keeps a setup failure from racing a learner attempt. The normal window holds
its result until the learner closes it.
`test_native_window_route_real.py` passes an actual Ghostty-created isolated
tmux server: production native popup selection, M10.01 Neovim edit, two real
native confirmations, authored after-question and held PRACTICE COMPLETE.
No learner event is created. The owned window closes and all parent/global
passthrough values remain unchanged. Fresh .72 runs pass with Textual both on
and off. Each passing result plays all eight module frames. Independently
checked receipts bind canonical text, shared-canvas PNG hashes, font metrics,
positive terminal responses and actual timed holds to the edit attempt.
This proves uncredited-practice grading and native result playback.
Collected `.75` personal-config Textual runs also cover M10.REWARD at
80×24, 100×36 and 188×49. Each receipt has four native panels and eight timed
positive reward responses on the same 104×51-cell canvas. M10.06 passes the
same three-size native route on `.73`. These are revision-bound receipts;
they are not relabelled as `.76` or human contour approval.
The native result player shares one pixel canvas and origin across all frames.
It runs on both Textual and fallback result routes. Each actual edit attempt
can receive a separate `.reward.json` receipt bound to its keylog, canonical
text, emitted PNGs, positive responses, font metrics and timed holds. Failure
to play or save this bonus receipt leaves the grade unchanged. Focused fixtures
cover the production post-lesson route. The reached-result run uses current
generated metadata, not a direct player fixture.
ACKs prove transport, not
human contour approval. This terminal preview updates before editing and
before credit, not continuously while typing in Neovim.
Protocol: [Kitty graphics](https://sw.kovidgoyal.net/kitty/graphics-protocol/).
Support: [Ghostty features](https://ghostty.org/docs/features).

```sh
vim-daily-sjis preview --source /absolute/source.sjis --source-encoding shift_jis --yours /absolute/working.txt --target /absolute/target.txt --target-encoding utf-8 --receipt /absolute/attempt-receipt.json
```

Add `--surface browser` to select the optional local page. The page shows selectable BEFORE, YOURS and TARGET text, the three native
rasters, and a changed-pixel image. It refreshes YOURS when the working UTF-8
file changes. Native rasters keep their original pixel dimensions. The page
loads the exact font for its raw selectable text as well.

The default font is the operator-local
`/Users/r/Projects/ascii-art-archive/collections/aahub/Saitamaar.ttf`.
Its measured SHA-256 is
`592bf6be803ed76311841b95a10b20db3df0ec693a15f858757d47420b9b3a28`.
The preview uses 16 px glyph size and 17 px line pitch, with the font's actual
1280-unit/em advances. Supply `--font` for another explicit local path.
The tutor adapter also accepts `VIM_DAILY_SAITAMAAR_FONT`.
Missing font/dependencies and an on-disk font change fail visibly. There is no
terminal-metric fallback.

The server binds only `127.0.0.1`. Its page, data, font and display-acknowledgement
routes require a per-session token. It uploads nothing. A payload rendered in
memory does not count as a displayed preview. The page acknowledges its
source/YOURS/TARGET/font/diff hashes only after the font and four images load.
A changed artifact invalidates that display receipt. Pressing Enter checks
the current bytes and writes the caller's declared receipt path.

## Evidence boundaries

- Transcription equality compares every codepoint, including trailing spaces.
- Pixel equality compares native-font rasters over the union of both extents.
- Target registration compares declared visible glyph starts in native font
  units. A same-terminal-width spacing change can fail this check.
- Browser display proves the page loaded the bound font and images. It does
  not prove a human inspected them.
- Human contour/join approval is still required. Target registration does not
  infer which strokes an artist intended to connect.

`test_sjis_authoring.py` covers the backend. `test_sjis_tutor.py` covers connected
strict-byte, font-change, stale-display and no-display controls.
`test_sjis_browser.py` is a real-browser fixture isolated from learner state.
Its successful display receipt is browser evidence, not operator acceptance.

Runtime course integration and its final-source headed evidence are tracked in
`audits/COURSE_COMPLETION_LEDGER_2026-10-01.md` (C21–C23 and C25).

Final `.77` runtime proof uses
`d27b95b1876a71cc06076f9eb9aff82611605344c886f307a701d5e509c8e5c7`.
Six actual personal-config Ghostty runs cover M10.06 and M10.REWARD at
80×24, 100×36 and 188×49. Each run observes four native panels, a real
uncredited-practice edit and grade, held completion, all eight timed reward
frames, owned-window closure and restored options. Thirteen native-routing
and ten publication/identity controls pass, including the nonce-bound child
load acknowledgement. These receipts prove the exercised terminal workflow,
not proportional Neovim buffer layout, continuous live preview or human
contour approval. The older receipts above retain their original revisions.
