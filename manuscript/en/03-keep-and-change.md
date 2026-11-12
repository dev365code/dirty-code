# Chapter 3. What carries over from *Clean Code*, and what changes

## Scene

You learned to drive on a car with a manual transmission. Then you bought an automatic. On the first morning your left foot reached for a clutch pedal that wasn't there, and your right hand went looking for the gear stick at every red light.

Some of your habits moved to the new car without any change. You still checked your mirrors before changing lanes. You still left room behind the car in front. Those habits were never about the gearbox. They were about the road and the other drivers.

Other habits had to go. Pressing the clutch before you braked, and picking a gear before a hill, were things you did because of how the old gearbox worked. The new gearbox does that work itself.

Your team has coding habits too, and many of them came from *Clean Code*. Now an AI reads and changes your code. Which of your habits were about the code, and which were about the person who used to read it?

## Claim

> Keep the habits that tell any reader what the code does, and weigh again the habits that only saved a human reader's memory or a human writer's typing.

## Why: some habits help every reader, and some were a bargain with a human reader

*Clean Code* starts from one fact about programmers: they spend far more time reading code than writing it. <!-- check against original --> So the book asks you to write code that the next reader can understand and change safely. This book keeps that goal. What has changed is who the next reader is.

Chapters 1 and 2 described the new reader. An AI has no memory, so every session reads your code for the first time. A session finds code by searching, and it reads only part of the repository, because everything it reads uses up its context window. It goes by names, comments, and tests when it doesn't open the code behind them. And typing costs it almost nothing.

A human reader is different in each of those ways. A person remembers the code from last month. A person asks the colleague at the next desk. A person gets tired of long names and of typing the same fix in three places.

So sort your habits into two groups.

The first group is habits that put information into the code. A name that says what a function does is one. A test that states the right answer is another. So is an error message that says what the program was doing when it failed. These habits help a person, and they help an AI more, because the AI can't ask anyone and can't remember what it was told last week.

The second group is habits that were a bargain with a human reader. A team accepted a cost because a person could cover it. Take a rule that every function must be short. A team accepts that the steps of one task end up in five small functions across three files, because a person who knows the code remembers where the five are. Or take the rule against duplicated code. A team accepts that seven callers share one function, because someone on the team remembers who the seven are. An AI session has no such memory. For this second group, the bargain has to be weighed again.

Weighing again does not mean doing the opposite every time. Today's AI learned to code from code that people wrote, so code written the *Clean Code* way is easy for it to read, and most of the time the old answer still wins. Chapters 4 to 11 go through the cases one at a time, and each chapter names the conditions under which the answer changes.

Under those conditions, this book's advice differs from *Clean Code*'s, and it says so. Chapter 5 keeps the code for one change in one place, even when that makes a function long. Chapter 6 gives a caller its own copy of a function that other callers share. Chapter 8 takes out a layer of classes that a well-known design would keep.

## Code: seven habits from *Clean Code*, and what each one means for an AI reader

The table lists seven habits. The second column is my one-line summary of what *Clean Code* advises. <!-- check against original: all seven rows --> The third column says what this book does with the habit.

| Habit | What *Clean Code* advises | For an AI reader | Chapter |
|---|---|---|---|
| Names | A name should tell you why the thing exists and what it does. | Keep, and it matters more. A session often goes by the name without opening the function. | 4 |
| Small functions | A function should be small and do one thing. | Keep "one thing." Weigh again how far apart the pieces of one change end up. | 5, 8 |
| Duplication | Don't repeat yourself. | Keep where the copies must stay equal. Weigh again where the callers change for different reasons. | 6 |
| Comments | Explain yourself in code. Comments that explain intent or warn of consequences are the good kind. | Keep. Write down the reasons that used to live in people's heads. | 7 |
| Errors | Give an exception enough context to find the cause. | Keep, and add the values and the next step. | 9 |
| Closeness | Put things that belong together near each other in the file. | Keep. "Near" now also means "found by one search" and "read in one file." | 5, 10 |
| Tests | Write the failing test first, and keep the tests as clean as the code. | Keep, and it matters more. For a person who doesn't read the code, the tests are the specification. | 14 |

Five of the seven rows say "keep" with nothing to weigh. In those rows the AI needs the same thing a person needs, and it needs it more. The other two rows, small functions and duplication, keep the habit and add a condition.

Here is one example from each kind of row. Both come from later chapters.

A row that carries over is names. In Chapter 4, a lookup function also stores what it finds in a cache. Under the name `get_user`, a session that reuses the call has no way to see the cache from the line it copies. Under the name `get_user_and_fill_cache`, the call site says it. *Clean Code* would ask for the second name too. <!-- check against original -->

