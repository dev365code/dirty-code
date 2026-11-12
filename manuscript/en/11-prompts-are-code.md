# Chapter 11. Prompts are code that AI reads

## Scene

On your first driving lesson, the instructor doesn't hand you the traffic code. The instructor has taught on this street for years and knows where learners go wrong. Before you turn the key, the instructor says three things. "Stay under 20 on this street. Don't turn into that alley, because it's one-way. When I say stop, you stop."

Your parent, in the back seat, says one thing. "Drive carefully."

You nod at both. At the next corner, the instructor's three sentences change what your hands and feet do. Your parent's sentence changes nothing. You were already trying to drive carefully, and the sentence doesn't say what careful means on this street.

You write sentences to an AI every day. Are they the instructor's kind, or your parent's?

## Claim

> Write a prompt the way you write code: state the rule, name what may change and what may not, say how to tell the work is done, and then run it to see what it does.

## Why: an AI does what the words of a prompt say, and where the words are silent it decides for itself

Code runs exactly as written. If a function doesn't say what to do with an empty list, the program still does something with an empty list, and you find out later what that was. A prompt behaves the same way. An AI tends to follow the words of a prompt to the letter. Where the prompt leaves a decision open, the AI makes the decision and keeps working.

A colleague handles the same sentence differently. Say "add free shipping for orders over $50" to a colleague, and the colleague asks, "Before the coupon or after?" The colleague can see the gap, because the colleague knows the shop. The colleague may even have been in the meeting where the owner answered that question.

An AI has no memory of that meeting, and a new session knows nothing about the shop except what it reads. A session can ask a question, and sometimes it does. When it doesn't, it picks one answer and writes the code, and the code looks just as finished whichever answer it picked. Experiment E10, described below, will count how often a session asks.

There is a second reason to treat a prompt as code: some prompts run again and again. A rules file is the instruction file in your repository that the AI reads when it starts work. Every session reads it. A vague sentence in that file is read by every session, and so are two sentences that contradict each other.

The third reason is the one programmers know best. Programmers don't trust code because it reads well. They run it. A prompt needs the same treatment. It looks clear to the person who wrote it, because that person already knows what it was meant to say. To find out what it actually says, give it to a session that doesn't know, and look at what comes back.

## Code: one line of prompt can become four functions, and they charge the same two customers four different ways

The shop charges $5.00 for shipping on every order. Here is the code before any change. The listing joins `orders.py` and `shipping.py`, and it runs as shown. Amounts are integer cents, so `5000` is $50.00.

```python
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


# shipping.py
SHIPPING_FEE = 500


def shipping_fee(order):
    """Cents to charge for shipping."""
    return SHIPPING_FEE
```

The owner wants to stop charging for shipping on larger orders, and you type one line to the AI.

```text
Add free shipping for orders over $50.
```

That line leaves two questions open.

The first question is: $50 of what? An order has a list total, which is the sum of the prices before any coupon. It also has the amount the customer paid after the coupon. The line doesn't say which of the two has to reach $50.

The second question is: does an order of exactly $50.00 count? Read strictly, "over $50" says no. An owner who says "over $50" may well mean "$50 and up."

Two questions with two answers each make four functions. Here are two of them.

```python
# Reading 1: the list prices add up to more than $50.00.
def shipping_fee(order):
    """Cents to charge for shipping. Free when the list total is over $50.00."""
    return 0 if sum(order.prices.values()) > 5000 else SHIPPING_FEE


# Reading 4: the customer paid $50.00 or more.
def shipping_fee(order):
    """Cents to charge for shipping. Free when the customer paid $50.00 or more."""
    return 0 if order.paid >= 5000 else SHIPPING_FEE
```

Reading 2 is Reading 1 with `>=` in place of `>`. Reading 3 is Reading 4 with `>` in place of `>=`.

The table shows what each reading charges two customers for shipping. The first customer buys a keyboard and a mouse and has no coupon. The list total is $50.00, and the customer pays $50.00. The second customer buys a keyboard, a mouse, and a cable with a $15.00 coupon. The list total is $60.00, and the customer pays $45.00.

| Reading | $50 of what | Does exactly $50.00 count? | First customer | Second customer |
|---|---|---|---|---|
| 1 | list total | no | `500` | `0` |
| 2 | list total | yes | `0` | `0` |
| 3 | amount paid | no | `500` | `500` |
| 4 | amount paid | yes | `0` | `500` |

