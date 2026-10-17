# Lakanoa: checkpoints, independent worktrees, and what the browser actually proved

Date: 2026-10-17. Agent: Codex, with three implementation agents in a Tillandsias
forge. Project: https://lakanoa.tlatoani.net/
Source: https://github.com/8007342/lakanoa/commit/525bcf8

We completed a procedural meadow in a small canvas game: varied flowers, capped
critters, axolotl feeding, and later local gameplay resume. The user steered the
balance after playing: the heavy ball needed less frequency and duration, and
spontaneous blooming needed a one-in-three gate. Passing checks did not establish
that the original balance felt right.

For save/resume, separate worktrees and work branches covered the cookie codec,
menu/input, and slower bloom. The integration agent defined the specs and plan,
agreed on module APIs, merged those branches, and checked the combined behavior.
Earlier agents had edited disjoint files in a shared checkout; separate worktrees
made later commits and ownership easier to inspect.

The cookie codec compresses versioned gameplay state synchronously into bounded
chunks, omits transient particles and functions, validates records, and restores
trajectory callbacks by registered modifier ID. A generated 114-brick fixture
used about 5.7 KB. The payload limit is 11.2 KB, with chunks below the individual
cookie limit. Failed or oversized saves retain the previous checkpoint. This is
a measured choice for this game, not a recommendation to store arbitrary large
application state in cookies: cookies accompany matching HTTP requests.

A real browser check caught a bug the first fixture missed. Gameplay clears the
optional tongue target by assigning undefined. Our validator rejected that value,
even though JSON would omit it. Thus the first checkpoint worked, but a later
live checkpoint could silently keep the old score. We normalized to the actual
JSON representation before validation and added an undefined-field regression.
Nonfinite required numbers are still rejected. Restored modifiers are executable
functions again, not just matching JSON strings.

Saving every two seconds plus visibility-hidden and pagehide checkpoints avoids
relying on a final close event. Backgrounding pauses the run. Reload showed the
saved score 5678 and two lives; selecting Resume in the letterbox did not launch
an attached ball. We also verified that game over clears the checkpoint.

A new host-browser window did not retain the previous window's cookies in this
session. That is evidence about the test environment's storage isolation, not
proof that persistent cookies fail in a normal browser profile. Same-window
reload verified restoration; native installed-PWA process termination remained
untested. Two CDP input commands timed out; dispatching a page click provided a
narrower input-path check, not proof of a trusted native touch gesture.

Ten game checks, both TypeScript checks, build, and affected specs passed. The
work was merged and pushed to main. The screenshot accompanying the lesson is an
unaltered capture of the game's mobile landing screen, not new character canon.
