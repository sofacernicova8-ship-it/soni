---
name: редактор
description: >
  Named shortcut/alias for the "hyperframes" skill in this project. Trigger this skill whenever the
  user says "редактор" (Russian for "editor"), or asks in any language to make, create, edit, animate,
  or render a video, animation, or motion graphic — promos, explainers, captioned clips, title cards,
  overlays, slideshows, Remotion ports, or any HyperFrames HTML composition. Also trigger it to
  inspect, diagnose, validate, preview, publish, or batch-render an existing HyperFrames project. Make
  sure to use this skill whenever the user says "редактор" even with no other context, since that word
  alone means "open the video editor and figure out what I need."
---

# редактор

This is a thin alias. It has no logic of its own — it exists only so the user can say
"редактор" and reliably land on the video/motion editing workflow.

When this skill triggers, immediately load and follow the `hyperframes` skill
(`.agents/skills/hyperframes/SKILL.md`). Treat its instructions as authoritative: it is the mandatory
entry point for HyperFrames work and routes to the specialized workflow skills
(`hyperframes-cli`, `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`,
`hyperframes-keyframes`, `hyperframes-registry`, `media-use`, and the domain skills like
`general-video`, `motion-graphics`, `product-launch-video`, etc).

Do not duplicate or second-guess `hyperframes`'s routing logic here — just defer to it.
If the user's message after "редактор" gives no further detail, follow `hyperframes`'s own
state table (project resume, brief detection, or the intent interview for a fresh request).
