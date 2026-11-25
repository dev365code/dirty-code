# Dirty code patterns: what each one looks like, what it costs, and how far it was tested

This list gathers the patterns of Chapters 2 to 18 in one place. Each entry shows what the pattern looks like, what a new session gets from it, and what a person pays for it. Then it says how the pattern relates to *Clean Code*, how far this book's experiments back it, and where not to use it.

For the relation to *Clean Code*, "same" means *Clean Code* gives the same advice, and "extends" means this book adds to that advice. "Differs" means this book's advice goes another way. "New" means *Clean Code* doesn't take up the question. As I read it, that is usually because its reader remembered yesterday and could ask a colleague.

The evidence line gives one deciding number, with its experiment. "Pays off" means the version with the pattern did better in that experiment. "No difference yet" means both versions did equally well, so the pattern may still pay off under conditions the chapter names. Each chapter gives the date, the tool, and the model, and Appendix A gives how the sessions were run.

## 1. Yesterday's rule, written where the next session reads it (Chapter 2)

```python
    # Partial refunds: split what the customer paid across the items by
    # list price, round each share down to the cent, and add any leftover
    # cents to whichever item is refunded last.
```

- The session gets the rule your team settled, which it would otherwise write for itself.
- A person pays for one more line to keep current when the rule changes.
- *Clean Code*: new.
- Evidence: pays off. With the rule in no file, all 10 Codex sessions refunded a three-item order differently from the rule. With the rule in a comment or in the rules file, all 20 followed it (E2).
- Not for a script you will run once and delete.

## 2. A name that says what the function writes (Chapter 4)

```python
def get_user_and_fill_cache(user_id):
```

- Every line that calls the function shows the write.
- A person pays for a longer name, and for a rename across the repository.
- *Clean Code*: same. A name that hides a side effect misleads.
- Evidence: no difference yet when the prompt named the write to avoid: 0 of 140 sessions called the writing function under either name (E3). When the prompt didn't mention the cache, Claude Haiku 5.5 filled it in 9 of 10 sessions under the short name and 5 of 10 under the long one, and Sonnet, Opus, and Codex filled it in none.
- Not for a write nobody else reads, such as logging.

## 3. The lines one change touches, kept in one function (Chapter 5)

```python
    if email.endswith("@throwaway.example"):
        return rejected("email_blocked", "Use a different email address.")
```

- The check, the value, and the message sit in the function the session's search finds.
- A person pays for a longer function, and someone in operations can no longer change the value in a settings file.
- *Clean Code*: differs. Its small functions and classes would split the rule up.
- Evidence: pays off in one case. In a repository of 518 files with the rule spread over five files, Claude Sonnet 5.5 left out the message in 4 of 10 runs. Every other model and layout passed every run (E4).
- Not for a rule every handler must share, such as who is logged in.

## 4. Its own copy for a caller whose output someone else decides (Chapter 6)

```python
# Own copy of format_amount on purpose: the accountant sets this format.
def report_amount(cents):
```

- A change made for the accountant can't reach the six other callers, whether or not the session searched for them.
- A person pays for fixing a bug in the shared arithmetic once in each copy.
- *Clean Code*: differs. Don't repeat yourself.
- Evidence: mixed. No session broke another caller in 80 runs with either version, and with one shared function 22 of 40 sessions gave it a switch that only one caller uses (E5).
- Not for a rule two places must agree on, such as the refund and the payout deduction.

## 5. A reason comment that repeats the value (Chapter 7)

```python
# 48, not 50: the provider's settlement call rejects more than 48 IDs.
SETTLE_BATCH_SIZE = 48
```

- The session reads a reason that lives outside the code, here at the payment provider.
- A person pays for updating the comment in the same commit as the value.
- *Clean Code*: differs in one detail. It counts a comment that warns of consequences as a good one, and it calls a comment that repeats the code redundant. This comment repeats the value on purpose, so a reader can see when the comment and the code drift apart.
- Evidence: pays off when a cleanup asks for round values. In the combined experiment, all 30 cleanups of the version without the reasons changed the 37-second timeout, with three models, and none of the 30 in the version with the reasons and the rules-file line did (R04). In the small repository of E6, the reasons alone kept the values in all 9 runs. Without the words "round values" in the request, none of 40 Codex and Sonnet sessions changed it, with or without the reasons.
- Not for a value anyone would expect, such as a 2-second wait between retries.

## 6. A rules-file line that says when it doesn't apply (Chapters 7, 11, and 16)

