# Failure Log

## VD-01 · 2026-09-20 — touch typing was incorrectly framed as separable

- GitHub issue: https://github.com/rikiyanai/daily-neovim-ascii-art-tutor/issues/1
- Intended product: hourly drills should make Vim skill and typing reliability
  stronger through the same meaningful ASCII-art authoring practice loop.
- Observed mismatch: treating touch typing as a separate track would reproduce
  the failure mode of generic typing platforms and generic Vim trainers: filler
  material with no reason to care, which makes the routine easy to abandon.
- User correction: touch typing practice belongs inside the Vim/ascii-art drill
  itself. Drills should bias toward motions, operators, counts, text objects,
  and common command combos on meaningful Stone Story-style art.
- Required successor: add live feedback or a trailing typed-history surface
  during the drill, then add quick quizzes, repeated practice, and milestones
  around conceptual handles such as Vim's count-verb-object grammar.
- Acceptance remains open until progress can report typing reliability and Vim
  operation gains without splitting them into separate products or modes.
