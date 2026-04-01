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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

One tradeoff the scheduler makes is collecting all scheduled pending tasks into a list, and comparing every pair. This is a simple and correct solution, especially for a smaller number of tasks, but for a greater number of tasks (e.g. 1000 tasks) the runtime will be longer.

- Why is that tradeoff reasonable for this scenario?

The tradeoff is reasonable for this scenario because a real pet owner usually has no more than 20 tasks per day across all pets. At this small scale, this simpler implemented approach is faster and signaficantly easier to read.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
