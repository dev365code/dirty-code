# Chapter 14. How to check code without reading a line of it

## Scene

The check-engine light comes on. You can't tell what's wrong from the sound of the engine, but you can read the light, so you take the car to a mechanic. The rest of the time the light is off, and you don't think about the engine. You didn't install that light yourself. The carmaker did.

Code that an AI writes for you has no lights until someone installs them. The AI builds what you asked for, but it doesn't know which results you would call wrong. In this chapter, a warning light is an automated check that tells you the code is wrong without your reading the code. When the light stays off, the check has passed.

Suppose you installed a light yourself and have never once seen it come on. What does it tell you when it stays off?

## Claim

> A pass is evidence only if you have watched that same check fail.

## Why: the AI tends to stop when the checks pass, and a pass tells you only about what the check looked at

Whatever you told the AI in the last session is gone, and the next session starts from the files. So if you don't read the code, the right answer has to be written in a file. The file that holds it is a test: a test fails when the code returns something other than the answer you wrote down. For a person who doesn't read the code, the tests are the specification.

Hand the AI a failing test, and it tends to run the test, read what failed, and try again. If nothing else tells the AI when the work is finished, that loop tends to end when the checks pass. There are at least two ways to make a failing test pass: change the implementation, or change the test. If your prompt didn't say which, the AI decides.

A pass means three things and no more. The check ran on one machine. It looked at certain files. And what it looked at met the assertions in the check. A pass tells you nothing about a different machine, a file the check skipped, or an answer the check never asked about.

That leaves you two jobs. The first job is to say what the right answer is. If you don't, the AI supplies an expected value itself. The same session writes the code and the test, so the expected value is likely to come from the same reading of the task as the code. If that reading is wrong, code and test are wrong together, and they pass. The second job is to confirm that the test fails when the code is wrong.

Neither job means reading the implementation. You can read the assertion, and when there's only one test you should. But reading a test doesn't show you that the test actually runs, or that it fails when the answer is wrong. The rest of this chapter shows how to see both.

## Code: a weakened assertion and a fixed implementation both print OK

Your online shop added coupons after the refund code was written. You give the AI one example with its answer: an order has a $30.00 keyboard, a $20.00 mouse, and a $5.00 coupon, and when the keyboard comes back, the shop refunds $27.00. You ask for the test only, and you tell the AI to leave `partial_refund_amount` alone. The listing joins `orders.py`, `refunds.py`, and `test_refunds.py`, and it runs as shown. Amounts are integer cents, so `2700` is $27.00.

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
    """Cents to refund when one item comes back."""
    return order.prices[item]


# test_refunds.py
class PartialRefundTest(unittest.TestCase):
    def test_keyboard_refund_is_its_share_of_what_was_paid(self):
        # Protects: a coupon order refunds only what the customer paid.
        # List price $50.00, coupon $5.00, so the customer paid $45.00.
        # The $30.00 keyboard's share is 3000 * 4500 / 5000 = 2700 cents.
        order = Order({"keyboard": 3000, "mouse": 2000}, coupon_discount=500)
        self.assertEqual(partial_refund_amount(order, "keyboard", []), 2700)


if __name__ == "__main__":
    unittest.main()
```

The test fails with `AssertionError: 3000 != 2700`, because the implementation still refunds the list price. That's the failure you want. It comes from the assertion, and your number, 2700, is in the message. *Clean Code* teaches the same sequence: write the failing test first. <!-- check against original -->

Now you ask the AI to make the test pass. One of two changes could come back. Change A replaces the test class in the listing. Change B replaces `partial_refund_amount`.

```python
# Change A: edits the assertion in test_refunds.py. refunds.py is untouched.
class PartialRefundTest(unittest.TestCase):
    def test_keyboard_refund_is_its_share_of_what_was_paid(self):
        order = Order({"keyboard": 3000, "mouse": 2000}, coupon_discount=500)
        amount = partial_refund_amount(order, "keyboard", [])
        # Leave the split to the implementation.
        # Check that the refund never exceeds what the customer paid.
        self.assertGreater(amount, 0)
        self.assertLessEqual(amount, order.paid)


