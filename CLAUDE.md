# Project notes

## HyperFrames skills

Installed via `npx skills add heygen-com/hyperframes` (2026-07-31). This pulled in
the full HyperFrames bundle: 25 skills total, including `hyperframes`,
`hyperframes-cli`, `hyperframes-core`, `hyperframes-animation`,
`hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-registry`,
`media-use`, plus related video/motion skills (`general-video`,
`motion-graphics`, `motion-doctrine`, `cut-the-curve`, `seam-craft`,
`embedded-captions`, `captions-overlay`, `slideshow`,
`talking-head-recut`, `pr-to-video`, `product-launch-video`,
`faceless-explainer`, `music-to-video`, `changelog-video`, `figma`,
`oversized-cursor`, `remotion-to-hyperframes`).

- Actual skill files live under `.agents/skills/<name>/`.
- `.claude/skills/<name>` are symlinks into `.agents/skills/<name>` so
  Claude Code picks them up.
- `skills-lock.json` tracks installed versions — re-run
  `npx skills add heygen-com/hyperframes` to update.
- For any request to make, create, edit, animate, or render a video or
  motion graphic, `hyperframes` is the mandatory entry-point skill; it
  routes to the specialized workflow skills above.
- Committed and pushed on branch `claude/heygen-hyperframes-setup-ei5pu4`
  (commit `d86deae`, 943 files).
