# Chapter 2. AI doesn't remember the code it read yesterday

## Scene

Say you spent yesterday afternoon with the AI on refunds. Take a customer who buys a $20.00 webcam and a $10.00 cable with a $5.00 coupon and pays $25.00. Refunding the whole order was easy.

Refunding one item took an hour in the chat. It ended in a rule: split what the customer paid across the items by list price, round each share down to the cent, and add any leftover cents to whichever item is refunded last. You stopped for the day before any of that rule was code.

This morning you open a new chat and ask for partial refunds. The function that comes back splits by list price and rounds down, as you'd hoped. It does nothing with the leftover cent, so a customer who returns both items gets back $24.99.

You start to type "we went over this yesterday" and stop. The session you went over it with is closed. This morning's session runs the same model, and it has never seen that chat.

So where is the rule you spent an hour working out?

## Claim

> AI remembers nothing from yesterday, so all it knows about your code today is what you tell it and what it finds in your files.

## Why: a new session starts with the prompt and the files, and yesterday's rule is in neither

The rule you worked out yesterday is in that session's chat, and a new session doesn't get that chat. A session is one conversation with the AI, from start to finish, and each one starts without the last.

What a new session does get is your prompt and the files: the code, its comments, the docs, the commit history, and the rules file (an instruction file kept in the repository that the AI reads when it starts work, such as `CLAUDE.md` or `AGENTS.md`). <!-- source: notes/sources.md, rules files and sessions --> Your rule is in none of them.

To see what a new session does have, give it this morning's prompt, and make the same request of a second reader: Dana, a developer who has been on your team for three years. Neither was in yesterday's chat.

What follows is how today's tools usually work. It isn't a transcript of one session. Each step gets a chapter of its own later in the book.

The prompt asks for a function, `partial_refund_amount`, and names its arguments. It doesn't mention coupons. Dana hears the request and thinks of the support ticket that started all this: a customer returned one item from a coupon order, and a support agent, refunding it by hand, gave back its full list price.

The session has only the words of the prompt. It has never seen the ticket.

Its first move is to search. It doesn't know where anything is, so it searches for `refund` and opens the files that match. Dana just opens `refunds.py`.

If some refund math lived in `helpers.py` under the name `adjust()`, the search could miss it. That happens when the word `refund` appears nowhere in the file and none of the files the search did find leads there.

Next it reads, and it doesn't read everything. Its context window (the amount of text the AI can see at once) is limited, and reading costs time and fills it. So it usually reads around its search hits and a few of the functions they call, then starts writing.

If it never opens `settlement.py`, it doesn't learn that every refund changes a payout there, and that the two have to agree to the cent. Dana knows that without opening a file.

Then it reaches what the prompt left open. Each item has a list price, and the coupon belongs to the whole order. To refund one item, the function has to split the coupon somehow, do something with a fraction of a cent, and put the leftover cent somewhere.

A session usually doesn't stop to ask. It picks the answer that looks most plausible and keeps working. It may even pick yours, and it has no way to know that it did.

It checks its work when it can: it runs the tests, reads the failures, and tries again. When nothing says how to run the tests, it tends to stop at a guess. Dana knows the test command by heart, and which test is flaky.

Here the tests run and pass, because no test says how a single item's refund is worked out.

None of this makes Dana the better reader. People forget, and they misremember: she may recall that ticket and get the amount wrong. But she can ask you about the rule this morning, and she's likely to still know it next week. Yesterday's memory and the colleague at the next desk cost a person nothing, and the AI has neither.

## Code: yesterday's rule reaches a new session only if a file states it

Yesterday's session left one function and one test in the repository, for refunding a whole order. The rule for a single item stayed in the chat. Here is what a new session finds: the order model from `orders.py`, the function from `refunds.py`, and the test, joined into one listing that runs as shown. This is the version for people. Amounts are integer cents, so `2500` is $25.00.

```python
import unittest
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    prices: dict[str, int]  # item name -> list price in cents, before coupon
    coupon_discount: int    # coupon discount on the whole order, in cents


def full_refund_amount(order: Order) -> int:
    """Cents to refund when the whole order comes back."""
    return sum(order.prices.values()) - order.coupon_discount


class FullRefundAmountTest(unittest.TestCase):
    def test_whole_order_refunds_what_the_customer_paid(self):
        prices = {"webcam": 2000, "cable": 1000}
        order = Order(prices, coupon_discount=500)
        self.assertEqual(full_refund_amount(order), 2500)


if __name__ == "__main__":
    unittest.main()
```

If you were in yesterday's chat, nothing is missing. You know how a single item will be refunded, and there was no code yet to write it into. A new session reads one fact here: when a whole order comes back, the refund is what the customer paid. The test guards this one function and is silent about a function written tomorrow. A test for `partial_refund_amount` could hold the rule too, but yesterday there was no such function to test (Chapter 14 covers that test).

If you'd added the rule to yesterday's commit message, it would be in the repository too, but a session would see it only by reading the commit history.

The version for AI writes the rule into a function that a session working on refunds is likely to open. It replaces `full_refund_amount` in the listing, and nothing else changes.

