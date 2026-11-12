# Chapter 17. When the GPS is wrong: the moments people must read code

## Scene

The GPS says to turn left in 300 feet. You turn, and a hundred yards on, the road ends at an orange barrier. The bridge ahead has been closed for a month. The GPS redraws the route and tells you to make a U-turn and then turn left, back onto the same road.

Your passenger has lived here all her life. She doesn't look at the screen. "Go back to the gas station and take the river road," she says. "It comes out past the bridge."

For years the GPS has been right, and you stopped paying attention to the roads. If she weren't in the car, you would be following the screen in circles.

Your AI reads your code faster than you do, and it is usually right. On the night it is wrong, who in your company still knows the river road?

## Claim

> Keep a short list of the code a person must be able to read, shape that code so a person can follow it, and have people read it regularly, because on the night the AI's account is wrong, someone has to read the code itself.

## Why: some decisions can't be taken back, a person answers for them, and the AI's account of the code can be wrong

This book has assumed that you no longer read code line by line. There are moments when that stops being true.

One is an outage. Customers are being charged twice, and someone has to decide in the next ten minutes whether to switch payments off. Another is a security report. A test checks the inputs you thought of, and an attacker chooses the one you didn't, so "the tests pass" says little about the sign-in code. A third is a question from outside: an auditor or a customer asks how refunds are calculated and who checked it. In each of these, someone makes a decision that can't be taken back, and that someone is a person who will answer for it. A session can't answer for anything. Tomorrow it won't remember what it approved.

In those moments the AI is still your fastest reader, and you will ask it. What comes back is an account of the code, written by a session that read part of the repository (Chapter 2) and may have stopped one hop short of the line that matters (Chapter 8). On an ordinary day you check an account by running a test. In an outage, the failing case is one that no test covers. If a test had covered it, the bug wouldn't have shipped.

So a person reads. And that person is in the same position as the AI. Nobody on the team wrote this code, and nobody has read it since it was merged. The engineer who is woken at 3 a.m. opens the file for the first time, with no memory of it. Part II prepared the code for a reader with no memory, and most of it serves this reader too: a name that says what a function writes, one change in one place, a comment that gives the reason, an error line that carries the values, a page that says where things live.

The two readers differ in one respect that matters here. A person tires, reads slowly, and can follow only a few hundred lines in the time an outage allows. So for the short list of code where a person will have to decide something, the person's limits come first (Chapter 3).

## Code: a retry hidden in a decorator charges a customer twice without an error, and a `charge` that says everything in one place

Here is the payment code from Chapter 9 after someone made it more resilient. The listing joins `retries.py`, `payments.py`, and the tests. It runs as shown. One test passes and one fails.

```python
import functools
import unittest

APPROVE_TIMEOUT_SEC = 3


class PaymentError(Exception):
    """No approval came back for a payment request."""


# retries.py
def with_retries(times):
    """Call the function again when it raises TimeoutError, up to `times` calls in all."""

    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except TimeoutError:
                    if attempt == times - 1:
                        raise

        return wrapper

    return decorate


# payments.py
@with_retries(3)
def approve(order_id, amount_cents, provider):
    """Send one approval request to the payment provider."""
    return provider.approve(order_id, amount_cents, timeout=APPROVE_TIMEOUT_SEC)


def charge(order_id, amount_cents, provider):
    """Ask the payment provider to approve a charge. Return the approval ID."""
    try:
        return approve(order_id, amount_cents, provider)
    except TimeoutError as exc:
        raise PaymentError(
            "PAY-0303 approval request timed out"
            " | where=payments.charge"
            f" | order_id={order_id} amount_cents={amount_cents}"
            f" timeout_sec={APPROVE_TIMEOUT_SEC}"
            " | next=do not retry; call provider.lookup() first"
            " to see if the charge went through"
        ) from exc


# test_payments.py
class LateProvider:
    """Charges the card on every request. Its first replies arrive too late."""

    def __init__(self, late_replies):
        self.requests = []
        self.late_replies = late_replies

    def approve(self, order_id, amount_cents, timeout):
        self.requests.append((order_id, amount_cents))
        if len(self.requests) <= self.late_replies:
            raise TimeoutError
        return f"approval-{len(self.requests)}"


class ChargeTest(unittest.TestCase):
    def test_charge_returns_the_approval_id(self):
        provider = LateProvider(late_replies=0)
        self.assertEqual(charge(1042, 1500, provider), "approval-1")

    def test_a_timeout_never_sends_a_second_request(self):
        provider = LateProvider(late_replies=1)
        try:
            charge(1042, 1500, provider)
        except PaymentError:
            pass
        self.assertEqual(len(provider.requests), 1)


if __name__ == "__main__":
    unittest.main()
```

The retry is tidy work. It is written once in `retries.py`, and any function can use it by adding one line above its definition. In `charge`, one call changed: it now goes through `approve`.

Now it is 3 a.m. Eleven customers have written to say they were charged twice. The log shows no errors for their orders. You open `charge`. It makes one call, to `approve`. Its error message says "do not retry." Nothing in the function sends a second request.

The second request is sent from one line above `approve`. `@with_retries(3)` wraps the function, and the loop that repeats the call is in another file. The payment provider in this example charges the card every time a request reaches it. Its reply to the first request arrived after the 3-second limit, so the wrapper sent the request again. The second reply came back in time. `charge` returned an approval ID and logged nothing, and the card had been charged twice.

The second test asks the question you are asking at 3 a.m., and it fails with `AssertionError: 2 != 1`. Nobody had written that test before tonight.

Here is the version a person can follow. It replaces `retries.py`, `approve`, and `charge`.

