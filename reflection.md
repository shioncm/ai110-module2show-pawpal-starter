# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

Three core actions a user should be able to perform include: adding a pet, adding a task, and viewing today's tasks. 

- What classes did you include, and what responsibilities did you assign to each?

The four main objects, or classes, may include: `Pet` (attributes: pet type, name; methods: add, delete, get_tasks), `Owner` (attributes: name; methods: change_name, add_pet, remove_pet), `Task` (attributes: category, priority, duration, date_time, status; methods: add, delete, edit), `Scheduler` (attributes: tasks, available_time, pet, date; methods: generate_plan, view_today, get_summary)

[Initial UML Mermaid.js class diagram](https://mermaid.live/edit#pako:eNqVU01v2zAM_SsCT_tIA7t248SHXdbjgA1oT4MBg7NYW6glGZKczAvy3yc5aWcn6bDpJD5Rj--R0h4qzQlyqFq09l5gbVAWivk1IuzrTpFh-yMU1scHZ4SqmUJJExQ5Lzty795PMENSb-kCrhpUNZWB4AU_FGpa9Bu5ayU9UemGjv5FzKwip5YczaA6cKF9tm9IePRn1zRU6KjWZriizghthJueCOUY7w06odUEvvccj0IS435TOiGvOLIOXW__zxNx4d6w81A1xPv2bJRfhHVs7MKZaNyiaPFHe6EuTMaP4czMaGTWXP9ogreuRTWTuBW0K53mOFxMw_ZSohkuDBxfYAFxAezm5lPYLZcffBC05Ezv1El9iKdp0TFtnGTOGjyl_WnFjPOV0J7OLXvS5m9X5vwSFdbka8ACaiM45M70tABJRmIIYex8Aa4h31LI_ZajeS6gUAd_p0P1XWv5cs3ovm4gf8LW-qjvQodP3_MVNaQ4mc-6Vw7y1e3IAfkefkIex6vlOks36zRL49s42qQLGHxSttxkd3erJEo3SbxKDwv4NRaNxmy_1kkSZeskTQ-_AeNfLSA)

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design did slightly change during implementation. The initial UML design designated the `Task` class' `priority` attribute type as a stirng. However, I changed the data type of the `priorty` attribute to be an `int`, as it is cleaner and more explicit. I also changed the skeleton of my classes in `pawpal_system.py` according to the AI agent's feedback. One relevant feedback from the AI agent was adding a `Pet` parameter to the Owner object's `add_pet` and `remove_pet` methods. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler considers constraints such as scheduled time, duration, priority, and completion status of tasks. Recurring tasks also carry a frequency and a due date.

- How did you decide which constraints mattered most?

Scheduled time and duration of tasks were prioritized most. Without both, the scheduler cannot detect conflicting tasks. Task priority was added after the core logic was stable since they do not have a large effect on the scheduling logic itself.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

One tradeoff the scheduler makes is collecting all scheduled pending tasks into a list, and comparing every pair. This is a simple and correct solution, especially for a smaller number of tasks, but for a greater number of tasks (e.g. 1000 tasks) the runtime will be longer.

- Why is that tradeoff reasonable for this scenario?

The tradeoff is reasonable for this scenario because a real pet owner usually has no more than 20 tasks per day across all pets. At this small scale, this simpler implemented approach is faster and signaficantly easier to read.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI to implement class logic from UML skeletons, extend methods with new features, write the pytest suite, and review the code for flaws or improvements to be made.

- What kinds of prompts or questions were most helpful?

Code review prompts were most helpful. Having the AI tool look over the code and find flaws or suggest improvements quickly helped speed up the development immensely.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

One moment I did not accept an AI suggestion was when I was connecting the UI to the program logic. Many newly added features were not being reflected in the UI, and the AI prompts needed refinement.

- How did you evaluate or verify what the AI suggested?

Running the test suite helped verify AI suggestions. By immediatly generating tests and verifying them for every new implementation, I was able to guarantee that the program runs correctly for each new feature.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

Behavior I tested include task sort order, filtering by completion status and pet name, daily and weekly task recurrence, and task conflict detection.

- Why were these tests important?

These tests were important because they are essential to the schedule generation and overall function of the program. Many features have an edge case, and it is important to detect them beforehand.

**b. Confidence**

- How confident are you that your scheduler works correctly?

I have high confidence for the core logic. All tests pass and there are many edge-cases covered. However, I have lower confidence for the integration with the UI, which has no automated tests and was only verified manually.

- What edge cases would you test next if you had more time?

If I had more time, an edge case I would test next is two pets with the same name under different owners.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am satisfied with the overall core logic implementation. In particular, the conflict detection and recurrence features work well together. All features necessary are implemented sufficiently.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would improve the UI integration, and overall UI experience for the user. The current UI is still clunky and unpolished.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned about designing systems is the importance of having an overall structure layed out. In particular, having a draft UML diagram was immensely helpful in implementing the core logic. AI tools were also helpful in this process of drafting the UML diagrams.
