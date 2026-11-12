# Chapter 13. People decide what must never break when things run at once

## Scene

Forty cars cross a busy intersection every minute. No driver knows where the others are going or what their engines are doing. Nobody is hit, because every driver obeys two things that no driver decided: the lights and the lanes. Someone at the city's traffic office decided that north-south and east-west never get a green light at the same time.

One night the lights fail and blink yellow in every direction. Each driver still drives carefully. Each one slows down, looks, judges the gap, and goes. Every one of those decisions is reasonable when you look at it alone. Two of them meet in the middle of the intersection.

Your server handles two requests at the same moment, and three AI sessions are working in your repository right now. Who decided what must never happen at the same time?

## Claim

> When things run at once, a person decides what must never happen between them and writes it down as a check, because each request and each AI session sees only itself.

## Why: each request and each AI session is right when you look at it alone, and the failure happens between them

The code for one request reads the same whether one request runs or a thousand run at once. Nothing in the text of a function says that a second request for the same gift card can arrive while the first is still working.

A session that writes that function works from the prompt and the files. It tests the function the way it wrote it: one request, and then the next. Those tests pass. The failure needs two requests in a particular order, and that order is in no line the session read or ran.

A person who has run a shop for a year knows that it happens. A customer double-clicks the pay button. A phone and a laptop pay with the same gift card in the same second. An AI has no memory of the night it happened to you. So what you know has to be written down as a guarantee, in a sentence like this: "X never happens, even when two requests arrive at the same moment."

The same thing happens one level up, between AI sessions. You can run several sessions on one repository, because each one is cheap. Each session reads the files, decides, and writes. No session knows that the others exist. If two of them share one folder, one session's commit can sweep up the other's half-written file. If each works on its own branch, both can pass their tests and still break each other when the branches are merged.

In both cases every participant is right when you look at it alone. What goes wrong is between them, and none of them looks there. Someone has to decide what must never happen in that place. Whether a gift card may ever pay out more than it holds is a question about the business, so a person at the shop decides it.

## Code: two requests pass the same balance check, and one statement that closes the gap

The shop sells gift cards. Here is the version for people of the function that takes money off a card, with its tests. Amounts are integer cents, so `5000` is $50.00. The listing runs as shown. Two tests pass and the third fails.

```python
import sqlite3
import unittest


class InsufficientBalance(Exception):
    pass


# giftcards.py (the version for people)
def redeem(db, card_id, amount):
    """Take `amount` cents off a gift card."""
    (balance,) = db.execute(
        "SELECT balance FROM gift_cards WHERE id = ?", (card_id,)
    ).fetchone()
    if balance < amount:
        raise InsufficientBalance(f"card {card_id} has {balance}, needs {amount}")
    db.execute(
        "UPDATE gift_cards SET balance = ? WHERE id = ?", (balance - amount, card_id)
    )


# test_giftcards.py
def new_db():
    """A database with one gift card that holds $50.00."""
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE gift_cards (id TEXT PRIMARY KEY, balance INTEGER)")
    db.execute("INSERT INTO gift_cards VALUES ('card-1', 5000)")
    return db


def balance_of(db):
    return db.execute("SELECT balance FROM gift_cards WHERE id = 'card-1'").fetchone()[0]


class RedeemTest(unittest.TestCase):
    def test_redeem_lowers_the_balance(self):
        db = new_db()
        redeem(db, "card-1", 3000)
        self.assertEqual(balance_of(db), 2000)

    def test_redeem_refuses_more_than_the_balance(self):
        db = new_db()
        with self.assertRaises(InsufficientBalance):
            redeem(db, "card-1", 6000)
        self.assertEqual(balance_of(db), 5000)


class GapDB:
    """A connection that lets a second request run just before the first UPDATE."""

    def __init__(self, db, second):
        self.db, self.second = db, second

    def execute(self, sql, params=()):
        if sql.startswith("UPDATE") and self.second:
            second, self.second = self.second, None
            second()
        return self.db.execute(sql, params)


class GiftCardGuarantee(unittest.TestCase):
    def test_two_requests_at_once_never_pay_out_more_than_was_loaded(self):
        db = new_db()
        paid_out = []

        def request(conn):
            try:
                redeem(conn, "card-1", 3000)
                paid_out.append(3000)
            except InsufficientBalance:
                pass

        request(GapDB(db, lambda: request(db)))
        self.assertLessEqual(sum(paid_out), 5000)


if __name__ == "__main__":
    unittest.main()
```

