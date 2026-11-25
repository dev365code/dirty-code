# Chapter 16. The experiment: one feature, two engine bays

## Scene

A carmaker wants to settle an argument in its design office. One group says an engine bay should be laid out so that a mechanic can see and reach every part. The other group says the mechanic now starts with a scanner, so the bay should be laid out for the scanner: a sensor on every part, a port by the steering column, and everything else packed tight under covers.

So the company builds the same car twice. The engine, the top speed, and the fuel economy are the same. Only the engine bay differs. Then it breaks both cars in the same twenty ways and sends each broken car to ten garages that have never seen it.

Nobody in the design office judges the repairs. Each car comes back and is driven around a test track, and the track decides.

This book has made eight claims about code, one in each chapter of Part II. What does the test track for code look like?

## Claim

> Built twice and sent the same twenty requests, the version arranged for an AI reader passed about as often as the clean one, and the two lost different requests: one changed a value whose reason was written nowhere, and one stopped to ask because of a line in its rules file.

<!-- Claim draft for the owner, 2026-11-25. Before: "To find out whether code arranged for an AI reader works better, build the same program twice, send both the same change requests in fresh sessions, and let tests the AI never sees decide." -->

## Why: a fresh session has never seen the task, so the same task can be given to the same reader ten times

Advice about code has mostly been argued from experience, because it is hard to test on people. You can't give one developer the same task twice. The second time, the developer remembers the first. You can give the task to two developers, and then you are comparing the developers as much as the code.

An AI can be tested in a way a person can't. A fresh session has no memory of the last run, so the same task can go to the same reader ten times, or a hundred, and every time is the first time. Chapter 2 counted that lack of memory as a cost. Here it is what makes the experiment possible.

Each chapter in Part II has an experiment of its own that changes one habit and holds the rest still. A real repository has all the habits at once. Their effects could add up. They could cancel each other out. They could vanish once the repository is large enough that finding the code is the hard part. So one more experiment puts all of Part II into one repository and compares it with a repository that has none of it.

Two rules of the experiment come from earlier chapters. Tests the AI never sees judge the result, because a session that can see a test can make the test pass without making the code right (Chapter 14). And every request runs at least ten times, because one run can be luck. Suppose a session gets a certain task right 8 times in 10 over the long run. Ten runs of that task will show exactly 8 passes only 30% of the time. They will show 6 or fewer 12% of the time, and all 10 passing 11% of the time. <!-- computed 2026-11-13, binomial n=10 p=0.8 -->

## Code: the same shop in two repositories, different in eight ways and equal in what it does

The "code" in this chapter is two repositories. Both hold the shop's order server from the earlier chapters: orders, payments, refunds, shipping, settlement, and users. Repository A is the version for people. Repository B is the version for AI. The table lists the eight differences. Each row is the example from its chapter.

| Chapter | Repository A, for people | Repository B, for AI |
|---|---|---|
| 4 | The lookup that also fills a cache is named `get_user` | The same function is named `get_user_and_fill_cache` |
| 5 | The sign-up email rule is spread over `settings.py`, `validation.py`, and `users.py` | The rule is inside `register` |
| 6 | Seven callers share one `format_amount` | The settlement report and the refund export each have their own copy |
| 7 | `APPROVE_TIMEOUT_SEC = 37`, with no comment | The same value under a comment that starts `# 37, not 30 or 40:` |
| 8 | Payment fees sit behind `strategy_for` and three classes | A fee table sits next to `checkout_total` |
| 9 | Errors say what failed | Errors carry a code, the values, `where=`, and `next=` |
| 10 | `services/`, `utils/`, and `models.py` | A folder for each thing the shop does, and `INDEX.md` |
| 11 | A rules file with one line about clean code | The rules file from Chapter 11 |

Everything else is the same, and the experiment checks that it is. Function names differ between the two repositories, so the tests can't call the inner functions. They go through the shop's outer functions, the ones that place an order, cancel it, refund it, sign up a user, and build the payout report. Those have the same names in both. Before any request is sent, both repositories must return the same answers to the same calls and pass the same visible tests.

Each request then gets two hidden checks. The first is the new behavior the request asks for. It fails before the change and has to pass after it. The second is everything the request didn't ask for. It passes before the change and has to keep passing.

## Prompt: the same twenty requests go to both repositories, in three groups

Each request is sent to a clean copy of Repository A and a clean copy of Repository B, in the same words. No request names an existing file or function, because those names differ between the two.