A row that gets weighed again is duplication. In Chapter 6, seven callers share one function that formats an amount of money. The shop's accountant asks for commas in one report. A session that edits the shared function gives commas to all seven callers, and one of the seven is a file that the payment provider splits on commas. If the report has its own copy of the function, the same edit can't reach the other six. Chapter 6 also shows the case where a copy is the wrong choice.

## Prompt: a style rule in your rules file is a prompt, and the AI follows it to the letter

Your team's coding conventions used to be advice for people. A person reads "keep functions short" and uses judgment about when to stop. Once you put the same sentence in your rules file, it becomes part of every prompt. A rules file is the instruction file in your repository that the AI reads when it starts work.

Compare two ways to write the same convention.

```text
- Keep every function under 20 lines.
```

```text
- Keep the lines that one change has to touch in one function, even if
  the function runs long. Split a function when one part of it has its
  own reason to change.
```

An AI tends to follow an instruction to the letter. Given the first rule, a session that writes a 35-line function is likely to cut it into two or three functions at whatever line makes the count work. The rule is satisfied. Whether the pieces make sense apart is a question the rule never asked.

The second rule is longer, and it gives the session the reason along with the limit. A session can apply a reason to a case the rule's author didn't foresee. I haven't measured the difference between these two rules. Chapter 11 looks at how to write instructions like these.

## Evidence: each row of the table is tested by the experiment in its own chapter

This chapter runs no experiment of its own. Each row in the table is a claim that a later chapter tests. The table below says which experiment tests which row. None of them has been run yet, so the last column is empty.

| Habit | Experiment | What it counts | Result |
|---|---|---|---|
| Names | E3 (Chapter 4) | How often a session calls a function that writes when the prompt said not to write | **[Result slot: E3]** |
| Small functions, closeness | E4 (Chapter 5), E7 (Chapter 8), E9 (Chapter 10) | How often a session finishes a change when the code for it is in 1, 3, or 5 files, or behind 0, 1, or 3 hops, and how often it finds the right file from the folder names | **[Result slot: E4, E7, E9]** |
| Duplication | E5 (Chapter 6) | How many other callers change when a session is asked to change one | **[Result slot: E5]** |
| Comments | E6 (Chapter 7) | How often a number survives a cleanup when a comment gives its reason | **[Result slot: E6]** |
| Errors | E8 (Chapter 9) | What a session does next when the error line carries the values and the next step | **[Result slot: E8]** |
| Tests | E12 (Chapter 14) | How often a session changes the assertion when asked to make a test pass | **[Result slot: E12]** |

If an experiment shows no difference, I will say so in that chapter and change the row here.

## What people do

- [ ] Open your team's style guide, or your linter's configuration if that's where the rules live. For each rule, ask: "Does this rule put information into the code, or does it save a person some effort?" Mark the rule I for information or E for effort.
- [ ] Leave the rules you marked I alone. They carry over.
- [ ] For each rule you marked E, write one line next to it: what the rule costs a reader who has no memory of the code. If you can't name a cost, the rule carries over too.
- [ ] Open your rules file. For each sentence that states a limit without a reason ("under 20 lines," "no comments," "never duplicate"), add the reason, or delete the sentence.

## Where it breaks

People still read some of your code. Someone gets paged when the payment code fails at night, and that person has to follow the code under pressure (Chapter 17). Code like that has two readers, and a habit that helps the AI but slows that person down is a bad trade there. When the two readers pull in different directions, choose for the person who has to act when things go wrong.

Some rules exist for tools, not for readers. A formatter's line length and an import order are examples. No reader's memory is involved, so nothing in this chapter applies to them. Keep them.

The table can be read as a list of things to stop doing. That reading is wrong. Five rows carry over, and the other two keep the habit and add a condition. A team that drops small functions, shared code, and self-explaining code because "the reader is an AI now" will have code that neither reader can follow.

Better models will move some of these lines. A model with a larger context window can read more files before it writes, so code spread across files will cost it less. A model that checks every caller before it edits a shared function will make the duplication row matter less. The rows about names, errors, and tests don't depend on those limits. They are about information that isn't anywhere unless someone writes it down.

I expect the table to change in the other direction as well. *Clean Code*'s advice was shaped by what a human reader can hold in mind and what a human writer is willing to type. An AI reader has different limits, and code arranged for those limits already differs from clean code in two rows of the table. As more code is written by AI and read by AI, I expect more rows to change. Code arranged that way is what this book's title calls dirty code. The seven rows show where it stands today, and the experiment in each chapter is how a row gets corrected.
