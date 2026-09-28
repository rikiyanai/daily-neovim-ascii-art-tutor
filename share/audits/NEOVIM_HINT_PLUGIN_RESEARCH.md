# Neovim hint and key-feedback plugin research

**Review status:** research and proposal only. No plugin was installed, enabled,
configured, or added to the tutor. Operator approval is required before any
generator or runtime change.

**Evidence date:** 2026-09-28 (America/New_York). Upstream source was read
directly from the repositories' README, help, Lua source, license, changelog,
and release/tag refs. The exact `HEAD` refs below were obtained with
`git ls-remote` on this date. A current `HEAD` is not a recommendation to track
an unpinned development branch.

## Decision in one page

1. Keep the tutor's current Neovim `-w` scriptout and its runtime as the only
   authoritative raw-key capture and grader. It already supports alternate valid
   key sequences, effect-based checking, and the actual-vs-taught ledger.
2. A floating display is not a grader, and a plugin's semantic action name is
   not proof that the learner used the taught method. Preserve the operator's
   configured plugins by default; do not equate “answer-hidden” with silently
   disabling their environment.
3. If the operator elects to add a discoverability aid to a user's own config,
   use **WhichKey or mini.clue (one, not both) only for an explicit grammar
   primer or demonstration**. Do not install it or change an existing instance.
   Both can reveal an exact next key and install trigger mappings; any future
   tutor-managed exam-isolation toggle therefore requires explicit opt-in.
4. Use **screenkey.nvim for demonstrations only**, when the operator explicitly
   asks to show a live keycast. It is not a hint engine or a grader. Do not add
   it to the tutor's normal popup path.
5. Do not use `nvzone/showkeys` in the tutor. It is a simple keycast window with
   no public capture/export or semantic API; it is at most an operator-run,
   outside-the-lesson screencast aid.
6. Preserve Hardtime when it is part of the operator's config. It creates
   expression mappings, can block input, and gives advice, but that real
   behavior is explicitly part of this operator's learning environment. It is
   advisory and never grading evidence. Do not install, disable, or retune it
   without an explicit operator choice.
7. Reject Precognition for this product: its defining implementation is virtual
   lines, virtual text/extmarks, and gutter signs, exactly the rendering classes
   the fixed-width art surface forbids.
8. Track-action.nvim is the strongest future candidate for a *semantic* post-
   lesson ledger, but it requires Neovim 0.13's `CmdAtom`; this machine is on
   Neovim 0.12.5. Even on 0.13 it must remain advisory and must not replace raw
   scriptout grading.

## Scope and non-negotiable boundaries