The twenty requests fall into three groups.

Eight requests come from Part II, one from each chapter. They are those chapters' prompts, reworded where a prompt named a file: export the customers' emails without touching the cache, reject sign-ups from a throwaway email domain, put thousands separators in the amounts of the settlement report, clean up the payment constants, add a 3% fee to card payments, find the cause of a rejected coupon from its error line, say where the refund amount is decided, and add free shipping. Each chapter's own experiment tests its habit in a repository built around that one habit. Here each runs with the other seven habits present.

One of the eight can't be the same in both repositories. The request from Chapter 9 pastes the error line that the server printed, and the two servers print different lines. Each repository gets its own line under the same sentence. The failure behind the line is also different from Chapter 9's. A timed-out approval leaves no bug for a test to catch, so in both repositories I planted a coupon that is turned away at exactly its minimum.

Eight requests are ordinary work that no chapter was built around: a new field on the order, a second coupon type, a bug in a date comparison, a new report. They are there to show whether the shape of the code matters on work that I didn't design as a trap.

Four requests are chosen to favor Repository A. One asks to fix how negative amounts are shown, a mistake in the arithmetic that all three formatters share. In A that is one edit to the shared function. In B it is an edit to each of the three copies, and a copy the session misses prints the wrong amount. Another asks for a payment method that needs a step of its own, which A's classes were built for. The other two come from the places where Chapters 5 and 7 say their advice breaks: translators who change the sign-up messages while the server runs, and a batch limit that the provider has raised while B's reason comment still gives the old one. Chapters 5 through 8 said that these are the cases where their advice costs something, and this group is where that cost is measured.

With 20 requests, 2 repositories, and 10 fresh sessions each, one model takes 400 sessions.

On 2026-11-23 I ran all 400 with Codex CLI, OpenAI's coding agent, with gpt-6.2-sol, and on 2026-11-25 I ran them again with Claude Code and two Claude models. Here is one Codex session per repository on two of the requests.

The first is Chapter 7's cleanup of the payment code. In Repository A, the session listed the files, printed the rules file, the payment modules in `services/`, the money helpers, and two test files, and searched for `37`, `48`, and the names of the constants. Then it edited five files. It renamed the constants, deleted the unused provider URL and retry delay, changed `APPROVE_TIMEOUT_SEC = 37` to `APPROVAL_TIMEOUT_SECONDS = 40`, changed the settlement batch size from 48 to 50, and edited two tests to expect 40 and 50. Its report said that it had "rounded the approval timeout from 37 to 40 seconds and the settlement batch size from 48 to 50 orders." All 259 visible tests passed. In Repository B, the session printed `INDEX.md` first, as B's rules file says to, then everything in the `payments` folder, renamed the constants and two functions, and deleted the same leftovers. It kept 37. Its report said it had kept "the documented 37-second timeout, which leaves three seconds to record the timeout before the provider closes the connection." In B the batch size sits in the `settlement` folder, and the session didn't open it.

The second is an ordinary bug: a customer who bought on November 30 was refused a return on December 1. In both repositories the session searched for the return check, printed it with its tests, changed the date comparison to count calendar days, checked the reported dates, and ran the tests. It took 7 tool calls in A and 8 in B, one of them to read `INDEX.md`. Both reports said that a purchase on November 30 can now be returned through December 7.

## Evidence: with three models both repositories passed about equally often, and each lost a different request

For every session the experiment records the date, the tool and the model, the prompt, whether both hidden checks passed, the files the session opened, its tool calls, the tokens it used, and the time it took.

I report the results request by request for a reason. Ten runs can't separate two versions on a single request. If both versions pass a task 8 times in 10 over the long run, their counts in 10 runs each will still differ by 2 or more 39% of the time. A result of 9 passes against 7 is well within what chance alone produces. <!-- computed 2026-11-13: P(|X-Y|>=2) = 0.394 for two binomials n=10 p=0.8; Fisher exact two-sided p = 0.58 for 9/10 vs 7/10 -->

The totals can show more. If B passes 180 of its 200 runs and A passes 160 of 200, a gap that size would be unlikely with no real difference behind it. <!-- Fisher exact two-sided p = 0.007 --> That calculation treats the 200 runs as 200 separate trials, and they are 20 requests run 10 times each. So a difference in the totals counts only if it also shows up across the requests and doesn't come from two or three of them.

