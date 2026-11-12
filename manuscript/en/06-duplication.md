# Chapter 6. When a copy is safer than a shared function

## Scene

You stop at a parts store for wiper blades. The box says the blade fits your car and six others. That's a good arrangement: the maker tests one blade, and the store stocks one box for seven cars.

Suppose drivers of one of those cars complain that the blade chatters across their windshield. The engineers bend its frame to match that glass, and the complaints stop.

But there's only one blade, so the same bend ships to the other six cars. Nobody tested it on their windshields, because every complaint came from one car.

Your repository has parts like that blade: one function that seven places call. One day you'll ask an AI to change what it does for one of them.

When should seven callers share one function, and when is each safer with its own copy?

## Claim

> When a function's callers change for different reasons, give each its own copy, because an AI asked to change one may change them all.

## Why: one edit to a shared function can change every caller, and a session may have read only one

An AI has no memory, so a new session doesn't know which places call a shared function until it searches for them. Take `format_amount` in a small online shop's order server. It turns integer cents into text, so `3000` becomes `30.00`.

Seven places call it. Five are pages and emails that customers read. One is the settlement report, which the shop's accountant reads. One is the refund export, a file of refunds that goes to the payment provider.

Because the seven share one function, one edit to it can change what all seven produce. When all seven must stay alike, that's the benefit: you fix the function once and all seven are fixed.

*Clean Code* argues against duplication on these grounds: logic written in several places has to be changed in every one of them, and each is a chance to miss one. <!-- check against original --> This chapter keeps that argument for every case where the copies have to stay the same.

Now the accountant asks for commas in the report's amounts: `12,345.67` instead of `12345.67`. One edit to the shared function adds them.

The same edit also puts commas into the other six callers' output, unless whoever makes the edit remembers those callers. A developer on the team may remember that the refund export is one of them, or can ask someone who does.

A new session has your prompt and the files, and no memory of who calls what. The prompt mentions the settlement report, so the session is likely to open `settlement.py` and follow the call into `format_amount`. If so, it has read one of the seven callers.

Finding the other six takes a search the prompt didn't ask for, so whether it happens is up to the session. Even then, the warning about commas is written in `refunds.py`, which the session has to open and read.

The alternative is to give the settlement report its own copy, so an edit made for the report can't reach the other six callers.

For a person, copies were costly: three copies meant typing every fix three times and remembering that there were three. An AI can type the same fix three times at almost no cost. But the AI still has to find all three copies. When a fix belongs in all three, a copy that the session doesn't find keeps the old behavior.

To tell whether callers change for different reasons, ask who decides each caller's output. Here the shop's owner decides how a receipt looks, the accountant decides how the settlement report looks, and the payment provider decides the format of the refund export. Each of them asks for changes to one caller. Every time one of them asks, a session may make an edit like the comma edit, and that edit may reach the other six callers.

## Code: the settlement report and the refund export each get their own copy of the formatter

Here is that function with three of its seven callers: the receipt, the settlement report, and the refund export. This is the version for people.

```python
# money.py
def format_amount(cents):
    """Integer cents as dollars and cents: 3000 -> '30.00'."""
    sign = "-" if cents < 0 else ""
    dollars, rest = divmod(abs(cents), 100)
    return f"{sign}{dollars}.{rest:02d}"


# orders.py
def receipt_row(item, cents):
    """One row of the receipt email a customer gets."""
    return f"{item}: ${format_amount(cents)}"


# settlement.py
def payout_row(day, cents):
    """One row of the settlement report the shop's accountant reads."""
    return f"{day} payout {format_amount(cents)}"


# refunds.py
def refund_export_row(order_id, cents):
    """One row of the refund export. The provider splits rows on commas."""
    return f"{order_id},{format_amount(cents)}"
```

Each caller has a test. Put this block under the first one and the file runs as shown, printing `Ran 3 tests` and `OK`.

