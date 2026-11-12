# Chapter 5. Keep what changes together on one screen

## Scene

A headlight bulb burns out. On your first car, changing one took five minutes: you opened the hood, reached behind the lamp, and twisted the bulb out.

On this car the lamp won't come out until the bumper cover is loose, and the bumper cover won't come loose until you unclip the liner inside the wheel arch. That makes three places to work in, and you learn about each one only when the one before it stops you.

An hour later the new bulb works and everything is bolted back on. That night the fog lamp on the same side stays dark.

You unplugged its connector to get the bumper cover off, and nothing near the headlight reminded you to plug it back in. A mechanic who has done this job on this car before would have plugged it in without thinking.

When an AI changes one rule in your code, what tells it how many places that rule lives in?

## Claim

> An AI edits only the places it finds, so keep the code that one change touches in one place.

## Why: a new session edits the file its search finds, and that file doesn't mention the other two

A developer who has spent a year on a small online shop's order server knows where its rules live. Ask her to add a rule for the email addresses customers sign up with, and she makes three edits from memory: the rule's value in `settings.py`, the message the customer sees in a table in `validation.py`, and the check in `users.py`.

She learned that layout in her first weeks. When she does forget one of the three, a reviewer who knows the layout asks about it.

An AI has no memory of earlier sessions, so a new session doesn't know there are three files. The session usually searches for a word from the prompt, opens some of the files the search returns, and starts writing once it has read enough to write something.

Suppose the search leads it to `users.py`. The class there has three checks, and each returns an error code such as `email_too_long`. The session can add a fourth check that returns a fourth error code, and the result looks like a finished change. Nothing in `users.py` mentions the table of messages.

The session could still find the table. The class names its parent class, and the table is in the parent.

But opening the parent's file is another read, and every read uses up room in the context window. The session has to decide to keep reading when it already has a change that looks complete. One session may keep reading and find the table, and the next, given the same prompt, may stop.

In this chapter, one screen means what a session takes in when it reads one file once: a function, or a file short enough to read whole. "What changes together" means the lines you have to edit to make one change in behavior. For a sign-up rule those are the check, the value, and the message.

*Clean Code* gives similar advice for human readers: things that belong together should sit near each other in the source and shouldn't be split across files without a good reason. <!-- check against original -->

The three-file layout has good reasons, and they're about people. Someone in operations can change a value in `settings.py` without touching a check, and the customer messages stay consistent because they're in one table. Weigh those reasons again now that the reader is an AI session, which has to find every one of those files by searching.

## Code: an email rule's check, value, and message move from three files into one function

The shop's sign-up handler, `register`, applies three rules to an email address: it must be present, be at most 254 characters long, and have the shape of an address. The version for people is three files, shown as two blocks that run as one file when joined top to bottom. The `import` lines between the files are left out.

```python
# settings.py: values that operations can change without touching a check
EMAIL_MAX_LENGTH = 254


# validation.py: shared by every handler in the shop
import functools


class Validator:
    """Parent class of every validator. A subclass defines broken_rule()."""

    messages = {  # every sentence the shop shows a customer
        "email_required": "Enter your email address.",
        "email_too_long": "That email address is too long.",
        "email_invalid": "Enter a valid email address.",
    }

    def rejection(self, value):
        """Return a 400 response if the value breaks a rule, else None."""
        code = self.broken_rule(value)
        if code is None:
            return None
        return {"status": 400, "code": code, "message": self.messages[code]}


def validated(validator_class):
    """Decorator: call the handler only if the validator accepts the value."""
    def decorate(handler):
        @functools.wraps(handler)
        def wrapper(value):
            return validator_class().rejection(value) or handler(value)
        return wrapper
    return decorate
```

```python
# users.py
import re

EMAIL_SHAPE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class SignupEmail(Validator):
    def broken_rule(self, email):
        """Return the error code of the first broken rule, or None."""
        if not email:
            return "email_required"
        if len(email) > EMAIL_MAX_LENGTH:
            return "email_too_long"
        if not EMAIL_SHAPE.fullmatch(email):
            return "email_invalid"
        return None


@validated(SignupEmail)
def register(email):
    """Handle a sign-up: create a customer account."""
    return {"status": 201, "email": email}
```

The version for AI writes each rule as one statement.

```python
# users.py
import re

EMAIL_SHAPE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def rejected(code, message):
    """A 400 response: an error code and a message for the customer."""
    return {"status": 400, "code": code, "message": message}


def register(email):
    """Handle a sign-up: create a customer account or reject the email."""
    if not email:
        return rejected("email_required", "Enter your email address.")
    if len(email) > 254:
        return rejected("email_too_long", "That email address is too long.")
    if not EMAIL_SHAPE.fullmatch(email):
        return rejected("email_invalid", "Enter a valid email address.")
    return {"status": 201, "email": email}
```

Both versions give the same answer to every address and pass the same four tests: a good address, an empty one, one of 255 characters, and one with no `@`.

Now add a fourth rule: the shop stops accepting addresses at `throwaway.example`. In the version for people that takes three edits in three files: the domain in `settings.py`, a new message in `Validator.messages`, and a new check in `SignupEmail.broken_rule`. Suppose a session makes only the third edit and types the domain straight into the check.

```python
# users.py, in SignupEmail.broken_rule, above the last return
        if email.endswith("@throwaway.example"):
            return "email_blocked"
```

The four tests still pass, because none of them signs up from that domain. A new test that calls `SignupEmail().broken_rule("pat@throwaway.example")` and expects `"email_blocked"` passes too. But when a customer signs up with that address, `register` raises `KeyError: 'email_blocked'`, because `Validator.rejection` looks up a message for the new error code and the table has none.

