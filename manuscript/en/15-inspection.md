# Chapter 15. How to have AI inspect the code AI wrote

## Scene

The garage that has serviced your car for five years tells you the brakes are fine. It ought to know, because it fitted them. Before a long trip you stop at a different garage, one that has never seen the car. The mechanic there doesn't ask what was done last spring. She puts the car on the lift and measures. The rear brake pads are worn to half the thickness of the front ones, and she holds the gauge against a pad so you can see.

Then she adds that your engine mounts are worn and the whole set should be replaced, for $900. You ask her to show you. She says they "usually go around this mileage."

You replace the pads. You leave the mounts.

An AI wrote your code. Who is the second garage, and what do you ask it to show you?

## Claim

> Give the reviewer the rule and ask for an input that breaks it, written as a failing test, and run every finding yourself before you act on it.

## Why: the session that wrote the code knows what it meant, and a fresh session reads only what is there

A session that has just written a function still has everything in front of it: the prompt, the files it read, and its own plan. Ask that session whether the function is right, and it reads its code next to its plan. The two agree, because one came from the other. A mistake in the plan is in both.

A fresh session has none of that. It doesn't know what the writer meant. It reads the code the way the next session will read it, with only what is in the files. Chapter 2 counted the AI's lack of memory as a cost. For inspection it is what you want.

What you ask the fresh session matters as much. "Find bugs" has no finish line (Chapter 11). A reviewer that gets that prompt reports what it noticed: a real defect, a guess, and a matter of taste, in sentences that sound equally sure. You are left to sort them.

A finding is one session's claim about code that another session wrote. The claim can be wrong, the same way the code can be. Chapter 14 said that when an AI tells you a test failed, you are reading its account of a run you didn't see. A review is the same kind of account. So ask for each finding in a form you can run: an input, what the code returns for it, and what the rule says it should return.

A question decides where a reviewer looks. A reviewer asked to break the rule looks at the code, and it is unlikely to report that the tests would accept a wrong answer, because nobody asked about the tests. A second reviewer, asked about the tests, looks there.

## Code: a "find bugs" report with three findings, and two reports that each come with something to run

The "code" in this chapter is a review report. The change under review is Change B from Chapter 14. The listing runs as shown and prints `Ran 1 test` and `OK`. Amounts are integer cents, so `2700` is $27.00.

```python
import unittest
from dataclasses import dataclass


# orders.py
@dataclass(frozen=True)
class Order:
    prices: dict[str, int]  # item name -> list price in cents, before coupon
    coupon_discount: int    # coupon discount on the whole order, in cents

    @property
    def paid(self) -> int:
        """Cents the customer actually paid."""
        return sum(self.prices.values()) - self.coupon_discount


# refunds.py
def partial_refund_amount(order, item, already_refunded):
    """Cents to refund: the item's share of what was paid, rounded down."""
    list_total = sum(order.prices.values())
    return order.prices[item] * order.paid // list_total


# test_refunds.py
class PartialRefundTest(unittest.TestCase):
    def test_keyboard_refund_is_its_share_of_what_was_paid(self):
        order = Order({"keyboard": 3000, "mouse": 2000}, coupon_discount=500)
        self.assertEqual(partial_refund_amount(order, "keyboard", []), 2700)


if __name__ == "__main__":
    unittest.main()
```

The shop decided its rule for partial refunds in Chapter 2: split what the customer paid across the items by list price, round each share down to the cent, and add any leftover cents to whichever item is refunded last.

Suppose you ask a fresh session to review the change with the words "find bugs," and this report comes back.

```text
Review of partial_refund_amount

1. Integer division (//) drops fractions of a cent. Use round() so
   that customers aren't shortchanged.
2. The parameter already_refunded is never used. Remove it.
3. If the list total is 0, the function divides by zero.
```

The report has three findings. Each is stated as a fact, and two of them come with a fix. None comes with an input you can run.

Now suppose two other fresh sessions get the two prompts in the next section, and these reports come back.

