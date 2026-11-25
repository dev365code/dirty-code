# Chapter 2. AI doesn't remember the code it read yesterday

## Scene

Say you spent yesterday afternoon with the AI on refunds. Take a customer who buys a $20.00 webcam and a $10.00 cable with a $5.00 coupon and pays $25.00. Refunding the whole order was easy.

Refunding one item took an hour in the chat. It ended in a rule: split what the customer paid across the items by list price, round each share down to the cent, and add any leftover cents to whichever item is refunded last. You stopped for the day before any of that rule was code.

This morning you open a new chat and ask for partial refunds. The function that comes back splits by list price and rounds down, as you'd hoped. It does nothing with the leftover cent, so a customer who returns both items gets back $24.99.

You start to type "we went over this yesterday" and stop. The session you went over it with is closed. This morning's session runs the same model, and it has never seen that chat.

So where is the rule you spent an hour working out?

## Claim

> If a rule you settled in yesterday's chat isn't written in a file, today's new session writes a reasonable rule of its own.

## Why: a new session starts with the prompt and the files, and yesterday's rule is in neither

The rule you worked out yesterday is in that session's chat, and a new session doesn't get that chat. A session is one conversation with the AI, from start to finish, and each one starts without the last.

What a new session does get is your prompt and the files: the code, its comments, the docs, the commit history, and the rules file (an instruction file kept in the repository that the AI reads when it starts work, such as `CLAUDE.md` or `AGENTS.md`). <!-- source: notes/sources.md, rules files and sessions --> Your rule is in none of them.

To see what a new session does have, give it this morning's prompt, and make the same request of a second reader: Dana, a developer who has been on your team for three years. Neither was in yesterday's chat.

What follows is how today's tools usually work. It isn't a transcript of one session. Each step gets a chapter of its own later in the book.

The prompt asks for a function, `partial_refund_amount`, and names its arguments. The prompt doesn't mention coupons. Dana hears the request and thinks of the support ticket that started all this: a customer returned one item from a coupon order, and a support agent, refunding it by hand, gave back its full list price.

The session has only the words of the prompt. It has never seen the ticket.

The session starts by searching. It doesn't know where anything is in your repository, so it searches for `refund` and opens the files that match. Dana just opens `refunds.py`.

If some refund math lived in `helpers.py` under the name `adjust()`, the search could miss that file. The search misses a file when the word `refund` appears nowhere in it and none of the files the search did find calls it.

Next the session reads, and it doesn't read everything. The AI can see only a limited amount of text at once (that amount is its context window), and every file the session reads takes time and uses up part of that amount. So the session usually reads the lines around its search hits and a few of the functions those lines call, and then it starts writing.

If the session never opens `settlement.py`, it doesn't learn that every refund also lowers a payout there, and that the refund and the payout have to match to the cent. Dana knows that without opening a file.

Then the session reaches three questions that the prompt didn't answer. Each item has a list price, and the coupon belongs to the whole order. So to refund one item, the function has to split the coupon between the items, decide what to do with a fraction of a cent, and decide which refund gets the leftover cent.

A session usually doesn't stop to ask you. It picks the answer that looks most plausible and keeps working. The session may even pick the same answer you did yesterday, and it has no way to know that its answer matches your rule.

The session checks its own work when it can: it runs the tests, reads the failures, and tries again. When no file says how to run the tests, the session tends to stop at a guess. Dana knows the test command by heart, and which test is flaky.

Here the tests run and pass, because no test says how a single item's refund is worked out.

Dana isn't a better reader than the AI. People forget, and they misremember: Dana may recall that ticket and get the amount wrong. But she can ask you about the rule this morning, and she's likely to still know it next week. The session can ask you questions too. But it asks only about a gap it notices, and no file tells it that yesterday's chat settled a rule, so it doesn't know there is something to ask. Dana knows the rule exists, so she knows to ask.

*Clean Code* writes for a reader like Dana: a developer on the team who remembers yesterday and can ask a colleague. A new session does neither. So this chapter asks for something that *Clean Code*'s reader didn't need: the rule written in a file that the session will read.

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

If you were in yesterday's chat, nothing is missing from this listing. You know how a single item will be refunded, and yesterday there was no partial-refund code to write that rule into. A new session reads one fact here: when a whole order comes back, the refund is what the customer paid. The test checks this one function. It checks nothing about a function that someone writes tomorrow. A test for `partial_refund_amount` could hold the rule too, but yesterday there was no such function to test (Chapter 14 covers that test).

If you had added the rule to yesterday's commit message, the rule would be in the repository too, but a session would see it only if it read the commit history.

The version for AI writes the rule into a function that a session working on refunds is likely to open. It replaces `full_refund_amount` in the listing, and nothing else changes.

```python
def full_refund_amount(order: Order) -> int:
    """Cents to refund when the whole order comes back."""
    # Partial refunds: split what the customer paid across the items by
    # list price, round each share down to the cent, and add any leftover
    # cents to whichever item is refunded last.
    return sum(order.prices.values()) - order.coupon_discount
```

Both versions behave the same and pass the same test. The only difference is that tomorrow's session can read the rule in the second version.

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

In the first copy, the session has to choose. It may well split by list price and round down, the way the function in the Scene did. It could drop the leftover cent, add it to the first refund, or add it to the last, and no file in the repository says which. Whichever the session does, the old test still passes, because that test calls only `full_refund_amount`.

The second and third copies differ in which sessions get to read the rule. A comment inside a function reaches a session that opens that function, or whose search lands on those lines. A search for `refund` returns the first and last lines of that comment and skips the middle one, which doesn't contain the word.