No two rows are alike. None of the four functions is broken. Each one applies a rule correctly, and the four rules are different. The prompt didn't say which rule the owner wants, and the owner may not have decided yet.

A test doesn't settle the question if the same session writes the test. A session that wrote Reading 1 writes a test that expects Reading 1, and that test passes (Chapter 14).

## Prompt: the same task again, with the rule, the files, one don't, and a finish line

The one-line prompt is the version for people. It is how you would ask a colleague, and a colleague would fill the gaps by asking you. For the version for AI, you first take the two questions to the owner. The owner says: after the coupon, and exactly $50.00 counts. Then you write this.

```text
Add free shipping.

Rule: shipping is free when the customer paid $50.00 or more after
the coupon (order.paid >= 5000). Otherwise it stays $5.00.

Change only shipping.py and test_shipping.py.

Don't touch refunds. Whether a returned item takes free shipping
away is not decided yet.

Done when test_shipping.py has a test for each of these three cases
and python3 -m unittest prints OK:
  paid 4999 -> shipping 500
  paid 5000 -> shipping 0
  list total 6000 with a 1500 coupon -> shipping 500

If you find you need to change any other file, stop and tell me why.
```

The prompt has five parts, and each part closes a gap that the one-line prompt left open.

The first part is the rule. It is the owner's decision, written once in the words of the shop and once in the words of the code. With `order.paid >= 5000` in the prompt, the session doesn't have to guess how "after the coupon" is spelled in this repository. Only a person at the shop can supply this part.

The second part names the two files the session may change. Without it, a session may add a helper to `orders.py` or tidy something it noticed on the way, and the diff you have to read grows.

The third part is a don't, and it names a decision the session shouldn't make. Take the first customer in the table, who paid $50.00 and got free shipping. Suppose that customer sends the $20.00 mouse back. What remains is a $30.00 order. Does the shop refund $20.00, or $15.00 because a $30.00 order doesn't earn free shipping? Nobody at the shop has decided. A session that notices the question may answer it in code. The don't tells the session to leave the question alone, and it says why, so the session can recognize the same question if it turns up in another file.

The fourth part is the finish line. It says how both of you will know the work is done. It gives three cases with their answers, and the cases were chosen to catch the other readings. The order that paid exactly `5000` separates "or more" from "more than." The third case is the second customer in the table, whose list total is over $50.00 and whose payment is under it. Each of Readings 1, 2, and 3 gets at least one of the three cases wrong.

The fifth part says what to do when the prompt itself turns out to be wrong. Suppose the session finds that it can't finish without changing `orders.py`. Without the last line it can break the scope or stop short. The last line gives it a third choice: stop and say why.

Before you rely on a prompt like this, test it the way you would test code. Send it to three fresh sessions and compare what comes back. If the three functions charge some customer differently, the prompt still has a gap, and that customer shows you where it is.

A rules file needs the same care, because every session reads it. Here is a rules file with one line.

```text
- Write clean, maintainable code and follow best practices.
```

Here is one made of lines that Chapters 2, 4, 6, 7, 10, and 14 ask you to add.

```text
- Run the tests with: python3 -m unittest
- All amounts are integer cents.
- Read INDEX.md before you search.
- If a function writes to the database, the cache, a file, or the
  network, its name says what it writes. Logging doesn't count.
- Before editing a function with more than one caller, list the
  callers and say which ones the change is for.
- Don't change a value whose comment gives a reason. If you think
  the reason is out of date, tell me and wait.
- Fix the code, not the tests. If you think a test has to change,
  tell me why and wait for my answer.
```

The one-line file is "drive carefully." A session was already trying to write good code, and the line doesn't say what good means in this repository. Each line of the second file names something a session does or doesn't do, and each leaves something you can check afterward: a command in the session's record, the name of a new function, the list of changed files in the diff.

> **[Run record slot: E10]** For the one-line prompt and for the full prompt: the function the session wrote, the files it changed, any question it asked, and its report. Date, tool, model.

## Evidence: experiment E10 will send the free-shipping task in three forms and record which reading comes back

Experiment E10 will give the free-shipping task to fresh sessions in three forms. The first form is the one-line prompt. The second is the one-line prompt followed by the rule and nothing else. The third is the full prompt above. Each form goes to 10 fresh sessions, 30 in all.

