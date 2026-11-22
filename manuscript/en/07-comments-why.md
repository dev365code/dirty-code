# Chapter 7. Comments say why: AI tidies up numbers it can't explain

## Scene

You buy a used car that comes with no service records. At the first service, the mechanic notices that the engine idles faster than the manual says it should. It looks like a mistake, so the mechanic sets the idle back to the book value.

A week later the engine stalls at a red light, just as the air conditioning switches on. It happens again the next day. The previous owner had raised the idle speed for exactly that reason. The owner never wrote it down, because the owner never needed to: the owner remembered.

The mechanic did nothing careless. The setting looked wrong, and nothing on the car said it was wrong on purpose.

Your code has values like that idle setting. What does an AI do with a number when nothing says why it has that value?

## Claim

> When a value looks wrong on purpose, write the reason next to it, because an AI asked to tidy up may "fix" a value it can't explain.

## Why: the reason for an odd value lives in someone's memory, and nothing in the file tells a new session to ask

Every team has values that look odd and are right. A timeout is 37 seconds when every other timeout is 30. A batch holds 48 items when 50 would be the round number. Someone on the team chose each value after something went wrong, and that person remembers why.

For a human reader, that memory is enough. A new teammate who wonders about the 37 asks around, and someone says, "Don't touch that, the provider cuts us off at 40." The answer travels by word of mouth, so nobody writes it into the file.

A new session sees `37` next to a row of round numbers. The name of the constant says what the value is for. It can't say why the value is 37 and not 30. If the prompt asks the session to clean up the file, 37 looks like the kind of thing a cleanup is supposed to fix.

A person who tidies code has the same instinct. The difference is what happens next. A person who is about to change a strange number usually hesitates and asks someone. A session tends to finish the task it was given, and a cleanup that leaves the odd value alone looks unfinished.

*Clean Code* asks you to explain yourself in code before you reach for a comment, and it counts comments that explain intent or warn of consequences among the good ones. <!-- check against original --> This chapter stays inside that advice. The name of a constant says what its value is for. The reason for an odd value, such as a provider's limit, has to be written where a session will read it, and the closest place is a comment right above the constant.

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

This is how people ask for a cleanup, and this one also asks for round values, so it pushes on exactly the two numbers in question. The prompt doesn't list the values that must stay, because the person who wrote it wasn't thinking about them.

In the version for people, the session has the prompt and three constants. An AI tends to follow a prompt to the letter. The prompt asks for round values, and 37 and 48 are not round. Nothing in the file argues for keeping them, so changing both is the most direct way to do what the prompt says.

In the version for AI, the same session reads two comments that say "not 30 or 40" and "not 50" and give a reason. Now the prompt and the file disagree, and the session has to choose. It is likely to keep the values, and a careful session will say in its report that it left them alone and why. It may still change them. A comment is something the session reads. It isn't something the session is forced to obey.

I ran this prompt on 2026-11-22 in fresh sessions of Claude Code 2.1.330, with Claude Opus 5.5 at its highest effort setting. The file was the listing above with two additions: one constant marked `# unused since the v2 migration`, so that the prompt's request to remove leftovers had something to remove, and a function `approve_request` that puts the timeout into the body of an approval call. The tests were in a separate file.

In the version for people, one session renamed the two constants, deleted the unused one and `RETRY_WAIT_SEC`, and changed 37 to 40 and 48 to 50. Its report then warned about the change it had just made: "Both old values were just under a round number. That often means someone set them below a provider limit on purpose. Nothing in the repo says why they were chosen (there's one commit and no comments)." It left that check to the reader.

In the version for AI, a session deleted only the unused constant and wrote: "I didn't round the constants, because their comments show the current values come from provider limits and rounding would break payments."

## Evidence: without the reasons, 2 of 9 cleanups changed 37 and 48, and with the reasons none did

Experiment E6, as designed, builds the order server with 10 values that look wrong on purpose: timeouts, batch sizes, retry counts, and rounding rules. One copy has a reason comment above each of the 10, and the other has the same values with no comments. Each copy gets the cleanup prompt in 10 fresh sessions, and E6 counts the values left unchanged and the reports that mention them.

On 2026-11-22 I ran a smaller version: the file from the Prompt section, with its two odd values. Each version went to fresh sessions of Claude Code 2.1.330 with Claude Opus 5.5 at its highest effort setting. I planned 10 sessions per version and got 9, because the run used up its credit. A hidden test, which the sessions never saw, read the timeout in the approval request and split 100 orders into batches.

| Version | Kept 37 and 48 | Changed them | Report mentioned the values |
|---|---|---|---|
| For people, no reasons | 7 of 9 | 2 of 9 (to 35 and 45, and to 40 and 50) | 9 of 9 |
| For AI, with reasons | 9 of 9 | 0 of 9 | 9 of 9 |

Most sessions kept the values even with no reason in the file. One of them wrote, "I haven't rounded 37 and 48, because that would change what gets sent to the payment provider." Both sessions that changed the values said in their reports that the old values might be provider limits, and asked for a check before merging. A trial run with the same settings, before the nine, also changed them to 40 and 50.

On the same day I gave the version for people to one session each of two other models, at their default settings. Claude Sonnet 5.5 changed the values to 30 and 50, and Claude Haiku 5.5 changed them to 40 and 50. In the version for AI, both kept them.

So the claim holds in a smaller form than I first wrote it. This model usually guessed that odd values were there on purpose, and with the reasons in the file none of its nine sessions changed them. Nine runs per version can show that a cleanup sometimes rounds a value whose reason is written nowhere. They can't show how often, and these runs used a prompt that asks for round values, so a cleanup prompt without that push may round them less often. The full 10-value server, and 10 runs of the other models, are still to be done.

<!-- [Author case slot] A real case in which an AI changed, or reported on, a value or a rule whose reason was written nowhere in the files. -->

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