`redeem` is easy to read. It reads the balance, checks it, and writes the new balance, in the order a person would explain it. The first two tests each send one request, and they pass.

The third test is the guarantee. Two requests each try to take $30.00 off a card that holds $50.00. `GapDB` places the second request in one exact spot: after the first request has checked the balance, and before the first request writes. The test uses no threads, so the second request lands in that spot on every run.

Here is what happens. The first request reads `5000` and passes the check. The second request reads `5000`, passes the check, and writes `2000`. Then the first request writes `2000` as well. Both requests succeed, and the test fails with `AssertionError: 6000 not less than or equal to 5000`.

The card's balance reads $20.00, which looks right. The shop has handed over $60.00 of goods against a $50.00 card.

The version for AI replaces `redeem` and nothing else.

```python
# giftcards.py (the version for AI)
def redeem(db, card_id, amount):
    """Take `amount` cents off a gift card."""
    # One statement on purpose. A SELECT followed by an UPDATE lets two requests
    # that arrive together both pass the balance check.
    done = db.execute(
        "UPDATE gift_cards SET balance = balance - ? WHERE id = ? AND balance >= ?",
        (amount, card_id, amount),
    )
    if done.rowcount == 0:
        raise InsufficientBalance(f"card {card_id} can't cover {amount}")
```

With this function all three tests pass. The check and the write are one statement, so there is no spot between them for a second request to land in. Whichever request's statement runs second finds a balance of `2000`, changes no row, and is refused.

The version for AI gives something up. Its error message can't say how much the card held, because the function never read the balance. Chapter 9 asks for that value in the error. Reading it would take a second statement, and the value could be out of date by the time the message is printed.

The comment is there for the reason Chapter 7 gives. The version for people reads more naturally, so a session asked to make this file easier to read may turn one statement back into three. The comment says why it is one, and the third test fails if a session does it anyway.

## Prompt: a prompt for the function, a prompt with the guarantee, and rules for several sessions in one repository

Here is a prompt that both versions of `redeem` satisfy to the letter.

```text
Add redeem(db, card_id, amount) to giftcards.py. Take the amount off the
card's balance, and refuse if the card doesn't have enough.
```

The version for people takes the amount off and refuses when the card doesn't have enough. The prompt asks for nothing more. Here is the prompt with the guarantee.

```text
Add redeem(db, card_id, amount) to giftcards.py.

Guarantee: a gift card never pays out more than was loaded onto it,
even when two requests for the same card arrive at the same moment.

Done when test_giftcards.py has a test in which a second request for
3000 runs between the first request's balance check and its write,
on a card that holds 5000, and at most one of the two succeeds.
Show me that test failing against a version that reads, checks, and
then writes, before you show it passing.
```

The guarantee is one sentence in the words of the shop. The finish line turns it into a test and names the gap. The last sentence asks to see the test fail first, for the reason Chapter 14 gives: a test that has never failed may be testing nothing.

The prompt doesn't say how to keep the guarantee. One statement, a lock, or a version number on the row would all pass the test. The session can choose. You decide what must hold and how you'll check it.

Several sessions in one repository need the same kind of sentence. These lines go in the rules file, the instruction file in your repository that the AI reads when it starts work.

```text
- Other AI sessions are working in this repository at the same time.
- Work only in your own worktree, on your own branch.
- Stage files by name. Don't run git add -A or git commit -a.
- Don't merge your branch. Tell me when it is ready.
```

Three decisions stay with you. Simple, separate tasks can run in parallel. Work on money, refunds, and stored data goes to one session at a time. And one person merges, one branch at a time, and runs the tests after every merge.

