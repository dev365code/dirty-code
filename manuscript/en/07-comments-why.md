# Chapter 7. Comments say why: AI tidies up numbers it can't explain

## Scene

You buy a used car that comes with no service records. At the first service, the mechanic notices that the engine idles faster than the manual says it should. It looks like a mistake, so the mechanic sets the idle back to the book value.

A week later the engine stalls at a red light, just as the air conditioning switches on. It happens again the next day. The previous owner had raised the idle speed for exactly that reason. The owner never wrote it down, because the owner never needed to: the owner remembered.

The mechanic did nothing careless. The setting looked wrong, and nothing on the car said it was wrong on purpose.

Your code has values like that idle setting. What does an AI do with a number when nothing says why it has that value?

## Claim

> When a value looks wrong on purpose, write the reason next to it, because an AI asked to tidy up may "fix" a value it can't explain.

## Why: the reason for an odd value lives in someone's memory, and a new session can't ask that person

Every team has values that look odd and are right. A timeout is 37 seconds when every other timeout is 30. A batch holds 48 items when 50 would be the round number. Someone on the team chose each value after something went wrong, and that person remembers why.

For a human reader, that memory is enough. A new teammate who wonders about the 37 asks around, and someone says, "Don't touch that, the provider cuts us off at 40." The answer travels by word of mouth, so nobody writes it into the file.

An AI has no memory, and a new session can't ask around. The session sees `37` next to a row of round numbers. The name of the constant says what the value is for. It can't say why the value is 37 and not 30. If the prompt asks the session to clean up the file, 37 looks like the kind of thing a cleanup is supposed to fix.

A person who tidies code has the same instinct. The difference is what happens next. A person who is about to change a strange number usually hesitates and asks someone. A session tends to finish the task it was given, and a cleanup that leaves the odd value alone looks unfinished.

*Clean Code* asks you to explain yourself in code before you reach for a comment, and it counts comments that explain intent or warn of consequences among the good ones. <!-- check against original --> This chapter stays inside that advice. A name can say what a value is. Only a comment can say why it isn't the value you'd expect.

## Code: two odd values get one comment each, and nothing else changes

The shop sends its payment provider two kinds of calls: a request to approve a charge, and a nightly settlement call that lists the day's orders in batches. Here is the version for people. The listing runs as shown and prints `Ran 1 test` and `OK`.

```python
"""payments.py (the version for people)"""
import unittest

APPROVE_TIMEOUT_SEC = 37
SETTLE_BATCH_SIZE = 48
RETRY_WAIT_SEC = 2


def settlement_batches(order_ids):
    """Split order IDs into the batches sent to the nightly settlement call."""
    size = SETTLE_BATCH_SIZE
    return [order_ids[i:i + size] for i in range(0, len(order_ids), size)]


class SettlementBatchesTest(unittest.TestCase):
    def test_every_order_is_in_exactly_one_batch(self):
        ids = list(range(100))
        flat = [i for batch in settlement_batches(ids) for i in batch]
        self.assertEqual(flat, ids)


if __name__ == "__main__":
    unittest.main()
```

For 100 orders, `settlement_batches` returns three batches, of 48, 48, and 4 orders.

This is tidy code. The constants have clear names, and the function is four lines. Everyone on the team knows two facts that the file doesn't state. The provider closes a connection after 40 seconds, so the shop stops waiting at 37 and uses the last 3 seconds to record the timeout. And the provider's settlement call rejects any batch with more than 48 order IDs.

Now suppose you ask an AI to clean up this file, and this change comes back.

```python
APPROVE_TIMEOUT_SEC = 30
SETTLE_BATCH_SIZE = 50
RETRY_WAIT_SEC = 2
```

The test still passes. It checks that every order lands in exactly one batch, and that's still true. For 100 orders the function now returns two batches of 50. Tonight the provider rejects the first batch, because 50 is more than 48, and no orders are settled.

Nothing in the diff looks wrong. A reviewer who doesn't know about the provider's limit sees two odd numbers replaced by two round ones, and approves.

The version for AI adds the reasons. It replaces the three constants in the listing, and nothing else changes.

```python
# 37, not 30 or 40: the provider closes the connection at 40 seconds.
# We stop 3 seconds earlier so there is time to record the timeout.
APPROVE_TIMEOUT_SEC = 37

# 48, not 50: the provider's settlement call rejects more than 48 IDs.
SETTLE_BATCH_SIZE = 48

RETRY_WAIT_SEC = 2
```