```python
def full_refund_amount(order: Order) -> int:
    """Cents to refund when the whole order comes back."""
    # Partial refunds: split what the customer paid across the items by
    # list price, round each share down to the cent, and add any leftover
    # cents to whichever item is refunded last.
    return sum(order.prices.values()) - order.coupon_discount
```

Both versions behave the same and pass the same test. They differ only in what tomorrow's session can read here.

## Prompt: one prompt goes to three copies of the repository that differ only in where the rule is written

This morning's prompt goes to three copies of the repository, word for word.

```text
Add partial refunds. Write partial_refund_amount(order, item,
already_refunded): the cents to refund when one item of an order
comes back. already_refunded lists the items refunded before it.
```

In the first copy the rule is written nowhere. The second has the comment from the Code section. The third has no comment, and its rules file has one more entry than the other two, added before you closed yesterday's session.

```text
- Run the tests with: python3 -m unittest
- All amounts are integer cents.
- Partial refunds: split what the customer paid across the items by
  list price, round each share down to the cent, and add any leftover
  cents to whichever item is refunded last.
```

In the first copy, the session has to choose. It may well split by list price and round down, the way the function in the Scene did. It could drop the leftover cent, add it to the first refund, or add it to the last, and nothing in the repository picks one. Whichever it does, the old test still passes, because that test calls only `full_refund_amount`.

The second and third copies differ in which sessions get to read the rule. A comment inside a function reaches a session that opens that function, or whose search lands on those lines. A search for `refund` returns the first and last lines of that comment and skips the middle one, which doesn't contain the word.

The rules file is read when a session starts, before the first search. Even then, a rules file is context the session reads, not a setting the tool enforces, so a session may not follow the entry every time. <!-- source: notes/sources.md, rules files and sessions --> Experiment E2 counts how often it does.

> **[Run record slot: E2]** For each copy: files opened, commands run, and the `partial_refund_amount` written. Date, tool, and model.

## Evidence: experiment E2 will count how many of 10 fresh sessions follow the rule in each copy

Experiment E2 uses the three copies from the Prompt section, and each gets the same prompt in 10 fresh sessions. It hasn't been run yet.

The verdict comes from a hidden test (a test the AI never sees, used to judge whether the result is right). It calls `partial_refund_amount` to play out every sequence in which a customer could return a coupon order one item at a time, for one order that splits into whole cents and one that leaves cents over.

It gives each run one of four marks: "right" if every refund is the amount the rule gives, "over" if at any point the customer has been refunded more in total than the rule allows, "under" if the total is never over but at some point falls short, and "did not run" if the function is missing or raises an error.

Zero misses in 10 runs would mean "rare" and nothing stronger, because a miss that happens one time in ten stays hidden in 10 runs about 35% of the time.

> **[Result slot: experiment E2]** Date, tool and model, and for each copy the runs marked right, over, under, and did not run out of 10, with files opened and tool calls per session.

## What people do

- [ ] Before you close a session, ask the AI: "What did you learn in this session that is not written in any file here?" Move what the next session will need into the rules file, or into a comment in the function it concerns.
- [ ] Open your rules file now and add the one thing you remember explaining to the AI twice this week. Keep the file short, because every session reads all of it before it starts.
- [ ] Pick a decision your code can't show, and ask three fresh sessions about it: "How do we split a coupon when one item comes back, and which file says so?" An answer that names no file means the decision isn't written where a session looks. If it does name a file, open the file and find the sentence, because a file name can be a guess too. A right answer is weak evidence for the same reason.
- [ ] Ask whoever has been on your team longest for three things every newcomer gets wrong once. Search the repository to see whether each is written down.

## Where it breaks

In this chapter, "yesterday" stands for "in an earlier session." If your tool lets you continue yesterday's conversation, you're still in the same session, and the claim doesn't apply for as long as the whole conversation still fits in the context window. That conversation still isn't in the session a colleague opens. And if you write a script to run once and delete, no later session will work on it, so there's nothing to write down. <!-- no source: continuing a conversation, written as a conditional -->

The AI is new to your repository. It is not new to programming. It can guess what a function does from its name because it already knows what common code looks like.

So this chapter's problem is likely small where your code follows common practice and large where your team made its own decisions. A session may well split a coupon by list price unprompted. It can't know that your shop rounds down, or where the leftover cent goes, unless a file says so. <!-- no source: what a model already knows; the size comparison is not measured -->

If your tool carries memory from one session to the next, "it doesn't remember yesterday" is less true for you. Ask where that memory lives.

Unless the model itself is retrained, a memory has to be something written down that the new session reads. If the tool loads all of it when a session starts, it works like a rules file, and every session pays to read it. If the tool looks things up only when it needs them, a memory it doesn't find is as good as unwritten.

You can open a rules file and correct it, and it travels with the repository. Check whether the same holds for the memory. <!-- no source: memory features, written as a conditional -->

Better models should make two of these problems smaller: reading only part of the repository, and searches that miss. If a context window can hold the whole repository, and the tool loads all of it, the session will have read `settlement.py`.

Two things remain. Reading everything has to happen again in every session, and it costs each time. And no window, however large, holds what was never written down.
