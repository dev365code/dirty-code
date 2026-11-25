# Chapter 8. A layer that does no job today: three payment classes become one table

## Claim

> Add a layer between a call and the code that runs only when the layer does a job today.

## Why: a session has to follow each hop by reading, and it can take a wrong turn at any of them

To change what a program does, a session first has to find the line that decides it. Sometimes that line is right where the call is. Often it isn't. The call goes to a function, the function looks something up in a dictionary, the dictionary returns a class, and the class inherits the method from its parent. I'll call each of those steps a hop: a place where the reader has to go and read another definition to learn what happens next.

A developer who has worked in the code for a year doesn't follow the hops. The developer knows that card payments end up in `CardStrategy`, and goes straight there.

A new session knows nothing about the route. It has to read its way along, one hop at a time. At every hop, two things can go wrong.

The first is that the session takes a wrong turn. A search for the method name returns the parent class and three subclasses, and the session has to work out which one runs for a card payment. If it picks the wrong one, every edit it makes from there is a correct edit in the wrong place.

The second is that the session stops early. It reaches a class that has the right name and a plausible-looking attribute, and that looks like the destination. Following one more hop costs another read, and each read uses up part of the session's context window. The session has no way to know that one more hop would have changed the answer.

None of this means layers are a mistake: *Clean Code* hides a choice between types behind a factory, and that layer does a job when the classes do different work. <!-- check against original --> This chapter is about the layers that are there because they might be useful one day.

## Code: three payment classes that differ in one number become one table

The shop accepts three ways to pay: card, bank transfer, and gift card. Here is the version for people. The listing joins `payments.py` and `checkout.py`, and it runs as shown.

```python
"""payments.py (the version for people)"""


class PaymentStrategy:
    """One subclass per way to pay. A subclass overrides what differs."""

    fee_rate_percent = 0

    def amount_to_charge(self, order_total):
        """Cents to charge: the order total plus this method's fee."""
        return order_total + order_total * self.fee_rate_percent // 100


class CardStrategy(PaymentStrategy):
    pass


class BankTransferStrategy(PaymentStrategy):
    pass


class GiftCardStrategy(PaymentStrategy):
    pass


STRATEGIES = {
    "card": CardStrategy,
    "bank": BankTransferStrategy,
    "gift": GiftCardStrategy,
}


def strategy_for(method):
    """Factory: the strategy object for a payment method name."""
    return STRATEGIES[method]()


# checkout.py
def checkout_total(order_total, method):
    """Cents to charge for an order paid with the given method."""
    return strategy_for(method).amount_to_charge(order_total)
```

Amounts are integer cents, so `10000` is $100.00. Today no payment method has a fee, and `checkout_total(10000, "card")` returns `10000`.

This is a well-known design, and it's laid out with care. Each way to pay has its own class. The dictionary is the only place that maps a name to a class. When card payments need different behavior someday, there's a class waiting for it.

Count the hops from `checkout_total` to the number that decides the fee. The call goes to `strategy_for`. That function looks the name up in `STRATEGIES`. The dictionary gives back `CardStrategy`, which is empty. The number, `fee_rate_percent = 0`, is in the parent class. That's three hops: a function, a dictionary, and a parent class.

Now the shop decides that card payments carry a 3% fee. Two edits could come back, and they look alike.

```python
# Edit 1: in CardStrategy
class CardStrategy(PaymentStrategy):
    fee_rate_percent = 3


# Edit 2: in PaymentStrategy
class PaymentStrategy:
    fee_rate_percent = 3
```

Edit 1 is right. Edit 2 changes the number where the number is written, which is in the parent class. Here is what `checkout_total(10000, method)` returns after each edit.

| Method | Before | After Edit 1 | After Edit 2 |
|---|---|---|---|
| `"card"` | `10000` | `10300` | `10300` |
| `"bank"` | `10000` | `10000` | `10300` |
| `"gift"` | `10000` | `10000` | `10300` |

After Edit 2, a customer who pays by bank transfer is charged $103.00 for a $100.00 order. A test that checks the card total passes after either edit, because the card total is `10300` both times. A test for bank transfers would catch Edit 2. That test exists only if someone wrote it before the fee was added.

The version for AI removes the hops. The three classes differed in one number, so the number goes into a table next to the function that uses it.

```python
"""checkout.py (the version for AI)"""

# Fee for each payment method, in percent of the order total.
FEE_RATE_PERCENT = {"card": 0, "bank": 0, "gift": 0}


def checkout_total(order_total, method):
    """Cents to charge for an order paid with the given method."""
    fee = order_total * FEE_RATE_PERCENT[method] // 100
    return order_total + fee
```

Both versions return the same totals for all three methods. In this version, adding the card fee means changing `"card": 0` to `"card": 3`. The session that makes the change sees `"bank": 0` and `"gift": 0` on the same line, so it can see what it is not changing. From `checkout_total` to the number there are no hops: the table sits right above the function, and the number is in it.

The version for AI gives something up. It has no class for card payments to grow into. If card payments later need a step that the other methods don't, such as asking the customer's bank to confirm the charge, someone will have to bring a class back. That day the class will do a job. Today it holds a number.

## Prompt: one sentence about card fees, and the session has to find where the fee lives

Both versions get the same prompt.

```text
Card payments now carry a 3% fee. Add it.
```

In the version for people, a session is likely to search for `card` or `fee`. The search for `card` finds `CardStrategy`, which contains only `pass`. The search for `fee` finds `fee_rate_percent = 0` in `PaymentStrategy`.

From there the session has to decide where the 3 goes. It can add a line to the empty class, which is Edit 1. It can change the line that already holds the number, which is Edit 2. It can also skip both and add `if method == "card":` to `checkout_total`. That third way charges the right amounts. It also leaves the fee outside the class that was built to hold it, where the next reader won't look.