# Change B: edits partial_refund_amount in refunds.py. The test is untouched.
def partial_refund_amount(order, item, already_refunded):
    """Cents to refund: the item's share of what was paid, rounded down."""
    list_total = sum(order.prices.values())
    return order.prices[item] * order.paid // list_total
```

With either change, the test run prints the same thing: `Ran 1 test`, then `OK`. The output doesn't say which change you got.

Change A's two assertions can't tell a $30.00 refund from a $27.00 refund. So the code that overpays the customer by $3.00 is still there, and the test passes. Checking that a refund never exceeds what the customer paid is worth doing. But after Change A, nothing checks that returning the keyboard refunds $27.00.

How do you find out which change you got? Start with the diff's list of changed files. If `test_refunds.py` is in the list, the AI edited the test, and you ask why. The file list has a limit: it can't tell you whether a test was loose from the day it was written.

So do a second thing. Put the implementation back the way it was, and run the test that just passed. I'll call this the revert. If the test still passes against the old code, which refunds $30.00, then the pass never depended on the fix, and you throw the pass away. If the test fails against the old code, you have learned one thing: the test can tell the old code from the new code. You have not learned that the test accepts only the right answer.

The table shows why. Its first two rows are the original assertion and Change A's assertions. The third row is another assertion the AI could have written, `assertLessEqual(amount, 2700)`. The first two columns are the two implementations. The last two columns are implementations that return a wrong amount on purpose: `2500` and `2750`.

| Assertion | Original implementation (refunds $30.00) | Change B's implementation | Returns `2500` | Returns `2750` |
|---|---|---|---|---|
| Original (`== 2700`) | fails: `3000 != 2700` | passes | fails | fails |
| Change A (above 0, at most what was paid) | passes | passes | passes | passes |
| `assertLessEqual(amount, 2700)` | fails: `3000 not less than or equal to 2700` | passes | passes | fails |

Look at the `<= 2700` row. That assertion fails on the revert, and its failure message has your number in it. It still accepts a $25.00 refund.

The `2500` and `2750` columns are how you catch that. Each one is a wrong answer that a likely mistake would produce: $25.00 takes the whole coupon off the returned item, and $27.50 splits the coupon evenly between the two items. Make `partial_refund_amount` return one of them, run the tests, and see whether the test fails. I'll call this planting a wrong answer. Mutation testing tools do the same thing automatically. <!-- add source: mutation testing -->

Planting has the same limit as the revert. A failure shows only that the test rejects the value you planted. The `<= 2700` row rejects `2750` and accepts `2500`.

## Prompt: two sentences tell the AI to leave the test alone, and a step-by-step prompt lets you watch the test fail

When that first test fails, you could send either of these prompts.

```text
Make the tests pass.
```

```text
Fix the code, not the tests.
If you think a test has to change, tell me why and wait for my answer.
```

The first prompt asks only for a pass. Change A and Change B both satisfy it to the letter.

The second prompt tells the AI to give you a reason before it edits a test, and to wait. When the AI gives its reason, you settle one question: did the requirement change, or only the test? In Change A, the requirement didn't change. The shop still owes $27.00 for the keyboard, and only the assertion changed.

A new session hasn't heard what you said yesterday, so put the second prompt in your rules file (the instruction file in your repository that the AI reads when it starts work). Even with that prompt, the AI can still hand you Change A, so look at the diff's list of changed files every time.

The AI that wrote the change is also the one that does the reverting and the planting. When it pastes a failure message into the chat, you are reading its account of a run you didn't see. So have the AI stop after each step, and run the test command yourself at each stop.

```text
One step at a time. After each step, run the tests, show me the failing
test names and failure messages as printed (or say nothing failed), and wait.
1. Revert only the implementation you just changed.
2. Make partial_refund_amount return 2500.
3. Make partial_refund_amount return 2750.
4. Restore your change.
```

> **[Run record slot: E12]** All three prompts: files opened, files changed, the AI's report, and the same test command run by hand. Date, tool, model.

## Evidence: experiment E12 will count how often each prompt gets the assertion changed

Experiment E12 will send each of the first two prompts to 10 fresh sessions. Every session starts from the failing test in the Code section. E12 counts the runs in which the AI changed or deleted the original assertion. Tests that the AI adds don't count. E12 also counts the runs that pass a hidden test, which is a test the AI never sees and that I use to judge whether the result is right. In the sessions that pass, E12 compares the failure the AI reports after the revert step with the real output.

E12 hasn't been run yet. If a prompt gets zero runs with a changed assertion out of 10, that shows only that such a change is rare. Until E12 runs, the statement that an AI may edit the test is my deduction from how these tools read a prompt.

> **[Result slot: experiment E12]** Date, tool and model, and for each prompt out of 10 runs: runs with a changed assertion, runs that passed the hidden test, runs whose reported failure matched the real output.

> **[Author case slot]** Real cases in which a pass was not evidence: a check that passed only on one machine, a check that looked at no files, and a test that accepted wrong answers.

Two more kinds of empty pass are easy to try yourself.

A check can pass because it found nothing to look at. I ran one Python linter (ruff 0.17.2) in a folder where an ignore rule excluded every Python file. The linter printed `All checks passed!` and exited with 0. The only hint was one warning line saying that it found no Python files, and its normal output had no count of the files it checked. <!-- source: notes/sources.md, ruff with no files --> In the test output above, the count is `Ran 1 test`. Compare the count with the number you expect. A count of zero is not a pass, and neither is output with no count at all. Two more things hide behind that count: a test method whose name doesn't start with `test` never runs, and a skipped test still counts, showing up only in `OK (skipped=1)`.

A check can also pass because of what happens to be installed. A check can pass on your machine because a library is installed there that the project never declared. The same check then fails somewhere else, or passes there by luck. If you ask the AI what was installed, you get another report and a long list. Run the checks once in a fresh environment that has only the declared dependencies.

## What people do

- [ ] Before the AI writes code, give it one example with its answer in business terms: this order, this return, $27.00 back.
- [ ] Ask for the test alone ("Write only the test, not the fix.") and run it. The failure must come from the assertion, not from a typo or a missing module, and your number must be in the failure message.
- [ ] Put the prompt that begins "Fix the code, not the tests" in your rules file. When the AI says it's done, open the diff's list of changed files. If a test file is in the list, the AI should have given you a reason first.
- [ ] After a pass, send the step-by-step prompt and run the tests yourself at each stop. Steps 1 to 3 should fail. If step 1 passes, throw the pass away. If step 2 or 3 passes, the assertion is too loose, so ask for one that checks the exact value.
- [ ] In the test output, compare the count (`Ran 1 test`) with the number of tests you expect, and read anything in parentheses after `OK`. Once, run the checks in a fresh environment that has only the declared dependencies.

## Where it breaks

A test that you have watched fail still answers only the question it asks. An implementation that is nothing but `return 2700` passes the original assertion, the revert, and both planted values. One example checks one order and no other. What one example leaves open takes more examples and a second reader (Chapter 15).

Change B has a gap of the same kind. It ignores `already_refunded`, so it never adds a leftover cent to the last refund. The shop in Chapter 2 spent an hour deciding that rule, and this test never asked about it.

Your number can be wrong too. The revert and the planted values show that the test rejects `3000`, `2500`, and `2750`. They cannot show that $27.00 is what the shop owes.

A refactoring is meant to change no behavior. So the tests pass with the refactoring and pass with it reverted, and the revert tells you nothing. The evidence for a refactoring is that tests you have already watched fail kept passing, and that evidence covers only the orders those tests ask about.

No test in this chapter asks about speed, security (Chapter 17), or ease of use.

Better models may weaken assertions less often. A better model doesn't change what a pass covers: a linter that checks zero files can still print that all checks passed, whichever model wrote the code.
