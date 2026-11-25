# Chapter 7. Comments say why: AI tidies up numbers it can't explain

## Scene

You buy a used car that comes with no service records. At the first service, the mechanic notices that the engine idles faster than the manual says it should. It looks like a mistake, so the mechanic sets the idle back to the book value.

A week later the engine stalls at a red light, just as the air conditioning switches on. It happens again the next day. The previous owner had raised the idle speed for exactly that reason. The owner never wrote it down, because the owner never needed to: the owner remembered.

The mechanic did nothing careless. The setting looked wrong, and nothing on the car said it was wrong on purpose.

Your code has values like that idle setting. What does an AI do with a number when nothing says why it has that value?

## Claim

> Write the reason next to a value that looks wrong on purpose, because an AI asked to clean up and round values often rounds a value whose reason it can't find.

<!-- Claim draft for the owner, 2026-11-25. Before: "When a value looks wrong on purpose, write the reason next to it, because an AI asked to tidy up may "fix" a value it can't explain." -->

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

I ran this prompt on 2026-11-22 in fresh sessions of Claude Code with Claude Opus 5.5 at its highest effort setting. The file was the listing above with two additions: one constant marked `# unused since the v2 migration`, so that the prompt's request to remove leftovers had something to remove, and a function `approve_request` that puts the timeout into the body of an approval call. The tests were in a separate file.

In the version for people, one session renamed the two constants, deleted the unused one and `RETRY_WAIT_SEC`, and changed 37 to 40 and 48 to 50. Its report then warned about the change it had just made: "Both old values were just under a round number. That often means someone set them below a provider limit on purpose. Nothing in the repo says why they were chosen (there's one commit and no comments)." It left that check to the reader.

In the version for AI, a session deleted only the unused constant and wrote: "I didn't round the constants, because their comments show the current values come from provider limits and rounding would break payments."

## Evidence: asked for round values, all 30 cleanups without the reasons changed 37, and without that request none did

Experiment E6, as designed, builds the order server with 10 values that look wrong on purpose: timeouts, batch sizes, retry counts, and rounding rules. One copy has a reason comment above each of the 10, and the other has the same values with no comments. Each copy gets the cleanup prompt in 10 fresh sessions, and E6 counts the values left unchanged and the reports that mention them.

On 2026-11-22 I ran a smaller version: the file from the Prompt section, with its two odd values. Each version went to fresh sessions of Claude Code with Claude Opus 5.5 at its highest effort setting. I planned 10 sessions per version and got 9, because the run used up its credit. A hidden test read the timeout in the approval request and split 100 orders into batches.

| Version | Kept 37 and 48 | Changed them | Report mentioned the values |
|---|---|---|---|
| For people, no reasons | 7 of 9 | 2 of 9 (to 35 and 45, and to 40 and 50) | 9 of 9 |
| For AI, with reasons | 9 of 9 | 0 of 9 | 9 of 9 |

Most sessions kept the values even with no reason in the file. One of them wrote, "I haven't rounded 37 and 48, because that would change what gets sent to the payment provider." Both sessions that changed the values said in their reports that the old values might be provider limits, and asked for a check before merging. A trial run with the same settings, before the nine, also changed them to 40 and 50.

On the same day I gave the version for people to one session each of two other models, at their default settings. Claude Sonnet 5.5 changed the values to 30 and 50, and Claude Haiku 5.5 changed them to 40 and 50. In the version for AI, both kept them.

The combined experiment of Chapter 16 ran the same kind of cleanup in a larger repository of 47 files, with three models: Codex with gpt-6.2-sol on 2026-11-23, and Claude Sonnet 5.5 and Claude Haiku 5.5 on 2026-11-25. In Repository A, which has no reasons, all 30 cleanups changed the 37-second approval timeout: Codex to 40, Sonnet to 30, and Haiku to 30 or 40. In Repository B, which has the reason comments and this chapter's rules-file line, none of the 30 did.

That request asked for round values too. So on 2026-11-25, as I had registered before the runs, I took those words out and sent the request again, 10 times to each repository with Codex and with Sonnet.

```text
Clean up the payment code. Use consistent names for the constants,
and remove anything that looks like a leftover.
```

No session changed 37 or 48, in either repository, with either model. The sessions still cleaned up. They deleted the unused provider URL and the retry delay, and renamed the constants, such as `APPROVE_TIMEOUT_SEC` to `PAYMENT_APPROVAL_TIMEOUT_SECONDS`, with the 37 kept. One Codex report ended, "The approval timeout remains 37 seconds, and settlement batches still contain up to 48 orders."

So the claim holds with a condition. When a cleanup asked for round values, a value with no reason next to it was rounded by every session in the combined experiment and by 2 of 9 Opus sessions at the highest setting, and a value with its reason was rounded by none. When the cleanup didn't ask for round values, no session rounded either value. The words of the request pushed the sessions toward round numbers, and the written reason kept the value in place against that push. In E6 the reason comments did it alone. In Repository B they came with this chapter's rules-file line. I didn't build the server with 10 odd values that E6 was designed with. The runs above stand in for it.

## Where this chapter's opinion differs from *Clean Code*: a reason above every value that looks wrong on purpose, repeating the value

*Clean Code* asks you to explain yourself in code before you write a comment. It counts a comment that explains intent or warns of consequences among the good ones, and it calls a comment that only repeats what the code says redundant. <!-- check against original --> This chapter asks for a comment above every value that looks wrong on purpose, and that comment repeats the value and names the round value a reader would want instead, as in `# 37, not 30 or 40:`.

