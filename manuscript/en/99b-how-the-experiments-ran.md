# Appendix A. How the experiments were run

Each chapter gives the date, the tool, and the model with its numbers. This appendix gives the rest: how a session was started, what each repository held, what was counted, and how the hidden tests judged. A hidden test is a test the AI never sees, and I use it to decide whether a run's result is right.

## Three batches of runs

I ran the experiments in three batches.

- **2026-11-22, Claude Code 2.1.330.** In the small repositories, which hold each chapter's own listing, the model was Claude Opus 5.5 at its highest effort setting. I planned 10 sessions for each version of each experiment. Some stopped at 6 to 9 when the API credit for the month ran out, and each chapter says which. In the large repository, the models were Claude Haiku 5.5, Claude Sonnet 5.5, and Claude Opus 5.5 at their default settings.
- **2026-11-22 and 23, Codex CLI 0.171.0, OpenAI's coding agent.** The model was gpt-6.2-sol at its default setting.
- **2026-11-25, Claude Code 2.1.331.** The models were Claude Sonnet 5.5 and Claude Haiku 5.5 at their default settings for the combined experiment of Chapter 16, and the three Claude models at their default settings for the runs that the renewal of this book added.

## How a session was started

- **Claude Code** ran with `claude -p`, which runs one session without a person in the loop. User settings, hooks, connected servers, and the automatic memory were turned off. The session could read and edit files and run `python3`, `python`, `ls`, `cat`, `git`, `grep`, `find`, `head`, and `wc`. A command line that joined several commands sometimes ran `sed` and `echo` as well.
- **Codex CLI** ran with `codex exec`. My user settings and Codex's command rules were turned off, and so were web search, the browser, computer use, image generation, apps, multiple agents, goals, and tool suggestions. The sandbox let a session write inside the repository and not in `.git`, so no Codex session could commit.
- **Every run started from a fresh copy** of the starting repository, with one commit. Where an experiment needed a last commit to review, as in Chapter 15, a script made that commit before the session started. Codex sessions ran one at a time. Claude Code sessions ran up to eight at a time.
- **Rules files.** Codex reads `AGENTS.md`, and Claude Code 2.1.331 read `AGENTS.md` too. When a repository sat inside the temporary folder that Claude Code uses on my computer, Claude Code 2.1.331 loaded neither `AGENTS.md` nor `CLAUDE.md`, so I ran the combined experiment in folders under my home directory. No folder above a run held an instruction file. The small and large repositories of November 22 had no rules file.

## The repositories

- **Small repositories** hold one chapter's listing, sometimes with one or two additions that the chapter names.
- **The large repository** is a made-up shop with 518 Python files and 1,317 tests. I wrote the code that holds each chapter's trap. Claude Haiku 5.5 generated the other 210 modules, and I kept a module only if it imported and passed its own tests.
- **The two repositories of Chapter 16.** Repository A has 47 files and B has 55, about 3,400 lines each, with the same 259 visible tests. Codex built them, with a reference solution for each request, from a design I wrote. I checked that both repositories give the same answers to the same 926 calls, that every reference solution passes its hidden tests, and that 16 planted wrong solutions fail them.

## What was counted

- **Tool calls.** For Claude Code, each use of a tool: a file read, an edit, a search, or a shell command. For Codex, each shell command and each file edit. Codex 0.171.0 can run several commands inside one tool call, and each of those commands counts.
- **Files opened.** The files of the starting repository that a session read, with a read tool or with a shell command that prints a file (`cat`, `head`, `tail`, `nl`, `sed -n`). A wildcard such as `payments/*.py` counts every file it matches. A search with `grep`, `rg`, or a search tool doesn't count as opening a file.
- **Turns.** Claude Code's count of the model's replies in a session.
- **Tokens.** Everything the model read and wrote in a session, including the tokens it read from its cache.
- **Cost.** Claude Code's own estimate for each session. For November 22, the bill in Anthropic's console came to about 4% more than the sum of those estimates.

## How the hidden tests judged

- A hidden test runs outside the session, on the repository the session left behind.
- In Chapter 16, each request has two hidden tests. The first checks the new behavior the request asks for: it fails before the change and has to pass after it. The second runs 926 calls to the shop's outer functions and compares the answers with those of the unchanged repository. The calls that a request may change are listed for each request before any run.
- **A hidden test may ask only for what the request says, or for what the repository's own code already does in the same kind of case.** I checked all twenty requests of Chapter 16 against that rule. Two tests broke it, and I corrected them before counting.
  - R02's tests wanted the error code `email_blocked` and wanted an address at a subdomain accepted. The request names no error code and doesn't settle subdomains.
  - R13's test wanted `ValueError` for a threshold of `-1`. The shop's own code raises `StockError` for bad stock input.
  - Three demands passed the rule because the shop's code already settles them: `KeyError` for an unknown customer (R01), a card fee rounded down (R05), and `CouponError` for a bad coupon percentage (R10).
  - I ran each corrected test on both unchanged repositories, where the new-behavior test has to fail, and on the reference solutions, where it has to pass, before I judged any session with it. The verdicts of the original tests are kept.
- **Five outcomes.** I sort every run of Chapter 16 into one of five outcomes, decided before the runs of November 25: passed; the requested behavior failed; behavior the request didn't ask for changed; an output gained a key and nothing else changed; the session changed no file and asked before going on. A run whose output gained a key counts as failed, and the chapter also gives the count without those runs.
- Tests that a session ran could leave a `.pytest_cache` folder in the repository. I removed it before judging, as the hidden tests already ignore `__pycache__`.

## Amounts in the Korean edition

The Korean edition's listings use won. The experiments ran on the English code and prompts, so the amounts in experiment results are in cents in both editions.

## Limits

- I designed both versions of every repository and wrote every request, so each experiment tests my version of a habit.
- Ten runs per version can show a large difference and miss a small one (Chapter 16 works through the arithmetic).
- Every number belongs to the tool version and model named with it. The full tables, and runs on later models, are in the repository at `experiments/RESULTS.md`.