The local product says that the exact sequence stays hidden on independent,
transfer, comparison, review, and module-check cards, while the debrief replays
the artifact and actual keys ([README.md](../../README.md#L116-L128)). It also
says that a command appearing only in a displayed recipe is not verified
coverage ([README.md](../../README.md#L132-L136)). The current runtime captures
`-w` output, decodes it, and compares actual tokens with the taught path
([bin/vim-daily-gate](../../bin/vim-daily-gate#L634-L795);
[share/v2_runtime.py](../v2_runtime.py#L891-L907)). The method-evidence gate
separately checks a declared exact/required path ([share/v2_runtime.py](../v2_runtime.py#L919-L970)).

The supported popup tests are 188x49, 100x36, and 80x24
([README.md](../../README.md#L258-L286)). The art buffer is fixed-width material,
not a canvas on which an overlay may be silently painted. Therefore:

- No candidate may add virtual text, virtual lines, signs, conceal, inline
  extmarks, or an overlaid key strip to the art buffer during an attempt.
- A float must not cover the art or the read-only brief at any supported size.
  `no_overlap` in a plugin generally means “do not cover the cursor”, not “do
  not cover this tutor's two panes”.
- The operator's existing config remains authoritative. The tutor must not
  disable or reconfigure a user-configured plugin for art/brief buffers unless
  the operator explicitly enables a documented isolation setting. It may not
  rewrite global mappings or silently install anything.
- A plugin that displays keys, hints, statistics, or semantic actions is not a
  grader unless its API proves the exact input/effect contract needed by the
  card. For this product, that proof remains the scratch/real Neovim run plus
  `-w` capture.

## Current-source ledger

All “HEAD” values below are remote refs observed on 2026-09-28. The release is
the newest tag found in the remote refs or the newest dated changelog release;
where no release exists, that is stated. Source links are upstream links, not
search-result pages.

| Candidate | Current source evidence | Requirements / license | Maintenance and product fit |
|---|---|---|---|
| [NStefan002/screenkey.nvim](https://github.com/NStefan002/screenkey.nvim) | `main` HEAD `740e238d1f143cb5b3a9d932f9c5142d3581b986`; latest tag `v2.4.2` (2024-12-09 in [CHANGELOG.md](https://raw.githubusercontent.com/NStefan002/screenkey.nvim/main/CHANGELOG.md)) | Main README says Neovim >=0.11 and optional Nerd Font; the generated help currently says >=0.10. No runtime dependency; MIT ([LICENSE](https://raw.githubusercontent.com/NStefan002/screenkey.nvim/main/LICENSE)). | Good live keycast and filterable display; no grammar model, no effect grader, and no public raw-history export. Demo only. The README warns that `main` can be unstable; pin a release if an operator chooses it. |
| [nvzone/showkeys](https://github.com/nvzone/showkeys) | `main` HEAD `cb0a50296f11f1e585acffba8c253b9e8afc1f84`; no release tags found | README states only the Neovim plugin install; no version or dependency contract is documented. GPL-3.0 ([LICENSE](https://raw.githubusercontent.com/nvzone/showkeys/main/LICENSE)). | Small `vim.on_key` keycast with timeout/maxkeys/mode exclusion. No public event, history, semantic parse, or export API. Not suitable for hints, grading, or the tutor surface. |
| [m4xshen/hardtime.nvim](https://github.com/m4xshen/hardtime.nvim) | `main` HEAD `5165840fe680eab46de1fc6dbff48f148fdcf018`; `v1.2.0` (2025-06-16 [CHANGELOG.md](https://raw.githubusercontent.com/m4xshen/hardtime.nvim/main/CHANGELOG.md)) | Neovim >=0.10; requires [MunifTanjim/nui.nvim](https://github.com/MunifTanjim/nui.nvim); MIT ([LICENSE](https://raw.githubusercontent.com/m4xshen/hardtime.nvim/main/LICENSE)). | Useful rejected-input advice and habit reports, but it installs expression mappings, blocks keys by default, skips command-line and Replace handling, and has only a text notification callback. Optional user coach outside attempts; never the tutor grader. |
| [folke/which-key.nvim](https://github.com/folke/which-key.nvim) | `main` HEAD `3aab2147e74890957785941f0c1ad87d0a44c15a`; `v3.17.0` (2025-02-14 [CHANGELOG.md](https://raw.githubusercontent.com/folke/which-key.nvim/main/CHANGELOG.md)) | Neovim >=0.9.4; optional mini.icons or nvim-web-devicons/Nerd Font; Apache-2.0 ([LICENSE](https://raw.githubusercontent.com/folke/which-key.nvim/main/LICENSE)). | Strongest mature operator/motion/text-object discoverability and all-mode trigger support. It intentionally shows available mappings/presets, so it can reveal an answer. Recommend it for primers; preserve an existing operator-owned instance during attempts unless the operator opts into isolation. |
| [tris203/precognition.nvim](https://github.com/tris203/precognition.nvim) | `main` HEAD `201da44c95c634ae9d99414ec3cf8fc582fb323b`; `v1.3.0` (2026-05-12 [CHANGELOG.md](https://raw.githubusercontent.com/tris203/precognition.nvim/main/CHANGELOG.md)) | README supports stable/nightly >0.9; no external dependency documented; MIT ([LICENSE](https://raw.githubusercontent.com/tris203/precognition.nvim/main/LICENSE)). | Motion suggestions are context-aware but rendered through virtual text/virtual lines and gutter signs, and they expose exact motions. Reject for fixed-width art and Socratic hidden practice. |
| [nvim-mini/mini.clue](https://github.com/nvim-mini/mini.clue) | `main` HEAD `1c136d62729c8c3b0c2d91379bc37efac15d916e`; mini.nvim latest tag observed `v0.18.0`; current docs describe a stable branch | MIT ([LICENSE](https://raw.githubusercontent.com/nvim-mini/mini.clue/main/LICENSE)); standalone or mini.nvim; docs describe Neovim 0.12+ for `vim.pack`, but the module's general compatibility should be checked at pin time. | Strong alternative to WhichKey: explicit clue triggers and no mapping creation for clues, but triggers are buffer-local mappings that can override mappings; operator-pending support is explicitly not foolproof. Recommend it for primers; do not install or suppress it automatically. |
| [17xande/track-action.nvim](https://github.com/17xande/track-action.nvim) | `master` HEAD `1ff4fb111580d22300445891149d76d8faf164d4`; no release tags found | Neovim >=0.13 hard requirement for `CmdAtom`; no external dependency; MIT ([LICENSE](https://raw.githubusercontent.com/17xande/track-action.nvim/master/LICENSE)). | Best semantic action observer and future post-lesson ledger API, with key/ex-command callbacks and `CmdAtom` payloads. It does not itself provide the raw typed stream/effect grader, and its float/stats persistence must be opt-in. Not usable on current Neovim 0.12.5. |
| [wsdjeg/record-key.nvim](https://github.com/wsdjeg/record-key.nvim) | `master` HEAD `a18ad13d78bc1769a0e4dfb5bf50402c68456f3f`; `v1.4.0`; changelog release 2025-11-24 | No dependency documented; GPL-3.0 ([LICENSE](https://raw.githubusercontent.com/wsdjeg/record-key.nvim/master/LICENSE)). | Raw display only. It creates multiple bottom-right floats, uses `eventignore`, exposes no capture/export API, and its source notes that key windows do not update in command-line mode. Reject for the tutor. |
| [tamton-aquib/keys.nvim](https://github.com/tamton-aquib/keys.nvim) | `main` HEAD `572490e8efac66a6008e016dbe82ad49ebfb3250`; no release tags found | WIP README; license is present in the repository but no stable requirement/dependency contract is given. | README explicitly calls it WIP and recommends screenkey.nvim as the better implementation. Reject. |
| [hasundue/vim-keycasty](https://github.com/hasundue/vim-keycasty) | Official README calls it experimental; source is maintained as a Vim/Neovim Denops project | Requires Vim/Neovim plus Deno and denops.vim; license/source details are in the repository. | It estimates key input from editor events, explicitly says casts are not necessarily identical to true input, and does not support editing or custom mappings. Reject as evidence or grading. |

The activity evidence above is deliberately separated from correctness. A recent
commit or a large feature set does not make a display plugin an input oracle.

## Plugin-by-plugin findings

### screenkey.nvim: demonstration only

The [README configuration](https://raw.githubusercontent.com/NStefan002/screenkey.nvim/main/README.md)
creates a non-focusable floating window and documents `filter`, `colorize`, mode/
filetype/buftype disabling, grouping mappings, `emit_events`, and a statusline
`get_keys()` API. The source confirms that it registers `vim.on_key` in
[lua/screenkey/init.lua](https://github.com/NStefan002/screenkey.nvim/blob/main/lua/screenkey/init.lua),
stores queued key objects privately, and exposes only the currently displayed
string through `get_keys()` when the statusline component is active. The
`User` events are payload-less `ScreenkeyUpdated`/`ScreenkeyCleared` events and
are tied to that statusline component ([core.lua](https://github.com/NStefan002/screenkey.nvim/blob/main/lua/screenkey/core.lua)).

That makes it useful for a human watching a demonstration, not for the tutor's
ledger: the API does not promise a per-input callback, immutable raw sequence,
mode/action boundary, command-line text, or post-lesson export. Its default
40-column bottom-right float can cover the art/brief in an 80x24 or 100x36
popup. `filter` is a display filter, not a recording hook. The operator may run
`:Screenkey` outside an exercise, or in a deliberately labelled “watch the
keys” lesson where exact keys are meant to be visible. If it already belongs to
the user's config, preserve it; an operator may explicitly choose to hide its
display for an answer-hidden card, but that is not the tutor default.

### nvzone/showkeys: do not integrate

The [README](https://github.com/nvzone/showkeys/blob/main/README.md) calls it an
“eye-candy keys screencaster”. Its [init.lua](https://github.com/nvzone/showkeys/blob/main/lua/showkeys/init.lua)
uses `vim.on_key`, opens a float on each input, and calls
[utils.parse_key](https://github.com/nvzone/showkeys/blob/main/lua/showkeys/utils.lua),
which only maintains private `state.keys`. Options are `timeout`, `maxkeys`,
`show_count`, `excluded_modes`, position, and key formatting. There is no public
callback, semantic action, export, or post-attempt snapshot API. The overlay
uses extmark virtual text *inside its own float*, so it does not mutate the art,
but the default bottom-right position still competes for scarce popup space.

It is weaker than screenkey for this product: no event/statusline bridge and no
documented filtering boundary. GPL-3.0 is also a more consequential distribution
choice than the tutor needs. If a user already has it, leave that user config
alone. Do not add it as a tutor dependency or suppress it without an explicit
operator setting.

### Hardtime: optional user coach, never authoritative

Hardtime's [README](https://github.com/m4xshen/hardtime.nvim/blob/main/README.md)
promises bad-habit blocking, faster-motion hints, and reports. It requires
`nui.nvim`, and its defaults include `restriction_mode = "block"`.
[init.lua](https://github.com/m4xshen/hardtime.nvim/blob/main/lua/hardtime/init.lua)
installs expression mappings for resetting/restricted/disabled keys. A blocked
key may return `""`, so the plugin changes the command behavior itself. Its
`vim.on_key` observer skips command-line mode (`c`) and Replace mode (`R`), and
insert mode is handled only for idle timers; it is not a complete raw-key
capture. The callback receives only notification text, while the report reads
Hardtime's own log file. There is no callback with a stable action record or
effect result.

Its built-in messages can answer the exercise (“Use `[count]j` or CTRL-D”),
which conflicts with Socratic answer hiding. It also conflicts directly with
the requirement that the operator's mappings and behavior remain authoritative.
It remains an explicitly user-owned habit coach during tutor attempts when the
operator configured it that way. Its messages and blocking behavior are part of
the real environment, not mastery evidence. The tutor must neither disable nor
retune it silently, and setup must not enable it without consent.

### WhichKey: best primer/discoverability aid, gated

WhichKey's [README](https://github.com/folke/which-key.nvim/blob/main/README.md)
documents Normal, Insert, Visual, operator-pending, Terminal, and command modes;
operator/motion/text-object presets; delayed floating display; explicit
`triggers`; and `show_keys`. Its v3 mappings API reads keymap `desc` values and
also permits user-supplied groups. The source's default presets include exactly
the grammar vocabulary this course teaches.

The important cost is also explicit in the source: WhichKey sets up automatic
trigger mappings (unless configured otherwise), and its popup lists the available
next mappings. That is excellent for a primer where the learner is invited to
explore, but it gives away an answer if shown while a key-hidden card is being
graded. `show_keys` is a command-line display of the current prefix, not a raw
attempt recorder. WhichKey has no artifact/effect grader and no two-column ledger
export.

Recommended boundary: let a user choose WhichKey for M0's grammar primer or an
operator-requested “show me available operators” demonstration. Scope any new
custom clue mappings to the teaching buffer and never mutate the user's existing
maps. If WhichKey already belongs to the operator's config, preserve its normal
triggers and popup; suppressing them for independent or check attempts is only
an explicit future exam-isolation option. Do not recommend running it alongside
mini.clue.

### mini.clue: safer alternative primer, still gated

The [mini.clue README](https://github.com/nvim-mini/mini.clue/blob/main/readmes/mini-clue.md)
and its [help/source](https://github.com/nvim-mini/mini.clue/blob/main/lua/mini/clue.lua)
describe a custom key-query process: each key narrows possible targets, then a
float lists next keys and descriptions. It has generators for `g`, `z`, windows,
marks, registers, square brackets, and insert completion. It documents support
for Normal, Visual, Insert, operator-pending, command-line, and Terminal modes.

Unlike WhichKey, clues do not create mappings by design. However, its triggers
*are* special buffer-local mappings, can override a same-key buffer mapping, must
be created after other buffer-local maps, and are explicitly “not foolproof” in
operator-pending mode. The module also emulates query keys and postkeys; this is
not passive observation. It has no raw-key export or effect grader. A clue's
description can still reveal the exact next key.

Recommended boundary: choose it instead of WhichKey for an explicit grammar
primer if the operator prefers opt-in triggers and a separate clue vocabulary.
Preserve an existing configuration during attempts. An operator-approved
exam-isolation option may use `vim.b.miniclue_disable` (or the documented
equivalent), but the tutor must not do so by default. Never treat its query log
or clue window as grading evidence.

### Precognition: reject for fixed-width art

The official [README](https://github.com/tris203/precognition.nvim/blob/main/README.md)
describes context-aware `w/b/e`, line-end, matching-pair, gutter, targeted `f/F`,
and text-object hints. It also explicitly says it uses virtual text and gutter
signs. The implementation confirms `nvim_buf_set_extmark` with `virt_lines`,
range namespaces, and `sign_place` in [renderer.lua](https://github.com/tris203/precognition.nvim/blob/main/lua/precognition/renderer.lua).
It can pad an inline virtual line to the current window width and highlight
text-object ranges.

Those are direct violations of this tutor's art contract: virtual lines add
display rows; virtual text may overlay or shift; signs alter the gutter; and the
motion labels disclose a solution. It also has no grading/export API. Do not
attempt to “make it safe” by lowering priorities: even a subtle extmark/sign
pollutes the evidence surface. It is rejected, not merely disabled by default.

### track-action.nvim: future semantic observer, not current grader

Neovim's current master help documents `CmdAtom` as a deferred event after a
completed normal command, motion, operator, insert session, Visual sequence, Ex
cmdline, mapping, macro, scroll, or mouse. Its payload includes `cmd`, `cmdarg`,
`count`, resolved `keys`, user `lhs`, `operator`, position, text, changed state,
and type ([Neovim autocmd help](https://github.com/neovim/neovim/blob/master/runtime/doc/autocmd.txt#L423-L505)).
This is a promising core primitive for a future semantic ledger.

track-action.nvim is a thin consumer of that event. Its [README](https://github.com/17xande/track-action.nvim/blob/master/README.md)
documents separate key-action and Ex-command callbacks, `get_stats`/`top`,
`User` events, and normalized actions such as `[count]j`, `dw`, `ciw`, and
`ex:write`. Its [atom.lua](https://github.com/17xande/track-action.nvim/blob/master/lua/track-action/atom.lua)
pins the hard Neovim >=0.13 requirement and passes the event payload through;
[tracker.lua](https://github.com/17xande/track-action.nvim/blob/master/lua/track-action/tracker.lua)
exposes `data.atom`, `lhs`, `pressed`, `source`, and category to callbacks.

This machine currently reports **NVIM v0.12.5**, so the plugin's health check
would correctly fail and no actions would be counted. On a future >=0.13
baseline, an adapter could record `data.action`/`data.category` as semantic
post-lesson context and retain `data.atom` for an operator-audited ledger. It
must not use `get_stats()` as progress evidence: counts are persistent global
statistics, registers/counts are normalized, and the action string does not
prove that the exact taught path or final artifact was correct. The float at the
bottom-right must also stay closed in the art/brief attempt. Do not install it
until the operator explicitly approves a Neovim-version policy and evidence
schema.

### record-key.nvim, keys.nvim, and keycasty: reject

record-key.nvim is a raw display implementation, not a recorder. Its
[source](https://github.com/wsdjeg/record-key.nvim/blob/master/lua/record-key/init.lua)
opens a new bottom-right floating window for each key, manipulates `eventignore`,
and holds keys in a private table. The source contains the comment “key windows
does not update in cmdline mode”; there is no public callback or export. It is
therefore unsuitable for the four-mode lesson contract and the fixed popup
sizes. Its GPL-3.0 license is an additional unnecessary constraint.

keys.nvim's own [README](https://github.com/tamton-aquib/keys.nvim/blob/main/README.md)
labels it WIP, documents missing modifier/backspace support, and recommends
screenkey.nvim as the better implementation. It has no reason to displace the
current raw capture. keycasty is explicitly experimental and estimates inputs
from cursor/text events rather than observing true keys; it also lacks editing
and custom-mapping support. Neither can be evidence or grading infrastructure.

## What each candidate can and cannot do

| Need | Required baseline | Screenkey / showkeys / record-key | Hardtime | WhichKey / mini.clue | Precognition | track-action (>=0.13) |
|---|---|---|---|---|---|---|
| (a) Show keys just typed | Existing `-w` capture; optional local `vim.on_key` display | Yes, display only; no stable export | Partial observer, not complete | Prefix/current-key display only | No | Semantic action; `CmdAtom` carries payload but plugin normalizes |
| (b) Teach grammar without answer leak | Tutor-authored Socratic question + scratch evaluator | No | No; hints often reveal answer | Yes in primer; no during hidden card | No; labels expose motions | Names completed actions after the fact, not a question engine |
| (c) Explain inefficient/rejected input | Tutor owns wrong-answer breakdown and re-show | No | Yes, but may block and change behavior | No | No | No; advisory action stream only |
| (d) Actual-vs-taught replay | `-w` + artifact before/after + runtime ledger | No public replay/export | Own log only | No | No | Future semantic supplement, not raw/effect proof |
| (e) Discoverable command hints | Tutor primer and explicit question placement | No | Habit messages, not grammar | Strong operators/motions/text objects | Strong motion disclosure, disallowed | No next-key discoverability |
| Fixed-width art | No decoration on art | Float may cover art | Notifications/popup can cover; mappings alter behavior | Float/trigger isolation required | **Fails: virtual text/lines/signs** | Close stats float; no art decoration |

The distinction matters: “shows a key” is not “knows what the key did”; “knows
what command completed” is not “proves the learner solved this art task with the
required method”.

## Ranked architecture and integration boundary

### Rank 1 — required baseline: tutor-owned evidence

- Keep `nvim -w keylog` as the raw typed stream for every attempt, including
  retries. Continue stripping only the explicit save/quit suffix before method
  checks. Keep the final buffer/effect check independent of the key string.
- For open typed-key questions, launch a scratch Neovim buffer and grade the
  resulting cursor/buffer state. This is what permits semantically equivalent
  answers such as `4j` and `:+4<CR>` without requiring exact text.
- Keep the tutor's own feedback surface responsible for “what happened”,
  actual-vs-taught columns, wrong-answer re-show, and optional “next”. A plugin
  display may decorate a demonstration but cannot own those state transitions.
- If a future live key display is needed, use a small tutor-owned
  `vim.on_key` listener with its own namespace, returning `nil` and never
  modifying mappings. It must be display-only and shut down before grading;
  retain `-w` as the evidence source.

### Rank 2 — optional user configuration: one grammar clue aid

Offer a copyable, never-applied recommendation for **WhichKey** or **mini.clue**.
The operator chooses one. The recommended usage is:

- grammar primer and explicit “show available grammar” demonstration: enabled;
- guided card where the recipe is intentionally visible: optional, only if the
  operator wants the same visible teaching surface;
- independent/transfer/comparison/review/module-check: preserve the operator's
  normal config; only an explicitly enabled exam-isolation mode may suppress a
  clue display for that attempt;
- no automatic plugin installation, no global map replacement, and no plugin
  statistics as evidence.

WhichKey is the default recommendation for broad built-in operator/motion/text
object presets. mini.clue is the alternative when the operator wants a
separately authored clue vocabulary and opt-in triggers. Do not enable both;
their trigger windows and descriptions would duplicate or compete.

### Rank 3 — optional demonstrations

Screenkey.nvim may be used only for an operator-requested live demonstration,
preferably outside the tutor popup or while the art pane is not being evaluated.
Pin a stable tag, verify the actual Neovim requirement (README/help currently
disagree), and position/disable it so no art or brief row is covered. Treat its
events, filter, statusline string, and log as display diagnostics only.

showkeys, record-key, and keys.nvim add no evidence capability. They should not
be part of the tutor recommendation; if already installed by the user, the
tutor should leave their config and normal behavior untouched unless the
operator explicitly chooses isolation.

### Rank 4 — future semantic supplement

After an operator-approved Neovim >=0.13 migration, evaluate direct `CmdAtom`
capture or track-action.nvim for a semantic “what command completed” column in
the post-lesson ledger. Pin the source and define the event schema first. Store
it as advisory context beside the authoritative raw keylog and artifact hashes;
never replace the latter with normalized action counts. If the plugin is absent,
old, disabled, or reports no event, the tutor must continue using its current
baseline rather than treating the absence as a failed lesson.

## Proposed FAILURE_LOG paragraph (do not append here)

**VD-12 audit 3 — hint-plugin boundary (research/proposal, 2026-09-28):** A
review of current upstream screenkey.nvim, nvzone/showkeys, Hardtime, WhichKey,
mini.clue, Precognition, track-action.nvim, record-key.nvim, keys.nvim, and
keycasty found no display plugin that can replace the tutor's authoritative
Neovim `-w` capture plus effect-based grader. screenkey/showkeys/record-key are
keycasts without a stable grading/export contract; Hardtime changes behavior by
installing blocking expression mappings; WhichKey/mini.clue can expose exact
answers and install trigger mappings; Precognition pollutes fixed-width art with
virtual text/lines/signs; track-action is a promising semantic supplement only
on Neovim >=0.13 and still normalizes away evidence needed for exact method
grading. Proposal: keep plugins optional and operator-owned, use one clue aid
only in an explicit grammar primer, use screenkey only for demonstrations,
preserve configured Hardtime/WhichKey and other user plugins by default, require
explicit opt-in for any attempt-local isolation, and preserve
`-w`, scratch-Neovim effect checks, artifact checkpoints, and the two-column
post-lesson ledger as the sole authority. Stop before implementation pending
operator approval.