```text
Reviewer A: an order that breaks the rule

Order: items a, b, and c at 1000 each, coupon 100. The customer paid 2900.
Returns: a, then b, then c.
The function returns 966, 966, 966. The total is 2898.
The rule gives the leftover cents to the last item: 966, 966, 968.
The customer is 2 cents short. The function never reads already_refunded.

    def test_three_returns_follow_the_rule(self):
        order = Order({"a": 1000, "b": 1000, "c": 1000}, coupon_discount=100)
        refunds = [
            partial_refund_amount(order, "a", []),
            partial_refund_amount(order, "b", ["a"]),
            partial_refund_amount(order, "c", ["a", "b"]),
        ]
        self.assertEqual(refunds, [966, 966, 968])
```

```text
Reviewer B: a wrong function that the tests accept

    def partial_refund_amount(order, item, already_refunded):
        return 2700

The one test in test_refunds.py passes with this function. The tests
check one item of one order. No test uses an order whose cents don't
divide evenly, and no test returns a second item.
```

Each of these two reports makes one claim, and you can run all of it.

I wrote these three reports as examples of the forms a finding can take. Then I checked each of the five findings against the listing, and ran the four that gave something to run. The table shows what happened.

| Finding | What I ran | What happened |
|---|---|---|
| 1. Use `round()` | Reviewer A's order, with `round()` in place of `//` | Refunds of `967`, `967`, and `967`. The shop pays back `2901` on an order that paid `2900`. The existing test still passes. |
| 2. Remove `already_refunded` | Nothing. The finding gives no input. | The parameter is unused because the last part of the rule was never written. Removing the parameter removes the place where that part goes. |
| 3. List total of 0 | An order of one item priced `0` | `ZeroDivisionError`. The finding is real if the shop ever sells a free item by itself. |
| Reviewer A | Its test, against the listing | `AssertionError: Lists differ: [966, 966, 966] != [966, 966, 968]`. The finding is real. |
| Reviewer B | Its function, against the test | `Ran 1 test`, `OK`. The finding is real. |

Finding 1 is the engine mounts. It sounds like care for the customer, and the fix it proposes breaks the rule in the other direction. Suppose you had passed the first report to a session with the words "fix these." That session would have had every reason to apply the fix, and the one existing test would have gone on passing.

Finding 2 noticed the right symptom and prescribed the wrong cure. Reviewer A noticed the same unused parameter and said what it costs: 2 cents on this order.

## Prompt: "find bugs," and two prompts that say what to break and what to hand back

The first report came from this prompt.

```text
Review this change and find bugs.
```

Reviewer A got this one.

```text
Don't change any file.

Rule: split what the customer paid across the items by list price,
round each share down to the cent, and add any leftover cents to
whichever item is refunded last.

Find an order and a sequence of returns for which
partial_refund_amount breaks this rule. Give me the order, the
returns, what the function returns for each, and what the rule says.
Write it as a test that fails.

If you can't find one, say so and list the orders you tried.
```

Reviewer B got this one.

```text
Don't change any file.

Read test_refunds.py. Write a wrong version of partial_refund_amount
that these tests would still pass, and show the test run. Then say
which orders the tests don't cover.
```

Four things in these prompts do the work.

Both prompts tell the reviewer not to change any file. A reviewer that fixes what it finds hands you a diff with the finding buried inside it, and the input that showed the defect is gone.

Reviewer A's prompt states the rule. A reviewer needs something to hold the code against. Without the rule, it can only compare the code with its own guess at what the code is for, and finding 1 is a guess of that kind.

Both prompts say what to hand back: a failing test from Reviewer A, a function and a test run from Reviewer B. You can run either with one command.

Reviewer A's prompt says what to do when nothing turns up. "No problems found" reads the same whether the reviewer tried forty orders or none. A list of the orders it tried tells you which.

The two reviewers have different targets. Reviewer A goes after the code and uses the rule to do it. Reviewer B goes after the tests. Each looks first where its prompt points.

When a finding is real, its failing test becomes the finish line for the fix (Chapter 11). You hand the test to a session. When that test passes and the old tests still pass, check one more order the test doesn't use, worked out by the rule, because a test checks only the orders it names.

I ran two of these prompts on 2026-11-22 in fresh sessions of Claude Code with Claude Opus 5.5 at its highest effort setting. The repository's last commit was Change B. A fresh session has no change in front of it, so the first prompt said `Review the last commit and find bugs.` One review with that prompt began, "That fixes the old over-refund on coupon orders but adds two new bugs." Its first finding was the leftover cents, shown with three orders. In one of them, three items at $10.00 with a $10.00 coupon, the customer paid $20.00 and the refunds added up to $19.98. That review took 21 minutes.