```python
# payments.py
def charge(order_id, amount_cents, provider):
    """Ask the payment provider to approve a charge. Return the approval ID."""
    # One request and no retry, on purpose. A timeout means the reply was late.
    # It doesn't mean the card wasn't charged, and a second request can charge it again.
    try:
        return provider.approve(order_id, amount_cents, timeout=APPROVE_TIMEOUT_SEC)
    except TimeoutError as exc:
        raise PaymentError(
            "PAY-0303 approval request timed out"
            " | where=payments.charge"
            f" | order_id={order_id} amount_cents={amount_cents}"
            f" timeout_sec={APPROVE_TIMEOUT_SEC}"
            " | next=do not retry; call provider.lookup() first"
            " to see if the charge went through"
        ) from exc
```

With this version both tests pass. Everything that happens to a payment request is in one function, in the order it happens. A person who opens `charge` at 3 a.m. can answer "can this send two requests?" from the lines on the screen. The comment gives the reason, so the next session asked to make payments more resilient reads it before it adds a retry (Chapter 7).

This is the advice of Chapter 8, applied more strictly. In most code a layer that does a job today can stay. In code on the list of what people must read, behavior that changes what happens to money doesn't go into a decorator, a hook, or a parent class, even when that would be tidier.

## Prompt: a yes-or-no question at 3 a.m., and a prompt that asks for a route you can check

At 3 a.m. you will type something like this.

```text
Can charge() make the provider charge a customer twice for one order?
```

A session that opens `payments.py` and reads `charge` in the first version has reasons to answer no. The function makes one call, and its own error message says not to retry. If the session doesn't open `retries.py`, its answer is wrong, and it will be written as confidently as a right one. You can't tell the two apart by reading the answer.

This prompt asks for something you can check.

```text
Customers report being charged twice. Don't change any file.

Walk through what happens when provider.approve() raises TimeoutError
on the first request for one order. List every function and decorator
that runs, in order, with file and line. Quote the line that decides
whether another request is sent. Mark anything you inferred without
opening the file.

Then write a script that calls charge() with a fake provider whose
first reply times out, and prints how many requests the provider
received. Don't run a real payment.
```

The first half asks for a route through the code. Every step has a file and a line, so you can open each one and read it yourself. The answer tells you where to read, and you do the reading. Asking for decorators by name matters, because a decorator runs code that the function's body doesn't show.

The second half turns the question into a number from a run. If the script prints `2`, you have your answer whatever the walkthrough said.

You can ask for the same walkthrough on a quiet afternoon, one for each path on your list, and keep it next to the code. Read the lines it cites once while nothing is on fire. A walkthrough is a session's account, like any other. It is worth keeping after a person has checked it against the code.

> **[Run record slot: E16]** For each version of the payment code: the answer to the yes-or-no question, word for word, and the files the session opened before it answered. Date, tool, model.

## Evidence: with one late reply, the provider received two requests, and `charge` returned without an error

I ran both versions with a provider whose first reply is late. <!-- run 2026-11-13, Python 3.9.6 -->

In the first version the provider received 2 requests, and `charge` returned `approval-2`. No exception was raised, so nothing was logged. With three late replies the provider received 3 requests, and only then did `charge` raise `PAY-0303`. Its message told the reader not to retry after the code had already retried twice.

In the second version the provider received 1 request in both cases, and `charge` raised `PAY-0303` the first time.

These runs show what the hidden retry does. They don't show how often an AI gives the wrong answer to the 3 a.m. question. Experiment E16 will count that. It asks the yes-or-no question of 10 fresh sessions for each version, with no other instructions. For the first version the right answer is yes. E16 counts the sessions that answer no, and the sessions that opened `retries.py` before they answered.

> **[Result slot: experiment E16]** Date, tool and model. For each version, out of 10 sessions: right answers, and sessions that opened every file on the path before answering.

> **[Author case slot]** A real case in which an AI's account of what the code does was wrong, and a person found the fact by reading the code.

## What people do

- [ ] Write the list of code that a person must be able to read: code that moves money, sign-in and permissions, personal data, and anything that can't be undone, such as deleting records or emailing customers. Keep the list in the repository. A dozen files is a list. Half the repository isn't.
- [ ] For code on the list, a person reads every change before it merges, line by line. The list is short so that this stays affordable.
- [ ] On each path in the list, look for behavior that the function body doesn't show: decorators, hooks, parent classes, settings that change what the code does. Move it into the function, or put a comment at the call site that says where it is.
- [ ] For each path, ask for the walkthrough with file and line for one concrete case, and read the lines it cites. Ask for it again when the path changes.
- [ ] Twice a year, pick one path and have someone follow it from the request to the database without asking the AI. Count it as part of being on call.

## Where it breaks

If nobody reads code for a year, nobody can. The list in this chapter is short, and reading a dozen files twice a year won't keep a team able to read the other two thousand. A developer who has only ever prompted has no river road to remember. This is a cost of working the way this book describes, and the practice above reduces it without removing it.

A list that grows stops working. Every team that has an outage wants to add the file that caused it. If the list reaches half the repository, people are reading everything again, at the speed Chapter 1 started from. When you add a file, ask what decision a person would have to make from it.

Reading misses things too. People reviewed code for decades and bugs shipped anyway. Reading is here for the moment the other checks have already failed. It doesn't replace the tests of Chapter 14 or the second reader of Chapter 15.

The example assumes a provider that charges on every request. If the provider lets the shop mark a repeated request as the same charge, a retry is safe, and the decorator is fine. Whether that is true of your provider is exactly what a person has to know before the outage.

Better models will give a wrong account less often. The decision to switch payments off, and the answer to the auditor, will still belong to a person, and that person will need to have read the code at least once.