Each comment does three things. It repeats the value, so a reader can see when the comment and the code have drifted apart. It names the value that a tidy-minded reader would want instead: "not 30 or 40," "not 50." And it gives the reason in terms of something outside the code, which in both cases is the provider.

`RETRY_WAIT_SEC = 2` has no comment. Two seconds is the value anyone would expect, and nobody will be tempted to fix it. Comment the values that look wrong on purpose, and leave the rest alone.

Chapter 6 used a comment of the same kind. Above each copy of the formatting function it said `# Own copy of format_amount on purpose`, followed by the reason. Without that line, a session that tidies the repository has every reason to merge the copies back into one function.

## Prompt: a cleanup prompt doesn't say which values to leave alone

Both versions get the same prompt.

```text
Clean up payments.py. Use consistent names and round values for
the constants, and remove anything that looks like a leftover.
```

This is how people ask for a cleanup. The prompt doesn't list the values that must stay, because the person who wrote it wasn't thinking about them.

In the version for people, the session has the prompt and three constants. An AI tends to follow a prompt to the letter. The prompt asks for round values, and 37 and 48 are not round. Nothing in the file argues for keeping them, so changing both is the most direct way to do what the prompt says.

In the version for AI, the same session reads two comments that say "not 30 or 40" and "not 50" and give a reason. Now the prompt and the file disagree, and the session has to choose. It is likely to keep the values, and a careful session will say in its report that it left them alone and why. It may still change them. A comment is something the session reads. It isn't something the session is forced to obey.

> **[Run record slot: E6]** For each version: the values after the cleanup, and what the session's report said about them. Date, tool, model.

## Evidence: experiment E6 will count how many odd values survive a cleanup

Experiment E6 will build the order server with 10 values that look wrong on purpose: timeouts, batch sizes, retry counts, and rounding rules. One copy of the server has a reason comment above each of the 10. The other copy has the same values with no comments. Each copy gets the cleanup prompt above in 10 fresh sessions.

For each session, E6 counts how many of the 10 values are unchanged afterward. It also records whether the session's report mentions a value that it kept or changed. A hidden test checks each value. A hidden test is a test the AI never sees, and I use it to judge the result.

E6 hasn't been run yet. If both copies keep about the same number of values, I'll say so here, and this chapter's claim will shrink to the smaller point that the comment helps the human reviewer.

> **[Result slot: experiment E6]** Date, tool and model. For each copy: values unchanged out of 10 per session, and sessions whose report mentioned the odd values.

> **[Author case slot]** A real case in which an AI changed, or reported on, a value or a rule whose reason was written nowhere in the files.

## What people do

- [ ] List the numeric constants in one module: `git grep -nE "^[A-Z_]+ = [0-9]+" -- "*.py"`. The pattern finds constants defined at the top level of a file. It misses a number written inside a function, such as `time.sleep(37)`, so skim the functions that talk to other systems as well.
- [ ] For each value that isn't the one you'd expect, find the person who chose it and ask why. Write the answer above the value in this form: `# 37, not 30 or 40: <reason>`. If nobody knows the reason, write that: `# 48: reason unknown. Ask the payments team before changing.`
- [ ] Paste this into your rules file (the instruction file in your repository that the AI reads when it starts work): "Don't change a value whose comment gives a reason. If you think the reason is out of date, tell me and wait."
- [ ] Where you can, turn the reason into a test. A test that fails when a batch holds 49 orders protects the value even if someone deletes the comment (Chapter 14).

## Where it breaks

A comment can be wrong, and an AI tends to believe it. Suppose the provider raises its limit from 48 to 100 and nobody updates the comment. A session that reads "the provider's settlement call rejects more than 48 IDs" will keep defending a limit that no longer exists. So treat a reason comment as part of the code: when the value or the reason changes, change the comment in the same commit. A comment that repeats the value helps here, because a comment that says 37 above a constant set to 45 is visibly out of date.

Comments about what the code does are a different thing. `# loop over the orders` repeats the line below it and goes stale the first time someone edits that line. This chapter asks for one kind of comment only: the reason behind something that looks wrong.

A comment is weaker than a test. The comment asks the reader to leave the value alone, and the test fails if the reader doesn't. Use the comment for the values you can't test yet, and to explain why a test exists.

Better models may hesitate more often before they change an odd value, and some will ask first. Hesitating doesn't tell them the reason. The reason is known to one person on your team until someone writes it down.
