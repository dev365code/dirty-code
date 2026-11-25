# Terms

Each word below is explained where it first comes up, in Part I or in the chapter it belongs to. The chapters from Part II on can be read in any order, so they don't explain these words again and use the meanings below.

- **AI, coding agent.** An AI that reads and edits the code in a repository and runs commands in it. In this book, "AI" means a coding agent.
- **Session.** One conversation with a coding agent, from start to finish. A **fresh session** starts with no memory of any earlier session.
- **Context window.** The amount of text an AI can see at once.
- **Prompt.** The text you send the AI.
- **Rules file.** An instruction file kept in the repository that the AI reads when it starts work, such as `CLAUDE.md` or `AGENTS.md`.
- **Hidden test.** A test the AI never sees, used to judge whether a run's result is right. A **visible test** is one in the repository, which the AI can read and run.
- **Tool call.** One use of a tool by the AI: reading a file, editing a file, searching, or running a shell command. Appendix A says how each tool's records were counted.
- **Turn.** One reply from the model.
- **Files opened.** The files of the repository that a session read. Searches don't count. Appendix A gives the exact rule.
- **Diff.** The lines a change added and removed, shown with a few unchanged lines around them.
- **CI.** The service that runs your checks on every push.
- **Hop.** One step from a call toward the code that runs, such as a call through a factory function, a lookup in a dictionary, or a method inherited from a parent class.
- **Index file.** A one-page file in the repository, here `INDEX.md`, that says where each part of the code lives.
- **Finish line.** The command, and the output it has to print, that say a piece of work is done.
- **Guarantee.** A sentence that says what must never happen, kept by a check that runs.
- **Revert.** Putting the old implementation back and running the test that just passed, to see whether the pass depended on the change.
- **Planting a wrong answer.** Making the code return a wrong value on purpose, to see whether the test notices.
- **The version for people and the version for AI.** The two versions of the code that an experiment compares. The version for people follows *Clean Code*'s habits. The version for AI changes the habit its chapter is about and keeps everything else the same. Some chapters compare three versions, and Chapter 16 changes all eight habits of Part II at once.
- **Change A and Change B.** Two ways an AI can make Chapter 14's failing test pass: Change A edits the test, and Change B edits the code.