```python
# test_rows.py
import unittest


class RowTest(unittest.TestCase):
    def test_receipt_row(self):
        self.assertEqual(receipt_row("keyboard", 3000), "keyboard: $30.00")

    def test_payout_row(self):
        self.assertEqual(payout_row("Nov 2", 84550), "Nov 2 payout 845.50")

    def test_refund_export_row(self):
        self.assertEqual(refund_export_row(2318, 2700), "2318,27.00")


if __name__ == "__main__":
    unittest.main()
```

This is good code: the sign handling and the `divmod` are easy to get wrong, so the team wrote them once. To give the accountant the commas, one edit in `format_amount` is enough: `{dollars}` becomes `{dollars:,}`. Here is what each caller returns before and after, for amounts of $1,000 or more.

| Call | Before | After |
|---|---|---|
| `payout_row("Nov 2", 1234567)` | `Nov 2 payout 12345.67` | `Nov 2 payout 12,345.67` |
| `receipt_row("monitor", 125000)` | `monitor: $1250.00` | `monitor: $1,250.00` |
| `refund_export_row(2318, 125000)` | `2318,1250.00` | `2318,1,250.00` |

The report is right. The receipt changed too, though nobody asked for that. The refund export now has a comma inside the amount, so a program that splits the row on commas gets three fields: `2318`, `1`, and `250.00`.

All three tests still pass. Every amount in them is under $1,000, and an amount that small never gets a comma.

A fourth test that expects `2318,1250.00` for a $1,250.00 refund would catch the edit, failing with `AssertionError: '2318,1,250.00' != '2318,1250.00'`. But that test exists only if someone thought of four-digit refunds before the accountant thought of commas.

The version for AI gives the settlement report and the refund export their own copies. This block replaces the `settlement.py` and `refunds.py` sections of the listing, and the tests stay the same.

`format_amount` stays in `money.py` for the receipt and the four other customer-facing callers. Those five do change together: when the owner changes how a price looks to customers, the change is meant for all of them.

```python
# settlement.py
# Own copy of format_amount on purpose: the accountant sets this format.
def report_amount(cents):
    """Integer cents as dollars and cents: 3000 -> '30.00'."""
    sign = "-" if cents < 0 else ""
    dollars, rest = divmod(abs(cents), 100)
    return f"{sign}{dollars}.{rest:02d}"


def payout_row(day, cents):
    """One row of the settlement report the shop's accountant reads."""
    return f"{day} payout {report_amount(cents)}"


# refunds.py
# Own copy of format_amount on purpose: the provider sets this format.
def export_amount(cents):
    """Integer cents as dollars and cents: 3000 -> '30.00'."""
    sign = "-" if cents < 0 else ""
    dollars, rest = divmod(abs(cents), 100)
    return f"{sign}{dollars}.{rest:02d}"


def refund_export_row(order_id, cents):
    """One row of the refund export. The provider splits rows on commas."""
    return f"{order_id},{export_amount(cents)}"
```

Make the same edit in `report_amount`, and `payout_row` returns `Nov 2 payout 12,345.67`. The other two calls in the table return what they did before, because neither of them calls `report_amount`.

The comment above each copy says why the copy exists. A person or an AI tidying the repository then has a reason not to merge the three back into one (Chapter 7). The comment also names the original, so a search for `format_amount` returns the copies too.

## Prompt: a session can satisfy the same prompt in three ways, and the tests pass for all three

Both versions get the same prompt.

```text
On the settlement report, show amounts with thousands separators:
12,345.67 instead of 12345.67.
```

In the version for people, a session can satisfy it in at least three ways. It can edit `format_amount` in place, as above. It can add a parameter to `format_amount`, off by default, and turn it on from `payout_row`. Or it can leave `format_amount` alone and build the report's amount inside `settlement.py`.

The last two change nothing for the other six callers. All three put the commas in the report and pass the three tests.

So the test run can't tell you which of the three ways the session took, and the passing tests give the session no hint that the receipt and the refund export changed too. A session tends to stop once its tests pass (Chapter 14). I haven't measured how often a session takes the first way. The prompt leaves room for that choice: it says where the commas should appear and says nothing about the receipt or the refund export.

