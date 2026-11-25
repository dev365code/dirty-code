# Chapter 10. AI finds code by the words in your files, and an index saves it a step

## Claim

> An AI finds code by searching the words inside your files, so the names and descriptions in the files matter most, and folder names and an index save it about one step.

## Why: a session finds code by the words inside your files, and names tell it where to look first

A developer who has worked in a repository for a year knows where things are. Ask where the refund math lives, and the developer says "`utils/helpers.py`, near the bottom" without looking. The name of that file never had to mean anything, because nobody found the code by its name.

A new session finds everything by looking, and it can look in two ways. It can list the folders and files, which costs one command and a few lines of text, or it can search inside the files for a word from your question. In this chapter's runs, every Claude Sonnet 5.5 session searched first, and most Claude Haiku 5.5 sessions listed the files first. A search hits the words inside the files: function names, docstrings, and comments. So those words decide whether a session finds the code, and folder and file names help it decide which hit to open first.

If the code uses the word `refund`, a search for `refund` finds it. But the search returns every line with that word: the function, its callers, its tests, and an old comment. The session then has to choose which of those hits to open first. A file named `refunds/refund_amount.py` tells the session where to start. A file named `utils/helpers.py` tells it nothing.

A search also fails when your words and the code's words differ. You ask about "money back," and the code says `reversal`. A docstring that says "the money a customer gets back" bridges that gap, and so does a folder name the session sees in its first listing. A function with neither, in a helper file, won't turn up in a search for the words of your question.

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

Look for `refund` again. This time the listing itself has four matches: the folder `refunds/`, the two files inside it, and `tests/test_refunds.py`. A session that starts from the file list knows where to go before it opens anything.

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

In the version for people, a session that lists the files sees nothing about refunds and has to search inside them. It gets hits in several files and has to open them to tell the function that decides the amount from the code that only calls it. Each file it opens is another tool call, and it takes up more of the session's context window.

In the version for AI, the listing points at `refunds/refund_amount.py`. If the session reads `INDEX.md` first, the line for `refunds/` says the same thing in a sentence. The session opens one file to find the function name.

Both sessions can reach the right answer. What I expected to differ is how many steps each one takes, and how often a session stops at a caller and reports it as the answer. The Evidence section has both counts.

I ran ten questions of this kind on 2026-11-22 in fresh sessions of Claude Code, in the large repository of Appendix A, a made-up shop of 518 files. None of the ten was about refunds. Here is one of them, asked of all three layouts by Claude Sonnet 5.5: "Where is the code that decides how each payout line looks on the accountant's settlement report?"

In every layout, the session's first command searched the contents of all files for `settlement` and `payout`. In the layout for people, it then searched those files for lines that define a function, printed parts of `core/shared.py` and `core/rules.py`, and answered `payout_row` in `core/shared.py`, quoting the function's docstring. That took 5 calls to the shell tool. In the layout for AI, it listed the functions in `shop/settlement/report.py` and printed that file, in 4 calls. With `INDEX.md`, it printed the index and then the same file, also in 4. All three answers were right.

## Evidence: in a shop of 518 files, the three layouts got about the same answers, and generic names cost a little under one tool call per question

Experiment E9 builds the order server in three layouts that hold the same code. The first is the version for people. The second is the version for AI without `INDEX.md`. The third is the version for AI with `INDEX.md`. The second layout is there so I can tell what the names do from what the index does.

Each layout gets ten questions like the one above, about ten different parts of the shop. Each question goes to 5 fresh sessions per layout, 150 sessions in all. An answer counts as right when it names the file and the function that hold the code. E9 counts the right answers and the tool calls each session made before it answered.

This chapter's server has a few dozen files, and a session can read a repository that small from end to end. So I ran E9 on 2026-11-22 in the larger shop from the Prompt section. In its layout for people, the same modules are merged into 30 files with names like `services/manager.py` and `utils/extra.py`. The merge also dropped the description at the top of each module, so that layout lost those docstrings as well as the folder and file names. All three layouts pass the same 1,317 tests. I used Claude Haiku 5.5 and Claude Sonnet 5.5 at their default settings, 150 sessions per model. I didn't run this experiment with Claude Opus 5.5.

Two of my ten questions turned out to have two right answers, because two functions in the shop do the same job. I left those two out. For the other eight questions there are 40 answers per layout and model.

| Layout | Haiku right | Sonnet right | Tool calls per session, Haiku / Sonnet |
|---|---|---|---|
| For people, generic file names | 38 of 40 | 39 of 40 | 4.3 / 4.4 |
| For AI, without `INDEX.md` | 40 of 40 | 40 of 40 | 3.7 / 3.5 |
| For AI, with `INDEX.md` | 40 of 40 | 40 of 40 | 3.3 / 3.4 |

The tool calls are averages over all ten questions.

Two of the three wrong answers said the session couldn't find the code that makes a wishlist's share link. When I merged the modules into generic files, the description at the top of each module was lost, so nothing in the file names or the code said that those functions belonged to the wishlist. The third wrong answer named a customer-segment function in place of the loyalty tier function. No answer named a caller in place of the code that decides.

Every Sonnet session started with a search of the files' contents for words from the question, as in the run above. Most Haiku sessions started with a list of the files: 111 of 150 ran `git ls-files` first and 36 ran `git status`. Either way, the names and docstrings inside the files decided the answer. Going from the generic layout to feature folders, a change that also restored each module's description, saved a little under one tool call per question, and adding the index saved another 0.1 to 0.4.

Before the runs, the experiment plan said that if the three layouts scored about the same, I would limit the claim to larger repositories. This repository was large, and the layouts still scored about the same, so the claim is narrower than that. Folder names and an index saved these sessions a step. The words inside the files, the function names and the description at the top of each module, decided whether a session found the code at all. *Clean Code*'s advice to choose names that reveal intent covers the first of those. <!-- checked 2026-11-25 against Clean Code (2008): ch. 2 "Use Intention-Revealing Names" p. 18 (notes/sources.md) -->

<!-- [Author case slot] A real case in which an AI looked for something in a repository and the folder names or an index file sent it to the right place, or the wrong one. -->

## What people do

- [ ] List the files whose names say nothing: `git ls-files | grep -iE "(utils|helpers|common|misc)"`. For each one, write down in a few words what's actually inside. Those words are the names the files should have.
- [ ] Ask a fresh session three questions of the form "Where is the code that decides X? Name the file and the function. Don't change anything." Use three things your business cares about. Check each answer by opening the file, and count the files the session opened on the way.
- [ ] Write `INDEX.md` at the top of the repository: one or two lines per top-level folder, saying what it holds, which file to start at, and which other folder it has to agree with. Then add one line to your rules file: "Read INDEX.md before you search."
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

In a small repository, none of this matters much: a session can list every file and open most of them.

A tool that searches code by meaning can find the refund math whatever the file is called. It still can't know that the payout report has to match the refund amount to the cent. Someone has to write that sentence down, and the index is one place where a session can find it.