Three outcomes are possible, and I'll say which one happened.

Repository B may pass clearly more often in the first two groups. Then the habits in Part II pay off together, today, on this model.

The two repositories may pass about equally often. That would fit what Chapter 3 said: today's AI learned to code from code that people wrote, and it reads clean code well. Each chapter's claim would then be limited to the cases its own experiment isolates, and I would say so in each chapter.

Repository A may pass more often. Then some habit in B costs more than it gives, and the chapters' own experiments have to show which one.

Two rules decided how a run counts. The first is that a hidden check may ask only for what the request says, or for what the shop's own code already does in the same kind of case. I wrote that rule down after the Codex runs, when two of my checks turned out to ask for more, and I applied it to every model's runs. Appendix A lists the three things it corrected and how I checked each correction. The corrections turned 40 failed runs into passes with Codex, 40 with Sonnet, and 38 with Haiku. The second rule, set before the Claude runs, is that every run falls into one of five outcomes: it passed, the requested behavior failed, behavior the request didn't ask for changed, an output gained a key and nothing else changed, or the session changed no file and asked before going on. A run whose output gained a key counts as failed.

I ran the 400 sessions three times: on 2026-11-23 with Codex CLI and gpt-6.2-sol, and on 2026-11-25 with Claude Code and two Claude models at their default settings, Claude Sonnet 5.5 and Claude Haiku 5.5. The full table for each model, request by request, with the files opened and the tool calls, is in the repository at `experiments/RESULTS.md`.

| Group | Codex, A | Codex, B | Sonnet, A | Sonnet, B | Haiku, A | Haiku, B |
|---|---|---|---|---|---|---|
| 1. Part II's prompts (80 runs) | 70 | 80 | 70 | 67 | 70 | 65 |
| 2. Ordinary work (80 runs) | 80 | 80 | 67 | 72 | 63 | 67 |
| 3. Chosen to favor A (40 runs) | 40 | 30 | 40 | 39 | 40 | 39 |
| All (200 runs) | 190 | 190 | 177 | 178 | 173 | 171 |

| Model, repository | Passed | Requested behavior failed | Other behavior changed | Gained a key | Asked and stopped |
|---|---|---|---|---|---|
| Codex, A | 190 | 0 | 10 | 0 | 0 |
| Codex, B | 190 | 0 | 0 | 0 | 10 |
| Sonnet, A | 177 | 0 | 10 | 13 | 0 |
| Sonnet, B | 178 | 3 | 0 | 8 | 11 |
| Haiku, A | 173 | 0 | 10 | 17 | 0 |
| Haiku, B | 171 | 5 | 0 | 13 | 11 |

Thirteen of the twenty requests passed 10 times in 10 in both repositories with all three models. Here are the other seven, with passes out of 10.

| Request | Codex, A and B | Sonnet, A and B | Haiku, A and B | What the runs that failed did |
|---|---|---|---|---|
| R01 Export emails without touching the cache (Ch. 4) | 10, 10 | 10, 7 | 10, 5 | Raised another error than the shop's `KeyError` for an unknown customer, such as `LookupError` |
| R03 Thousands separators in the settlement report (Ch. 6) | 10, 10 | 10, 0 | 10, 0 | Stopped and asked |
| R04 Clean up the payment constants (Ch. 7) | 0, 10 | 0, 10 | 0, 10 | Changed the 37-second approval timeout |
| R10 Percentage coupons | 10, 10 | 10, 10 | 4, 10 | Added `kind: "fixed"` to the details of the existing coupons |
| R12 A daily sales summary | 10, 10 | 7, 9 | 9, 7 | Added a `day` key to the summary |
| R15 An expiry date on coupons | 10, 10 | 0, 3 | 0, 0 | Added `expires_on: null` to coupons that have no expiry date |
| R20 Settlement batches of 100 | 10, 0 | 10, 9 | 10, 9 | Stopped and asked |

That is the second of the three outcomes, with all three models. The totals of A and B differ by at most two runs in 200, and each repository's main loss came from one place: in A, a value with no reason written next to it, and in B, one line of its rules file.

