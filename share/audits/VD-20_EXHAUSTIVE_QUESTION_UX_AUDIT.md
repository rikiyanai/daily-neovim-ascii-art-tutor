# VD-20 exhaustive learner-facing curriculum audit

Snapshot: live checkout and installed curriculum at 2026-09-28 18:09 EDT. The
JSON is revision 2026-09-28.24: 19 modules, 174 cards, 326 questions. This is
the current generated course, not the older 169-card/.23 snapshot named in
the operator's failure.

Scope and method

I inspected every card and every question record, then exercised the live
question renderer and the installed client-attached popup in isolated
temporary state at 80x24. No runtime, generator, test, curriculum, or
operator state was edited; this report is the only repository file written.

The question table below records every question. Codes:

- form: MC multiple choice, TK typed keys, DEC decode, PA predict art, CMP
  complete, WHY explanation.
- response/template is Y/Y for visible input instructions plus a worked
  example or non-leaking response template. All 326 currently pass this
  narrow interface check. The template for MC/PA is the visible a-d option
  list; open-text forms receive runtime answer-format guidance.
- variants: Y = accepted variants are reasonably inferable; P = partly
  inferable from the blank/grammar but the accepted synonym set is hidden; N
  = the grader's accepted term groups are not displayed.
- blank/invalid is Y when blank or invalid input is rejected with a specific
  next action. MC/PA reprompt with allowed letters; open text reprompts blank
  and typed-key notation reports the concrete rejection.
- wrong held is G(grammar breakdown)/E(example in the held result)/L(hidden
  answer leak). G0/E0 means a choice result only replays selected/correct
  rationale, not a grammar/example. G1/E0 means the held page replays grammar
  but no example. L1 identifies a hidden typed-key card whose pre-clear
  wrong-answer path prints its exact sample answer; the held page then clears
  it. This is still a leak in the live path.
- A<n> is the measured pre-input visual row count at 68 cells (the inner
  width of an 80-column popup), using the current renderer and a 20-row
  popup. RISK means the question is likely to scroll the input or prior
  context off a compact popup once its route header/check context is included.
  Predict-art and the other open-text rows fit this question-only threshold;
  all 39 typed-key prompts overflow. The 102 MC rows marked RISK are used in
  the module-check bank, which adds context rows; many also overflow their
  concept route.

Summary findings

- Pairing/placement is complete structurally: all 174 cards have one paired
  question; 153 paired questions are before and 19 are after. The remaining
  154 questions are the multiple-choice module banks.
- Forms: 190 MC, 40 DEC, 39 TK, 19 PA, 19 WHY, 19 CMP.
- Response instructions/templates: 326/326. Accepted-variant inferability:
  248 Y, 19 P (CMP), 59 N (DEC/WHY).
- Blank/invalid handling: 326/326 has an actionable path. This is a
  runtime-level result, not a claim that each author supplied a visible
  accepted-term list.
- Wrong held-result quality: 209 G0/E0/L0, 98 G1/E0/L0, 19 G1/E0/L1.
  Thus no held result has both grammar and a worked example. More seriously,
  the 19 hidden transfer TK questions expose the exact expected key sequence
  through ONE WORKING ANSWER before the held page clears.
- Compact pre-input risk: 141 rows are marked RISK (102 MC plus all 39 TK);
  the exact counts are in the table. This is a renderer/layout defect, not
  an authoring defect: long q text is emitted as raw terminal lines and
  wraps/scrolls in the 68-cell inner popup.

Evidence

- Question input and invalid handling: share/v2_runtime.py:545-576 and
  748-807.
- Runtime answer-format guidance: share/v2_runtime.py:719-746. The guidance
  is deliberately non-leaking before input, but wrong open-text answers then
  print the contract sample at lines 797-803.
- Held wrong-result render: share/v2_runtime.py:1782-1884 and
  1906-2010. The held question replay calls grammar breakdown but does not
  print an example.
- Card/question inventory is share/curriculum-v2.json revision .24. The
  runtime validator is share/v2_runtime.py:55-286.

