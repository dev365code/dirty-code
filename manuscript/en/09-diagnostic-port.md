# Chapter 9. Install a diagnostic port: errors and logs for AI to read

## Scene

Something is off with your car, so you pop the hood. All you see is a plastic cover, and it tells you nothing. You take the car to a mechanic. The mechanic plugs a scan tool into the diagnostic port, and the screen shows P0303. That's the fault code for a misfire in cylinder 3.

Nobody has looked inside the engine yet, and the mechanic already knows which cylinder to check first. The car reported its own state in a form her tool could read. A car that reported nothing would have left her in front of the cover, guessing.

An AI that comes to fix your program works the same way: from what the program reports. When your program breaks, what does it report?

## Claim

> An error message should carry the values and the next step, because for a one-time failure it may be all the AI gets.

## Why: a person got the rest of the story from screens and memory, and a new AI session may have neither

A person on call read an error line already knowing the system around it. Someone who read `approval request timed out` in the production log used the timestamp on that line to find the order in the shop's admin site, then checked the payment provider's dashboard. They recalled what the team did last time, or asked the colleague who wrote the payment code. So a short line was a sound choice: the rest was a click or a question away.

A new session has no last time to recall and no colleague to ask. Its tools mostly return text, and a page that only a browser renders can be out of their reach. So for a failure that happened once in production, what the program wrote at the time may be all the session has.

A program writes out its own state, as text a machine can read, in three places: error messages, logs, and the exit code (0 means success). This chapter calls those three places the program's **diagnostic port**.

A diagnostic port is worth wording carefully only if two things hold. Tools can reach what the program writes. And what the program writes is true.

The second condition fails more quietly than you'd expect. A script that catches an exception, prints the message, and ends normally still exits with 0, and 0 says success. Or take these two lines. Each is meant to record the exit code of `cmd`.

```sh
cmd; echo "name $(basename "$f") rc=$?"
cmd; rc=$?; echo "name $(basename "$f") rc=$rc"
```

`$?` holds the exit code of the most recent command. In bash and zsh, `basename` runs inside that string before the shell reads `$?`. So the first line prints the exit code of `basename`, which is always 0, whatever `cmd` did. The second line captures the exit code of `cmd` first and prints the right number.

*Clean Code* already advises giving an exception enough context to find where an error came from, with a message that says what was attempted and how it failed. <!-- check against original --> This chapter keeps that advice and adds what the person on call looked up or remembered.

## Code: the timeout line gains the values, the next step, and an error code to search for

The shop asks its payment provider to approve a charge, and no answer comes within 3 seconds. Here's the version for people. It needs Python 3.10 or later, because before 3.10 a socket timeout isn't a `TimeoutError`.

```python
"""payments.py (the version for people)"""

APPROVE_TIMEOUT_SEC = 3


class PaymentError(Exception):
    """No approval came back for a payment request."""


def charge(order_id, amount_cents, provider):
    """Ask the payment provider to approve a charge. Return the approval ID."""
    try:
        return provider.approve(
            order_id, amount_cents, timeout=APPROVE_TIMEOUT_SEC
        )
    except TimeoutError as exc:
        raise PaymentError("approval request timed out") from exc
```

Order 1042, for $15.00, hits the timeout. Whoever catches the exception logs its name and message, then the stack trace. After the timestamp, the line reads:

```text
PaymentError: approval request timed out
```

A careful developer writes it this way. `from exc` marks the `TimeoutError` as the direct cause, and the stack trace shows both exceptions and the functions they passed through. One fact is in no file and on no screen. A timeout is not a refusal. The provider may have approved the charge while its answer never arrived, and a second request can then charge the customer twice. Everyone on this team knows that, and nothing in the code says so.

If your team already logs the order ID as a structured field, the values row in the table below is covered. What's left for you to add is the error code and `next=`.

The version for AI changes one statement, the `raise`.

```python
"""payments.py (the version for AI)"""

APPROVE_TIMEOUT_SEC = 3


class PaymentError(Exception):
    """No approval came back for a payment request."""


def charge(order_id, amount_cents, provider):
    """Ask the payment provider to approve a charge. Return the approval ID."""
    try:
        return provider.approve(
            order_id, amount_cents, timeout=APPROVE_TIMEOUT_SEC
        )
    except TimeoutError as exc:
        # The only statement that raises this error code.
        # Tests and docs may quote it.
        raise PaymentError(
            "PAY-0303 approval request timed out"
            " | where=payments.charge"
            f" | order_id={order_id} amount_cents={amount_cents}"
            f" timeout_sec={APPROVE_TIMEOUT_SEC}"
            " | next=do not retry; call provider.lookup() first"
            " to see if the charge went through"
        ) from exc
```

The same failure now leaves this line:

```text
PaymentError: PAY-0303 approval request timed out | where=payments.charge | order_id=1042 amount_cents=1500 timeout_sec=3 | next=do not retry; call provider.lookup() first to see if the charge went through
```

| In the line | Where a person got it |
|---|---|
| What happened: `approval request timed out` | The short line says it too |
| Where: `PAY-0303`, `where=payments.charge` | The stack trace |
| With what values: `order_id`, `amount_cents`, `timeout_sec` | The admin site's order list, found by the log line's timestamp, and the constant in `payments.py` |
| What to do next: `next=` | Memory, a colleague, and the provider's dashboard |

`next=` speaks to whoever reads the line, a person or an AI, and says what to check before doing anything else. Assume this shop's provider client also has `lookup(order_id)`, which reports whether a charge exists for an order. `where=` repeats the trace, for the day someone pastes the one line and leaves the trace behind.

