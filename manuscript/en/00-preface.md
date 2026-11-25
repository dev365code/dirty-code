# Preface. To *Clean Code*: we learned to write code for people

Look along the bookshelf of a developer who has been at it for ten years, and there is a good chance you'll find *Clean Code*, with pencil lines under some of its sentences. In its first chapter the book makes one observation: programmers spend far more time reading code than writing it. So it asks you to write code for the person who will read it next. <!-- checked 2026-11-25 against Clean Code (2008): ch. 1 "We Are Authors" p. 14 (notes/sources.md) -->

Now count something. Of the code that was merged into your repository today, how many lines did you read one by one? If an AI wrote most of it, the honest answer is probably "few." And when you told the AI to fix a bug, the first one to find the code and read it was the AI.

The next reader of your code has changed. *Clean Code* taught us to write for a person. This book asks what to write for an AI, and what the person does once the reading has moved to someone else.

## What "dirty code" means

Start with what the experiments found. Today's AI learned to code from code that people wrote, and it reads clean code well. Built both ways and given the same twenty requests in the combined experiment of Chapter 16, the version for people and the version for AI passed about equally often: 190 and 190 of 200 runs with Codex, 177 and 178 with Claude Sonnet 5.5, and 173 and 171 with Claude Haiku 5.5.

The two versions came apart where a session had to guess a fact that no code shows. In the version for people, nothing said why the approval timeout was 37 seconds, and every session asked to clean up the payment code and round its constants changed it, with all three models. In a copy where nobody had written down where a partial refund's leftover cents go, all ten Codex sessions wrote a rule of their own.

In this book, dirty code is code that puts what a teammate used to remember, or used to answer when asked, into the files a session reads, and that reports its own state in a form a machine can check. Most of it is advice *Clean Code* would accept. In four places my advice differs from *Clean Code*'s. Chapter 5 keeps the lines that one change touches in one function, even when the function runs long, where *Clean Code* asks for small functions that do one thing. Chapter 6 gives a caller its own copy when someone else decides what it outputs, where *Clean Code* would remove the duplication. Chapter 7 asks for a comment above every value that looks wrong on purpose, and the comment repeats the value, a repetition *Clean Code* calls redundant. Chapter 8 replaces classes that differ in one number with a table, where *Clean Code* prefers polymorphism to code that switches on a type. <!-- checked 2026-11-25 against Clean Code (2008): ch. 3 "Do One Thing" p. 35 and "Don't Repeat Yourself" p. 48, ch. 4 "Redundant Comments" p. 60, ch. 17 G23 p. 299 (notes/sources.md) --> Each of those chapters gives its reason and says how far its experiment backs it. So far the experiments back Chapter 7, back Chapter 5 in one case, are mixed for Chapter 6, and show no difference yet for Chapter 8.

I also expect something the experiments don't show yet. As more code is written by AI and read by AI, I expect people to arrange more of it for that reader, even where a person finds the result harder to follow. A modern engine bay already works that way: a person who opens the hood sees a plastic cover, and the scan tool plugged in under the dashboard reads the fault. The furthest my experiments reached in that direction is Chapter 18: in ten small programs, a session given only the assembly changed it as reliably as a session given the Rust source. By the old standard some of this code looks messy, and the name dirty code is meant to say so.

## Where I am writing from

For more than five years my job was to catch fraud and money laundering at crypto exchanges. No one can read every transaction an exchange handles in a day, so I wrote rules that read them and flagged what looked wrong. Today I build AI agents, and AI writes much of the code I work with. This book takes the same approach to code that I took to transactions: when you can't read everything, you decide what must never get through, and you build the check that catches it.

## What is proven and what isn't

Most claims in this book come with an experiment, and most experiments have one shape: the same feature built in two shapes, the same request sent to ten fresh sessions for each, and tests that the AI never sees deciding which runs succeeded. Where an experiment is shaped differently, such as three forms of a prompt in Chapters 12 and 13, answers read by hand in Chapters 15 and 17, or counts with no pass or fail in Chapter 4, the chapter says so. Chapter 3 runs no experiment of its own.

I expected the version for AI to win. In the combined experiment it didn't. The two repositories passed about equally often with all three models, and each lost on different requests. The version for people lost the cleanup that changed a value whose reason was written nowhere. The version for AI lost requests on which a line in its rules file, a line that Chapter 7 had recommended, made the session stop and ask. Chapter 7 tells that story and tests two rewritten lines.

Where an experiment went against a claim, I narrowed the claim and said so in the chapter: Chapters 4, 5, 6, 7, 8, 10, 12, 15, 17, and 18. Every chapter's Evidence section gives the date, the tool, the models, and the counts. Appendix A says how the sessions were run and judged, including the three places where my hidden tests asked for more than a request said and how I corrected them. The full tables are in the repository at `experiments/RESULTS.md`. Nothing in the text is a made-up result. Where I ran something myself while writing, such as a listing or a command, the text says "I ran" and reports what happened.

## How to read this book

Part I has three chapters, and they are meant to be read in order. They describe the new reader: an AI that reads your code before you do, that has no memory of yesterday, and that changes which of your habits still pay.

Part II has eight chapters, one for each thing you can change in the code: names, where code lives, duplication, comments, layers, errors, folders, and prompts. Each stands alone. Start with the one that hurt you last week.

Part III is about what people do when they no longer read every line. They cut the work into pieces they can check, decide what must never break, watch a test fail before they trust it, and have a second reader inspect what the first one wrote.

Part IV asks whether any of this is true and how far it goes. It describes the experiment that puts the whole book in one repository, the moments when a person still has to read code, and the question of whether code itself is on its way out.

Most chapters have the same eight sections in the same order, and each has a checklist called "What people do." If you read nothing else in a chapter, read that. Chapters 5 to 8 add a section on where their opinion differs from *Clean Code*. A page of terms follows this preface. After the closing come a list of the book's patterns, with what each one costs and how far it was tested, and Appendix A, on how the experiments were run.
