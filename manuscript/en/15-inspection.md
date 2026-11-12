# Chapter 15. How to have AI inspect the code AI wrote

## Scene

The garage that has serviced your car for five years tells you the brakes are fine. It ought to know, because it fitted them. Before a long trip you stop at a different garage, one that has never seen the car. The mechanic there doesn't ask what was done last spring. She puts the car on the lift and measures. The rear brake pads are worn to half the thickness of the front ones, and she holds the gauge against a pad so you can see.

Then she adds that your engine mounts are worn and the whole set should be replaced, for $900. You ask her to show you. She says they "usually go around this mileage."

You replace the pads. You leave the mounts.

An AI wrote your code. Who is the second garage, and what do you ask it to show you?

## Claim

> Have a fresh session inspect what another session wrote, give each inspector a different question, and act on a finding only after you have run it yourself.

## Why: the session that wrote the code knows what it meant, and a fresh session reads only what is there

A session that has just written a function still has everything in front of it: the prompt, the files it read, and its own plan. Ask that session whether the function is right, and it reads its code next to its plan. The two agree, because one came from the other. A mistake in the plan is in both.

A fresh session has none of that. It doesn't know what the writer meant. It reads the code the way the next session will read it, with only what is in the files. Chapter 2 counted the AI's lack of memory as a cost. For inspection it is what you want.

What you ask the fresh session matters as much. "Find bugs" has no finish line (Chapter 11). A reviewer that gets that prompt reports what it noticed: a real defect, a guess, and a matter of taste, in sentences that sound equally sure. You are left to sort them.

A finding is one session's claim about code that another session wrote. The claim can be wrong, the same way the code can be. Chapter 14 said that when an AI tells you a test failed, you are reading its account of a run you didn't see. A review is the same kind of account. So ask for each finding in a form you can run: an input, what the code returns for it, and what the rule says it should return.

One question finds one kind of problem. A reviewer asked to break the rule looks at the code. It won't tell you that the tests would accept a wrong answer. A second reviewer with a different question looks at a different side.

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

    def test_three_returns_add_up_to_what_the_customer_paid(self):
        order = Order({"a": 1000, "b": 1000, "c": 1000}, coupon_discount=100)
        refunds = [
            partial_refund_amount(order, "a", []),
            partial_refund_amount(order, "b", ["a"]),
            partial_refund_amount(order, "c", ["a", "b"]),
        ]
        self.assertEqual(sum(refunds), order.paid)
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

I wrote these three reports as examples of the forms a finding can take. Then I ran each of the five findings against the listing. The table shows what happened.

| Finding | What I ran | What happened |
|---|---|---|
| 1. Use `round()` | Reviewer A's order, with `round()` in place of `//` | Refunds of `967`, `967`, and `967`. The shop pays back `2901` on an order that paid `2900`. The existing test still passes. |
| 2. Remove `already_refunded` | Nothing. The finding gives no input. | The parameter is unused because the last part of the rule was never written. Removing the parameter removes the place where that part goes. |
| 3. List total of 0 | An order of one item priced `0` | `ZeroDivisionError`. The finding is real if the shop ever sells a free item by itself. |
| Reviewer A | Its test, against the listing | `AssertionError: 2898 != 2900`. The finding is real. |
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

The two reviewers have different targets. Reviewer A goes after the code and uses the rule to do it. Reviewer B goes after the tests. Neither would have found what the other found.

When a finding is real, its failing test becomes the finish line for the fix (Chapter 11). You hand the test to a session, and the fix is done when that test passes and the old tests still pass.

> **[Run record slot: E15]** For each of the three prompts: the report that came back, word for word, and what happened when each finding was run. Date, tool, model.

## Evidence: I ran the five findings, and one proposed fix made the shop pay back $29.01 on a $29.00 order

Every row of the table is a run on the listing above. <!-- run 2026-11-13, Python 3.9.6 --> Three of the five findings were real: the leftover cents, the constant function that the tests accept, and the division by zero. One finding proposed a fix that pays back $29.01 on a $29.00 order. One finding pointed at a real symptom and asked for the wrong change.

After `partial_refund_amount` is changed to add the leftover cents to the last item, Reviewer A's test passes and the refunds are `966`, `966`, and `968`. The keyboard test from Chapter 14 still passes.

The runs are mine, and the reports are examples I wrote. They show why a finding has to be run. They don't show how often a reviewing session produces a finding like the first one.

Experiment E15 will collect real reports. It asks for a review of Change B in three ways. In the first, the session that wrote the change is asked, "Is this right?" To get such sessions, each one is first given the task from Chapter 14, and I keep the runs in which the session wrote Change B. In the second way, a fresh session gets "Review this change and find bugs." In the third, a fresh session gets Reviewer A's prompt. Each way runs 10 times.

E15 counts the reviews that report the leftover-cent defect with an order that reproduces it. For every review it also counts the findings I could reproduce and the findings I couldn't.

> **[Result slot: experiment E15]** Date, tool and model. For each way, out of 10 reviews: reviews that reported the leftover-cent defect with a reproducing order, findings reproduced, and findings not reproduced.

> **[Author case slot]** A real case in which a second AI reader found a defect that the writing session had missed, and one in which a reviewer's finding turned out to be wrong.

## What people do

- [ ] Don't ask the session that wrote a change whether the change is right. Open a fresh session for the review, and tell it not to change any file.
- [ ] Give the reviewer the rule, and ask for an input that breaks it, written as a failing test.
- [ ] Give a second reviewer a different question: "Write a wrong version that these tests would still pass, and show the test run."
- [ ] Run every finding yourself before anything is changed. A finding that arrives as a failing test takes one command. Send back a finding that arrives without one: "Show me the input."
- [ ] When a finding is real, add its failing test to the repository first. The fix is done when that test passes and the old tests still pass.

## Where it breaks

A reviewer is an AI, and it can be wrong in both directions. It reports problems that aren't there, and finding 1 shows what acting on one of those costs. It also misses problems that are there, so a clean report is weak evidence.

A pointed prompt needs a rule to point at. Reviewer A could break the rule because someone had written the rule down. Where nobody has, the first job is to decide the rule, and no reviewer can do that for you.

Two reviewers that run on the same model can share a blind spot. I expect a different question to help more than a second copy of the same question, and I haven't measured it. For the code that matters most, a person still reads it (Chapter 17).

Reviews cost a session each, and reading their findings costs your time. A typo fix doesn't need two reviewers. A change to money, to stored data, or to anything on your list of guarantees (Chapter 13) does.

Better models will write fewer defects and find more of them. A finding will still be a claim about code, and a claim that arrives as a failing test still takes one command to check.