Both versions say `timed out`, and neither says `failed`. Write what the program saw, not a conclusion. The program saw 3 seconds pass with no answer. `payment failed` would be a conclusion, and here possibly a false one. An AI that reads `failed` has nothing to check it against and is likely to conclude that no money moved.

`PAY-0303` is there so that you or the AI can search for it. You can search for the message text too, but the same wording can sit on a second failure path, and people edit wording. The error code is written as a literal in the `raise` statement, so a search of the code shows every place where that code is written. Open each hit and count the `raise` statements: tests and docs may quote the code too, and a search can't find a code that the program puts together while it runs.

A fixed width makes it less likely that one code turns up inside another. Keep the whole message on one line, and a search of the log for `PAY-0303` returns the values and the next step along with the code.

## Prompt: the prompt is the same sentence, and only the pasted log line differs

With the version for people, you send this:

```text
This line showed up in the production log. Find the cause and fix it.

PaymentError: approval request timed out
```

With the version for AI, only the pasted line changes:

```text
This line showed up in the production log. Find the cause and fix it.

PaymentError: PAY-0303 approval request timed out | where=payments.charge | order_id=1042 amount_cents=1500 timeout_sec=3 | next=do not retry; call provider.lookup() first to see if the charge went through
```

The first prompt tells the AI that the failure was a timeout, and the trace, if you paste it, says where. The AI has to guess the rest: which order, how much, and what this shop does after a timeout. None of that is in the line or the code. It is likely to end on a guess, and the likely guess is a retry. A timeout looks temporary, and nothing the AI can read says that asking the provider a second time is dangerous.

With the second prompt, the AI is likely to leave the retry alone, because the line it was given says not to retry and names what to check first. The cause is outside the repository, at a provider that didn't answer in time, so there's nothing to fix in the `raise` statement.

A good outcome has two parts. First, you or the AI look up order 1042 before anyone asks the provider for approval again. Second, if the AI adds a retry to `charge`, the new code calls `lookup` before it calls `approve` again.

A pasted log line becomes part of the prompt. The error message you write today is the prompt you'll send on the day of the incident. A procedure in a separate document has to be found before it can be read, while one in the error line arrives with the failure.

> **[Run record slot: E8]** For each prompt: files the AI opened, tool calls, what it changed. Date, tool, model.

## Evidence: experiment E8 will plant five failures and report each one two ways

Experiment E8 will test whether what the error line says changes what the AI does next. Two copies of the order server differ only in that line: one copy has the short line, and the other has the line with the values and the next step. I plant five failures in both copies. One of the five, this approval timeout, can't be reproduced.

Each failure goes to 10 fresh sessions per copy, 100 sessions in all. E8 counts the sessions that name the true cause, the sessions that write code that asks for approval again without looking the charge up first, and the tool calls. E8 hasn't been run yet.

> **[Result slot: experiment E8]** Date, tool and model, sessions per failure, sessions that named the true cause, sessions that asked for approval again without a lookup, tool calls.

> **[Author case slot]** Two real cases: a check result that existed only on a screen the AI's tools couldn't read, and a log that recorded exit code 0 for every command.

## What people do

- [ ] In one module that moves money, run `grep -n "raise" payments.py` with your own file's name. Paste the list to the AI with this prompt: "For each raise statement, add what the program saw, where, and the values it had. Don't add a next step unless I give you one." Dictate `next=` yourself, only where your team has a procedure the code doesn't show.
- [ ] Give each of those errors a fixed-width error code, as a literal in its `raise` statement. Then search the repository for the code and open each hit. Exactly one `raise` statement should contain it. The other hits should be tests and docs that quote it.
- [ ] Paste this into your rules file (the instruction file in your repository that the AI reads when it starts work) so new error lines follow the format:

  ```text
  Error format: CODE what the program saw | where=module.function | key=value ... | next=what to check first
  CODE is a literal in the raise statement. next= appears only when a person dictates it.
  Values are numbers and IDs the program made itself. No names, card numbers, or tokens.
  ```
- [ ] Make one script fail on purpose. Pick a script your CI runs, and give a bad argument to a command that is not the last one in the script. Run the script in bash or zsh, type `echo $?`, and check that the script exits nonzero and that the log records that same number. This check tells you only about the command you broke.
- [ ] Take a result you read on your last CI run's page and search the raw job log for it. If the log doesn't have it, print the same line to the log.

## Where it breaks

This chapter asks for more in the error line, not for more logging. Everything the AI reads takes room in its context window. A search for the error code brings back one line. If the AI reads the whole log, or you paste the whole log, every success line comes along, and those lines can fill the window.

"With what values" doesn't mean every value. Card numbers, passwords, auth tokens, names, and phone numbers stay out of the log. Many people read a log, and anything the AI reads can be sent outside the company as part of that conversation. Keep to numbers and IDs the program made itself. Any other string can carry a line break or a second `next=`, and a pasted log line becomes part of the prompt.

What you write in the line can drift from the code. If the lookup procedure changes and `next=` still describes the old one, the AI is likely to follow the old one. `where=` is typed by hand and goes stale the day someone renames the function. So when you change the lookup procedure or rename the function, edit the error line in the same commit.

Better models and wider tool access make the values in the line matter less. A model that reproduces more failures can print what it needs. A session whose tools reach the order database or the admin site can look up the amount as a person did. The line still has to carry the key that ties it to one order, and the procedure that lives only in your team's memory.
