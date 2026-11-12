# Chapter 10. The map AI navigates by: folder names and an index file

## Scene

A courier has a parcel for "the house with the blue door on Mill Road." Mill Road turns out to have three blue doors. The courier parks, walks up to the first one, and rings the bell. Wrong house. The second one has nobody home. A neighbor finally points across the street.

The next parcel says "14 Mill Road." The courier drives to number 14 and hands it over. It takes one look at the numbers on the gates.

The person who wrote "the blue door" wasn't being careless. Everyone on Mill Road knows which house that is.

When an AI comes into your repository to find the refund code, what do your folder names give it: an address, or a blue door?

## Claim

> An AI finds its way by the names of folders and files, so name them for what's inside, and keep one page that says what lives where.

## Why: a session's first look at your repository is a list of names

A developer who has worked in a repository for a year knows where things are. Ask where the refund math lives, and the developer says "`utils/helpers.py`, near the bottom" without looking. The name of that file never had to mean anything, because nobody found the code by its name.

A new session finds everything by looking. The cheapest thing it can look at is the list of folders and files, which costs one command and a few lines of text. If the names in that list say what's inside, the list alone answers the question "where is the refund code?" If the names are `utils`, `common`, `helpers`, and `misc`, the list answers nothing, and the session has to search inside the files.

Searching inside files often works. If the code uses the word `refund`, a search for `refund` finds it. But the search returns every line with that word: the function, its callers, its tests, and an old comment. The session then has to choose which of those hits to open first. A file named `refunds/refund_amount.py` tells the session where to start. A file named `utils/helpers.py` tells it nothing.

A search also fails when your words and the code's words differ. You ask about "money back," and the code says `reversal`. A folder name the session can see in the first listing bridges that gap. A function buried in a helper file doesn't.

Names can only say so much. They can't say that two folders have to agree with each other, or which file to open first. That's what the index file is for. An index file is one page at the top of the repository that lists what lives where. A session that reads it has the map before it takes a step.

## Code: the same shop in two layouts, and the one-page index that goes with the second

The "code" in this chapter is a folder tree. Here is the shop's order server in the version for people.

```text
shop/
├── app.py
├── models.py
├── services/
│   ├── manager.py
│   └── processor.py
├── utils/
│   ├── common.py
│   ├── helpers.py
│   └── misc.py
└── tests/
    ├── test_services.py
    └── test_utils.py
```

A team can work in this layout for years. Each folder holds one kind of thing: services in one, helpers in another, and tests beside them. The people on the team know that `processor.py` charges cards, that the refund math is in `helpers.py`, and that the settlement totals are in `common.py`. None of that is in the names.

Look for the word `refund` in this tree. No folder name has it and no file name has it. A session has to search inside the files, and the first thing it learns is that refund code is spread across `helpers.py`, `common.py`, and `processor.py`.

Here is the version for AI. The code is the same. The files are grouped by what the shop does, and they're named for what they hold.

```text
shop/
├── INDEX.md
├── orders/
│   ├── orders.py
│   └── cancel_order.py
├── payments/
│   ├── charge.py
│   └── provider_client.py
├── refunds/
│   ├── refund_amount.py
│   └── refund_export.py
├── settlement/
│   └── payout_report.py
├── users/
│   └── signup.py
└── tests/
    ├── test_orders.py
    ├── test_payments.py
    ├── test_refunds.py
    ├── test_settlement.py
    └── test_users.py
```

Look for `refund` again. This time the listing itself has four matches: the folder `refunds/`, the two files inside it, and `tests/test_refunds.py`. A session knows where to go before it opens anything.

The index file, `INDEX.md`, says what the names can't.

```text
# Where things live

- orders/      Creating and canceling orders. Start at orders/orders.py.
- payments/    Charging cards through the payment provider.
               All calls to the provider go through payments/provider_client.py.
- refunds/     How much to refund, and the refund file sent to the provider.
- settlement/  The accountant's payout report. A refund here must match
               refunds/refund_amount.py to the cent.
- users/       Sign-up and the rules for email addresses.
- tests/       One test file per folder above.
               Run: python3 -m unittest discover -s tests
```

Three things in that page aren't in any name. The line for `orders/` says which file to open first. The line for `payments/` says that one file is the only door to the provider. The line for `settlement/` says that two folders have to agree. A session working on refunds that reads that last line knows to open `settlement/` too.