```text
- Don't change a value whose comment gives a reason. If you think
  the reason is out of date, tell me and wait. When the request names
  that value and gives its new value, change the value and its comment
  in the same edit. A general request, such as a cleanup, doesn't count.
```

- The session knows when to stop and ask, and when the request has already answered the question.
- A person pays for testing the line on requests that should and shouldn't stop the session.
- *Clean Code*: new.
- Evidence: the line without its last two sentences cost the version for AI in the combined experiment. All 10 Codex sessions stopped and asked on a request that gave the new value and its reason, and all 10 Sonnet and all 10 Haiku sessions stopped on another. With the last two sentences added, Codex and Sonnet each passed all 40 runs of those two requests and two controls.
- Not for a value with no reason comment. The line protects only what a comment explains.

## 7. A table in place of classes that differ in one number (Chapter 8)

```python
FEE_RATE_PERCENT = {"card": 0, "bank": 0, "gift": 0}
```

- The number has no hops in front of it, and the other methods' values sit on the same line.
- A person pays for bringing a class back on the day card payments need code of their own.
- *Clean Code*: differs. It prefers polymorphism to code that switches on a type.
- Evidence: no difference yet. At 0, 1, and 3 hops, all 120 sessions put the fee on the card and nowhere else (E7).
- Not for classes whose code really differs, or a layer through which a test passes in a fake.

## 8. An error line with a code, the values, and the next step (Chapter 9)

```text
PaymentError: PAY-0303 approval request timed out | where=payments.charge | order_id=1042 amount_cents=1500 timeout_sec=3 | next=do not retry; call provider.lookup() first to see if the charge went through
```

- From the line alone, the session knows which order to check and what to check first, and one search for `PAY-0303` finds the one `raise` that writes it.
- A person pays for updating `where=` and `next=` when the code or the procedure changes, and for keeping names and card numbers out of the line.
- *Clean Code*: extends. Give an exception enough context to find where and why it failed.
- Evidence: pays off in the report. All 100 Codex sessions fixed their failure with either line. With the long line, all 10 reports on the timeout named order 1042 as the order to check, and with the short line, 39 of 50 reports said the line couldn't show what had happened in production (E8).
- Not for values a person must not see, such as card numbers, names, or tokens.

## 9. Exit codes and check results that reach the log (Chapter 9)

```sh
cmd; rc=$?; echo "name $(basename "$f") rc=$rc"
```

- The session reads what the command really returned, in text its tools can reach.
- A person pays nothing, once the line is written this way.
- *Clean Code*: new.
- Evidence: I ran it. The one-line form `cmd; echo "name $(basename "$f") rc=$?"` records the exit code of `basename`, which is 0, whatever `cmd` returned. No session experiment measured this pattern.
- Not for a result that only a browser shows. Print it to the log as well.

## 10. Names and descriptions inside the files, and a one-page index (Chapter 10)

```text
- settlement/  The accountant's payout report. A refund here must match
               refunds/refund_amount.py to the cent.
```

- A search for the words of a question hits the right function, and the index says which folders have to agree.
- A person pays for updating the index in the same commit that moves a folder.
- *Clean Code*: same for names inside files, which should reveal intent. The index is new.
- Evidence: a small difference. With generic file names and no module descriptions, Claude Haiku 5.5 found the code in 38 of 40 answers and Claude Sonnet 5.5 in 39, against 40 of 40 with feature folders. Feature folders with module descriptions saved 0.6 to 0.9 tool calls per question, and the index another 0.1 to 0.4 (E9).
- Not for framework folders you can't rename. Describe them in the index.

## 11. A prompt with the owner's rule and a finish line with examples (Chapter 11)

```text
Rule: shipping is free when the customer paid $50.00 or more after
the coupon (order.paid >= 5000). Otherwise it stays $5.00.
```

- The session writes the shop's rule, not the reading it would choose for itself.
- A person pays for deciding the rule before sending the prompt.
- *Clean Code*: new.
- Evidence: pays off. Given `Add free shipping for orders over $50.`, all 9 Claude Opus 5.5 sessions wrote the same reading, and it wasn't the shop's rule. With the rule in the prompt, all 16 wrote the shop's rule (E10).
- Not for a typo fix, where writing the rule takes longer than the fix.

## 12. A plan file with a check for each piece and the owner's open questions (Chapter 12)

```text
Piece 4. refunds.py: full_refund_amount counts quantities.
         Check: new test: two keyboards at 3000, whole order back -> refund 6000.
         Returning one keyboard of two needs a rule from the owner. It waits.
```

