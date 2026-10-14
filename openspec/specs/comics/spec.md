# comics

## Purpose

`comics.macron.dev` is where future comics land: short strips that explain
practical development topics, built by AI in Tillandsias forges.

## Requirements

### Requirement: One folder per episode

Each episode SHALL live in its own folder, holding:
- the strip itself;
- a text transcript of the strip;
- a "do it yourself" guide for the topic it covers;
- provenance links (sources, the forge session or commit that produced it).

### Requirement: Flutter + Flame

Strips SHALL be built with Flutter + Flame.

### Requirement: Extremely subtle animation

Animations SHALL be extremely subtle, and triggered only by a tap, a drag or a
timer.

### Requirement: Every strip has a text transcript

Every strip SHALL ship with a text transcript, so its content does not depend
on the art or the animation.

### Requirement: Comics follow the character canon

The art guidelines are the character canon,
`assets/Tlatoāni + Mācron cannon guidelines.md`. Every strip SHALL follow it,
and SHALL pass its Visual QA and Scene QA checklists (§45–47). Generated art
SHALL stay `reference` until a human promotes it (§42–44).

### Requirement: Episodes are distilled from lessons

Each episode SHALL retell one lesson from `public/lessons/`, preferring the
highest-ranked ones, and SHALL link back to it. An episode is scripted first,
panel by panel, in `plan/comics-backlog.yaml` (`lesson`, `panels`, and a
`punchline` that lands on the second read). Any agent with an image tool can
then draw a scripted episode. The lesson's dialogue lines are a starting
point, not a constraint.

#### Scenario: A lesson rises to the top

- WHEN a lesson's rank puts it among the top lessons and no episode retells it
- THEN an agent adds a scripted episode for it to the backlog, and a later
  agent with an image tool draws it.
