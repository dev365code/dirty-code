# Chapter 1. "My way used to be faster": the day developers stopped reading code

## Scene

For ten years you drove the same road to work. You knew which light ran long and which lane cleared first. One morning the GPS told you to turn onto a side street you had never taken. You glanced at the screen and stayed on the main road. *My way is faster.*

It used to be. More than once you had followed the GPS and arrived later than usual. That morning, traffic stood still at an intersection that had always been clear, and you reached the office twenty minutes late. You had trusted the route you memorized over ten years. The GPS had seen the road as it was that morning.

Now you check the GPS before you pull out, even on roads you know. You still drive, and you still know the road. But the GPS has looked at this morning's traffic before you have.

In your repository today, who reads the code first?

## Claim

> When you hand a task to an AI, the AI reads your code before you do.

## Why: an AI usually reads before it edits, and with no memory it has to read the same code again next time

In this book, "AI" means a coding agent: an AI that reads and edits the code in a repository and runs commands in it. One conversation with it, from start to finish, is a session.

An AI has no memory, so every session reads your code for the first time. Before a session edits anything, it usually reads: it searches for a name, opens the files that match, and sometimes runs the tests. On that task you read after the AI does. What you read is the diff and the report the AI gives you, unless you open more files yourself.

A person who read a function last week usually remembers enough to skim it today. A new session remembers none of it. If the next task touches the same function, the new session has to read that function again.

The day in this chapter's title is the first day you merge an AI-written change that no one has read line by line. The title doesn't mean you stopped reading code altogether. It means that from that day the repository holds lines you neither wrote nor read, and "I know this code" is true only for the rest. On a team, a colleague's code was already like that for you. What's new is that no person has read these lines.

*Clean Code* observes that developers spend far more time reading code than writing it, and concludes that code should be easy to read. <!-- check against original --> This book keeps that principle. The AI, like the developer *Clean Code* writes for, reads code in order to change it. <!-- check against original --> Two things differ. This reader has no memory of the code. And when this reader misreads the code, the wrong edit is already in your files before any person has looked. So when you write or accept code, ask how a reader with no memory will read it, and what that reader will then change.

## Code: the reviewer sees the cancel function that changed, and the refund rule it depends on sits in a file that didn't

"I review the AI's code before I merge it." That's the first objection, and it's a fair one. A review is reading. So look at what a review puts in front of you: the diff. A diff shows the lines a change touched and, by default, a few lines around them. <!-- source: notes/sources.md, git-diff default context -->

Take a small online shop's order server. You ask an AI to change the code so that canceling an order also refunds the customer, and its change comes up for review. Assume you've never read the refund code. Here's the change, minus one new import line.

```python
# orders.py: the change. The diff shows these lines.
def cancel_order(order, today):
    """Cancel the order and refund whatever can still be refunded."""
    amount = refund_amount(order, today)
    return replace(order, status="canceled", refunded=order.refunded + amount)
```

The diff also shows a few of the `orders.py` lines below as context. It shows nothing from `refunds.py`.

```python
# orders.py: the lines that did not change.
from dataclasses import dataclass, replace
from datetime import date


@dataclass(frozen=True)
class Order:
    paid: int             # cents the customer paid
    paid_on: date
    refunded: int = 0     # cents already refunded
    status: str = "paid"


# refunds.py: nothing here changed.
REFUND_WINDOW_DAYS = 7


def refund_amount(order, today):
    """Return how many cents can be refunded today."""
    if (today - order.paid_on).days > REFUND_WINDOW_DAYS:
        return 0
    return order.paid - order.refunded
```

Whether `cancel_order` is right depends on what `refund_amount` returns, and one of the answers `refund_amount` can return is 0. If a customer cancels an order 7 days after payment, the customer gets the money back. If the customer cancels 8 or more days after payment, the order is marked canceled and the customer gets nothing.

That may be the policy you want, or a late cancellation may be something the shop should refuse. A person has to decide. But the line that raises the question, `return 0`, isn't in the diff. The changed lines do pass `today`, so a careful reviewer can guess that time matters. The changed lines don't show the 7-day window or what happens after it.

To write the change correctly, someone had to know those answers. An AI has no memory to get them from, so the AI is likely to have opened `refunds.py`. You open that file only if you go looking.

A colleague's change reached you as the same kind of diff, but a person had written it. That person may have read `refund_amount` before calling it, and you could ask them. With an AI-written change you can ask too: the session that wrote the change is usually still open, and it will answer. What you get back is another report. Tomorrow that session is closed, and a new session can only read `refunds.py` again and tell you what the code does.