- A fresh session starts from the file and knows where its piece ends.
- A person pays for writing the list, correcting it, and running each check.
- *Clean Code*: new.
- Evidence: no difference in passing: all 30 Codex runs passed in every form. A difference in what came back: all 10 sessions given the whole plan reported the case that waits for the owner, against none of the 10 with the one-line prompt (E13).
- Not for a change one command can check, such as a rename across the repository.

## 13. A guarantee in one sentence, and a test that puts a second request in the gap (Chapter 13)

```text
Guarantee: a gift card never pays out more than was loaded onto it,
even when two requests for the same card arrive at the same moment.
```

- The session gets what must never happen, in the shop's words, and a test that keeps checking it after the session ends.
- A person pays for slower sessions, a median of 14 minutes with the sentence against 7 without it, and for deciding what not to guarantee.
- *Clean Code*: new.
- Evidence: pays off in what stays behind. Every Claude Opus 5.5 session wrote safe code with or without the sentence. With the sentence, all 20 sessions left a two-request test in the repository, against 1 of 10 without it (E14).
- Not for data that may be a minute old, such as a "customers also bought" list.

## 14. A worktree for each session, and files staged by name (Chapter 13)

```text
- Work only in your own worktree, on your own branch.
- Stage files by name. Don't run git add -A or git commit -a.
```

- One session's half-written change can't end up in another session's commit.
- A person pays for merging one branch at a time and running the tests after every merge.
- *Clean Code*: new.
- Evidence: I ran it with plain Git commands in place of sessions. In one shared folder, `git add -A` put the other session's half-written function into the commit. Separate worktrees kept the two apart. Two branches that each passed their tests merged without a conflict into code that failed on import.
- Not for two sessions that only read.

## 15. A test you have watched fail on the old code and on a planted wrong answer (Chapter 14)

```text
1. Revert only the implementation you just changed.
2. Make partial_refund_amount return 2500.
```

- The session leaves you a test that has been seen to fail, not only a pass.
- A person pays for two or three more test runs per change, and for reading the failure messages.
- *Clean Code*: extends. A test written first fails first. This adds the planted wrong answer.
- Evidence: the method is the point. No session weakened an assertion (0 of 16 runs with Claude Opus 5.5, 0 of 20 with Codex, E12), and the chapter shows by hand that a weakened assertion and a fixed implementation both print `OK`.
- Not for a check that can't fail, such as a linter set up to check zero files. Fix the check first.

## 16. A reviewer asked to break the rule, with a failing test as the answer (Chapter 15)

```text
Find an order and a sequence of returns for which
partial_refund_amount breaks this rule. Give me the order, the
returns, what the function returns for each, and what the rule says.
Write it as a test that fails.
```

- The finding arrives as something you can run with one command.
- A person pays for writing the rule into the prompt, for one more session per change when the reviewer is a fresh one, and for running every finding before acting on it.
- *Clean Code*: new.
- Evidence: pays off with Codex. Asked `Is this right?`, all 10 sessions that wrote the change began with yes and gave no order that shows the defect. With this prompt, a failing test came back in all 10 reviews by a fresh session and in all 10 by the session that wrote the change (E15). A fresh session asked whether the change was right gave an order in 9 of 10 answers, and left the verdict to the refund policy in all 9.
- Not for a typo fix. Two reviewers cost more than the change.

## 17. A short list of code a person must be able to read, written for a person (Chapter 17)

```python
    # One request and no retry, on purpose. A timeout means the reply was late.
    # It doesn't mean the card wasn't charged, and a second request can charge it again.
```

- On the night of an outage, the person who has to decide can follow everything that happens to the money in one function, in order.
- A person pays for reading every change to the listed files, and for keeping the list short.
- *Clean Code*: same. Small, readable code for a person.
- Evidence: no difference yet in what the sessions said. All 76 sessions answered the 3 a.m. question right, with the retry hidden in a decorator and without it (E16). The list exists for the person who answers for the decision.
- Not for half the repository. A list that long means reading everything again.

## 18. Source kept for the checks that attach to it (Chapter 18)

```rust
pub fn refund_share(price: u64, paid: u64, list_total: u64) -> u64 {
```

- The compiler refuses a caller that passes the wrong type, in every file, on every build.
- A person pays for a stricter language, which matters less when an AI does the writing.
- *Clean Code*: new.
- Evidence: in ten small programs, Codex sessions changed the assembly as reliably as the Rust, 10 of 10 each (E11). What the assembly lacked was the check: in the Rust, the build stopped at a caller that still treated the result as a plain number.
- Not for a hot spot you have measured. Tune it, and keep the plain version beside it with a test that compares the two.
