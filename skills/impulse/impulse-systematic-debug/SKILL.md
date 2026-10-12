---
name: impulse-systematic-debug
description: "Disciplined bug hunting instead of changing code at random — use whenever there is an OBSERVED failure to explain: \"this is broken\", failing or flaky test, heisenbug, prod incident cause-finding, regression, \"worked yesterday\", wrong output. Triggers: \"/impulse-debug\", \"debug\", \"bug\", \"broken\", \"not working\", \"почини баг\", \"найди баг\", \"баг\", \"не работает\", \"сломалось\", \"почему падает\", \"плавающий баг\", \"отладка\". Inspecting a diff with no observed failure = impulse-review."
---

# impulse-systematic-debug

Random edits until it works is not debugging — it's gambling that leaves the
real cause live. **The one rule that matters: fix only after you can
reproduce the bug and name its cause in one sentence.** Output is a fix plus
proof it fixed the named cause — not "seems fine now." Use this for ANY
observed failure — failing or flaky test, prod incident, regression, perf,
build, integration — and especially when the pressure is loudest ("just one
quick fix"): that is exactly when guessing costs the most and the loop pays
off fastest.

## The loop — do not skip steps

1. **Reproduce.** A reliable repro is the whole game. Nail down the exact
   inputs/state/timing that trigger it. Can't reproduce → the job right now is
   building a repro (add logging, shrink inputs), NOT guessing a fix.
2. **Observe, don't assume.** Read the actual error/stack/logs. Quote them
   exact. The bug is almost never where you first think — confirm with data.
3. **Bisect the search space.** Halve it each step: `git bisect` for "worked
   yesterday", binary-search the pipeline for "where does the value go wrong",
   comment-halve for "which line". Turn N suspects into log₂N checks.
4. **Hypothesize explicitly.** Write the hypothesis before testing it: "I
   think X because Y; if true, changing Z shows W." Keep a running log — a
   killed hypothesis is progress, not waste. A hunt that outlives the
   session (heisenbug, flaky test, spans days): persist the log to
   `.impulse/memory/sessions/` (shared/memory.md) — re-deriving killed
   hypotheses is the expensive part of resuming.
5. **Smallest fix at the root.** Fix the cause, not the symptom. No drive-by
   refactor, no "while I'm here." One bug, one minimal change.
6. **Prove it.** Re-run the repro → gone. Add a regression test that FAILS
   without the fix (RED first — see `impulse-backend/references/testing.md`). "Can't
   repro anymore" without a test is not proof. Then run the full suite, not
   just the one test — a fix that greens the repro and reddens something else
   isn't a fix.

### Building the repro — the loop is the work

When no clean repro exists, constructing one IS the job; guessing a fix
instead is the failure this skill exists to prevent. Try, roughly in order:

1. A failing test at the seam that reaches the bug (unit / integration / e2e).
2. An HTTP script / curl against a running dev server.
3. A CLI invocation with fixture input, diffing stdout/stderr against expected.
4. A headless-browser script (Playwright/Puppeteer) asserting on DOM, console or network.
5. Replay a captured trace: HAR, request payload, event log, queue message, webhook body.
6. A throwaway harness that boots the smallest useful slice and calls the failing path.
7. A property/fuzz loop when the bug is intermittent wrong output over a broad input space.
8. A bisection harness fit for `git bisect run` when the bug appeared between two known states.
9. A differential loop comparing old vs new, two configs, two providers, two datasets.
10. Human-in-the-loop only as a last resort — script the human steps so the loop stays structured.

Once it exists, tighten it on three axes: **faster** (cache setup, narrow
scope, skip unrelated init), **sharper signal** (assert the exact symptom, not
generic success), **more deterministic** (pin time, seed randomness, isolate
the filesystem, freeze the network).

For a non-deterministic bug the immediate goal is a higher reproduction rate,
not perfection: run the trigger 100x, parallelize, add stress, narrow the
timing window, inject sleeps. A 50% flake is debuggable; a 1% flake usually
is not — get the rate up before you dig.

Techniques per bug class (heisenbug, flaky test, race, leak, works-on-my-
machine, prod-only): `references/techniques.md`.

## Hard rules

1. **Reproduce before you fix.** If you can't trigger it on demand, you can't
   know you fixed it. Building the repro IS the work. The repro's bar: one
   command, deterministic, fast, agent-runnable, ALREADY RUN at least once —
   until that exists, hypothesis work hasn't started.
2. **Read the error before touching code.** Quote it exact. Guessing past the
   stack trace wastes the cheapest clue you have.
3. **One change at a time.** Batch edits hide which one worked and add new
   bugs. Change, test, keep or revert.
4. **Name the cause in one sentence** before fixing. Can't name it → you're
   symptom-patching; keep bisecting.
5. **Every fix ships a regression test** that fails without it. Non-negotiable
   for anything that reached a human.
6. **Revert your debug scaffolding.** Temp logs/prints/sleeps come out before
   the fix ships. Tag every scaffold line with one session marker
   (`[DEBUG-a4f2]`) — cleanup becomes one grep instead of a memory test.
7. **Three failed fixes = stop fixing, question the architecture.** At that
   point it's not a failed hypothesis — the component's design is likely
   wrong for the problem. The signals: each fix reveals new shared
   state/coupling in a *different* place, fixes demand "massive refactoring"
   to land, each fix spawns new symptoms elsewhere. Escalate to
   `impulse-brainstorm`/an ADR instead of a fourth patch.
8. **Debug spiral (conversation-level, distinct from rule 7's fix-level
   trigger — from ayghri/i-have-adhd, MIT):** if the last three turns were
   all "still broken," stop iterating on code entirely. In place of a fourth
   variation, name the assumption most likely wrong, out loud, and ask the
   user ONE diagnostic question. Guessing faster is not the fix for
   guessing wrong; rule 7 fires on failed fixes to the same bug, this one
   fires on the conversation pattern regardless of whether each attempt
   counted as a distinct "fix."

## Method notes

Extra moves that don't fit the six steps but earn their place:

- **Minimize the repro.** Once the loop is red, shrink it to the smallest
  scenario that still goes red — cut inputs, callers, config, data and steps
  ONE at a time, re-running after each cut. Keep only what's load-bearing;
  done when removing any remaining element turns the loop green. That minimal
  repro is usually the cleanest regression test. This is delta-debugging by
  hand (same ddmin principle as `git bisect`, applied to inputs not commits).
- **Instrument every component boundary.** In a multi-component system
  (API → service → db, CI → build → deploy), before proposing fixes, log what
  enters and exits EACH boundary and verify config/env propagation. Run once
  to see WHERE it breaks, THEN investigate only that component. A component
  that didn't fail is not the bug.
- **Trace the bad value upstream.** Don't stop where it surfaced — find where
  it originated and what handed it the bad value, then fix at the source, not
  at the symptom.
- **Diff against a working analogue.** Find similar working code in the same
  codebase, read the reference implementation COMPLETELY (don't skim), then
  list every difference however small — "that can't matter" is exactly how you
  miss the cause.
- **Rank 3-5 falsifiable hypotheses before testing any.** Rank by likelihood
  and cheapness to falsify; each must make a testable prediction ("if X is the
  cause, changing or observing Y makes Z happen"). Discard any with no
  prediction. If the user is present, show the ranked list — domain knowledge
  can re-rank it instantly.
- **Prefer a breakpoint to a print.** With a debugger/REPL available, one
  breakpoint beats ten logs; tag any log you do add with the session marker
  (rule 6) so cleanup stays one grep.
- **Say "I don't understand X" out loud** rather than pretending — an honest
  unknown is cheaper than a guessed fix. Research it or ask, don't bluff.
- **Delegate a read-only investigation** when the search spans many files or
  components: hand a subagent the exact error, file and repro command, and a
  goal of "report findings, do NOT fix yet". It localizes the fault without
  you spending the context to read everything yourself.

## Red flags — stop and re-enter the loop

When any of these surface in your own reasoning, you are gambling, not
debugging:

- "Quick fix for now, investigate later."
- "Just try changing X and see if it works."
- "Add a few changes, run the tests."
- "It's probably X, let me fix that."
- "I don't fully understand, but this might work."
- "Skip the test, I'll verify by hand."
- "One more fix attempt" — after two already failed.
- Each fix reveals a new problem somewhere else.

Every one of these means: back to step 1, keep bisecting.

## Boundaries

- Unfamiliar/legacy code where you don't yet understand the system →
  `impulse-legacy` first (characterization tests, blast radius), then debug.
- Live prod incident (mitigate-first, then RCA) → `impulse-devops`
  incident-response section; this skill owns the RCA/cause-finding half.
- Test-writing craft (flakiness roots, RED phase) →
  `impulse-backend/references/testing.md`.
- "stop impulse" / "normal mode": revert to default behavior.

## Before you finish

- Can you reproduce the bug on demand, right now, with one command?
- Can you name the cause in one sentence, backed by an actual error/log/stack
  trace you quoted?
- Did you change one thing at a time, not a batch of edits?
- Does a new regression test fail without your fix and pass with it?
- Does the full suite still pass — no fresh breakage from the fix?
- Is all debug scaffolding (temp logs/prints/sleeps) removed or tagged for
  cleanup?

If any answer is no: the core rule still stands — no fix ships until you can
reproduce and name the cause.
