# Closing. AI writes the code. People write the guarantees.

You are driving to work again. This time you follow the GPS without arguing, down the side street it picks. It has seen this morning's traffic, and you haven't.

Notice what you still did. You typed the destination. You glanced at the fuel gauge before you pulled out. When the screen told you to turn into a road with an orange barrier across it, you didn't turn. The GPS chose the route. You decided where the car had to end up and what it must not do on the way.

That is what this book has said about code, in eighteen chapters.

The hand that writes the code has changed. An AI writes it, and an AI reads it first. This book's experiments found that today's AI reads clean code well: built both ways, the shop passed about as often either way. The request that every model lost in the clean version needed a fact that no code showed, the reason for a 37-second timeout, and dirty code is code that writes such facts down: a name that says what a function writes, a reason next to an odd number, an error line with the values in it, a prompt that states the rule. By the standard most of us learned, some of that code looks messy.

Deciding what must never break has not changed hands. Does free shipping start at the list total or at the amount the customer paid? May a gift card ever pay out more than it holds? Does a timeout mean "try again" or "look it up first"? None of these answers is in the code until someone decides it. An AI can't decide it, because each answer is a fact about your shop. A person decides, writes the answer down as a sentence, and turns the sentence into a check that can fail.

This book has called those answers guarantees: a sentence that says what must never happen. What keeps a guarantee is small: one example with its answer, and a test that someone watched fail. A line in the rules file passes the guarantee on to the AI, but nothing enforces that line. A person can read every one of those sentences and tests. That is no longer true of the code.

Better models will make parts of this book matter less. A session that reads a whole repository before it writes won't miss the file that holds the rest of a rule, and a session that lists every caller before it edits won't need a copy to keep the other callers safe. No model can read a reason that nobody wrote down. Whose fee a restocking fee is, and what must never happen in your shop, are decisions, and a person at the shop makes them.

I expect code written for an AI reader to move further from clean code as time goes on. It differs in four places today, Chapters 5 to 8, and in Chapter 18 a session changed small programs in assembly as reliably as in Rust source. If I'm right, "dirty code" will cover more in five years than it covers in this book. The way to find out is the one this book uses: build the code two ways, give both to a reader that has never seen them, and let a test that the reader can't see decide.

Here is the smallest version of all of it, for tomorrow morning. Before you hand over your next task, write one sentence that begins "This must never happen:" and one example with its answer. Give the AI both. When it says it's done, run the example yourself.

AI writes the code. People write the guarantees.