For every session, E10 runs the function that came back on the two customers from the table. The two answers show which of the four readings the session wrote, because no two readings give the same pair. E10 also takes two things from the session's own record: whether the session asked a question before it changed any code, and whether it changed a file other than `shipping.py` and `test_shipping.py`.

The one-line form has no right answer to score, because the prompt doesn't state the rule. For that form the result is a tally: how many sessions wrote each reading, and how many asked first. For the other two forms the rule is in the prompt, so E10 counts the sessions that wrote Reading 4.

E10 hasn't been run yet. If all 10 sessions that get the one-line prompt write the same reading, I'll say so here. The claim would then be narrower. The sessions agreed with each other, and the prompt still gave nobody a way to know whether they agreed with the owner.

The maker of one coding agent gives similar advice about its rules file. The documentation for Claude Code says the tool treats that file "as context, not enforced configuration," and it asks for instructions that are "concrete enough to verify." One of its examples is "Use 2-space indentation" instead of "Format code properly." <!-- source: notes/sources.md, rules files and sessions, checked 2026-11-13 --> That is advice from the maker of one tool. It is not a measurement of mine.

> **[Result slot: experiment E10]** Date, tool and model. For each form, out of 10 sessions: how many wrote each of the four readings, how many asked a question before changing code, and how many changed a file outside the two named.

> **[Author case slot]** The parts the author puts in a task prompt for an AI that writes code, and a case in which a line missing from a prompt led to rework.

## What people do

- [ ] Take the last prompt you sent for a task that needed more than one round. Mark where it states the rule, the files that may change, what to leave alone, and how to tell the work is done. Write in the parts that are missing, and keep the result in the repository for the next task of that kind.
- [ ] Before you send a prompt for a task that touches money, paste it to a fresh session with this line: "List the different ways this prompt could be read. Don't write code." Take the list to whoever owns the rule, and put the answers in the prompt.
- [ ] Put cases with their answers in the finish line. Pick at least one case that two readings of your prompt would answer differently.
- [ ] Send a prompt you plan to reuse to three fresh sessions and compare the results. Where two results differ, the prompt has a gap.
- [ ] Open your rules file and read each line as an instruction to a stranger. For each line, ask: "After a session finishes, what would I look at to check that it followed this?" If you can't name anything, rewrite the line or delete it. Keep the file under version control, and when you change a line, rerun a task you've run before and compare the result with last time.

## Where it breaks

A long rules file works against itself. Every session reads the whole file before it starts, and the file takes up part of the session's context window. The documentation quoted above asks for a rules file under 200 lines and gives the reason: "Longer files consume more context and reduce adherence." It also warns that when two instructions contradict each other, the model "may pick one arbitrarily." <!-- source: notes/sources.md, rules files and sessions, checked 2026-11-13 --> A task prompt can contradict the rules file too. The cleanup prompt in Chapter 7 asks for round values, and the rules file above says not to change a value whose comment gives a reason. So when you add a rule, look for one you can remove, and write in the file what a session should do when a prompt and a rule collide: stop and ask.

Not every task needs the long form. Writing out the rule, the files, and the finish line for a typo fix takes longer than fixing the typo. Use the long form when a wrong guess costs something: money, customer data, or an afternoon of rework.

Sometimes you can't write the rule, because nobody has decided it. Say so in the prompt, and ask for the readings first: "List the ways this request could be read, and wait." The session's list becomes the questions you take to the owner.

A prompt goes stale the way a comment does (Chapter 7), and a stale line in a rules file can fail without a sound. Suppose the team moves the tests into a folder named `tests/`, as the layout in Chapter 10 does, and the first line of the rules file still says `python3 -m unittest`. On Python 3.9.6, which is the `python3` on my Mac, that command no longer finds the tests. It prints `Ran 0 tests` and `OK`, and it exits with status 0. Every session runs the command it was told to run and truthfully reports a pass. From Python 3.12 on, the same run prints `NO TESTS RAN` and exits with status 5. <!-- source: notes/sources.md, tool behavior, unittest with no tests, run 2026-11-13 --> Change the rules file in the same commit that changes what it describes, and compare the number of tests in the output with the number you expect (Chapter 14).

Better models will need fewer instructions about how to do the work. A model that always asks before it changes a test doesn't need the line that tells it to. No model can do without the rule itself. Whether free shipping starts at the list total or at the amount paid is something a person at the shop decides, and the prompt is where a session finds out.
