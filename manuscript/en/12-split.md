# Chapter 12. Where to cut: hand off work in pieces you can check

## Scene

You're driving 400 miles to your sister's wedding. Every two hours you pull into a rest stop. You look at the fuel gauge, walk once around the car, and glance at the tires. Each stop costs you five minutes.

At the third stop, a rear tire looks soft. You fill it at the pump next door and drive on. You also know something useful: the tire was fine two hours ago, so whatever happened, happened on the last stretch of road.

A friend makes the same trip without stopping. Sixty miles from the end, the car starts pulling to one side. Your friend doesn't know when it began or what else might be wrong.

When you hand an AI a week of work in one prompt, where are your rest stops?

## Claim

> Cut the work you hand to an AI into pieces you can check, and end each piece at a point where a command can say pass or fail.

## Why: an AI can change twenty files in one session, and a person can check only what a command can pass or fail

An AI can change twenty files in one session, because typing costs it almost nothing (Chapter 1). So the size of a task is no longer limited by how much the writer can write. It is limited by how much you can check.

You don't check by reading every line. This book assumes you stopped doing that (Chapter 1). You check by running something: the tests, an example whose answer you know, a search. A check like that gives you one piece of news, pass or fail. After a small change, a failure points at a few lines. After a change to twenty files, the same failure points at twenty files.

A pass tells you even less. It says that the cases somebody thought of came out right. In a large change, that somebody is usually the session that wrote the code, because it wrote the tests too. Its tests cover the places it knew about. A place the session never opened has no new test, so nothing there can fail (Chapter 14).

An AI's lack of memory adds another reason to cut. A long task can stop halfway. The session reaches a usage limit, the laptop goes to sleep, or you stop the session because it went the wrong way. A new session doesn't remember what the old one had finished. If the work was cut into pieces, and each piece ended with a commit and passing tests, the new session starts from the last commit and from a list that says which pieces are done. If the work was one piece, the new session starts from a half-changed repository and has to work out by reading what state it is in.

So decide where the checks go before you write the prompt. A good place to cut is a point where every test that passed before still passes, and one new example with a known answer passes too.

## Code: a one-piece change that prints OK with two places missed, and the same change cut into four pieces

The "code" in this chapter is a change. Here is the shop before the change. The listing joins `orders.py`, `shipping.py`, `refunds.py`, `settlement.py`, and the tests. It runs as shown and prints `Ran 4 tests` and `OK`. Amounts are integer cents, so `3000` is $30.00.

```python
import unittest
from dataclasses import dataclass


# orders.py
@dataclass(frozen=True)
class Order:
    prices: dict[str, int]  # item name -> list price in cents
    coupon_discount: int    # coupon discount on the whole order, in cents

    @property
    def paid(self) -> int:
        """Cents the customer actually paid."""
        return sum(self.prices.values()) - self.coupon_discount


# shipping.py
def shipping_fee(order):
    """Cents to charge for shipping. Free when the customer paid $50.00 or more."""
    return 0 if order.paid >= 5000 else 500


# refunds.py
def full_refund_amount(order):
    """Cents to refund when the whole order comes back."""
    return sum(order.prices.values()) - order.coupon_discount


# settlement.py
def payout_total(orders):
    """Cents the payment provider owes the shop for these orders."""
    return sum(sum(o.prices.values()) - o.coupon_discount for o in orders)


# test_shop.py
class ShopTest(unittest.TestCase):
    def setUp(self):
        self.order = Order({"keyboard": 3000, "mouse": 2000}, 500)

    def test_paid(self):
        self.assertEqual(self.order.paid, 4500)

    def test_shipping(self):
        self.assertEqual(shipping_fee(self.order), 500)

    def test_full_refund(self):
        self.assertEqual(full_refund_amount(self.order), 4500)

    def test_payout(self):
        self.assertEqual(payout_total([self.order]), 4500)


if __name__ == "__main__":
    unittest.main()
```

Until now an order could hold one of each item. The shop wants to sell two keyboards in one order, and you type one line to the AI.

```text
Let a customer buy more than one of the same item.
```

Suppose this change comes back. Only `orders.py` and the test file changed.