Edit 2 is the mistake this chapter is about. The session followed two hops correctly, found a line that looks like the answer, and changed it. To avoid Edit 2, the session has to know that the parent class's number is shared by all three methods. It learns that only by reading the two other subclasses.

In the version for AI, the search for `fee` finds one dictionary with three entries, and the prompt names one of them.

I ran this prompt on 2026-11-22 in fresh sessions of Claude Code with Claude Opus 5.5 at its highest effort setting. In the version for people, one session didn't search at all. The repository is small, so it listed the files and read all three. It added `fee_rate_percent = 3` to `CardStrategy`, which is Edit 1, and updated the old card test. Afterward the totals were `10300` for a card and `10000` for a bank transfer and for a gift card. Its report said, "The base class already handles per-method fees, so checkout uses the new rate without any other changes." In the version for AI, a session changed the card's entry in the fee table from 0 to 3.

## Evidence: at 0, 1, and 3 hops, all 120 sessions put the fee on the card and nowhere else

Experiment E7 builds the checkout code in three versions that return the same totals. In the first version the fee table sits next to `checkout_total`, as in the version for AI, so there are no hops. In the second the table is in another module behind one function call, which is one hop. The third is the version for people, with three hops.

Each version gets the prompt above in 10 fresh sessions. A hidden test judges each session. It checks the total for all three payment methods: `10300` for a card, and `10000` for a bank transfer and for a gift card. E7 counts the sessions that pass, the sessions that changed the total for a method the prompt didn't name, and the files each session opened.

This example is small, and a session may well read all of it and choose Edit 1 every time. So I ran E7 on 2026-11-22 with Claude Code in two repositories: this chapter's files, with Claude Opus 5.5 at its highest effort setting, and the large repository of Appendix A, where the checkout code sits among 210 other modules, with Claude Haiku 5.5, Claude Sonnet 5.5, and Claude Opus 5.5 at their default settings. Each version went to 10 fresh sessions per model, 120 sessions in all.

All 120 sessions passed the hidden test, and none changed the total for a bank transfer or a gift card. In the three-hop version, all 40 made Edit 1 and put `fee_rate_percent = 3` in `CardStrategy`. The number of files a session opened didn't rise with the hops in any steady way. In the large repository the median Haiku session opened 5.5, 5.5, and 6 files at 0, 1, and 3 hops, and the median Opus session 5, 5, and 3.5.

Something did go wrong, though not where I was looking. The old test said that a card payment of `10000` totals `10000`. Sonnet often added the fee and left that test failing: when the session ended, the full test suite failed in 5, 6, and 8 of its 10 runs at 0, 1, and 3 hops. Haiku and Opus updated the test in every run.

Before the runs, the experiment plan said that if the three versions scored the same, the claim would need a condition about how much code surrounds the hops. They scored the same in a repository of 518 files as well, so size isn't the condition. In this example the hops are short, and each class says what it holds, so a session that follows them lands on the right line. I haven't measured longer chains, or classes whose names say less.

## Where this chapter's opinion differs from *Clean Code*: a layer has to do a job today

*Clean Code* prefers polymorphism to code that switches on a type: hide the choice behind a factory, and let each type's class hold its own behavior. <!-- check against original --> This chapter replaces the three payment classes with a table, because today the classes differ in one number and hold no behavior of their own. It keeps a layer that does a job today: classes whose code really differs, or an argument through which a test passes in a fake. Each hop is a place where a session can stop early or turn the wrong way, as the Why section says, so a layer has to be worth that.

How far the experiment backs this opinion: not yet. No run failed at any number of hops, and the conditions under which the hops might matter, a longer chain or classes whose names say less, haven't been tested.

<!-- [Author case slot] A real change in which an AI edited a parent class or a shared layer and changed behavior the prompt didn't mention. -->

## What people do

- [ ] Pick one value your business cares about, such as a fee or a limit. Ask the AI: "Start from the function that handles checkout. List every function, dictionary, and class you pass through to reach the line that sets the card fee. Quote the file and line for each." Count the items in its answer. Then open each quoted line yourself, because the list is the AI's report and not the code.
- [ ] For each layer on that list, ask what job it does today. A layer does a job if two implementations really differ in behavior, or if a test swaps in a fake through it. If the answer is "we might need it later," mark the layer.
- [ ] For one marked layer, send this with your own names: "Replace the three strategy classes with a table next to checkout_total. Don't change any total. Run the tests before and after, and show me both results."
- [ ] Before you merge an AI's change to a class that has subclasses or a parent, run the code once for every branch, not only the branch the prompt named. For the example, that means the totals for card, bank transfer, and gift card.

## Where it breaks

Keep the layer when the implementations do different work. Suppose card payments must ask the customer's bank to confirm, bank transfers must wait for a deposit, and gift cards must check a balance. Then each class holds real code, and putting all three inside one function would make that function long and hard to change. Three hops that lead to three different pieces of code are worth what they cost.

Keep the layer when a test needs it. In Chapter 9, `charge` takes the payment provider as an argument. That's a hop too, and it lets a test pass in a fake provider that times out on purpose. Without it, nobody could test the timeout.

Some hops aren't yours to remove. A web framework decides how a request reaches your handler, and you can't flatten its layers. For those, write the route down where a session starts reading: a comment at the call site that names the class and file where the work happens.

A session that can ask a language server "where is this defined?" follows a direct call in one step and gets the right answer. A class chosen by a string in a dictionary, as in `STRATEGIES[method]`, is chosen while the program runs, and a tool that reads the code without running it can't always tell which class that will be.