Exact operator failure and compact popup reproduction

The durable learner ledger records the exact failure at
~/.local/state/vim-daily/events-v2.jsonl:34-36: M0.P0.P01, revision .23,
placement before, raw answer "", question fail, card fail reason
concept-answer, and remediation Q-M0.P0. The empty answer explains the
operator's report that there was no usable answer format/example.

At the current .24 snapshot, an isolated 80x24 client-attached popup shows
M0.P0.P01 with an explicit one-sentence ANSWER FORMAT and a different-command
EXAMPLE before input. A wrong answer produces a held grammar breakdown and
the page remains readable. The historical garbled text in the operator's
message is not stored in the ledger, so that exact prior pixels cannot be
reconstructed from repository evidence. A current compact reproduction of the
route-control transition does show a related defect: after sending n, the
newly opened M0.P0 popup retains the old wrapped prompt line and echoed n above
the new lesson, e.g. “press Enter to close · r then Enter = repeat this lesson · n then”
followed by “Enter = next lesson now n”. This is the same stale/garbled
held-prompt class at 80x24.

Post-result route controls

The current normal popup now displays “press Enter to close · r then Enter =
repeat this lesson · n then Enter = next lesson now”. I exercised r in a
compact isolated popup and it reopened M0.P0, so r is live for the normal
popup route. Enter closes the final held page.

The remaining n behavior is not the requested “next eligible/due normally”:

- n calls bin/vim-daily-gate's --force loop. On a failed current card,
  next_card returns that same unpassed card, so n repeats the failed card
  rather than moving to another eligible item. A compact isolated failure
  followed by n reopened M0.P0.
- --force sets explicit_force, so a due spaced review is bypassed instead of
  being selected normally.
- active remediation rows are displayed but next_card does not consume the
  remediation queue. n therefore is not a due/eligible scheduler.
- The visible wording says “next lesson now”, which accurately describes the
  force behavior but not the requested due-normal semantics.

Route matrix:

| post-result route | Enter | r | n |
|---|---|---|---|
| pass guided/hidden/transfer/module | close after held progress | practice repeat path | force next_card; can bypass review |
| fail paired question/concept | close | repeat current unpassed card | same failed current card |
| fail module check | close | repeat current unpassed card | same failed current card |
| fail artifact/method | page advance, then close | current card / practice repeat | force next_card |
| review pass/fail | close | practice changed-art review | force next_card, bypasses due review |
| remediation scheduled | close | repeats owning card | remediation queue ignored |

The route plumbing is in bin/vim-daily-gate:843-868 and 1023-1058;
card selection is share/v2_runtime.py:492-531 and 2932-3058.

Per-question exhaustive record