```python
# orders.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Order:
    prices: dict[str, int]  # item name -> list price of one unit, in cents
    coupon_discount: int    # coupon discount on the whole order, in cents
    quantities: dict[str, int] = field(default_factory=dict)  # item name -> units; missing means 1

    @property
    def paid(self) -> int:
        """Cents the customer actually paid."""
        total = sum(price * self.quantities.get(item, 1) for item, price in self.prices.items())
        return total - self.coupon_discount


# test_shop.py: two tests added to ShopTest
    def test_paid_counts_quantities(self):
        two = Order({"keyboard": 3000}, 0, {"keyboard": 2})
        self.assertEqual(two.paid, 6000)

    def test_two_keyboards_ship_free(self):
        two = Order({"keyboard": 3000}, 0, {"keyboard": 2})
        self.assertEqual(shipping_fee(two), 0)
```

The session gave `Order` a `quantities` field and made `paid` count it. `shipping_fee` reads `order.paid`, so it needed no change, and the session wrote a test to show that. The four old tests pass untouched, and the two new ones pass. The run prints `Ran 6 tests` and `OK`.

Two functions were missed. `full_refund_amount` and `payout_total` don't call `order.paid`. Each has its own copy of the sum, and neither copy knows about quantities. For an order of two keyboards, here is what the four functions return.

| Function | Returns | Should return |
|---|---|---|
| `order.paid` | `6000` | `6000` |
| `shipping_fee(order)` | `0` | `0` |
| `full_refund_amount(order)` | `3000` | `6000` |
| `payout_total([order])` | `3000` | `6000` |

A customer who pays $60.00 and sends the whole order back gets $30.00. The payout report tells the accountant that the payment provider owes the shop $30.00 for a $60.00 sale.

Nothing in front of you says so. The tests print `OK`. The diff lists two files, and both changes are sensible.

Here is the same change cut into four pieces. The list is written before any code changes.

```text
Piece 1. orders.py: Order gets quantities (missing means 1), and paid counts them.
         Check: the four old tests pass, and none of them was edited.
                New test: two keyboards at 3000, no coupon -> paid 6000.
Piece 2. shipping.py: it reads order.paid, so there may be nothing to change.
         Check: new test: two keyboards at 3000 -> shipping 0.
Piece 3. settlement.py: payout_total counts quantities.
         Check: new test: one order of two keyboards at 3000 -> payout_total 6000.
Piece 4. refunds.py: full_refund_amount counts quantities.
         Check: new test: two keyboards at 3000, whole order back -> refund 6000.
         Returning one keyboard of two needs a rule from the owner. It waits.
```

Pieces 3 and 4 are the two places the one-piece change missed. They are on the list because of a question you asked before any code changed: which lines read `prices`? In this repository one command answers it.

```sh
git grep -n "\.prices" -- "*.py"
```

```text
orders.py:12:        return sum(self.prices.values()) - self.coupon_discount
refunds.py:3:    return sum(order.prices.values()) - order.coupon_discount
settlement.py:3:    return sum(sum(o.prices.values()) - o.coupon_discount for o in orders)
```

The search prints three lines, and each one becomes a piece.

Piece 2 is on the list for a different reason. You know the shop ships free at $50.00, so you want to see two keyboards ship free even if no code has to change.

The last line of piece 4 isn't in any search result. No code handles the return of one keyboard out of two, because until today an order couldn't hold two. You add that line yourself, because you know customers send things back.

The list is ten lines long, and a person can read every one of them. You can ask "what's missing?" of a list that size, and you can show it to the accountant. You can't do either with a diff of twenty files.

## Prompt: one line for the whole change, and a prompt for piece 3 alone

The one-line prompt hands over everything at once.

```text
Let a customer buy more than one of the same item.
```

In the cut version you send two kinds of prompt. The first kind changes nothing. It asks for the list.

```text
I want to let a customer buy more than one of the same item.
Don't change anything yet. List every function that reads Order.prices
or would have to change, with file and line. For each one, say what
has to change and give one example I could check it with.
```

You correct the list, add what only you know, and save it in the repository as `PLAN.md`. Then you send one prompt for each piece. Here is the prompt for piece 3.

```text
Do piece 3 of PLAN.md and nothing else.

payout_total in settlement.py adds up prices without quantities.
Make it count them.

Change only settlement.py and test_shop.py.
Don't edit an existing test. If one fails, stop and tell me why.

Done when test_shop.py has this case and python3 -m unittest prints OK:
  one order of two keyboards at 3000, no coupon -> payout_total 6000

Then mark piece 3 done in PLAN.md, commit, and stop. Don't start piece 4.
```

This prompt has the parts from Chapter 11: the rule, the files, a don't, and a finish line. Three things are new.

The prompt names the piece and the plan file. A fresh session can do piece 3 knowing nothing about pieces 1 and 2 except what the repository says. The plan and the progress are in a file because the session that did piece 2 won't remember doing it.

