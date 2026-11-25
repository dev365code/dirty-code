# Chapter 4. A function that writes says so in its name

## Scene

Your first car had a fuel gauge that lied. The needle dropped to a quarter tank and stayed there until the engine quit. It caught you once, on a highway on-ramp. After that you knew that a quarter meant empty, so you filled up early and never had the gauge fixed.

Then a friend borrowed the car for a weekend. The gauge showed a quarter tank, and she had forty miles to go. She phoned you from the shoulder.

She did what every driver does. Nobody looks inside the tank, so she read the gauge, and nothing on the dashboard said that in this car a quarter means empty. You knew, and you hadn't told her.

Your code has names like that gauge: functions that do a little more than they say, which your team has learned to read correctly. What does an AI make of such a name when it reads it for the first time?

## Claim

> When a function changes stored data, say so in its name, so that every line that calls it carries the warning, even when the prompt doesn't.

## Why: your team knows what `get_user` really does, and at the call site a new session sees only its name

A new session has never seen any of the functions it is about to call. Say a session needs a customer's email address. The session searches the repository, and one of the lines it finds is this one from `orders.py`.

```python
user = get_user(order.user_id)
```

A call site shows this much of a function: its name and its arguments. The body and the docstring are in another file. In this chapter's runs, every session looked at the defining file, or at least the line that defines the function, before its first edit, so no session had to go by the name alone. The name is still what a session reads first, at every line that calls the function, and what you read in a diff. By the ordinary meaning of the words, `get_user` looks a customer up and changes nothing.

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

I ran this prompt on 2026-11-22 in fresh sessions of Claude Code, in the large repository of Appendix A, a made-up shop of 518 files where this code sits among 210 other modules. There `get_user` is called from 121 places, and four other export modules call it, so it is the easy call to copy. The prompt named the new file `shop/exports/customer_emails.py`.

In the version for people, a session on Claude Sonnet 5.5 listed the files, then ran `cat shop/accounts/users.py shop/exports/newsletter_list.py` and searched for `cache`. It wrote `return [load_user(user_id).email for user_id in user_ids]`, ran the function on three IDs, and printed the cache, which was empty. Its report said, "It reads each user with `load_user`, which goes straight to the database, so it never uses or fills the cache." The session took 6 turns and 12 seconds.

In the version for AI, a session on Claude Opus 5.5 read `users.py` and the newsletter export, wrote the same line, and added a test. Its report named the other function: "It doesn't use `get_user_and_fill_cache`, which saves every user it loads into the shared cache; that's what the newsletter export uses."

## Evidence: told which write to avoid, no session called the function that does it, and without that clause one model of four filled the cache less often under the longer name

Experiment E3 builds the order server in both versions, with five functions like `get_user`. Each does one write, a change to stored data, that its short name doesn't mention: a lookup that fills a cache, a lookup that creates a missing row, a coupon validation that marks the coupon used, a payment verification that marks the order paid, and a settlement total that saves the figure it computes. The version for AI puts the write in each name. Bodies and docstrings are the same, tests differ only in the names they call, and both versions have a second function that does the lookup without the write.

Each function gets one prompt like the one above, with a sentence saying that the write must not happen. Each prompt goes to 10 fresh sessions per version, 100 sessions in all. A hidden test passes a session only if its new code returns the right value and leaves the stored data unchanged. E3 counts the passes out of 50 for each version. For each session it also notes whether the session opened the file that defines the function before it added the call, because a session that opened it didn't have to go by the name.

On 2026-11-22 I ran the first of the five functions, the lookup that fills a cache. I ran it in the large repository from the Prompt section, with Claude Code and three models at their default settings: Claude Haiku 5.5, Claude Sonnet 5.5, and Claude Opus 5.5. Each model got the prompt in 10 fresh sessions per version, 60 sessions in all.

All 60 passed the hidden test: the right three addresses, and an empty cache afterward. All 60 called `load_user`, and none called `get_user` or `get_user_and_fill_cache`. All 60 looked at `users.py`, with a file read or a shell command. The versions didn't differ in the work either: each model made about the same number of tool calls in both.

The reason is in the prompt. It says not to touch the cache. 52 of the 60 sessions searched for `cache`, and the search led them to `users.py`, where the lookup's docstring says that it stores what it loads. The other 8 printed whole files from the file list and read `users.py` that way. So these runs test the case where the prompt names the constraint, and there the name made no difference. The case this chapter warns about is the one where the person forgets that clause, and then the prompt gives a session no word to search for. E3 as designed doesn't measure that case.

On 2026-11-22 and 23 I ran the other four functions in the same large repository, with one more coding agent, Codex CLI with gpt-6.2-sol. I added the four to the shop in both versions: a cart lookup that creates a missing cart, a coupon check that marks the coupon used, a payment check that marks the order paid, and a settlement total that saves the figure it computes. Each sits in the normal flow with a few callers, next to its twin that only reads. Each prompt asked for a new function in a new file and said which write must not happen, such as "it must not create a cart for anyone." Each function went to 10 fresh sessions per version, 80 sessions in all.