A new test that calls `register` instead raises the same `KeyError`, and a session that reads an error can go looking for its cause. So the error shows up before a customer hits it only if the new test calls `register`. A new test that calls `broken_rule` directly passes.

Even a test that calls `register` doesn't catch the missing edit to `settings.py`. Once the session adds the message, that test passes, and the domain is still typed into the check. Someone in operations who looks in `settings.py` for the blocked domains won't find this one.

In the version for AI the whole rule is two lines.

```python
# users.py, in register, above the last return
    if email.endswith("@throwaway.example"):
        return rejected("email_blocked", "Use a different email address.")
```

Whoever writes those lines has three older rules directly above them on the same screen, and each one is a complete example to follow. With the two lines added, `register("pat@throwaway.example")` returns a 400 response with the error code `email_blocked`.

The version for AI gives up what the three files were for. To change the 254, someone in operations now has to edit `register`. To read every sentence the shop shows to customers, you now have to search the code for them.

Your commit history shows how this code usually changes. If most commits that touch `users.py` also touch `settings.py` and `validation.py`, most changes need all three files, and few are the one-file changes the split was meant to make easy.

## Prompt: a one-line prompt for a new email rule doesn't mention the message or the settings file

Both versions get the same prompt.

```text
Add a sign-up rule: reject email addresses at throwaway.example.
```

The prompt says nothing about a message or about where values are kept, and a teammate's request wouldn't either.

A session that searches for `sign-up` lands in `users.py` in both versions: in the files shown here the word appears on one line, the docstring of `register`.

In the version for AI, reading that function shows three complete rules, each with its message. In the version for people, reading that file shows three checks that return error codes. To finish the change the session has to open two more files, and the prompt gave no hint that they exist.

The session may open those two files anyway. A case-sensitive search for `email` also returns the three lines of the message table in `validation.py`. But a session doesn't run the same searches every time, so one fresh session can make all three edits and the next can stop after one.

> **[Run record slot: E4]** For each version: searches run, files opened, files changed, and which function the new test calls. Date, tool, and model.

You can name the three places in the prompt. That works only as long as whoever is asking remembers all three, every time they ask.

## Evidence: experiment E4 will give that prompt to the same server laid out in 1, 3, and 5 files

Experiment E4 builds the order server in three layouts that give the same answer to every sign-up and pass the same four tests. It hasn't been run yet. The email rules are in one file (the version for AI), in three (the version for people), or in five (the version for people with the message table moved to `messages.py` and the decorator to `decorators.py`). Each layout gets the one-line prompt in 10 fresh sessions.

A hidden test (a test the AI never sees, used to judge whether the result is right) judges each run. It expects a 400 response with an error code and a message for an address at `throwaway.example`, a 201 for another domain and for a look-alike, `notthrowaway.example`, and the old answers in the four existing tests.

E4 also records which files each session opened and which parts of the new rule its change left out. A domain typed into the check, in a layout that keeps values in `settings.py`, is counted from the diff, because no test can see it.

With 10 runs per layout, only a large difference will be visible. If the three layouts pass about equally often, I will have to limit this chapter's claim to larger repositories, or drop it.

> **[Result slot: experiment E4]** Date, tool and model. For each layout: runs out of 10 that passed the hidden test, parts of the rule left out per run, files opened and tool calls per session.

> **[Author case slot]** A change in which an AI edited one of several places that had to change together: the date, the places, the one it missed, and what caught it.

## What people do

- [ ] Pick a code file your latest AI task changed and count what else changed in the last 20 commits that touched it: `git log -20 --name-only --full-diff --format= -- path/to/file.py | sort | uniq -c | sort -rn | head`. A file whose count is close to the top one has changed along with yours almost every time. Keep `--full-diff`, because without it Git lists only the file you named. <!-- source: notes/sources.md, git log --full-diff --> Skip the changelog and test files, which tend to change with everything, and ignore low counts, since one commit that reformats the repository adds 1 to every file. The list can't show a file that a change should have touched and didn't.
- [ ] When an AI adds a rule to code spread over several files, open its new test. If the test calls only the function the AI just wrote, ask for one that goes through the handler (`register` here).
- [ ] For one pair of files with high counts, ask the AI, with your own file names: "Move what this rule needs from settings.py into the function that enforces it. Don't change behavior. Run the tests before and after, and show me both results." Where a part has to stay put, paste a comment at the line a session will edit, such as `# A new rule also needs a message in Validator.messages (validation.py) and its value in settings.py.` Keep that comment current, because a session that reads it can't tell that the table has moved.
- [ ] Add one question to your code review checklist: "If this rule changes again, how many files will that change touch?"

## Where it breaks

Some rules have to hold in every handler: who is logged in, who may issue a refund, how tax is added. Keep a rule like that in one shared function or decorator, even though each handler's reader then has to open a second file.

If the login check were copied into every handler, a later change would have to find every copy, and a missed login check costs more than one more file to open. Chapter 6 looks at when copies are the safer choice.

Some parts can't move. If operations change values while the server is running, or translators own the messages, those parts stay in files those people can edit, and the rule stays split.

One screen also has a size limit. A session tends to read a `users.py` that holds everything about customers one section at a time, because reading the whole file uses up its context window. <!-- no source: how a session reads a long file, written as a tendency --> So move together only the lines that one change touches.

In a repository as small as this chapter's example, a session may simply open every file, and then it has seen every part of the rule. Larger context windows and better search should make that possible in bigger repositories too. The session would then have the message table in front of it, and it would still spend three reads where the one-function version needs one.