The index is short on purpose. It has one line or two for each top-level folder, and nothing about individual functions. A page that tries to describe every file goes out of date the first week.

## Prompt: a question about where the refund code is, asked of both layouts

Both layouts get the same prompt. It asks a question and changes nothing.

```text
Where is the code that decides how much to refund when an item comes back?
Name the file and the function. Don't change anything.
```

In the version for people, a session is likely to list the files, see nothing about refunds, and search inside them. It gets hits in several files and has to open them to tell the function that decides the amount from the code that only calls it. Each file it opens is another tool call, and it takes up more of the session's context window.

In the version for AI, the listing points at `refunds/refund_amount.py`. If the session reads `INDEX.md` first, the line for `refunds/` says the same thing in a sentence. The session opens one file to find the function name.

Both sessions can reach the right answer. What I expect to differ is how many steps each one takes, and how often a session stops at a caller and reports it as the answer. I haven't measured either.

> **[Run record slot: E9]** For each layout: the commands the session ran, the files it opened, and its answer. Date, tool, model.

## Evidence: experiment E9 will ask ten "where is it?" questions of three layouts

Experiment E9 will build the order server in three layouts that hold the same code. The first is the version for people. The second is the version for AI without `INDEX.md`. The third is the version for AI with `INDEX.md`. The second layout is there so I can tell what the names do from what the index does.

Each layout gets ten questions like the one above, about ten different parts of the shop. Each question goes to 5 fresh sessions per layout, 150 sessions in all. An answer counts as right when it names the file and the function that hold the code. E9 counts the right answers and the tool calls each session made before it answered.

E9 hasn't been run yet. This server has a few dozen files, and a session can read a repository that small from end to end. If the three layouts score about the same, I'll say so here, and the claim will be limited to larger repositories.

> **[Result slot: experiment E9]** Date, tool and model. For each layout: right answers out of 50, and tool calls per session before answering.

> **[Author case slot]** A real case in which an AI looked for something in a repository and the folder names or an index file sent it to the right place, or the wrong one.

## What people do

- [ ] List the files whose names say nothing: `git ls-files | grep -iE "(utils|helpers|common|misc)"`. For each one, write down in a few words what's actually inside. Those words are the names the files should have.
- [ ] Ask a fresh session three questions of the form "Where is the code that decides X? Name the file and the function. Don't change anything." Use three things your business cares about. Check each answer by opening the file, and count the files the session opened on the way.
- [ ] Write `INDEX.md` at the top of the repository: one or two lines per top-level folder, saying what it holds, which file to start at, and which other folder it has to agree with. Then add one line to your rules file (the instruction file in your repository that the AI reads when it starts work): "Read INDEX.md before you search."
- [ ] Check the index against the folders whenever the folders change. These two commands print a folder that the index names and that doesn't exist, and a folder that exists and isn't in the index:

  ```sh
  grep -oE "^- [A-Za-z_]+/" INDEX.md | cut -c3- | while read d; do [ -d "$d" ] || echo "in index, missing: $d"; done
  for d in */; do grep -q "^- $d" INDEX.md || echo "not in index: $d"; done
  ```

  The commands compare names only. They can't tell you that a description is still true.

## Where it breaks

An index that is wrong is worse than no index. A session that reads "all calls to the provider go through `payments/provider_client.py`" will believe it, even after someone has added a second client in another folder. It will then tell you with confidence that it found every call. So keep the index short enough that you'll actually update it, and change it in the same commit that moves a folder.

Renaming folders has a cost. Imports change, open branches conflict, and the history of a moved file is harder to follow. You don't have to rename everything at once. Write the index first, which costs one page. Then move code out of `utils/` a piece at a time, when you're already changing that piece.

Some names aren't yours to choose. A web framework may require folders called `models`, `views`, and `migrations`. Leave those alone and let the index say which business each one serves.

In a small repository, none of this matters much. A session can list every file and open most of them. The gap between an address and a blue door grows as the repository does.

Better search will take over part of this. A tool that searches code by meaning can find the refund math whatever the file is called. It still can't know that the payout report has to match the refund amount to the cent. Someone has to write that sentence down, and the index is where a session will look for it.