- Repository A lost the cleanup of the payment constants (R04) with every model, all ten times. Every session changed the 37-second approval timeout: Codex to 40, Sonnet to 30, and Haiku to 30 or 40. Nothing in A says why 37 was chosen. This is the failure Chapter 7 predicts.
- Repository B lost to a line in its own rules file, the line Chapter 7 had recommended: "Don't change a value whose comment gives a reason. If you think the reason is out of date, tell me and wait." With Codex, all ten sessions stopped on the batches of 100 (R20), although the request gave the new limit and its reason. With Sonnet and Haiku, all ten sessions stopped on the thousands separators (R03), because the settlement report's copy of the formatter says that the accountant sets its format. One Sonnet session asked, "Please confirm the accountant has signed off on the new format." In a real session you would answer, and the change would likely follow. The hidden check counts what the session did, and it changed nothing. Chapter 7 tells this story and tests two rewritten lines.

The Claude models also failed in a way Codex didn't. Some sessions added a key to an output, such as `expires_on: null` on a coupon with no expiry date, and left every value that was there before unchanged. These runs count as failures, by the rule set before the runs. Counted as passes, they would make the totals 190 and 186 for Sonnet, and 190 and 184 for Haiku. And in Repository B, 3 Sonnet and 5 Haiku sessions raised another error than `KeyError` for an unknown customer, where the shop's existing lookups raise `KeyError`. No session in A did that, and I can't tell from the runs what in B led them there.

The work went different ways with different models. With Codex, the median session in B used about a fifth more tokens than in A, 101,000 against 83,000, counting the ones the model read from its cache, and made 7 tool calls against 6. Every Codex session in B printed `INDEX.md`, as B's rules file tells it to. With Sonnet, the median session in B used fewer tokens, 119,000 against 131,000. With Haiku the two were about the same, 232,000 in B and 228,000 in A.

So with three models, the eight habits together didn't make Repository B pass more often. They decided which requests failed. A lost the request that touched a value with no reason written next to it. B lost requests that its own rules file told the session to stop on. By what I wrote above, this outcome limits each chapter's claim to the cases its own experiment isolates, and each chapter now says so.

## What people do

My two repositories are a small shop that I built. Yours is the repository that matters to you, and your Git history already holds the material for the same experiment. The steps below replay a change your team has already made.

- [ ] Pick a merged change that added tests along with its fix. Write down the request that led to it in a sentence or two, the way you would have typed it to an AI. Don't use the commit message if it describes the solution.
- [ ] Make a copy of the repository as it was just before that change, without its Git history, and save the tests the change added outside the copy. Those are your hidden tests. A worktree or a clone would bring the history along, and a session could read the change and its tests there.

  ```sh
  mkdir ../replay && git archive <commit>~1 | tar -x -C ../replay
  git -C ../replay init -q && git -C ../replay add -A && git -C ../replay commit -q -m start
  git diff <commit>~1 <commit> -- <test files> > ../hidden.patch
  ```

- [ ] In `../replay`, give a fresh session your request. When it says it's done, apply the hidden tests and run them: `git apply ../hidden.patch`, then your test command. Write down pass or fail and the number of files the session opened. Reset the folder and repeat with a fresh session, ten times in all.
- [ ] Change one thing from Part II in a second copy: add the index file from Chapter 10, or move one rule into one file as in Chapter 5. Run the same request ten more times there.
- [ ] Compare the two rows of ten, and don't read much into a difference of one or two passes. Replay three or four different changes before you decide anything.

I ran the commands in the second and third steps on the repository from Chapter 12, with the commit for piece 3 as the past change. Before any work, the hidden test fails with `AssertionError: 3000 != 6000`. After the change, the run prints `Ran 7 tests` and `OK`. <!-- run 2026-11-22 with git archive, Git 2.50.1, Python 3.9.6 -->

## Where it breaks

The numbers in this chapter belong to the three models and the dates named with them, and a new model will change them. The method can be run again on the next model: I'll publish the two repositories and the twenty requests with the results.

The shop is small. It has a few dozen files, and a session can read most of them before it writes. In a repository of 2,000 files, finding the code is a larger part of the work, and the differences in the table may matter more or less than they do here. That is why your own replay counts for more than my numbers.

I built both repositories and chose the requests, and I know which result I expect. The four requests that favor Repository A are there to push against that. They don't remove it.

Hidden tests judge what the code does. They don't judge whether the person who is woken at 3 a.m. can follow Repository B. Chapter 17 is about that person.

Replaying history has limits of its own. If your repository is public, a model may have seen the real fix during training. And a request written after the fact can give away more than the original one did. Change requests that are still open don't have either problem, and you can save their tests as hidden tests from now on.
