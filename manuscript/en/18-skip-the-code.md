# Chapter 18. Can we skip the code? We asked AI to write machine code directly

## Scene

When cars got automatic transmissions, drivers stopped shifting gears. The gearbox didn't go away. It stayed under the floor and did the same job, and a machine worked it in place of your left foot and your right hand.

Then came the electric car. Most electric cars have a single fixed gear. An electric motor pulls well from a standstill all the way to highway speed, so the job the gears did is gone, and the gears went with it.

From the driver's seat the two changes look the same: one less thing to do. Under the floor they are opposites. In the first, the layer is still there and somebody else operates it. In the second, the layer no longer exists.

AI writes your code now, and you have stopped reading it. Is code the gearbox in an automatic, or the gearbox in an electric car?

## Claim

> Even if an AI can write machine code directly, code stays and its human reader goes away, because the next session has to read what this session wrote and a guarantee needs a place to attach.

## Why: next month's session has to read what today's session wrote, and machine code gives it nothing to read by

Today the path from a wish to a running program has four steps. A person writes a prompt. An AI writes code. A compiler turns the code into machine code. The machine runs it.

This book has argued that the person no longer reads the code. So here is the argument taken to its end. Code is a format made for human readers. If no human reads it, the AI could write machine code directly, and the code and the compiler could both go. The path would be shorter, and people who make this argument expect it to be faster.

Take speed first. A program written in a compiled language such as C or Rust already runs as machine code. The compiler does its work once, when the program is built, and it isn't there when the program runs. Removing it doesn't make the program faster. The program gets faster only if the AI writes better machine code than the compiler does, and that is a narrower question. The Evidence section has one study of it.

The larger problem is the reader. An AI has no memory. The session that changes this program next month starts from what is in the repository. Part II listed what that session reads by: names it can search for, comments that give reasons, error lines with values, a page that says where things live, tests with names. All of those are in code. None of them is in machine code. If the repository holds only machine code, next month's session has to work out what the number in each register meant before it can change anything.

So code was never kept only for the human. Code is what one session leaves for the next.

The last problem is where guarantees go. A type on a parameter is a guarantee. So is a check the compiler makes on every build, and so is a test that calls a function by its name. Each of them is attached to something in the code. A compiler is a large set of guarantees that other people already wrote, and it gives the same verdict on the same input every time. An AI doesn't.

That is my answer before the experiment. Experiment E11, described in the Evidence section, can change it.

## Code: the same function in Python, in Rust, and in twelve bytes of machine code

Here is one function three times. It returns an item's share of what the customer paid, rounded down, as in Chapter 15. Amounts are integer cents.

```python
def refund_share(price, paid, list_total):
    """Cents to refund for one item: its share of what was paid, rounded down."""
    return price * paid // list_total
```

```rust
/// Cents to refund for one item: its share of what was paid, rounded down.
pub fn refund_share(price: u64, paid: u64, list_total: u64) -> u64 {
    price * paid / list_total
}
```

```asm
_refund_share:
    mul   x0, x0, x1
    udiv  x0, x0, x2
    ret
```

The third version is assembly for the arm64 chip in my Mac. Assembly is machine code written out in letters, one instruction per line. In the file that actually runs, these three lines are twelve bytes: `00 7c 01 9b 00 08 c2 9a c0 03 5f d6`. A C compiler given the same function produces the same three instructions.

Look at what each version says. The Python version names the three inputs and describes the result. The Rust version does that too, and it adds that each input is a whole number that can't be negative. In the assembly, the function's name survives as a label. `price`, `paid`, and `list_total` have become `x0`, `x1`, and `x2`, and the sentence about cents and rounding is gone.

All three return `2700` for a $30.00 keyboard on an order with a $50.00 list total that the customer paid $45.00 for. They part ways on input that should never arrive. I ran each one.

| Call | Python | Rust | arm64 assembly |
|---|---|---|---|
| `refund_share(3000, 4500, 5000)` | `2700` | `2700` | `2700` |
| The list total is `0` | Stops: `ZeroDivisionError` | Stops: `attempt to divide by zero` | Returns `0` |
| The price is the text `"3000"` | Stops: `TypeError` | Doesn't build: ``expected `u64`, found `&str` `` | Returns a number made from the text's memory address |

Python refuses when the bad call runs. Rust refuses one of the two before the program exists, because its compiler checks every call against the types. The assembly refuses nothing. On this chip, dividing by zero gives zero, so the shop refunds $0.00 and no error is raised. Nobody decided that. It is what the instruction does.

Nobody wrote Python's check or Rust's checks for this function. They came with the language. In the assembly, each one would have to be written by hand, in every function, by a writer that sometimes makes mistakes.

## Prompt: "write it in assembly," "write it in Rust," and the change request that comes a month later

Two prompts ask for the function.

```text
Write refund_share(price, paid, list_total) in arm64 assembly. It returns
price * paid / list_total, rounded down. Give me only the assembly.
```

