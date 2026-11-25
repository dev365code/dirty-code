# Chapter 3. What carries over from *Clean Code*, and what changes

## Scene

You learned to drive on a car with a manual transmission. Then you bought an automatic. On the first morning your left foot reached for a clutch pedal that wasn't there, and your right hand went looking for the gear stick at every red light.

Some of your habits moved to the new car without any change. You still checked your mirrors before changing lanes. You still left room behind the car in front. Those habits were never about the gearbox. They were about the road and the other drivers.

Other habits had to go. Pressing the clutch before you braked, and picking a gear before a hill, were things you did because of how the old gearbox worked. The new gearbox does that work itself.

Your team has coding habits too, and many of them came from *Clean Code*. Now an AI reads and changes your code. Which of your habits were about the code, and which were about the person who used to read it?

## Claim

> Today's AI reads clean code well, so keep *Clean Code*'s habits, and depart from them only in the four places of Chapters 5 to 8, where a new session can't remember the team's reasons or ask a colleague.

## Why: some habits help every reader, and some were a bargain with a human reader

*Clean Code* starts from one fact about programmers: they spend far more time reading code than writing it. <!-- check against original --> So the book asks you to write code that the next reader can understand and change safely. This book keeps that goal. What has changed is who the next reader is.

Chapters 1 and 2 described the new reader. An AI has no memory, so every session reads your code for the first time. A session finds code by searching, and it reads only part of the repository, because everything it reads uses up its context window. It goes by names, comments, and tests when it doesn't open the code behind them. And typing costs it almost nothing.

A human reader is different in each of those ways. A person remembers the code from last month. A person asks the colleague at the next desk. A person gets tired of long names and of typing the same fix in three places.

So sort your habits into two groups.

The first group is habits that put information into the code. A name that says what a function does is one. A test that states the right answer is another. So is an error message that says what the program was doing when it failed. These habits help a person, and they help an AI more. An AI can ask you a question, but only about a gap it notices, and it can't remember what it was told last week.

The second group is habits that were a bargain with a human reader. A team accepted a cost because a person could cover it. Take a rule that every function must be short. A team accepts that the steps of one task end up in five small functions across three files, because a person who knows the code remembers where the five are. Or take the rule against duplicated code. A team accepts that seven callers share one function, because someone on the team remembers who the seven are. An AI session has no such memory. For this second group, the bargain has to be weighed again.

Weighing again does not mean doing the opposite every time. Today's AI learned to code from code that people wrote, so code written the *Clean Code* way is easy for it to read, and in this book's experiments the old answer usually still won. Chapters 4 to 11 go through the cases one at a time, and each chapter names the conditions under which the answer changes.

## Code: nine habits, what *Clean Code* advises, and what this book does with each

The table lists nine habits. The second column is my one-line summary of what *Clean Code* advises. <!-- check against original: all nine rows --> The last two columns say how far this book's experiments back the change, in a few words, and which chapter has the details.

| Habit | What *Clean Code* advises | What this book does, and why | How far the experiments back it | Chapter |
|---|---|---|---|---|
| A rule settled in a chat | Doesn't take this up: its reader remembers yesterday and can ask a colleague | Write the rule in a comment or the rules file, because a new session reads only the files | Pays off | 2 |
| Names | A name says what the thing does, side effects included | The same, and a function that changes stored data says so, because the name is what shows at every call | No difference when the prompt named the write. When it didn't, one model filled a cache less often under the longer name | 4 |
| Small functions | A function is small and does one thing | Keep the lines that one change touches in one function, because a session edits the files its search finds | Pays off in one case: a rule in five files of a large repository, with one model | 5 |
| Duplication | Don't repeat yourself | A caller whose output someone else decides gets its own copy, because a session knows only the callers it searched for | Mixed: no caller broke either way, and sharing grew a switch that one caller uses | 6 |
| Comments | Explain yourself in code. Comments that explain intent or warn of consequences are the good kind | A reason above every value that looks wrong on purpose, repeating the value, because the reason lives outside the code | Pays off when a cleanup asks for round values | 7 |
| Layers | Prefer polymorphism to code that switches on a type | A layer only when it does a job today, because a session can stop early at any hop | No difference yet | 8 |
| Errors | Give an exception enough context to find where and why it failed | The same, and the line adds the values and the next step, because a session may have only the line | Changed what the reports said, not whether the fix was right | 9 |
| Names of files and folders | Choose names that reveal intent | The same inside files. Folder names and a one-page index save a step, because a session searches the words inside files first | A small difference: about one tool call per question | 10 |
| Tests | Write the failing test first, and keep the tests as clean as the code | The same, and watch every check fail, on the old code and on a wrong answer you planted, because a pass shows only what the check looked at | The method is the point. No session weakened an assertion | 14 |

Four rows, Chapters 5 to 8, go another way from *Clean Code*. Each of them moves something a teammate used to carry in memory into the code: which files a rule touches, which callers share a function, why a value is odd, and where the route through the classes ends. Two rows, errors and tests, add to *Clean Code*'s advice, and two, names and the names of files, keep it as it is. The first row is a question *Clean Code* had no reason to ask.

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

## Evidence: the last column of the table, and the experiment that puts all the rows in one repository

This chapter runs no experiment of its own. The last column of the table gives each row's result in a few words, the chapter named in that row gives the experiment, and the list of patterns at the end of the book gives the deciding number for each.

Chapter 16 tests the rows together. It builds one shop twice, once with *Clean Code*'s habits and once with this book's, and sends both the same twenty requests. With three models, the two versions passed about equally often: 190 and 190 of 200 runs with Codex, 177 and 178 with Claude Sonnet 5.5, and 173 and 171 with Claude Haiku 5.5. That is the result this chapter's claim rests on: today's AI reads clean code well. The one request that every model lost in the version for people was the cleanup that needed a fact no code in that version showed, the reason for a 37-second timeout.

## What people do

- [ ] Open your team's style guide, or your linter's configuration if that's where the rules live. For each rule, ask: "Does this rule put information into the code, or does it save a person some effort?" Mark the rule I if it puts information into the code, E if it saves a person effort, or both.
- [ ] Leave the rules you marked only I alone. They carry over.
- [ ] For each rule you marked E, write one line next to it: what the rule costs a reader who has no memory of the code. If you can't name a cost, the rule carries over too.
- [ ] Open your rules file. For each sentence that states a limit without a reason ("under 20 lines," "no comments," "never duplicate"), add the reason, or delete the sentence.

## Where it breaks

People still read some of your code. Someone gets paged when the payment code fails at night, and that person has to follow the code under pressure (Chapter 17). Code like that has two readers, and a habit that helps the AI but slows that person down is a bad trade there. When the two readers pull in different directions, choose for the person who has to act when things go wrong.

Some rules exist for tools, not for readers. A formatter's line length and an import order are examples. No reader's memory is involved, so nothing in this chapter applies to them. Keep them.

The table can be read as a list of things to stop doing. Most of its rows keep *Clean Code*'s advice, and the four that go another way each name the case where they do. A team that drops small functions, shared code, and self-explaining code because "the reader is an AI now" will have code that neither reader can follow.

A session that can read more files before it writes would pay less for code spread across files, and a session that checks every caller before it edits a shared function would make the duplication row matter less. The rows about names, errors, and tests are about information that is nowhere in the code until someone writes it down, so a larger context window or a better search leaves them as they are.

The rows that go another way today are those of Chapters 5 to 8. Chapter 18 says where I expect the table to go from here.