| QID | card | form | place | response/template | variants | blank/invalid | wrong held | compact 68-cell pre-input |
|---|---|---:|:---:|:---:|:---:|:---:|:---:|---:|
| M0.Q01 | M0.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M0.Q02 | M0.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M0.Q03 | M0.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M0.Q04 | M0.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M0.Q05 | M0.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M0.Q06 | M0.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M0.Q07 | M0.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M0.Q08 | M0.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M0.Q09 | M0.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M0.Q10 | M0.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A16 RISK |
| M0.P0.P01 | M0.P0 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M1.Q01 | M1.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M1.Q02 | M1.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M1.Q03 | M1.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M1.Q04 | M1.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M1.Q05 | M1.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M1.Q06 | M1.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M1.Q07 | M1.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M1.Q08 | M1.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M1.Q09 | M1.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M1.Q10 | M1.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M2.Q01 | M2.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M2.Q02 | M2.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M2.Q03 | M2.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M2.Q04 | M2.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M2.Q05 | M2.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M2.Q06 | M2.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M2.Q07 | M2.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M2.Q08 | M2.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A10 OK |
| M2.Q09 | M2.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M2.Q10 | M2.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M3.Q01 | M3.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M3.Q02 | M3.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M3.Q03 | M3.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M3.Q04 | M3.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M3.Q05 | M3.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M3.Q06 | M3.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A23 RISK |
| M3.Q07 | M3.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M3.Q08 | M3.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M3.Q09 | M3.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M3.Q10 | M3.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A22 RISK |
| M4.Q01 | M4.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M4.Q02 | M4.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M4.Q03 | M4.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M4.Q04 | M4.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A15 RISK |
| M4.Q05 | M4.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M4.Q06 | M4.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M4.Q07 | M4.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M4.Q08 | M4.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M4.Q09 | M4.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M4.Q10 | M4.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M5.Q01 | M5.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M5.Q02 | M5.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M5.Q03 | M5.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M5.Q04 | M5.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M5.Q05 | M5.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M5.Q06 | M5.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M5.Q07 | M5.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A22 RISK |
| M5.Q08 | M5.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M5.Q09 | M5.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M5.Q10 | M5.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M6.Q01 | M6.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M6.Q02 | M6.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M6.Q03 | M6.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M6.Q04 | M6.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M6.Q05 | M6.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M6.Q06 | M6.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A26 RISK |
| M6.Q07 | M6.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M6.Q08 | M6.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A10 OK |
| M6.Q09 | M6.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M6.Q10 | M6.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M7.Q01 | M7.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A30 RISK |
| M7.Q02 | M7.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A10 OK |
| M7.Q03 | M7.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A31 RISK |
| M7.Q04 | M7.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M7.Q05 | M7.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M7.Q06 | M7.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A23 RISK |
| M7.Q07 | M7.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M7.Q08 | M7.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M7.Q09 | M7.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M7.Q10 | M7.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A29 RISK |
| M8.Q01 | M8.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M8.Q02 | M8.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M8.Q03 | M8.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M8.Q04 | M8.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M8.Q05 | M8.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M8.Q06 | M8.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M8.Q07 | M8.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M8.Q08 | M8.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M8.Q09 | M8.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M8.Q10 | M8.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M9.Q01 | M9.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M9.Q02 | M9.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M9.Q03 | M9.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A16 RISK |
| M9.Q04 | M9.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M9.Q05 | M9.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A15 RISK |
| M9.Q06 | M9.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M9.Q07 | M9.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M9.Q08 | M9.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M9.Q09 | M9.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M9.Q10 | M9.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M10.Q01 | M10.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M10.Q02 | M10.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M10.Q03 | M10.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M10.Q04 | M10.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M10.Q05 | M10.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M10.Q06 | M10.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M10.Q07 | M10.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M10.Q08 | M10.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A15 RISK |
| M10.Q09 | M10.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M10.Q10 | M10.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M11.Q01 | M11.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M11.Q02 | M11.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M11.Q03 | M11.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M11.Q04 | M11.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M11.Q05 | M11.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M11.Q06 | M11.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A16 RISK |
| M11.Q07 | M11.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M11.Q08 | M11.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M11.Q09 | M11.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M11.Q10 | M11.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M12.Q01 | M12.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M12.Q02 | M12.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M12.Q03 | M12.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M12.Q04 | M12.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M12.Q05 | M12.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M12.Q06 | M12.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A15 RISK |
| M12.Q07 | M12.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M12.Q08 | M12.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M12.Q09 | M12.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M12.Q10 | M12.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M13.Q01 | M13.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A16 RISK |
| M13.Q02 | M13.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M13.Q03 | M13.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M13.Q04 | M13.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A10 OK |
| M13.Q05 | M13.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M13.Q06 | M13.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M13.Q07 | M13.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A24 RISK |
| M13.Q08 | M13.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M13.Q09 | M13.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M13.Q10 | M13.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M14.Q01 | M14.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M14.Q02 | M14.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M14.Q03 | M14.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M14.Q04 | M14.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M14.Q05 | M14.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M14.Q06 | M14.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M14.Q07 | M14.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M14.Q08 | M14.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A15 RISK |
| M14.Q09 | M14.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M14.Q10 | M14.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M15.Q01 | M15.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M15.Q02 | M15.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A15 RISK |
| M15.Q03 | M15.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M15.Q04 | M15.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A15 RISK |
| M15.Q05 | M15.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M15.Q06 | M15.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M15.Q07 | M15.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M15.Q08 | M15.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M15.Q09 | M15.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M15.Q10 | M15.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M16.Q01 | M16.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M16.Q02 | M16.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M16.Q03 | M16.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M16.Q04 | M16.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M16.Q05 | M16.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M16.Q06 | M16.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M16.Q07 | M16.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A21 RISK |
| M16.Q08 | M16.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M16.Q09 | M16.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M16.Q10 | M16.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M17.Q01 | M17.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A23 RISK |
| M17.Q02 | M17.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M17.Q03 | M17.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A24 RISK |
| M17.Q04 | M17.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A15 RISK |
| M17.Q05 | M17.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M17.Q06 | M17.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A24 RISK |
| M17.Q07 | M17.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A16 RISK |
| M17.Q08 | M17.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M17.Q09 | M17.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M17.Q10 | M17.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A26 RISK |
| M18.Q01 | M18.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A20 RISK |
| M18.Q02 | M18.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M18.Q03 | M18.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A18 RISK |
| M18.Q04 | M18.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M18.Q05 | M18.03 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M18.Q06 | M18.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A19 RISK |
| M18.Q07 | M18.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M18.Q08 | M18.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A12 OK |
| M18.Q09 | M18.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A11 OK |
| M18.Q10 | M18.07 | MC | B | Y/Y | Y | Y | G0/E0/L0 | A17 RISK |
| M0.01.P01 | M0.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A19 RISK |
| M0.02.P01 | M0.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M0.O.P01 | M0.O | TK | B | Y/Y | Y | Y | G1/E0/L0 | A22 RISK |
| M0.04.P01 | M0.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M0.T.P01 | M0.T | DEC | B | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M0.05.P01 | M0.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M0.SL.P01 | M0.SL | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M0.06.P01 | M0.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A19 RISK |
| M0.08.P01 | M0.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A9 OK |
| M1.01.P01 | M1.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A19 RISK |
| M1.02.P01 | M1.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M1.DD.P01 | M1.DD | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M1.04.P01 | M1.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M1.05.P01 | M1.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M1.06.P01 | M1.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A19 RISK |
| M1.08.P01 | M1.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A9 OK |
| M2.01.P01 | M2.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A21 RISK |
| M2.02.P01 | M2.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M2.04.P01 | M2.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A13 OK |
| M2.05.P01 | M2.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M2.06.P01 | M2.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A20 RISK |
| M2.08.P01 | M2.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A10 OK |
| M3.01.P01 | M3.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A25 RISK |
| M3.02.P01 | M3.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M3.CI.P01 | M3.CI | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M3.04.P01 | M3.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M3.05.P01 | M3.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M3.REG.P01 | M3.REG | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M3.06.P01 | M3.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A31 RISK |
| M3.DI.P01 | M3.DI | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M3.08.P01 | M3.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A10 OK |
| M4.01.P01 | M4.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A25 RISK |
| M4.02.P01 | M4.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M4.VB.P01 | M4.VB | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M4.04.P01 | M4.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M4.05.P01 | M4.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M4.06.P01 | M4.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A28 RISK |
| M4.08.P01 | M4.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A10 OK |
| M5.01.P01 | M5.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A27 RISK |
| M5.02.P01 | M5.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M5.04.P01 | M5.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M5.05.P01 | M5.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M5.06.P01 | M5.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A27 RISK |
| M5.08.P01 | M5.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A11 OK |
| M6.01.P01 | M6.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A23 RISK |
| M6.02.P01 | M6.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M6.D.P01 | M6.D | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M6.04.P01 | M6.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M6.05.P01 | M6.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M6.MOVE.P01 | M6.MOVE | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M6.06.P01 | M6.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A33 RISK |
| M6.08.P01 | M6.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A10 OK |
| M7.01.P01 | M7.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A48 RISK |
| M7.02.P01 | M7.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M7.DOT.P01 | M7.DOT | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M7.MAC.P01 | M7.MAC | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M7.VIS.P01 | M7.VIS | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M7.04.P01 | M7.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M7.GLOBAL.P01 | M7.GLOBAL | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M7.05.P01 | M7.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A10 OK |
| M7.06.P01 | M7.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A33 RISK |
| M7.08.P01 | M7.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A10 OK |
| M8.01.P01 | M8.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A23 RISK |
| M8.02.P01 | M8.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M8.04.P01 | M8.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M8.05.P01 | M8.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M8.06.P01 | M8.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A23 RISK |
| M8.08.P01 | M8.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A10 OK |
| M9.01.P01 | M9.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A19 RISK |
| M9.02.P01 | M9.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M9.04.P01 | M9.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M9.05.P01 | M9.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M9.06.P01 | M9.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A19 RISK |
| M9.08.P01 | M9.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A10 OK |
| M10.01.P01 | M10.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A19 RISK |
| M10.02.P01 | M10.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M10.04.P01 | M10.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M10.05.P01 | M10.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M10.06.P01 | M10.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A19 RISK |
| M10.08.P01 | M10.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A10 OK |
| M11.01.P01 | M11.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A19 RISK |
| M11.02.P01 | M11.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M11.UR.P01 | M11.UR | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M11.04.P01 | M11.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M11.05.P01 | M11.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M11.06.P01 | M11.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A19 RISK |
| M11.VE.P01 | M11.VE | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M11.08.P01 | M11.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A12 OK |
| M12.01.P01 | M12.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A19 RISK |
| M12.02.P01 | M12.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M12.FIND.P01 | M12.FIND | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M12.04.P01 | M12.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M12.05.P01 | M12.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M12.06.P01 | M12.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A19 RISK |
| M12.08.P01 | M12.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A11 OK |
| M13.01.P01 | M13.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A19 RISK |
| M13.02.P01 | M13.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M13.BE.P01 | M13.BE | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M13.04.P01 | M13.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M13.05.P01 | M13.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M13.06.P01 | M13.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A19 RISK |
| M13.08.P01 | M13.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A11 OK |
| M14.01.P01 | M14.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A22 RISK |
| M14.02.P01 | M14.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M14.04.P01 | M14.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M14.PARA.P01 | M14.PARA | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M14.05.P01 | M14.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M14.06.P01 | M14.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A21 RISK |
| M14.08.P01 | M14.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A12 OK |
| M15.01.P01 | M15.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A20 RISK |
| M15.02.P01 | M15.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M15.04.P01 | M15.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M15.BA.P01 | M15.BA | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M15.05.P01 | M15.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M15.06.P01 | M15.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A19 RISK |
| M15.08.P01 | M15.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A11 OK |
| M16.01.P01 | M16.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A23 RISK |
| M16.02.P01 | M16.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M16.04.P01 | M16.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M16.05.P01 | M16.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M16.06.P01 | M16.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A23 RISK |
| M16.08.P01 | M16.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A11 OK |
| M17.01.P01 | M17.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A31 RISK |
| M17.02.P01 | M17.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M17.04.P01 | M17.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M17.05.P01 | M17.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M17.06.P01 | M17.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A31 RISK |
| M17.08.P01 | M17.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A12 OK |
| M18.01.P01 | M18.01 | TK | B | Y/Y | Y | Y | G1/E0/L0 | A22 RISK |
| M18.02.P01 | M18.02 | DEC | B | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M18.04.P01 | M18.04 | PA | B | Y/Y | Y | Y | G0/E0/L0 | A14 OK |
| M18.EXPR.P01 | M18.EXPR | DEC | B | Y/Y | N | Y | G1/E0/L0 | A11 OK |
| M18.05.P01 | M18.05 | WHY | A | Y/Y | N | Y | G1/E0/L0 | A12 OK |
| M18.06.P01 | M18.06 | TK | B | Y/Y | Y | Y | G1/E0/L1 | A21 RISK |
| M18.08.P01 | M18.08 | CMP | B | Y/Y | P | Y | G1/E0/L0 | A11 OK |