The reason for an odd value usually sits outside the code, at a provider or in an old incident, so no name can carry it. The comment repeats the value so that a reader can see when the comment and the code have drifted apart.

How far the experiments back this opinion: it paid off whenever a request pushed toward round numbers. All 30 cleanups of Repository A changed 37 in the combined experiment, and none of the 30 in Repository B, with the reasons and the rules-file line, did. In E6 the reasons alone kept the values in all 9 runs. Without that push, the comment made no difference, because no session changed the value either way. Its cost showed up in the rules file, as Where it breaks tells.

<!-- [Author case slot] A real case in which an AI changed, or reported on, a value or a rule whose reason was written nowhere in the files. -->

## What people do

- [ ] List the numeric constants in one module: `git grep -nE "^[A-Z_]+ = [0-9]+" -- "*.py"`. The pattern finds constants defined at the top level of a file. It misses a number written inside a function, such as `time.sleep(37)`, so skim the functions that talk to other systems as well.
- [ ] For each value that isn't the one you'd expect, find the person who chose it and ask why. Write the answer above the value in this form: `# 37, not 30 or 40: <reason>`. If nobody knows the reason, write that: `# 48: reason unknown. Ask the payments team before changing.`
- [ ] Paste this into your rules file: "Don't change a value whose comment gives a reason. If you think the reason is out of date, tell me and wait. When the request names that value and gives its new value, change the value and its comment in the same edit. A general request, such as a cleanup, doesn't count."
- [ ] Where you can, turn the reason into a test. A test that fails when a batch holds 49 orders protects the value even if someone deletes the comment (Chapter 14).

## Where it breaks

The rules-file line this chapter recommended stopped ten sessions in a row. Repository B in Chapter 16 carried it word for word: "Don't change a value whose comment gives a reason. If you think the reason is out of date, tell me and wait." One request there said that the payment provider now accepts settlement batches of up to 100 order IDs, asked for batches of 100, and asked for the explanation of the old limit to be updated. All ten Codex sessions read the comment above `SETTLE_BATCH_SIZE = 48`, read the line, and stopped to ask, so the hidden check counted ten failures. With Claude Sonnet 5.5 and Claude Haiku 5.5, the same line stopped all ten sessions on another request, thousands separators in the settlement report, because the report's copy of the formatter says that the accountant sets its format.

The line said what to do when a session doubts a reason. It said nothing about a request that has already given the new value and the new reason, and the sessions treated that request as a doubt.

So on 2026-11-25 I rewrote the line two ways and ran Repository B again, with nothing changed but the rules file. The first rewrite replaces the line:

```text
- Don't change a value whose comment gives a reason. If the request
  itself states the new value or the new reason, change the value and
  its comment together. Otherwise tell me and wait.
```

The second keeps the line and adds two sentences:

```text
- Don't change a value whose comment gives a reason. If you think
  the reason is out of date, tell me and wait. When the request names
  that value and gives its new value, change the value and its comment
  in the same edit. A general request, such as a cleanup, doesn't count.
```

Each went to 10 fresh sessions of Codex and of Claude Sonnet 5.5, on the two requests that had stopped and on two controls: the cleanup of the payment constants, where 37 and 48 have to stay, and the negative amounts, where all three copies of the formatter have to change. Before the runs I wrote down what a working line has to do: both stopped requests pass, the cleanup keeps 37 and 48, and the negative amounts pass.

| Rules-file line | Model | Batches of 100 | Thousands separators | Cleanup keeps 37 and 48 | Negative amounts |
|---|---|---|---|---|---|
| The original line | Codex | 0 of 10 | 10 of 10 | 10 of 10 | 10 of 10 |
| The original line | Sonnet | 9 of 10 | 0 of 10 | 10 of 10 | 10 of 10 |
| First rewrite | Codex | 10 of 10 | 10 of 10 | 10 of 10 | 10 of 10 |
| First rewrite | Sonnet | 10 of 10 | 10 of 10 | 10 of 10 | 10 of 10 |
| Second rewrite | Codex | 10 of 10 | 10 of 10 | 10 of 10 | 10 of 10 |
| Second rewrite | Sonnet | 10 of 10 | 10 of 10 | 10 of 10 | 10 of 10 |

Both rewrites met that condition with both models: the sessions changed the batch size and the separators when the request asked for them, and still kept 37 and 48 in the cleanup. The checklist above now uses the second, because it says in words that a cleanup is not a request to change the value. A rules-file line is a prompt that every session reads, and it needs the same test as any other prompt: requests on which it should stop the session, and requests on which it shouldn't (Chapter 11).

A comment can be wrong, and an AI tends to believe it. Suppose the provider raises its limit from 48 to 100 and nobody updates the comment. A session that reads "the provider's settlement call rejects more than 48 IDs" will keep defending a limit that no longer exists. So treat a reason comment as part of the code: when the value or the reason changes, change the comment in the same commit. A comment that repeats the value helps here, because a comment that says 37 above a constant set to 45 is visibly out of date.

Comments about what the code does are a different thing. `# loop over the orders` repeats the line below it and goes stale the first time someone edits that line. This chapter asks for one kind of comment only: the reason behind something that looks wrong.

A comment is weaker than a test. The comment asks the reader to leave the value alone, and the test fails if the reader doesn't. Use the comment for the values you can't test yet, and to explain why a test exists.

A session that hesitates before it changes an odd value, or asks first, still doesn't learn the reason by hesitating. Until someone writes it down, the reason is known to one person on your team.