All 80 passed the hidden test. None called the function that writes, under either name. In all 80, the line that defines that function appeared in the output of a command the session ran before its first edit, so no session met the function only at a call site. The median session made 5 or 6 tool calls in both versions.

So all five functions came out the same way, the first with three Claude models and the other four with Codex: when the prompt names the write to avoid, sessions avoid it under either name. The prompt gives them a word to search for, and the definition they find says what the function writes.

On 2026-11-25 I ran the case these runs left out, as the experiment's plan had registered before the runs: the first function in the same large repository, with the clause about the cache taken out of the prompt.

```text
Add export_emails(user_ids) in a new file, shop/exports/customer_emails.py. It returns a
list with the email address for each ID. A nightly job will run it
over every customer.
```

Nothing passes or fails here, because the prompt no longer asks for anything about the cache. I counted three things instead: the sessions whose export left customers in the cache, the reports that mentioned the cache, and the sessions that saw `users.py` before their first edit. Each version went to 10 fresh sessions of each Claude model at its default setting, and to 10 Codex sessions with gpt-6.2-sol.

| Version | Model | Filled the cache | Report mentioned the cache | Saw `users.py` before the first edit |
|---|---|---|---|---|
| For people, `get_user` | Claude Haiku 5.5 | 9 of 10 | 8 of 10 | 10 of 10 |
| For people, `get_user` | Claude Sonnet 5.5 | 0 of 10 | 10 of 10 | 10 of 10 |
| For people, `get_user` | Claude Opus 5.5 | 0 of 10 | 10 of 10 | 10 of 10 |
| For people, `get_user` | Codex | 0 of 10 | 10 of 10 | 10 of 10 |
| For AI, `get_user_and_fill_cache` | Claude Haiku 5.5 | 5 of 10 | 9 of 10 | 10 of 10 |
| For AI, `get_user_and_fill_cache` | Claude Sonnet 5.5 | 0 of 10 | 10 of 10 | 10 of 10 |
| For AI, `get_user_and_fill_cache` | Claude Opus 5.5 | 0 of 10 | 10 of 10 | 10 of 10 |
| For AI, `get_user_and_fill_cache` | Codex | 0 of 10 | 10 of 10 | 10 of 10 |

Every session saw `users.py` before it wrote anything. Sonnet, Opus, and Codex never filled the cache. They called `load_user` and said why, for example: "a nightly run over every customer would copy the whole users table into the cache." Haiku followed the other export modules, which call the lookup that fills the cache, and its reports that filled the cache named that as a reason to do it: "It reuses `get_user_and_fill_cache`, the same lookup the other exports use." So a mention of the cache in a report isn't always a warning.

With the short name, 9 of the 10 Haiku sessions filled the cache, and with the long name, 5 did. The other three models never filled it under either name. With ten runs per version, chance alone gives a gap as large as Haiku's about one time in seven. So in these runs the longer name went with fewer filled caches for one model of the four, and only when the prompt said nothing about the cache.

<!-- [Author case slot] A real case in which an AI went by a description of the code, such as a name or a comment, and reported or changed the wrong thing. -->

## What people do

- [ ] List the functions whose names promise a lookup or a yes-or-no answer: `git grep -nE "def (get|find|is|has|check|validate)_" -- "*.py"`. The pattern goes by prefix, so `load_user` and a lookup named `user_for_order` aren't listed.
- [ ] Paste the list to the AI: "For each function, say whether it, or anything it calls, writes to a database, a cache, a file, or the network. Leave out logging. Quote the file and line of every write." Open each quoted line yourself. A function it reports as having no writes is still unverified.
- [ ] Have the AI rename one function that writes, in a commit that changes nothing else: "Rename get_user to get_user_and_fill_cache everywhere it's defined, imported, called, or mocked. Don't change any behavior." Then run the tests and `git grep -nw get_user`, which should print nothing. That search can't see a name the program puts together while it runs, such as `getattr(users, "get_" + kind)`. Only a test that executes that line will fail.
- [ ] Add one line to your rules file: "If a function writes to the database, the cache, a file, or the network, its name says what it writes. Logging doesn't count."

## Where it breaks

A session that is editing `users.py` already has the docstring a few lines below the name, so the longer name tells it nothing new. In this chapter's runs every session saw `users.py` before its first edit, even in a repository of 518 files. So the name made a difference only when the prompt didn't say what to avoid, and then only for one of the models.

Suppose the prompt above also asked for a test that the cache holds the same entries before and after the export. A session that calls `get_user` then sees the test fail and can work its way to `load_user`, whatever the lookups are named. That test has to start from an empty cache: if the customers are already cached, `get_user` stores nothing new, and the test passes for both functions. A line in the rules file ("get_user fills the cache; nightly jobs call load_user") warns every session too, for the names you already know about. Type hints don't carry the warning: both lookups are `(user_id: int) -> User`.

A name that describes a write becomes false when someone removes the write and keeps the name. A session that must avoid the cache is then likely to avoid a function it could have used. So the rename belongs in the same commit as the change in behavior.

However many definitions a session opens before it calls a function, the diff you review shows the call and not the function behind it.