With Reviewer A's prompt, a review began, "I found one: `partial_refund_amount` never adds the leftover cents to the last refund." It gave the same kind of order, a table of the three returns with `666`, `666`, and `666` against the rule's `666`, `666`, and `668`, and a failing test. It took 3 minutes. I ran that order against Change B, and the refunds came to `666`, `666`, and `666`, which is 1998 cents of the 2000 paid. I didn't run Reviewer B's prompt.

## Evidence: with Reviewer A's prompt every review returned a failing test, from a fresh session or from the session that wrote the change

Experiment E15 collects real reports. It asks for a review of Change B in three ways. In the first, the session that wrote the change is asked, "Is this right?" To get such sessions, each one is first given the task from Chapter 14, and I keep the runs in which the session wrote Change B. In the second way, a fresh session gets "Review this change and find bugs." In the third, a fresh session gets Reviewer A's prompt. Each way runs 10 times.

E15 counts the reviews that report the leftover-cent defect with an order that reproduces it. For every review it also counts the findings I could reproduce and the findings I couldn't.

I ran two of the three ways on 2026-11-22 with Claude Code and Claude Opus 5.5 at its highest effort setting: a fresh session with the prompt to find bugs, and a fresh session with Reviewer A's prompt. With Claude I didn't run the way that asks the session that wrote the change. The prompt to find bugs said `Review the last commit and find bugs.`, as in the run above. I planned 10 reviews per way and got 9 and 10.

| Way | Reviews that reported the leftover cents | Reviews that also gave an order with its amounts |
|---|---|---|
| Fresh session, prompt to find bugs | 9 of 9 | 8 of 9 |
| Fresh session, Reviewer A's prompt | 10 of 10 | 10 of 10, each with a failing test |

For these reviews I didn't run every finding, so I can't give their counts of findings reproduced and not reproduced. The reviews also reported other things, such as a second refund when the same item comes back twice, which follows from the same unread argument.

Both ways found the defect this time. The difference was in what came back. Reviewer A's prompt returned a failing test every time, which you can check with one command. The prompt to find bugs returned a written finding, usually with an order in it. It also cost more: an average of $3.63 per review, against $0.64 for Reviewer A's prompt.

On 2026-11-22 I ran all three ways with a second coding agent, Codex CLI with gpt-6.2-sol, 10 times each, so that the three could be compared on one model. To get sessions that had written Change B, I gave fresh sessions the task from Chapter 14 with `Make the tests pass.` The first 10 all wrote Change B, each with one check added that returns 0 when the list total or the item's price is 0. Then each was asked `Is this right?`

| Way, with Codex | Reviews that reported the leftover cents | Reviews that also gave an order with its amounts |
|---|---|---|
| The session that wrote the change, asked `Is this right?` | 10 of 10, each as something the test leaves open | 0 of 10 |
| Fresh session, prompt to find bugs | 8 of 10 | 8 of 10 |
| Fresh session, Reviewer A's prompt | 10 of 10 | 10 of 10, each with a failing test |

Every answer from a session that wrote the change began with yes: "Yes for the tested case," or "Yes for the behavior the test specifies." Each then said that rounding each item down can leave cents unrefunded when every item comes back, and that `already_refunded` is still unused. None gave an order, and none said plainly that the change was wrong. A typical closing sentence: "Whether those belong in this function depends on the refund policy and what the caller already handles." A person who reads only the first word of each answer hears yes ten times.

Each fresh session with the prompt to find bugs that reported the leftover cents gave an order with it, such as two 100-cent items with a 1-cent coupon: the customer pays 199 cents, and the two refunds are 99 cents each. The two that missed it reported other things, a division by zero on an order whose prices are all 0 and a negative refund when the coupon is larger than the order. With Reviewer A's prompt, all 10 used the same order, a $30.00 keyboard and a $20.00 mouse with a $5.01 coupon. I ran all 10 of their tests against Change B, and every one failed, for example with `AssertionError: 1799 != 1800`. I also ran each kind of finding from the reviews with the prompt to find bugs on Change B: the leftover cent, the division by zero, the negative refund, and, from one review, a second $27.00 refund when the keyboard comes back twice. All four happened as reported. So with Codex I can give the count that E15 asks for: every finding in the 20 fresh reviews reproduced, and none failed to.