> **[Run record slot: E14]** For each prompt: the function the session wrote, the tests it wrote, and whether its report mentions two requests at once. Date, tool, model.

## Evidence: the two-request test fails on the version for people, and Git merges two passing branches into code that doesn't import

I ran the listing with each version of `redeem`. With the version for people, the run prints `Ran 3 tests` and `FAILED (failures=1)`. Both requests are paid, and the balance ends at `2000`. With the version for AI, the run prints `Ran 3 tests` and `OK`. One request is paid and the other is refused.

I also ran three small tests of sessions sharing a repository, using plain Git commands in place of sessions. <!-- run 2026-11-13, Git 2.50.1, Python 3.9.6 -->

In the first, two sessions share one folder. Session A is halfway through a function in `refunds.py`. Session B finishes a change to `shipping.py` and runs `git add -A` and `git commit`. B's commit lists two files, `refunds.py` and `shipping.py`. A's half-written function is now in the history under B's message, and `git status` shows A nothing to commit.

In the second, each session has its own worktree. B's commit lists one file, `shipping.py`, and A still sees its own unfinished change.

In the third, each session works on its own branch. Session A renames `shipping_fee` to `shipping_cost` and updates the test. Session B adds `checkout.py`, which calls `shipping_fee`. Each branch passes its own tests. Git merges both without reporting a conflict, because the two branches touched different files. The merged code fails on import: `ImportError: cannot import name 'shipping_fee' from 'shipping'`. The tests caught it only because they were run after the second merge.

These runs show that the failures exist and what each check catches. They don't show how often a session writes the version for people when the prompt is silent. Experiment E14 will count that. It gives the gift card task to fresh sessions in three forms: the first prompt above, the first prompt plus the guarantee sentence, and the full second prompt. Each form goes to 10 fresh sessions. A hidden test, which the sessions never see, runs a second request between every pair of database statements the first request makes, and checks that the card never pays out more than `5000`. E14 counts the sessions whose function lets both requests through, and the sessions that wrote a two-request test of their own.

> **[Result slot: experiment E14]** Date, tool and model. For each form, out of 10 sessions: functions that paid both requests, and sessions that wrote a test with two requests.

> **[Author case slot]** A real case from running several AI sessions in one repository: the rule the author added, and the incident that led to it.

## What people do

- [ ] For each feature that moves money or stock, write one line: "X never happens, even when two requests arrive at the same moment." A gift card never pays out more than it holds. A coupon is never used twice. An order is never charged twice. The last item in stock is never sold twice.
- [ ] Turn each line into a test that puts a second request in the gap. Ask the AI to write it, and watch it fail against the old code before you accept a fix.
- [ ] Put the guarantee in the prompt in the words of the business, with the two-request example in the finish line. Leave the mechanism to the session.
- [ ] Before a second session starts work in a repository, give each session its own worktree: `git worktree add ../shop-b -b session-b`. Add the lines above to the rules file.
- [ ] Merge one branch at a time, and run the tests after every merge. A merge without conflicts tells you that the branches changed different lines. It doesn't tell you that the code still works.

## Where it breaks

Every guarantee costs something. A lock makes the second request wait. One session at a time on the payment code means your other sessions stand in line. So decide what you don't guarantee, too. The "customers also bought" list can be a minute old. Two sessions can fix typos in the documentation at the same time.

The test covers the gap you thought of. It places one second request just before one `UPDATE`. It says nothing about three requests, about a server that stops between two statements, or about a database that is set up differently in production. For money, ask what the database itself guarantees, and test against the same kind of database you run.

Separate worktrees separate the files and nothing else. Two sessions on one machine can still share a test database, a port number, or a cache folder. Each shared thing needs the same question: what must never happen here at the same time?

Better models may notice a gap like this one more often, and some will ask about it. Noticing it doesn't settle what the shop wants. A second request can be refused, or it can wait, or the card can be allowed to go below zero and be settled later. A person at the shop decides which.
