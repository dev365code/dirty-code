# Closing. AI writes the code. People write the guarantees.

You are driving to work again. This time you follow the GPS without arguing, down the side street it picks. It has seen this morning's traffic, and you haven't.

Notice what you still did. You typed the destination. You glanced at the fuel gauge before you pulled out. When the screen told you to turn into a road with an orange barrier across it, you didn't turn. The GPS chose the route. You decided where the car had to end up and what it must not do on the way.

That is what this book has said about code, in eighteen chapters.

The hand that writes the code has changed. An AI writes it, and an AI reads it first. So the code is arranged for a reader with no memory: a name that says what a function writes, one change in one place, a reason next to an odd number, an error line with the values in it, a page that says where things live, a prompt that states the rule. By the standard most of us learned, some of that code looks messy. This book has called it dirty code, and every chapter names an experiment that can show where it works better and where it doesn't.

Deciding what must never break has not changed hands. Does free shipping start at the list total or at the amount the customer paid? May a gift card ever pay out more than it holds? Does a timeout mean "try again" or "look it up first"? None of these answers is in the code until someone decides it. An AI can't decide it, because each answer is a fact about your shop. A person decides, writes the answer down as a sentence, and turns the sentence into a check that can fail.

This book has called those checks guarantees. A guarantee is a small thing: one example with its answer, a test that someone watched fail, a line in a rules file. A person can read every one of them. That is no longer true of the code.

The advice in this book will go out of date. Models will change. Some chapters will matter less, and some habits will be needed that I can't see from here. Chapter 3 said that I expect code written for an AI reader to move further from clean code as time goes on. If that is right, "dirty code" will cover more in five years than it covers in this book. The way to find out is the one this book uses: build the code two ways, give both to a reader that has never seen them, and let a test that the reader can't see decide.

Here is the smallest version of all of it, for tomorrow morning. Before you hand over your next task, write one sentence that begins "This must never happen:" and one example with its answer. Give the AI both. When it says it's done, run the example yourself.

AI writes the code. People write the guarantees.