So if the AI's report mentions the 7-day rule, you know the rule as the report words it. You still haven't seen `return 0`. Unless you open `refunds.py`, no person has read `refund_amount` for this change, and your review is the only time a person reads the change at all.

"I read the code that matters" is the second objection. It's true, and you should. But that sentence admits there's code you don't read. You also have to decide what matters before you read it. Here the rule that mattered was in the file that didn't change.

## Prompt: a one-line prompt names no file, so the AI decides what to read

Suppose the prompt behind that change was one line.

```text
When an order is canceled, refund the customer too.
```

The prompt doesn't say where canceling or refunding lives in the repository, so the AI has to find out. It tends to search for words like `cancel` and `refund`, open the files the search returns, and run the tests if there are any. The AI also decides when it has read enough. A fresh session given the same line may open different files, because the same prompt doesn't lead to the same steps every time.

> **[Run record slot: E1]** This one line given to 10 fresh sessions: the files each one opened and the commands it ran before its first edit, in order. Date, tool and model.

On this change you wrote one line. If you then read only what the diff showed, you read one function. Whatever reading happened in between was the AI's.

## Evidence: in 30 days of my logs, 8,819 shell calls read a code file, and the read tool opened one 377 times

I've been building a few open-source verification tools with the work split across AI sessions. I do not read the code line by line. I read reports and the results of checks. <!-- author check: casebook preamble -->

On November 11, 2026, I counted the tool calls in the previous 30 days of logs from one coding agent, Claude Code, on one computer. A tool call is one use of a tool, such as the shell tool, which runs commands, or the read tool, which opens a file. The logs cover every folder I worked in, not only code repositories, and they include six models.

In those 30 days, 8,819 calls to the shell tool ran a command that reads a file's contents and named a code file. I counted searches such as `grep` as reading. The read tool opened a code file 377 times. So if you count only the read tool, you miss most of the times the AI read code. The script that does the counting, and its rules for what counts as a read, are in `experiments/e1_count.py`. <!-- author check: E1 preliminary count -->

These counts have limits. They don't say how much of each file the AI took in, or how often it read the same file again. I counted nothing on my own side, so the counts can't say that the AI reads code more often than a person does. And I didn't count who reads first. That part needs no count: if you hand over a task without opening the code, the AI opens the code before you do. <!-- author check: E1 preliminary count -->

E1, the first experiment in this book's plan, is a count in one code repository. It counts how often the AI reads code files, through the read tool or a shell command, and how often a person does, in an editor or a diff. It also gives the one-line prompt above to 10 fresh sessions and records what each session opens and runs before its first edit.

> **[Result slot: experiment E1]** Dates, repository, tool and model, and the two counts.

## What people do

- [ ] On your main branch, run `git log --since="1 week ago" --first-parent --shortstat --oneline -- '*.py'`, with your own code extensions in place of `'*.py'`. Under each commit's summary line you get the files changed, insertions, and deletions (merge commits show these counts from Git 2.29 on, and `--since` filters by commit date).
- [ ] From that list, keep only the changes you merged or approved. On GitHub, searching pull requests for `is:pr is:merged reviewed-by:USERNAME`, with your username in place of `USERNAME`, lists the ones you reviewed. <!-- source: notes/sources.md, GitHub search qualifiers --> Mark each one "read every line," "skimmed," or "didn't open." Count a change you typed yourself as read, and when unsure pick the lower mark.
- [ ] Total the insertions for the changes marked "read every line" and divide by the insertions for all the changes you kept. That's the share of the added lines that you read line by line.
- [ ] Open the latest AI-written change you reviewed. Pick one function it calls that the diff didn't show, open it, and write down any rule in it that you didn't know.
- [ ] For each change marked "didn't open," write one line on what made you believe it was right: a test result, the AI's report, or nothing.

## Where it breaks

If you track down a bug yourself and only then hand over the fix, you read the code first. The lines the AI writes are new, so if you review them, you're their first human reader. And the less you hand over, the less the claim applies: if you use AI only for autocomplete, you still find and open the code yourself.

A person has to read some code no matter who read it first: code behind an outage, security code, regulated code. For that code, what matters is that a person can still follow it on the day they have to. Chapter 17 takes that up.

Better models and tools may carry memory from one session to the next. The AI would then reread less. On a task you hand over, it would still open the code before you do.