The prompt forbids edits to existing tests. The old tests are what this piece is checked against. If the session has to change one of them to finish, either the piece is cut in the wrong place or the requirement changed. You want to hear about that before it happens.

The prompt says where to stop. A session that finishes piece 3 and sees piece 4 in the plan may go on to do it, and piece 4 has a line that waits for the owner.

> **[Run record slot: E13]** For the one-line prompt and for the four prompts: the files each session opened and changed, the tests it added, and its report. Date, tool, model.

## Evidence: with the two places missed, the tests print OK, and the examples for pieces 3 and 4 fail

I ran both versions of the change on the listing above.

In the one-piece version, the run prints `Ran 6 tests` and `OK`, and the four functions return the values in the table: `6000`, `0`, `3000`, and `3000`.

In the cut version, the new test for piece 3 fails with `AssertionError: 3000 != 6000` until `payout_total` returns `sum(o.paid for o in orders)`. The new test for piece 4 fails with the same message until `full_refund_amount` returns `order.paid`. After piece 4 the run prints `Ran 8 tests` and `OK`.

These runs show what each check can tell you. They don't show how often a session misses the two places when it gets the one-line prompt. I wrote that miss into the example by hand.

I also tested what a commit per piece buys. I committed after each piece and planted a slip in piece 2: the change that added the shipping test also turned `>=` into `>` in `shipping_fee`. All eight tests still passed after piece 4. Then I ran a check that the tests don't contain: a customer who paid exactly $50.00 ships free. It failed. `git bisect run` with that check tried two commits and named the commit of piece 2. <!-- run 2026-11-13, Git 2.50.1 --> Had the whole change been one commit, the same failure would have pointed at the whole change.

Experiment E13 will measure the part I wrote by hand. It gives the quantity change to fresh sessions in three forms. The first form is the one-line prompt. The second is one prompt that contains the whole plan, with all four pieces and their examples. The third is four prompts, one per piece, each sent to a fresh session. Each form runs 10 times.

A hidden test judges each run. A hidden test is a test the AI never sees, and I use it to decide whether the result is right. This one checks the four functions on the order of two keyboards and on the old orders. E13 counts the runs that pass. For each run that fails, it records how many changed lines the failure points at: the whole diff in the first two forms, and one piece's diff in the third.

The second form is there to separate what the plan does from what the cutting does. If the second and third forms pass equally often, then cutting adds nothing to the AI's success on a change this small, and the chapter's claim rests on what cutting does for the person who checks.

> **[Result slot: experiment E13]** Date, tool and model. For each form, out of 10 runs: passes, the function that failed in each failing run, and the number of changed lines the failure points at.

> **[Author case slot]** A real case in which a large task handed over in one piece stopped partway: what could be recovered from the files, and what was lost.

## What people do

- [ ] Before you hand over a change that touches more than one file, send the prompt that asks for the list and changes nothing. Read the list as the person who knows the business, and add the lines no search could find.
- [ ] Next to each piece, write the check before you write the prompt: the command you'll run and what it should print. If you can't write the check, the piece is too big or a rule hasn't been decided.
- [ ] Save the list in the repository. End every piece with a commit and a mark in the list, so a new session can start from the list.
- [ ] In the prompt for each piece, forbid edits to existing tests and say where to stop.
- [ ] When a check fails later, let Git find the piece. Run `git bisect start <bad commit> <good commit>`, then `git bisect run <your check command>`. Git runs the check on commits in between and prints the first one that fails. `git bisect reset` puts the repository back.

## Where it breaks

Pieces that are too small make you the bottleneck. If every ten-line change waits for you to run a command and read its output, the AI spends most of its time waiting. When the check is automatic, hand over more at once. A session can run the tests and the examples for pieces 1 to 3 without you and stop only when one fails. You still read the list first.

The number of lines is the wrong measure of a piece. Renaming a function across 200 files is a large change, and two commands check it: a search shows that the old name is gone, and the tests pass. Hand that over as one piece. A ten-line change to how refunds round can't be checked at all until someone decides the rule.

Some changes can't be cut so that the old tests pass at every step. A change to the shape of stored data is one, because old rows and new code have to work together for a while. Such a change needs a plan of its own, with a step that converts the data and a way back if that step fails. This chapter's example avoided the problem by giving `quantities` a default.

Every piece can pass while the whole fails. Each example in the plan checks one function. None of them follows one order of two keyboards from payment through shipping, refund, and payout. Add one such example as the last line of the plan.

Better models will finish larger pieces correctly, so the pieces can grow. How much a person can check after one piece doesn't grow with the model. It grows when the checks are automated.