```text
Write refund_share(price, paid, list_total) in Rust. It returns
price * paid / list_total, rounded down. Amounts are whole cents.
```

For three instructions, a session can get either one right. The difference shows a month later, when a fresh session gets this.

```text
refund_share must refuse a list total of 0 and tell the caller.
```

With the Rust source, the session searches for `refund_share` and finds it. It changes the result type so that the function can return either an amount or a refusal. Then it builds. I made that change and built it. A caller that still treats the result as a plain number stops the build: ``expected `u64`, found `Option<u64>` ``. The compiler lists the callers the session forgot, every time, and it isn't an AI.

With only the machine code, the session starts by working out which register holds the list total. Nothing says. It adds a check for zero and has to invent a way to tell the caller, because there is no type to carry a refusal. Then it has to find every caller, and those are bytes as well. If it misses one, nothing fails.

> **[Run record slot: E11]** For one task: the assembly a session wrote directly, the Rust it wrote, how many rounds each took to pass the tests, and what a fresh session did with the change request in each case. Date, tool, model.

## Evidence: one study in which AI made compiled programs faster, and what my three runs show

One study measured the narrow question about speed. In 2025, Wei and others built a benchmark of 8,072 assembly programs, 130 lines long on average, and asked whether language models can produce assembly that runs faster than what an optimizing compiler produces. The task was to take a program and return a faster one that behaves the same. Of the 23 models they tested, the strongest general-purpose one passed the tests on 51.5% of the programs, and its programs ran 1.43 times as fast on average as the output of `gcc -O3`. A model they trained for this one task passed on 95.0%, with an average speedup of 1.46 times. <!-- source: notes/sources.md, SuperCoder, arXiv:2505.11480, abstract of version 4, checked 2026-11-13 -->

Three things about that result matter here. The speed is real: on small programs, an AI found machine code that a compiler didn't. The correctness is judged by tests, and even the trained model failed them on one program in twenty. And the yardstick was a compiler's output, which exists only because there was source code to compile. The study shows an AI improving on compiled code. It doesn't show an AI doing without the code.

My own runs are the table above. <!-- run 2026-11-13: Python 3.9.6; rustc 1.99.1 on the Rust Playground; Apple clang 21 on arm64 --> They show where the checks are in each version of one small function. They don't show what an AI does when it is asked for machine code.

Experiment E11 will ask. It has two halves. In the first, fresh sessions write the same 10 to 20 small tasks three ways: in Python, in Rust, and directly in assembly. Hidden tests judge each result. E11 counts the tasks that pass, the rounds of fixing each took, and how fast the result runs. The Rust version, compiled with optimization, is the baseline, which separates what the choice of language gains from what skipping the compiler gains. In the second half, a fresh session gets a change request for each finished task. One group gets the Rust source. The other gets only the assembly. E11 counts how many changes pass.

If sessions change the assembly as reliably as they change the Rust, the claim at the top of this chapter is wrong, and I will rewrite it.

> **[Result slot: experiment E11]** Date, tool and model. For each of the three ways: tasks passed, rounds of fixing, and running time against compiled Rust. For the change requests: passes with the source, and passes with the assembly alone.

## What people do

- [ ] If your team avoided a strict, compiled language because it was slow for people to write, ask whether that reason still holds now that an AI does the writing. Try it on one new service.
- [ ] When you choose a language for code an AI will write, list what its compiler checks on every build: types, missing cases, values that may be absent. Each item on the list is a guarantee you don't have to write or remember.
- [ ] Before you ask for hand-tuned low-level code, measure where the time goes. Tune only that spot, and keep the plain version next to it with a test that runs both on the same inputs and compares the results.
- [ ] Keep the source in the repository as the record. Machine code is something the build produces. The next session should read the source.

## Where it breaks

The layer can disappear when the machine under it changes, as it did in the electric car. Suppose an AI could write machine code together with a proof that the code does what a short statement says, and a small, trusted program could check the proof. Then the guarantee would have somewhere else to attach, and the argument about guarantees would weaken. The argument about the next reader would remain, unless the statement and the proof became what the next session reads. They would then be the code.

The next-reader argument depends on sessions having no memory. If a system comes to remember reliably everything it has built, it will need less from the repository, and this argument will have to be made again.

A compiler checks only what it is set to check. Built in release mode, the Rust version above doesn't check the multiplication for overflow. `refund_share(2^63, 4, 2)` returns `0`, the same wrong answer the assembly gives, and a debug build stops instead with `attempt to multiply with overflow`. A guarantee is only there if someone turned it on.

"Code stays" doesn't mean that today's languages stay. They were designed for people to write and read. A language chosen because a machine can check it and the next session can find its way in it may be one that people find tedious. Chapter 3 said that code arranged for an AI reader already differs from clean code in places, and that I expect the differences to grow. The same may happen to languages, and this book's title covers that too.
