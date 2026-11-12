# Preface. To *Clean Code*: we learned to write code for people

Look along the bookshelf of a developer who has been at it for ten years, and there is a good chance you'll find *Clean Code*, with pencil lines under some of its sentences. The book starts from one observation: programmers spend far more time reading code than writing it. So it asks you to write code for the person who will read it next. <!-- check against original -->

Now count something. Of the code that was merged into your repository today, how many lines did you read one by one? If an AI wrote most of it, the honest answer is probably "few." And when you told the AI to fix a bug, the first one to find the code and read it was the AI.

The next reader of your code has changed. *Clean Code* taught us to write for a person. This book asks what to write for an AI, and what the person does once the reading has moved to someone else.

## What "dirty code" means

Start with what hasn't changed. Today's AI learned to code from code that people wrote. So code written the way *Clean Code* teaches is easy for it to read as well.

But the advice in *Clean Code* was fitted to a human reader. It was fitted to how much a person can hold in mind, to a person's patience for typing, and to the fact that a person remembers last month and can ask a colleague. An AI reader differs in each of these. It has no memory, so it reads your code for the first time, every time. It finds code by searching, and it reads only part of the repository. It follows your words to the letter. And typing costs it almost nothing.

Fit the code to that reader, and in some places you get code that *Clean Code* would not call clean. A function is copied on purpose. A function is left long so that one change stays in one place. A number carries a comment that says why it isn't the round number next to it. A prompt is checked into the repository and tested like code.

I expect that list to grow. As more code is written by AI and read by AI, people will arrange more of it for that reader, and it will look less and less like clean code. That code is what this book calls dirty code. The name is deliberate. By the old standard, some of it looks messy.

Where this book's advice differs from *Clean Code*'s, it says so plainly. Chapter 5 lets a function run long. Chapter 6 copies a function that *Clean Code* would have you share. <!-- check against original --> Chapter 8 takes out a layer of classes. Where the old advice matters even more for the new reader, as with names and tests, the book says that too.

## Where I am writing from

For more than five years my job was to catch fraud and money laundering at crypto exchanges. No one can read every transaction an exchange handles in a day, so I wrote rules that read them and flagged what looked wrong. Today I build AI agents, and AI writes much of the code I work with. This book takes the same approach to code that I took to transactions: when you can't read everything, you decide what must never get through, and you build the check that catches it. <!-- author check: the same facts as the author note in the README -->

> **[Author case slot]** How the author works with AI on real projects: who writes, who inspects, and what has to pass before anything is released.

## What is proven and what isn't

Every claim in this book comes with an experiment. The same feature is built in two shapes. The same request is sent to fresh sessions at least ten times. Tests that the AI never sees decide which runs succeeded.

In this draft, the experiments have not been run. A line marked **[Result slot]** shows where a number will go, and a line marked **[Run record slot]** shows where the record of a real session will go. Nothing in the text is a made-up result. Where I ran something myself while writing, such as a listing or a command, the text says "I ran" and reports what happened.

If a result goes against a claim, I will change the claim and say so in that chapter.

## How to read this book

Part I has three chapters, and they are meant to be read in order. They describe the new reader: an AI that reads your code before you do, that has no memory of yesterday, and that changes which of your habits still pay.

Part II has eight chapters, one for each thing you can change in the code: names, where code lives, duplication, comments, layers, errors, folders, and prompts. Each stands alone. Start with the one that hurt you last week.

Part III is about what people do when they no longer read every line. They cut the work into pieces they can check, decide what must never break, watch a test fail before they trust it, and have a second reader inspect what the first one wrote.

Part IV asks whether any of this is true and how far it goes. It describes the experiment that puts the whole book in one repository, the moments when a person still has to read code, and the question of whether code itself is on its way out.

Every chapter has the same eight sections, and the seventh is always a checklist called "What people do." If you read nothing else in a chapter, read that.
