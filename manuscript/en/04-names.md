# Chapter 4. AI guesses what a function does from its name

## Scene

Your first car had a fuel gauge that lied. The needle dropped to a quarter tank and stayed there until the engine quit. It caught you once, on a highway on-ramp. After that you knew that a quarter meant empty, so you filled up early and never had the gauge fixed.

Then a friend borrowed the car for a weekend. The gauge showed a quarter tank, and she had forty miles to go. She phoned you from the shoulder.

She did what every driver does. Nobody looks inside the tank, so she read the gauge, and nothing on the dashboard said that in this car a quarter means empty. You knew, and you hadn't told her.

Your code has names like that gauge: functions that do a little more than they say, which your team has learned to read correctly. What does an AI make of such a name when it reads it for the first time?

## Claim

> AI guesses what a function does from its name, so a function that changes stored data has to say so in its name.

## Why: your team knows what `get_user` really does, and a new session sees only its name

An AI has no memory, so a new session has never seen any of the functions it is about to call. Say a session needs a customer's email address. The session searches the repository, and one of the lines it finds is this one from `orders.py`.

```python
user = get_user(order.user_id)
```

A call site shows this much of a function: its name and its arguments. The body and the docstring are in another file. Opening that file takes time and uses up part of the session's context window, so a session usually opens some of the functions it's about to call and goes by the name for the rest. By the ordinary meaning of the words, `get_user` looks a customer up and changes nothing. <!-- not measured: E3 notes whether the defining file was opened -->

You'd read the name the same way. Now suppose `get_user` also stores each customer it looks up in a cache. One day a script that loops over every customer fills that cache, the site slows down, and someone on your team spends an afternoon tracing the slowdown back to `get_user`. They tell the others. A new hire may still get caught once, and then someone tells them too. Nobody puts the warning in a file, because it travels well enough by word of mouth.

A new session gets none of that. It comes to `get_user` the way that new hire did on the first morning, and the session after it does the same.

*Clean Code* already makes this point: when a function changes something, its name should tell the caller. <!-- check against original --> This chapter keeps that rule. A team could live with a few names that broke it, because people told each other which ones, and a session has only what's in the files. The fix is also cheap for an AI: it can rename a function everywhere it's used in one commit.

## Code: one lookup in `users.py` gets a longer name, and nothing else changes

`users.py` holds the shop's customer data, and in the code a customer is a `User`. The file has two lookups. Here is the version for people. `_db` and `_cache` stand in for the `users` table and the shop's shared cache, so the listing runs as shown.

```python
"""users.py (the version for people)"""
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    user_id: int
    email: str


# Stand-ins so the listing runs: the users table and the shared cache.
_db = {
    7: User(7, "ava@example.com"),
    8: User(8, "ben@example.com"),
    9: User(9, "cora@example.com"),
}
_cache = {}


def load_user(user_id: int) -> User:
    """Return the user straight from the database."""
    return _db[user_id]


def get_user(user_id: int) -> User:
    """Return the user, from the cache if it's there.

    On a miss, load the user from the database and store it in the cache.
    """
    if user_id not in _cache:
        _cache[user_id] = load_user(user_id)
    return _cache[user_id]
```

This is careful code. `get_user` is the lookup that the rest of the code calls. `load_user` is there for the few callers that need the database row itself. The docstring of `get_user` says outright that on a miss the function stores the customer in the cache. On this team `get_` means "through the cache" and `load_` means "straight from the database." No file states that convention. People on the team learned it from each other.

Here is the same lookup in the version for AI. It replaces `get_user`, and every caller uses the new name.

```python
def get_user_and_fill_cache(user_id: int) -> User:
    """Return the user, from the cache if it's there.

    On a miss, load the user from the database and store it in the cache.
    """
    if user_id not in _cache:
        _cache[user_id] = load_user(user_id)
    return _cache[user_id]
```

The call site in `orders.py` becomes `user = get_user_and_fill_cache(order.user_id)`, so every line that calls the function now says that it fills the cache. The new name has an `and` in it because the function does two things: it returns a customer, and it stores that customer in the cache. It did both under the short name too.

Not everything a function does has to be in its name. A log line doesn't change what a caller should do, so it stays out. A cache fill matters to a nightly job that loops over every customer, so it goes in.

## Prompt: both versions get the same prompt, and only one shows `cache` at the call site

Here is a prompt for that kind of job.

```text
Add export_emails(user_ids) in a new file, exports.py. It returns a
list with the email address for each ID. A nightly job will run it
over every customer, so look them up without touching the cache.
```

`exports.py` doesn't exist yet, so a session first has to find out how this code looks a customer up. In the version for people, `orders.py` and the other files that need a customer call `get_user`. A session that reuses that call hands back the first function below.

