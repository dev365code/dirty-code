# Results

This page holds the full tables behind the book's experiments. Each chapter's Evidence section gives the numbers that decide its claim, and Appendix A says how the sessions were run, what was counted, and how the hidden tests judged. When a new model is run, its tables are added here with their date.

The runs so far:

- 2026-11-22: Claude Code 2.1.330, with Claude Opus 5.5 at its highest effort setting in the small repositories, and Claude Haiku 5.5, Claude Sonnet 5.5, and Claude Opus 5.5 at their default settings in the large repository.
- 2026-11-22 and 23: Codex CLI 0.171.0, OpenAI's coding agent, with gpt-6.2-sol at its default setting.
- 2026-11-25: Claude Code 2.1.331, with Claude Sonnet 5.5 and Claude Haiku 5.5 at their default settings for Chapter 16, and the runs added in the renewal of the book.

## Chapter 16: the combined experiment

Twenty requests, two repositories, 10 fresh sessions each: 400 sessions per model. Files opened and tool calls are medians over the 10 runs. A run passes when both hidden checks pass, judged with the corrected checks that Appendix A describes. A run whose output gained a key and changed nothing else counts as failed.

### Codex CLI 0.171.0 with gpt-6.2-sol, 2026-11-23

| Request | Group | A passes | B passes | A: files opened, tool calls | B: files opened, tool calls | Runs that didn't pass |
|---|---|---|---|---|---|---|
| R01 Export emails without touching the cache (Ch. 4) | 1 | 10 | 10 | 5.5, 5 | 6, 6 |  |
| R02 Reject a throwaway email domain (Ch. 5) | 1 | 10 | 10 | 5, 5 | 2.5, 7 |  |
| R03 Thousands separators in the settlement report (Ch. 6) | 1 | 10 | 10 | 3.5, 6 | 3, 6.5 |  |
| R04 Clean up the payment constants (Ch. 7) | 1 | 0 | 10 | 10.5, 6 | 9, 7 | A: 10 other behavior changed |
| R05 A 3% fee on card payments (Ch. 8) | 1 | 10 | 10 | 4, 7 | 7, 7 |  |
| R06 Find the cause from the error line (Ch. 9) | 1 | 10 | 10 | 2, 6 | 3.5, 7 |  |
| R07 Say where a refund's amount is decided (Ch. 10) | 1 | 10 | 10 | 0, 2 | 1.5, 2 |  |
| R08 Free shipping, with a finish line (Ch. 11) | 1 | 10 | 10 | 7, 5 | 8, 7.5 |  |
| R09 An optional gift message on an order | 2 | 10 | 10 | 6, 6.5 | 5.5, 8.5 |  |
| R10 Percentage coupons | 2 | 10 | 10 | 6, 5.5 | 6, 6 |  |
| R11 Returns across a month boundary | 2 | 10 | 10 | 3.5, 5.5 | 4, 7 |  |
| R12 A daily sales summary | 2 | 10 | 10 | 9.5, 7.5 | 6.5, 7 |  |
| R13 A low-stock watch list | 2 | 10 | 10 | 5.5, 5 | 6, 7 |  |
| R14 Deactivate a customer | 2 | 10 | 10 | 5.5, 6.5 | 10.5, 7 |  |
| R15 An expiry date on coupons | 2 | 10 | 10 | 3, 6 | 5.5, 7 |  |
| R16 Let a customer turn off notifications | 2 | 10 | 10 | 5, 5 | 7, 8 |  |
| R17 A negative amount shown as `--2.77` | 3 | 10 | 10 | 3, 4.5 | 5, 6.5 |  |
| R18 A payment method with a confirmation step | 3 | 10 | 10 | 4, 6 | 9.5, 7 |  |
| R19 Change the sign-up messages while the server runs | 3 | 10 | 10 | 5.5, 6 | 3, 7 |  |
| R20 Settlement batches of 100 | 3 | 10 | 0 | 2, 5 | 4, 4 | B: 10 asked and stopped |
| Group 1 (Part II's prompts) | | 70 of 80 | 80 of 80 | | | |
| Group 2 (ordinary work) | | 80 of 80 | 80 of 80 | | | |
| Group 3 (chosen to favor A) | | 40 of 40 | 30 of 40 | | | |
| All | | 190 of 200 | 190 of 200 | 5, 6 | 6, 7 | |

### Claude Code 2.1.331 with Claude Sonnet 5.5, 2026-11-25

| Request | Group | A passes | B passes | A: files opened, tool calls | B: files opened, tool calls | Runs that didn't pass |
|---|---|---|---|---|---|---|
| R01 Export emails without touching the cache (Ch. 4) | 1 | 10 | 7 | 4, 4 | 9, 6.5 | B: 3 requested behavior failed |
| R02 Reject a throwaway email domain (Ch. 5) | 1 | 10 | 10 | 4, 4 | 4, 5 |  |
| R03 Thousands separators in the settlement report (Ch. 6) | 1 | 10 | 0 | 4, 4 | 2, 4 | B: 10 asked and stopped |
| R04 Clean up the payment constants (Ch. 7) | 1 | 0 | 10 | 5.5, 6 | 5, 8 | A: 10 other behavior changed |
| R05 A 3% fee on card payments (Ch. 8) | 1 | 10 | 10 | 6, 7.5 | 4.5, 6 |  |
| R06 Find the cause from the error line (Ch. 9) | 1 | 10 | 10 | 2, 5 | 2, 5 |  |
| R07 Say where a refund's amount is decided (Ch. 10) | 1 | 10 | 10 | 0.5, 4 | 2, 3 |  |
| R08 Free shipping, with a finish line (Ch. 11) | 1 | 10 | 10 | 6, 9 | 9, 8.5 |  |
| R09 An optional gift message on an order | 2 | 10 | 10 | 5.5, 9 | 6, 6 |  |
| R10 Percentage coupons | 2 | 10 | 10 | 3.5, 12 | 5, 5 |  |
| R11 Returns across a month boundary | 2 | 10 | 10 | 2.5, 7 | 2, 7 |  |
| R12 A daily sales summary | 2 | 7 | 9 | 12, 10.5 | 15, 12 | A: 3 gained a key; B: 1 gained a key |
| R13 A low-stock watch list | 2 | 10 | 10 | 3, 4.5 | 5, 5.5 |  |
| R14 Deactivate a customer | 2 | 10 | 10 | 9.5, 5 | 13, 10 |  |
| R15 An expiry date on coupons | 2 | 0 | 3 | 4, 11.5 | 6, 5 | A: 10 gained a key; B: 7 gained a key |
| R16 Let a customer turn off notifications | 2 | 10 | 10 | 7, 5.5 | 12.5, 4 |  |
| R17 A negative amount shown as `--2.77` | 3 | 10 | 10 | 3, 4 | 4, 10 |  |
| R18 A payment method with a confirmation step | 3 | 10 | 10 | 5.5, 6 | 7, 6.5 |  |
| R19 Change the sign-up messages while the server runs | 3 | 10 | 10 | 5, 5 | 6, 12 |  |
| R20 Settlement batches of 100 | 3 | 10 | 9 | 2, 5 | 3, 6 | B: 1 asked and stopped |
| Group 1 (Part II's prompts) | | 70 of 80 | 67 of 80 | | | |
| Group 2 (ordinary work) | | 67 of 80 | 72 of 80 | | | |
| Group 3 (chosen to favor A) | | 40 of 40 | 39 of 40 | | | |
| All | | 177 of 200 | 178 of 200 | 4, 6 | 5, 6 | |

### Claude Code 2.1.331 with Claude Haiku 5.5, 2026-11-25

| Request | Group | A passes | B passes | A: files opened, tool calls | B: files opened, tool calls | Runs that didn't pass |
|---|---|---|---|---|---|---|
| R01 Export emails without touching the cache (Ch. 4) | 1 | 10 | 5 | 12.5, 10.5 | 10, 10 | B: 5 requested behavior failed |
| R02 Reject a throwaway email domain (Ch. 5) | 1 | 10 | 10 | 6, 9 | 6, 8 |  |
| R03 Thousands separators in the settlement report (Ch. 6) | 1 | 10 | 0 | 5.5, 9 | 5, 4.5 | B: 10 asked and stopped |
| R04 Clean up the payment constants (Ch. 7) | 1 | 0 | 10 | 16, 13.5 | 9, 13 | A: 10 other behavior changed |
| R05 A 3% fee on card payments (Ch. 8) | 1 | 10 | 10 | 10.5, 9 | 8.5, 8 |  |
| R06 Find the cause from the error line (Ch. 9) | 1 | 10 | 10 | 4, 10 | 4, 7 |  |
| R07 Say where a refund's amount is decided (Ch. 10) | 1 | 10 | 10 | 1, 2 | 3, 3 |  |
| R08 Free shipping, with a finish line (Ch. 11) | 1 | 10 | 10 | 10, 9.5 | 9.5, 9.5 |  |
| R09 An optional gift message on an order | 2 | 10 | 10 | 9, 16 | 11.5, 14.5 |  |
| R10 Percentage coupons | 2 | 4 | 10 | 9.5, 10 | 8, 10 | A: 6 gained a key |
| R11 Returns across a month boundary | 2 | 10 | 10 | 4, 8.5 | 4, 10 |  |
| R12 A daily sales summary | 2 | 9 | 7 | 19.5, 13.5 | 19.5, 11 | A: 1 gained a key; B: 3 gained a key |
| R13 A low-stock watch list | 2 | 10 | 10 | 9, 9 | 7, 9.5 |  |
| R14 Deactivate a customer | 2 | 10 | 10 | 19, 12 | 19.5, 14 |  |
| R15 An expiry date on coupons | 2 | 0 | 0 | 8.5, 10 | 9, 11 | A: 10 gained a key; B: 10 gained a key |
| R16 Let a customer turn off notifications | 2 | 10 | 10 | 13.5, 9 | 16, 10 |  |
| R17 A negative amount shown as `--2.77` | 3 | 10 | 10 | 3, 8 | 6, 10 |  |
| R18 A payment method with a confirmation step | 3 | 10 | 10 | 10, 13.5 | 11.5, 12 |  |
| R19 Change the sign-up messages while the server runs | 3 | 10 | 10 | 8.5, 11 | 9.5, 9 |  |
| R20 Settlement batches of 100 | 3 | 10 | 9 | 5, 8.5 | 4.5, 6 | B: 1 asked and stopped |
| Group 1 (Part II's prompts) | | 70 of 80 | 65 of 80 | | | |
| Group 2 (ordinary work) | | 63 of 80 | 67 of 80 | | | |
| Group 3 (chosen to favor A) | | 40 of 40 | 39 of 40 | | | |
| All | | 173 of 200 | 171 of 200 | 9, 10 | 8, 10 | |

### Five outcomes

| Model, repository | Passed | Requested behavior failed | Other behavior changed | Gained a key | Asked and stopped |
|---|---|---|---|---|---|
| Codex, A | 190 | 0 | 10 | 0 | 0 |
| Codex, B | 190 | 0 | 0 | 0 | 10 |
| Sonnet, A | 177 | 0 | 10 | 13 | 0 |
| Sonnet, B | 178 | 3 | 0 | 8 | 11 |
| Haiku, A | 173 | 0 | 10 | 17 | 0 |
| Haiku, B | 171 | 5 | 0 | 13 | 11 |

## Runs added on 2026-11-25

Each of these was registered in `experiments/README.md` before it ran, with what it would count and how the result would be read.

### Chapter 7: the rules-file line, rewritten two ways

Repository B of Chapter 16, with only one line of its rules file changed. Passes out of 10. The original line stopped sessions on the batches of 100 (R20) and the thousands separators (R03). The cleanup (R04) and the negative amounts (R17) are controls: the cleanup has to keep 37 and 48, and the negative amounts have to change all three copies of the formatter. The two rewritten lines are printed in Chapter 7.

| Rules-file line | Model | R20 batches of 100 | R03 thousands separators | R04 cleanup, 37 and 48 kept | R17 negative amounts |
|---|---|---|---|---|---|
| The original line | Codex | 0 | 10 | 10 | 10 |
| The original line | Claude Sonnet 5.5 | 9 | 0 | 10 | 10 |
| First rewrite | Codex | 10 | 10 | 10 | 10 |
| First rewrite | Claude Sonnet 5.5 | 10 | 10 | 10 | 10 |
| Second rewrite | Codex | 10 | 10 | 10 | 10 |
| Second rewrite | Claude Sonnet 5.5 | 10 | 10 | 10 | 10 |

### Chapter 7: a cleanup that doesn't ask for round values

R04 with the words "and round values" taken out of the request. A run passes when it keeps 37 and 48 and changes nothing else that the request didn't ask for.

| Request | Model | A passes | B passes |
|---|---|---|---|
| With "round values" | Codex | 0 | 10 |
| With "round values" | Claude Sonnet 5.5 | 0 | 10 |
| Without | Codex | 10 | 10 |
| Without | Claude Sonnet 5.5 | 10 | 10 |

<!-- [Chapter 4 without the cache clause; Chapter 15's two cells] -->

## The other experiments

The full table of each of these is in its chapter's Evidence section.

| Experiment | Chapter | What it measures |
|---|---|---|
| E1 | 1 | What ten fresh sessions open and run before their first edit |
| E2 | 2 | Whether a rule settled in an earlier chat reaches a new session from a comment or the rules file |
| E3 | 4 | Whether a session calls a function that writes, under a short name and under a name that says what it writes |
| E4 | 5 | Whether a session finishes a rule spread over 1, 3, or 5 files |
| E5 | 6 | Whether a change for one caller of a shared function reaches the others, and a restocking fee across a shared rule and a copy |
| E6 | 7 | Whether a cleanup keeps two odd values with and without their reasons |
| E7 | 8 | Whether a session puts a card fee in the right place behind 0, 1, or 3 hops |
| E8 | 9 | What a session does with a short error line and with one that carries the values and the next step |
| E9 | 10 | How sessions find code in feature folders, with and without an index, and in generic files |
| E10 | 11 | What a session writes from a one-line prompt and from one with the rule and a finish line |
| E13 | 12 | A change given as one line, as one prompt with the whole plan, and as four pieces |
| E14 | 13 | Whether a session writes a gift card redemption that two requests can both pass, and whether it leaves a test for that |
| E12 | 14 | Whether a session changes an assertion to make a test pass, and whether its reports of failures match the real output |
| E15 | 15 | What a review finds when it is asked "Is this right?", "find bugs", or for a failing test that breaks the rule |
| E16 | 17 | Whether a session answers the 3 a.m. question right when a retry hides in a decorator |
| E11 | 18 | Small programs written and changed in Python, Rust, and assembly |