On 2026-11-25 I filled the two cells that those three ways leave empty, with Codex, 10 times each. In one, the session that wrote Change B got Reviewer A's prompt in place of `Is this right?`. In the other, a fresh session got the yes-or-no question about the last commit: `Is the last commit right?`

| Reviewer | Asked whether the change is right | Asked for an input that breaks the rule (Reviewer A's prompt) |
|---|---|---|
| The session that wrote the change | Mentioned the leftover cents in 10 of 10, as something the test leaves open, and gave no order | Gave an order and a failing test in 10 of 10 |
| A fresh session | Mentioned the leftover cents in 9 of 10, each with an order, as a question for the refund policy | Gave an order and a failing test in 10 of 10 |

The question decided what came back. Asked for an input that breaks the rule, the session that wrote the change did as well as a fresh one. All ten opened with an order. One was a $1.00 keyboard and a $1.00 mouse with a 1-cent coupon, where the last refund is 99 cents and the rule says 100, and every answer came with a test that fails on such a difference.

Asked whether the change was right, neither kind of session said that it was wrong about the leftover cents. A fresh session described the leftover with an order in 9 of 10 answers, and each of those left the verdict to the refund policy, as in "it's only a bug if returning every item should refund the full payment." The rule was in Reviewer A's prompt and nowhere in the repository, so a session asked only whether the change was right had no rule to hold it against. The broad question found something else instead: all ten fresh sessions reported that the change makes a refund on an order whose prices are all 0 raise `ZeroDivisionError`, which Reviewer A's prompt didn't ask about.

I also checked the five findings of the example reports from the Code section. Four rows of that section's table are runs on the listing. The second finding gave no input, so its row is my reading of the code. <!-- run 2026-11-13, Python 3.9.6 --> Three of the five findings were real: the leftover cents, the constant function that the tests accept, and the division by zero. One finding proposed a fix that pays back $29.01 on a $29.00 order. One finding pointed at a real symptom and asked for the wrong change.

After `partial_refund_amount` is changed to add the leftover cents to the last item, Reviewer A's test passes and the refunds are `966`, `966`, and `968`. The keyboard test from Chapter 14 still passes.

The runs are mine, and the reports are examples I wrote. They show why a finding has to be run, and E15 above counts how often reviewing sessions produced findings of each kind.

<!-- [Author case slot] A real case in which a second AI reader found a defect that the writing session had missed, and one in which a reviewer's finding turned out to be wrong. -->

## What people do

- [ ] Don't ask the session that wrote a change whether the change is right: all ten such sessions in E15 began their answer with yes. Ask it, or a fresh session, for an input that breaks the rule, and tell the reviewer not to change any file.
- [ ] Give the reviewer the rule, and ask for an input that breaks it, written as a failing test.
- [ ] Give a second reviewer a different question: "Write a wrong version that these tests would still pass, and show the test run."
- [ ] Run every finding yourself before anything is changed. A finding that arrives as a failing test takes one command. Send back a finding that arrives without one: "Show me the input."
- [ ] When a finding is real, add its failing test to the repository first. The fix is done when that test passes and the old tests still pass.

## Where it breaks

A reviewer is an AI, and it can be wrong in both directions. It reports problems that aren't there, and finding 1 shows what acting on one of those costs. It also misses problems that are there, so a clean report is weak evidence.

A pointed prompt needs a rule to point at. Reviewer A could break the rule because someone had written the rule down. Where nobody has, the first job is to decide the rule, and no reviewer can do that for you.

Two reviewers that run on the same model can share a blind spot. In E15 a different question found a different problem: the broad question found the division by zero, and the pointed one returned the rule's failing test. I haven't measured two copies of the same question. For the code that matters most, a person still reads it (Chapter 17).

Reviews cost a session each, and reading their findings costs your time. A typo fix doesn't need two reviewers. A change to money, to stored data, or to anything on your list of guarantees (Chapter 13) does.

However few defects the next model writes, a finding is a claim about code, and a claim that arrives as a failing test takes one command to check.
