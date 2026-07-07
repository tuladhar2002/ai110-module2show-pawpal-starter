# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
=> A user should be able to add a pet, schedule task/chore, gain points by completing tasks, use points to level up a pet or add a new one.

- What classes did you include, and what responsibilities did you assign to each?
=> Started with four classes: User (owns pets, earns points), Pet (holds info), Task (describes what needs doing), and PetStore (lets users spend points). Each had a clear single job.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
=> Yes. The biggest change was adding a `Scheduler` class. Originally the User handled scheduling directly, but as sorting, filtering, and conflict detection grew, it made sense to move all of that logic into its own class. `User` was also renamed `Owner` to better match the domain. `PetStore` was dropped since points and leveling were enough for the scope.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

=> The scheduler considers priority (high/medium/low), scheduled time (HH:MM), duration, frequency (daily/weekly/once), and whether a task is already complete. Priority came first because a pet owner should always handle urgent care before optional tasks, regardless of when they're scheduled.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Tradeoff: conflict detection compares overlapping duration windows, not just exact start times.**

The scheduler flags two tasks as conflicting when their time windows overlap (`start_a < end_b and start_b < end_a`). This is more accurate than matching start times exactly, but it means tasks without a `due_date` are assumed to be on the same day — which can produce false conflicts between today's task and tomorrow's auto-spawned copy. This is acceptable because `due_date` is set automatically for all recurring tasks; only manually created tasks without a date are affected, which is an uncommon case.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

=> AI was used throughout — drafting class methods, refactoring duplicate logic (like extracting `_windows_overlap`), writing tests, and filling out documentation. The most helpful prompts were specific ones: asking for a "lightweight conflict detection strategy that returns warnings instead of crashing" got a focused answer, whereas broad prompts like "improve my code" were less useful.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

=> When the conflict detection was first implemented, the AI-generated output included false positives — completed tasks and their auto-spawned clones were flagging conflicts against each other. I caught this by reading the output from `main.py` and noticed tasks on different days were being compared. I pushed back and the fix (filtering to pending-only tasks and adding a `due_date` guard) was added. Running the test suite confirmed the fix held.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

=> Tested three core areas across 13 tests: sorting (chronological order and priority ranking), recurrence (daily/weekly spawning, once-task guard, double-complete guard), and conflict detection (same-pet overlap, cross-pet overlap, back-to-back boundary, empty pet). These matter because they're the behaviors a pet owner relies on every day — a wrong sort or missed conflict directly affects the animal's care.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

=> 4/5. All 13 tests pass and the key edge cases are covered. The remaining gap is the Streamlit UI (no automated tests), and a missing test for `spend_points` with an insufficient balance. Next I'd add tests for an owner with zero pets and for tasks intentionally created without a `due_date`.

---

## 5. AI Strategy

**Which AI coding assistant features were most effective?**

=> The most effective features were inline code generation for boilerplate (dataclass fields, method stubs) and the back-and-forth refactoring loop. Being able to say "extract the duplicate interval logic into a helper" and immediately see `_windows_overlap` appear saved significant time. The explanation feature was also useful — asking "why does `start_a < end_b and start_b < end_a` detect overlaps" before accepting the logic helped me understand it rather than just copy it.

**One AI suggestion you rejected or modified:**

=> The first version of the conflict detection included completed tasks in the pair loop and produced false positives — clones spawned for tomorrow were flagging against today's completed originals. The AI's initial fix was to filter only by `due_date` difference, but that didn't cover tasks with no `due_date` at all. I pushed back and combined two guards: filter to pending-only first, then add the `due_date` mismatch check. The AI suggested one or the other; I insisted on both.

**How did using separate sessions for different phases help?**

=> Each session had a clear scope — one for core class design, one for conflict detection, one for tests, one for the UI. That meant the AI's suggestions stayed relevant to the current problem instead of being influenced by stale context from earlier work. It also forced me to re-explain the system each time, which caught moments where my mental model had drifted from the actual code.

**What you learned about being the "lead architect":**

=> The AI is fast but not careful. It will implement whatever you ask without flagging that it contradicts a decision you made two sessions ago, or that the edge case you described verbally isn't handled by the code it wrote. The job of the architect is to hold the full picture — knowing which constraints are load-bearing, which simplifications are acceptable tradeoffs, and when to push back. AI handles the typing; you handle the thinking.

---

## 6. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

=> The conflict detection system. Starting from a simple same-pet overlap check and evolving it into same-pet + cross-pet detection with a clean warning output felt like a real design improvement. The `_windows_overlap` refactor that eliminated duplicate arithmetic was a satisfying simplification.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

=> Make `due_date` required on every task from the start. It was added partway through and caused false-positive conflicts that needed a workaround. A required date field from day one would have made the conflict logic cleaner and more predictable.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

=> Start with the data model, not the methods. Most of the refactoring — moving tasks from `Owner` to `Pet`, adding `due_date`, splitting `Scheduler` out — happened because the initial data model didn't reflect how the domain actually works. Getting that right first would have made everything downstream easier.