The rules file is read when a session starts, before the first search. Even then, a rules file is context the session reads, not a setting the tool enforces, so a session may not follow the entry every time. <!-- source: notes/sources.md, rules files and sessions --> Experiment E2 counts how often it does.

On 2026-11-22 I sent this prompt to fresh sessions of Codex CLI with gpt-6.2-sol. Each copy holds four files: the rules file, `orders.py`, `refunds.py`, and the test. In every copy, every session listed the files first and then printed all four with one `cat` command. So in the second copy every session read the comment, and in the third every session read the rules file.

A session in the first copy wrote a rule of its own. Its `partial_refund_amount` works out the share of the payment for all the items returned so far, this one included, and rounds it down. Then it subtracts the rounded share for the items returned before this one, and refunds the difference. Its docstring says, "Refund the increase in the cumulative share of the order payment." A session in the second copy wrote the rule in the comment: each share rounded down, and the item refunded last gets whatever is left of the payment. A session in the third copy wrote the same thing from the rules file.

## Evidence: every session that could read the rule followed it, and without the rule the sessions wrote a different one that agrees on two items

Experiment E2 uses the three copies from the Prompt section, and each gets the same prompt in 10 fresh sessions.

A hidden test judges each run. A hidden test is a test the AI never sees, and I use it to decide whether the result is right. This one calls `partial_refund_amount` to play out every order in which a customer could return the items of a coupon order one at a time, for one order that splits into whole cents and one that leaves cents over.

It gives each run one of four marks: "right" if every refund is the amount the rule gives, "over" if at any point the customer has been refunded more in total than the rule allows, "under" if the total is never over but at some point falls short, and "did not run" if the function is missing or raises an error.

If a copy gets zero misses in 10 runs, that shows only that misses are rare in that copy. A miss that happens one time in ten doesn't show up at all in 10 runs about 35% of the time.

I ran E2 on 2026-11-22 with Codex (gpt-6.2-sol), 10 fresh sessions per copy.

| Copy | Right | Over | Under | Did not run |
|---|---|---|---|---|
| Rule written nowhere | 9 | 1 | 0 | 0 |
| Rule in a comment in `full_refund_amount` | 10 | 0 | 0 | 0 |
| Rule in the rules file | 10 | 0 | 0 | 0 |

Every session in every copy opened the same four files. The median session made 4.5, 5.5, and 5 tool calls in the three copies, where a tool call is one shell command or one file edit.

The first row looks almost as good as the other two, but nine of the ten sessions in the first copy wrote the rule from the run above, and the tenth rounded each share to the nearest cent, which refunded one cent more than the rule on the first return. On any order of two items, the rule from the run above gives the same refunds as the written rule, so the hidden test's two orders couldn't tell them apart. The hidden test also played out a third order that it reported but didn't mark: three items at $10.00 with a $10.00 coupon, so the customer paid $20.00. There the written rule refunds `666`, `666`, and `668`, whatever order the items come back in. All ten sessions in the first copy differed from it, nine of them with `666`, `667`, and `667`. All twenty sessions in the other two copies matched it.

So the written rule was followed every time a session could read it. In this repository every session read every file, so the comment reached as many sessions as the rules file did. Telling the two places apart needs a repository large enough that a session doesn't read everything, and E2's copies aren't that large. Without the rule, each session wrote a reasonable rule of its own, and nothing in the old test showed that it differed from yesterday's.

## What people do

- [ ] Before you close a session, ask the AI: "What did you learn in this session that is not written in any file here?" Move what the next session will need into the rules file, or into a comment in the function it concerns.
- [ ] Open your rules file now and add the one thing you remember explaining to the AI twice this week. Keep the file short, because every session reads all of it before it starts.
- [ ] Pick a decision your code can't show, and ask three fresh sessions about it: "How do we split a coupon when one item comes back, and which file says so?" An answer that names no file means the decision isn't written where a session looks. If it does name a file, open the file and find the sentence, because a file name can be a guess too. A right answer is weak evidence for the same reason.
- [ ] Ask whoever has been on your team longest for three things every newcomer gets wrong once. Search the repository to see whether each is written down.

## Where it breaks

In this chapter, "yesterday" stands for "in an earlier session." If your tool lets you continue yesterday's conversation, you're still in the same session, and the AI still has yesterday's rule for as long as the whole conversation fits in its context window. A colleague who opens a session of their own doesn't get that conversation. And if you write a script to run once and delete, no later session will work on it, so there's nothing to write down. <!-- no source: continuing a conversation, written as a conditional -->

The AI is new to your repository. It is not new to programming. It can guess what a function does from its name because it already knows what common code looks like.

So a new session is likely to guess right where your code follows common practice, and likely to guess wrong where your team made its own decisions. A session may well split a coupon by list price unprompted. It can't know that your shop rounds down, or where the leftover cent goes, unless a file says so. <!-- no source: what a model already knows; the size comparison is not measured -->

If your tool carries memory from one session to the next, the AI does remember part of yesterday. Ask where the tool keeps that memory.

Unless someone retrains the model itself, a memory has to be text that the tool wrote down and that the new session reads. If the tool loads all of that text when a session starts, the memory works like a rules file, and every session spends time and context window reading it. If the tool looks a memory up only when the session needs it, a memory that the tool doesn't find helps the session no more than a memory nobody wrote.

You can open a rules file and correct it, and the rules file travels with the repository. Check whether you can do the same with your tool's memory. <!-- no source: memory features, written as a conditional -->

A context window large enough to hold the whole repository would shrink two of these problems: a session that reads only part of the repository, and a search that misses a file. Every new session would still read the whole repository again, at a cost in time and money, and it still couldn't read a rule that nobody wrote down.
