# Chapter 16. The experiment: one feature, two engine bays

## Scene

A carmaker wants to settle an argument in its design office. One group says an engine bay should be laid out so that a mechanic can see and reach every part. The other group says the mechanic now starts with a scanner, so the bay should be laid out for the scanner: a sensor on every part, a port by the steering column, and everything else packed tight under covers.

So the company builds the same car twice. The engine, the top speed, and the fuel economy are the same. Only the engine bay differs. Then it breaks both cars in the same twenty ways and sends each broken car to ten garages that have never seen it.

Nobody in the design office judges the repairs. Each car comes back and is driven around a test track, and the track decides.

This book has made eight claims about code, one in each chapter of Part II. What does the test track for code look like?

## Claim

> To find out whether code arranged for an AI reader works better, build the same program twice, send both the same change requests in fresh sessions, and let tests the AI never sees decide.

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

Eight requests come from Part II, one from each chapter. They are those chapters' prompts, reworded where a prompt named a file: export the customers' emails without touching the cache, reject sign-ups from a throwaway email domain, put thousands separators in the amounts of the settlement report, clean up the payment constants, add a 3% fee to card payments, find the cause of a failed payment from its error line, say where the refund amount is decided, and add free shipping. In the chapters' own experiments each of these ran in a repository built around it. Here each runs with the other seven habits present.

One of the eight can't be the same in both repositories. The request from Chapter 9 pastes the error line that the server printed, and the two servers print different lines. Each repository gets its own line under the same sentence.

Eight requests are ordinary work that no chapter was built around: a new field on the order, a second coupon type, a bug in a date comparison, a new report. They are there to show whether the shape of the code matters on work that I didn't design as a trap.

Four requests are chosen to favor Repository A. One asks for a new money format in every place a customer sees an amount. In A that is one edit to the shared function. In B it is an edit to each copy. Another asks for a payment method that needs steps of its own, which A's classes were built for. Chapter 6 and Chapter 8 said that these are the cases where their advice costs something, and this group is where that cost is measured.

With 20 requests, 2 repositories, and 10 fresh sessions each, one model takes 400 sessions.

> **[Run record slot: combined experiment]** For two requests, one from each of the first two groups: what one session did in Repository A and what one did in Repository B, step by step. Date, tool, model.

## Evidence: 400 sessions per model, judged by hidden tests and reported request by request

For every session the experiment records the date, the tool and the model, the prompt, whether both hidden checks passed, the files the session opened, its tool calls, the tokens it used, and the time it took.

The results go in one table with a row for each request: passes out of 10 in A, and passes out of 10 in B. I will report them request by request for a reason. Ten runs can't separate two versions on a single request. If both versions pass a task 8 times in 10 over the long run, their counts in 10 runs each will still differ by 2 or more 39% of the time. A result of 9 passes against 7 is well within what chance alone produces. <!-- computed 2026-11-13: P(|X-Y|>=2) = 0.394 for two binomials n=10 p=0.8; Fisher exact two-sided p = 0.58 for 9/10 vs 7/10 -->

The totals can show more. If B passes 180 of its 200 runs and A passes 160 of 200, a gap that size would be unlikely with no real difference behind it. <!-- Fisher exact two-sided p = 0.007 --> That calculation treats the 200 runs as 200 separate trials, and they are 20 requests run 10 times each. So a difference in the totals counts only if it also shows up across the requests and doesn't come from two or three of them.

Three outcomes are possible, and I'll say which one happened.

Repository B may pass clearly more often in the first two groups. Then the habits in Part II pay off together, today, on this model.

The two repositories may pass about equally often. That would fit what Chapter 3 said: today's AI learned to code from code that people wrote, and it reads clean code well. Each chapter's claim would then be limited to the cases its own experiment isolates, and I would say so in each chapter.

Repository A may pass more often. Then some habit in B costs more than it gives, and the chapters' own experiments have to show which one.

The experiment hasn't been run. Whatever the outcome, the numbers will carry their date and model. I plan to run the same 400 sessions on a second model as well, to see whether the result belongs to one model's habits.

> **[Result slot: combined experiment]** Date, tool and model. One row per request: passes out of 10 in A and in B, runs that broke behavior the request didn't ask for, and the median files opened and tool calls. Totals for each of the three groups.

## What people do

My two repositories are a small shop that I built. Yours is the repository that matters to you, and your Git history already holds the material for the same experiment. The steps below replay a change your team has already made.

- [ ] Pick a merged change that added tests along with its fix. Write down the request that led to it in a sentence or two, the way you would have typed it to an AI. Don't use the commit message if it describes the solution.
- [ ] Make a copy of the repository as it was just before that change, and save the tests the change added. Those are your hidden tests.

  ```sh
  git worktree add ../replay <commit>~1
  git diff <commit>~1 <commit> -- <test files> > ../hidden.patch
  ```

- [ ] In `../replay`, give a fresh session your request. When it says it's done, apply the hidden tests and run them: `git apply ../hidden.patch`, then your test command. Write down pass or fail and the number of files the session opened. Reset the folder and repeat with a fresh session, ten times in all.
- [ ] Change one thing from Part II in a second copy: add the index file from Chapter 10, or move one rule into one file as in Chapter 5. Run the same request ten more times there.
- [ ] Compare the two rows of ten, and don't read much into a difference of one or two passes. Replay three or four different changes before you decide anything.

I ran the commands in the second and third steps on the repository from Chapter 12, with the commit for piece 3 as the past change. Before any work, the hidden test fails with `AssertionError: 3000 != 6000`. After the change, the run prints `Ran 7 tests` and `OK`. <!-- run 2026-11-13, Git 2.50.1, Python 3.9.6 -->

## Where it breaks

The numbers in this chapter will be a photograph with a date on it. A new model changes them. What stays is the method. I'll publish the two repositories and the twenty requests with the results, so that anyone can run the experiment again on the next model.

The shop is small. It has a few dozen files, and a session can read most of them before it writes. In a repository of 2,000 files, finding the code is a larger part of the work, and the differences in the table may matter more or less than they do here. That is why your own replay counts for more than my numbers.

I built both repositories and chose the requests, and I know which result I expect. The four requests that favor Repository A are there to push against that. They don't remove it.

Hidden tests judge what the code does. They don't judge whether the person who is woken at 3 a.m. can follow Repository B. Chapter 17 is about that person.

Replaying history has limits of its own. If your repository is public, a model may have seen the real fix during training. And a request written after the fact can give away more than the original one did. Change requests that are still open don't have either problem, and you can save their tests as hidden tests from now on.