The parameter is what a careful developer might write, and it keeps the other callers safe today. It also leaves a switch in `format_amount` that only one caller uses. *Clean Code* advises against flag arguments like that one and recommends two functions instead. <!-- check against original --> A copy for the settlement report is that second function.

In the version for AI, the same three ways all end inside `settlement.py`, in code that only the settlement report runs.

> **[Run record slot: E5]** For each version: searches run, source files opened, the function edited, and whether the session searched for other callers first. Date, tool, model.

## Evidence: experiment E5 will count the callers that change when a session is asked to change one

Experiment E5 will build the order server two ways, with identical behavior and visible tests. It hasn't been run yet.

The first is the version for people: seven callers share `format_amount`, and `refunds.py` and `settlement.py` share `partial_refund_amount`, the rule for how much a returned item refunds. The second is the version for AI plus one copy this chapter advises against: `settlement.py` gets its own copy of that rule. With that extra copy, the experiment can also catch a case where copying goes wrong.

Each version gets two prompts, each in 10 fresh sessions: the one in the Prompt section, and a rule change, `Charge a $5.00 restocking fee: when an item comes back, refund $5.00 less than before.` A hidden test (a test the AI never sees, used to judge whether the result is right) judges each run.

After the first prompt it calls all seven callers with $27.00, $1,250.00, and -$5.00 and counts the callers, other than the settlement report, whose output changed. After the second it counts the runs in which the customer's refund differs from the amount taken off the payout.

I predict that other callers' output will change only in the first version, and that the refund and the payout will disagree only in the second. If a version gets zero failures in 10 runs, that shows only that the failure is uncommon.

> **[Result slot: experiment E5]** Date, tool and model. Out of 10 runs per version and prompt: runs where another caller's output changed, runs where refund and payout disagreed, and the kind of edit.

> **[Author case slot]** A real change where an AI's edit to a shared function changed another caller's output.

## What people do

- [ ] Pick three functions from wherever your shared helpers live (`utils.py`, `helpers.py`, `common/`). For each, run `grep -rn --include="*.py" "format_amount" .` with its name in place of `format_amount`, and beside each caller write who decides that caller's output. The search misses a call made through an import alias and a template that uses the function as a filter.
- [ ] Where one caller's answer differs from the others, send this with your own names: "Give settlement.py its own copy of format_amount, named report_amount, and call it from payout_row. Don't change any output or any other caller. Above the copy, add a comment that starts `# Own copy of format_amount on purpose:` and gives the reason." Then read the copy in the diff against the original function, since the tests cover only the amounts they use.
- [ ] Add this to your rules file (an instruction file kept in the repository that the AI reads when it starts work): "Before editing a function with more than one caller, list the callers and say which ones the change is for. If it isn't for all of them, change only the caller that needs it. Before moving code into a shared function, say who decides each caller's output." A session can skip these lines, and its search for callers has the same gaps as yours.

## Where it breaks

Don't copy a rule that two places must agree on. `partial_refund_amount` is one: `refunds.py` uses it to pay the customer, and `settlement.py` uses it to take the same amount off the payout.

If each had its own copy, a session asked to add a $5.00 restocking fee could edit the copy in `refunds.py` and never open `settlement.py`. A customer who returns a $40.00 lamp would get $35.00 back while the payout dropped by $40.00. This is the missed copy *Clean Code* warns about. <!-- check against original --> Tax rates and permission checks are rules of this kind.

A copy also duplicates anything inside it that really is one rule. All three formatters contain the same arithmetic, which turns cents into a sign, dollars, and two digits. A bug there has to be fixed three times.

The comment helps a session find the other two, but a copy made without the comment doesn't show up in that search. Three copies of five lines are manageable. Three copies of fifty lines are not. When callers differ in one detail of a long function, keep the function shared and make that detail a parameter.

Better models and tools should make the in-place edit rarer. A session that lists every caller before it edits a shared function would see the refund export.

The session would still need to know that the provider's program splits rows on commas. A search returns that fact only if someone wrote it down, as the docstring on `refund_export_row` does. <!-- no source: prediction -->