```python
# Reuses the call that the other files make:
def export_emails(user_ids):
    return [get_user(user_id).email for user_id in user_ids]


# Does what the prompt asked:
def export_emails(user_ids):
    return [load_user(user_id).email for user_id in user_ids]
```

To compare them, append either one to the listing and add `print(export_emails([7, 8, 9]), len(_cache))`. Both print the same three addresses. The first then prints `3` and the second prints `0`: the first function left three entries in the cache. Neither raises an error, so running the code doesn't show the difference unless you look in the cache. If the shop has 200,000 customers, the first function loads all 200,000 into a cache meant for the customers who are shopping right now.

In the version for people, the only file that says which lookup stores to the cache is `users.py`. The prompt mentions the cache, and a search for `cache` finds lines in that file and nowhere else. A session that starts from the call sites finds nothing that tells it to look further, and which search it runs first can differ from one session to the next. If the person who writes the prompt forgets the cache and leaves out the last clause, the prompt gives a session no word to search for.

In the version for AI, both searches lead to the warning. A search for `cache` now returns the call sites as well, and each call site says `get_user_and_fill_cache`. A session that was told not to touch the cache finds that word in the line it was about to reuse.

The longer name also helps you review what the session hands back. The diff is one new file, and `users.py` isn't in it, so the diff shows only the lookup's name. `get_user` in a loop looks fine. `get_user_and_fill_cache` in a loop over every customer is a line you can question without opening another file.

> **[Run record slot: E3]** For each version: searches run, whether `users.py` was opened first, and the `export_emails` handed back. Date, tool, model.

## Evidence: experiment E3 will count how often a session calls the lookup that fills the cache

Experiment E3 will build the order server in both versions, with five functions like `get_user`. Each does one write, a change to stored data, that its short name doesn't mention: a lookup that fills a cache, a lookup that creates a missing row, a coupon validation that marks the coupon used, a payment verification that marks the order paid, and a settlement total that saves the figure it computes. The version for AI puts the write in each name. Bodies and docstrings are the same, tests differ only in the names they call, and both versions have a second function that does the lookup without the write.

Each function gets one prompt like the one above, with a sentence saying that the write must not happen. Each prompt goes to 10 fresh sessions per version, 100 sessions in all. E3 hasn't been run yet. A hidden test (a test the AI never sees, used to judge whether the result is right) passes a session only if its new code returns the right value and leaves the stored data unchanged. E3 counts the passes out of 50 for each version. For each session it also notes whether the session opened the file that defines the function before it added the call, because a session that opened it didn't have to go by the name.

> **[Result slot: experiment E3]** Date, tool and model. For each version: passes out of 50 and per function, sessions that called the function that writes, sessions that opened the defining file first.

> **[Author case slot]** A real case in which an AI went by a description of the code, such as a name or a comment, and reported or changed the wrong thing.

## What people do

- [ ] List the functions whose names promise a lookup or a yes-or-no answer: `git grep -nE "def (get|find|is|has|check|validate)_" -- "*.py"`. The pattern goes by prefix, so `load_user` and a lookup named `user_for_order` aren't listed.
- [ ] Paste the list to the AI: "For each function, say whether it, or anything it calls, writes to a database, a cache, a file, or the network. Leave out logging. Quote the file and line of every write." Open each quoted line yourself. A function it reports as having no writes is still unverified.
- [ ] Have the AI rename one function that writes, in a commit that changes nothing else: "Rename get_user to get_user_and_fill_cache everywhere it's defined, imported, called, or mocked. Don't change any behavior." Then run the tests and `git grep -nw get_user`, which should print nothing. That search can't see a name the program puts together while it runs, such as `getattr(users, "get_" + kind)`. Only a test that executes that line will fail.
- [ ] Add one line to your rules file (an instruction file kept in the repository that the AI reads when it starts work): "If a function writes to the database, the cache, a file, or the network, its name says what it writes. Logging doesn't count."

## Where it breaks

A session that is editing `users.py` already has the docstring a few lines below the name, so the longer name tells it nothing new. In a small repository most sessions may be in that position. If E3 finds that, both versions will score the same, and this chapter's claim will need a condition about repository size.

Suppose the prompt above also asked for a test that the cache holds the same entries before and after the export. A session that calls `get_user` then sees the test fail and can work its way to `load_user`, whatever the lookups are named. That test has to start from an empty cache: if the customers are already cached, `get_user` stores nothing new, and the test passes for both functions. A line in the rules file ("get_user fills the cache; nightly jobs call load_user") warns every session too, for the names you already know about. Type hints don't carry the warning: both lookups are `(user_id: int) -> User`.

A name that describes a write becomes false when someone removes the write and keeps the name. A session that must avoid the cache is then likely to avoid a function it could have used. So the rename belongs in the same commit as the change in behavior.

Better models and tools may open more definitions before they call a function, which would make the name matter less to them. The diff you review will still show the call and not the function behind it. <!-- no source: written as a conditional -->
