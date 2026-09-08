# Pilot tasks and draft reference review

AI Answer Quality Audit: Annotation, Feedback and Correction  
Prepared for Dominic Da Silva · Version 0.1 · Prepared 8 September 2026

These eight tasks and references are **AI-prepared drafts awaiting Dominic’s verification**. They are not completed annotations or validated answer keys. No candidate responses or suggested candidate ratings appear here. The passages and company policies are original and fictional.

Review each full task prompt first, then check its expected answer, evidence and acceptable alternatives. Correct mistakes or unclear requirements before collecting candidate responses. If a task changes, update its task version and corresponding reference, and use the final prompt for both independent generations. Material post-generation changes may require regenerating both responses with preserved provenance.

The JSON in `02_tasks/pilot_tasks.json` contains candidate-facing tasks only. When collecting answers in a fresh chat, copy only a task’s `prompt` value. Do not share this review document, reference JSON, scoring guidelines or earlier candidate replies with the model generating responses.

Human verification below is intentionally blank. The recorded status remains `pending_dominic` until Dominic actually reviews and confirms it. Human verification of a draft reference is separate from scoring candidate answers, which Dominic must also do himself.

Record `verified`, `revise`, or `needs_clarification` in the verification CSV. If you suggest corrections, save and recheck the revised key before marking it verified. These are reference-review decisions, not candidate ratings.


---

## MP01 — Average speed with a stop

Category: `mathematics_physics` · Task v0.1 · Reference v0.1 · Status: `pending_dominic`

### Full candidate-facing prompt

A park ranger drives an electric cart 600 metres at a constant speed of 4.0 m/s, stops for 90 seconds, and then drives another 900 metres at a constant speed of 6.0 m/s. Ignore acceleration and braking time.

Calculate the average speed for the entire journey, including the stop, in m/s and km/h. Show your working and round both final speeds to two decimal places.

### Draft expected answer — verify before use

The first leg takes 600 ÷ 4.0 = 150 seconds. The second takes 900 ÷ 6.0 = 150 seconds. Total distance = 600 + 900 = 1,500 metres. Total elapsed time = 150 + 90 + 150 = 390 seconds. Average speed = 1,500 ÷ 390 = 3.846153… m/s, or 3.85 m/s to two decimal places. Converting the unrounded value: (1,500 ÷ 390) × 3.6 = 13.846153… km/h, or 13.85 km/h.

### Draft expected-answer checklist

- Calculate each moving leg as 150 seconds and include the 90-second stop, giving 390 seconds in total.
- Use total distance divided by total elapsed time: 1,500 metres ÷ 390 seconds.
- Report 3.85 m/s and 13.85 km/h, each rounded to two decimal places, with units.
- Show the time and distance calculation and the unit conversion, or equivalent working.
- Use unrounded intermediate values; multiplying the rounded 3.85 m/s by 3.6 can incorrectly produce 13.86 km/h.

### Supporting evidence and calculations

- Prompt quantities: first leg 600 m at 4.0 m/s; stop 90 s; second leg 900 m at 6.0 m/s.
- Definition used: average speed = total distance / total elapsed time.
- Unit conversion: 1 m/s × (3,600 s/hour) ÷ (1,000 m/km) = 3.6 km/h.
- Exact arithmetic check: 1,500/390 = 50/13 m/s; (50/13) × (18/5) = 180/13 km/h.

### Ambiguity and acceptable alternatives

No intended ambiguity. The prompt expressly includes the stop and excludes acceleration/braking time. The two rounded final values should each be derived from unrounded working.

### Dominic’s verification — leave blank until reviewed

| Human review field | Dominic’s entry |
|---|---|
| Reference decision | |
| Corrections to prompt/reference, if any | |
| Additional acceptable alternatives | |
| Remaining uncertainty or clarification needed | |
| Verified by | |
| Actual verification date | |


---

## MP02 — What does less effort mean on a ramp?

Category: `mathematics_physics` · Task v0.1 · Reference v0.1 · Status: `pending_dominic`

### Full candidate-facing prompt

A workshop needs to move the same loaded trolley from the floor to a platform 1 metre higher. It can use a straight ramp 2 metres long or a straight ramp 4 metres long. On either ramp, a worker pushes parallel to the slope and moves the trolley at the same constant speed. Assume friction and rolling resistance are negligible, and ignore starting and stopping.

A colleague says, “The longer ramp takes less effort, so the worker transfers less energy to the trolley.” Explain whether this statement is right and what “effort” could mean here. Use simple physics, state any qualification that matters, and keep your answer under 150 words.

### Draft expected answer — verify before use

“Effort” is ambiguous. If it means pushing force, the longer ramp requires half as much: at constant speed the force along the slope balances the downhill component of weight, F = mgh/L. Both ramps raise the same trolley through the same height, so the work transferred by the worker is the same, mgh. The longer ramp halves the force but doubles the distance. At the same speed it also takes twice as long. The claim of less transferred energy is therefore incorrect under the stated ideal assumptions. Human tiredness or energy used by the worker’s body cannot be determined from this simple mechanical model.

### Draft expected-answer checklist

- Distinguish at least pushing force from mechanical work/energy when interpreting “effort”.
- Explain that the 4-metre ramp needs a smaller pushing force; an exact comparison, if given, is half the force for the 2-metre ramp.
- Explain that both cases require the same mechanical work/energy transfer, because mass and vertical height are unchanged and resistance is neglected.
- Connect smaller force with the longer distance, or use an equivalent gravitational-potential-energy explanation.
- Avoid concluding that actual fatigue, metabolic energy expenditure or every possible meaning of “effort” must be lower.
- Keep the response under 150 words. The draft is an example, not a required wording.

### Supporting evidence and calculations

- Prompt: the same loaded trolley and a 1-metre vertical rise on both ramps; ramp lengths 2 and 4 metres.
- Geometry: sin(theta) = h/L. At constant speed and with negligible resistance, F = mg sin(theta) = mgh/L.
- Force comparison: F_long/F_short = (mgh/4)/(mgh/2) = 1/2.
- Work: W = FL = mgh for either ramp; kinetic energy does not change during the specified constant-speed motion.
- No specialist external facts are needed; the reference uses elementary force balance, work and gravitational potential energy. Dominic must verify this derivation.

### Ambiguity and acceptable alternatives

Deliberate ambiguity: “effort” can mean required force, energy transfer, perceived difficulty or fatigue. Accept a clear distinction expressed in plain language; equations, numerical mass and a numerical value of g are unnecessary. A response may also note lower mechanical power at the same speed, but that is optional. The body’s energy use is outside the supplied ideal model.

### Dominic’s verification — leave blank until reviewed

| Human review field | Dominic’s entry |
|---|---|
| Reference decision | |
| Corrections to prompt/reference, if any | |
| Additional acceptable alternatives | |
| Remaining uncertainty or clarification needed | |
| Verified by | |
| Actual verification date | |


---

## CS01 — A lamp return without its original carton

Category: `customer_support` · Task v0.1 · Reference v0.1 · Status: `pending_dominic`

### Full candidate-facing prompt

Use only this fictional Lark Desk Co policy:

[P1] Customers may request a change-of-mind return within 30 calendar days after delivery. The item must be unused and undamaged.
[P2] Before sending an item back, the customer must email support with the order number and a photo showing the item's current condition. Support then supplies a return authorisation and return address.
[P3] The original carton is preferred but not required. The customer must pack the item securely.
[P4] The customer pays return postage. The original standard delivery charge is not refunded for a change-of-mind return.
[P5] After the returned item has been received and inspected, the eligible item price is refunded to the original payment method within five business days.

Customer message: “My lamp arrived 18 days ago. It is unused and undamaged, but I threw away the carton. I paid £36 for the lamp and £4 for standard delivery. Can I return it and get all £40 back? Where should I send it?”

Draft a helpful customer-facing reply of no more than 130 words. You have no access to the customer's order or any address beyond the policy above.

### Draft expected answer — verify before use

You can request a return: the lamp is within the 30-day window and you say it is unused and undamaged. The original carton is not required, but please pack it securely. The eligible refund is £36 for the lamp; the £4 standard delivery charge is not refundable, and you pay return postage. Before sending it, email support with your order number and a photo showing its condition. Support will provide the return authorisation and address. After receipt and inspection, the eligible refund goes to your original payment method within five business days.

### Draft expected-answer checklist

- Explain that the described item is eligible for a return request within 30 days, subject to the stated item condition and subsequent inspection.
- Explain that discarding the original carton does not prevent the return; secure packaging is required.
- Identify £36 as the eligible item refund, excluding the original £4 standard delivery charge; the customer pays return postage.
- Request the order number and a condition photo by email to support, and explain that support supplies authorisation and the return address before shipping.
- Explain that the refund is to the original payment method within five business days after receipt and inspection.
- Use a helpful customer-facing reply within 130 words; do not invent an address, confirm an action already taken, or promise immediate/unconditional repayment.

### Supporting evidence and calculations

- [P1] supports the 30-calendar-day request window and unused/undamaged conditions; the customer reports delivery 18 days ago.
- [P2] supplies the order-number/photo requirement and the sequence for obtaining authorisation and the address.
- [P3] says the original carton is preferred but not required and requires secure packaging.
- [P4] makes return postage the customer’s responsibility and excludes the original standard delivery charge from a change-of-mind refund.
- [P5] supplies the refund method, inspection condition and five-business-day timescale.
- Customer’s item price = £36 and standard delivery = £4; only the £36 item price is eligible. The return-postage price is unspecified and must not be invented.

### Ambiguity and acceptable alternatives

No intended policy ambiguity. The customer’s condition statement supports a return request; the response should not imply inspection has occurred. “£36 refund” and “eligible refund of £36 after inspection” are both compatible if the rest of the reply preserves the condition and process.

### Dominic’s verification — leave blank until reviewed

| Human review field | Dominic’s entry |
|---|---|
| Reference decision | |
| Corrections to prompt/reference, if any | |
| Additional acceptable alternatives | |
| Remaining uncertainty or clarification needed | |
| Verified by | |
| Actual verification date | |


---

## CS02 — A pickup change when Sunday hours are missing

Category: `customer_support` · Task v0.1 · Reference v0.1 · Status: `pending_dominic`

### Full candidate-facing prompt

Use only this fictional Harbour Tool Hire policy:

[P1] The published depot collection hours are Monday–Friday 09:00–18:00 and Saturday 09:00–13:00. This extract does not list Sunday hours.
[P2] A request to change a collection date must be received before 16:00 on the day before the original collection date. Any change is subject to depot opening hours and equipment availability; submitting a request does not confirm a change.
[P3] A cancellation request received before 16:00 on the day before the original collection date incurs no charge. Later cancellation requests incur a fee equal to one day's hire. The time the request is received determines the fee, even if staff process it later.
[P4] Support must check opening hours and equipment availability before confirming a date change.

It is Thursday at 15:30. Customer message: “I am booked to collect a drill tomorrow, Friday. Please move my pickup to Sunday. If Sunday collection is unavailable, please cancel the booking instead. Would there be a cancellation fee?” Assume this message is received immediately.

Draft a customer-facing reply of no more than 150 words. You have only the policy extract, with no access to opening-hours checks, availability checks or booking actions.

### Draft expected answer — verify before use

Your request arrived at 15:30 on Thursday, before the 16:00 deadline for Friday’s booking. A move to Sunday still needs confirmation of the depot’s Sunday hours and drill availability; this extract does not confirm whether Sunday collection is possible. If Sunday collection is unavailable, your cancellation request qualifies for no charge because it was received before the deadline, even if processed later. The next step is for support to check Sunday collection and then confirm the change or cancellation. I cannot confirm a booking change or cancellation from the policy alone.

### Draft expected-answer checklist

- Recognise that Thursday 15:30 is before the Thursday 16:00 cutoff for the original Friday collection.
- Explain that an on-time change request does not confirm Sunday pickup; opening hours and equipment availability still need checking.
- Treat Sunday availability as unknown: the extract does not establish that the depot is either open or closed on Sunday.
- Answer the fee question: if the requested fallback cancellation is needed, the received-before-deadline request incurs no charge, even if processed later.
- Identify a practical next step of support checking Sunday hours/availability and confirming the resulting action.
- Keep the reply customer-facing and within 150 words; do not claim checks or booking actions have already been performed.

### Supporting evidence and calculations

- [P1] lists weekday/Saturday hours but explicitly omits Sunday hours.
- [P2] sets the change-request cutoff relative to the original booking and makes changes dependent on opening hours and availability.
- [P3] bases cancellation fees on receipt time, not processing time. The customer’s conditional cancellation request is received with the message at Thursday 15:30.
- [P4] requires checks before confirmation.
- Timeline: original booking Friday; day before is Thursday; message receipt 15:30 is 30 minutes before 16:00.

### Ambiguity and acceptable alternatives

Deliberate missing information: Sunday hours and stock availability are unknown. The conditional cancellation request is expressly included in the message, and [P3] makes its receipt time determinative; no later-processing fee should be invented. Dominic should verify this interpretation before candidate collection. Do not add policy exceptions or act as if an unperformed check is complete.

### Dominic’s verification — leave blank until reviewed

| Human review field | Dominic’s entry |
|---|---|
| Reference decision | |
| Corrections to prompt/reference, if any | |
| Additional acceptable alternatives | |
| Remaining uncertainty or clarification needed | |
| Verified by | |
| Actual verification date | |


---

## RC01 — What a small workshop trial establishes

Category: `reading_comprehension` · Task v0.1 · Reference v0.1 · Status: `pending_dominic`

### Full candidate-facing prompt

Read this original passage:

[S1] Riverside Community Library ran a six-week trial of a free Tuesday workshop starting at 17:00.
[S2] Twenty-four people registered, and eighteen attended at least once.
[S3] After the trial, twelve participants returned a survey: ten called the workshop useful, and eight said they would prefer a later start.
[S4] The survey did not ask why people missed sessions, and the library did not contact people who registered but never attended.
[S5] For the next six-week block, the library kept the 17:00 start because its caretaker was unavailable later in the evening.
[S6] Staff planned to record attendance and keep a waiting list during the next block before considering further changes.

Summarise the trial and the next steps in no more than 70 words. Then, in a separate sentence, state whether the passage establishes that starting later would increase attendance, and briefly explain why.

### Draft expected answer — verify before use

Example summary: Riverside’s six-week Tuesday workshop had 24 registrations and 18 people attend at least once. Of 12 survey respondents, ten found it useful and eight preferred a later start. The next block will remain at 17:00 because the caretaker is unavailable later, while staff track attendance and keep a waiting list before considering changes.

Separate conclusion: No—the survey records a preference among respondents, but it does not establish why people missed sessions or whether a later start would increase attendance.

### Draft expected-answer checklist

- Summarise the workshop trial and planned next block without changing the meaning of attendance or survey counts.
- If survey numbers are used, keep their denominator clear: 12 survey respondents, not all 24 registrants or all 18 attendees.
- State that the next block retains the 17:00 start because of caretaker availability.
- Include planned attendance recording and a waiting list before further changes.
- In a separate sentence, explain that the passage does not establish a later start would increase attendance; preference does not demonstrate attendance impact.
- Use no more than 70 words for the summary. The separate conclusion is additional to that summary limit.
- Do not describe planned monitoring or the next block as already completed. Exact example wording and every numerical detail are unnecessary if the summary remains faithful.

### Supporting evidence and calculations

- [S1] establishes the trial’s duration, day, start time and free status.
- [S2] distinguishes 24 registrations from 18 people attending at least once; it does not give attendance per session.
- [S3] gives the 12-response survey denominator, ten usefulness responses and eight later-start preferences.
- [S4] says reasons for missed sessions were not asked and never-attending registrants were not contacted.
- [S5] explains retaining the start time for the next block through caretaker availability.
- [S6] describes planned monitoring and a waiting list, not observed future results.

### Ambiguity and acceptable alternatives

The passage supports a limited preference statement and makes the causal attendance claim unresolved. A later start could help, have no effect or have other effects; the text does not choose among these. A sound concise summary may omit less central details such as “free” or some counts. Do not require all passage facts within 70 words.

### Dominic’s verification — leave blank until reviewed

| Human review field | Dominic’s entry |
|---|---|
| Reference decision | |
| Corrections to prompt/reference, if any | |
| Additional acceptable alternatives | |
| Remaining uncertainty or clarification needed | |
| Verified by | |
| Actual verification date | |


---

## RC02 — Actions, inference and an unresolved visit

Category: `reading_comprehension` · Task v0.1 · Reference v0.1 · Status: `pending_dominic`

### Full candidate-facing prompt

Read this original passage:

[S1] At 17:40, Anika switched off the main lights in the community reading room but left the lamp beside the entrance on.
[S2] She turned two chairs towards the door and put two clean mugs on the counter.
[S3] Outside, rain blurred the street, and the pavement was empty.
[S4] Tom reached for his coat and asked, “Are you coming?”
[S5] “I said I would be here until six,” Anika replied.
[S6] After Tom left, she checked the street twice and placed a note on the door: “Please ring the bell.”
[S7] At 17:55, she picked up a book, but turned only one page before looking outside again.

Answer in three numbered points, using no more than 120 words in total:
1. Give two actions Anika explicitly takes in the passage.
2. Offer one reasonable inference about her situation, supported by two details from the passage.
3. Identify one thing the passage leaves unresolved.

### Draft expected answer — verify before use

1. Anika leaves the entrance lamp on and places a “Please ring the bell” note on the door.
2. She may be waiting for a visitor: she prepares two clean mugs and repeatedly checks the street. This is an inference, not a confirmed explanation.
3. The passage does not establish whether anybody arrives.

### Draft expected-answer checklist

- Give two actual actions from the passage as explicit facts, rather than turning a possible motive into a fact.
- Offer one reasonable inference, clearly marked as uncertain or interpretive, and support it with two distinct relevant textual details.
- Identify one genuinely unresolved matter, such as whom she may expect, the purpose of a visit, whether anyone arrives or why she promised to remain.
- Use three numbered points and no more than 120 words in total.
- Accept alternative inferences that fit the passage and are supported by two details; do not require the example’s precise interpretation or wording.
- Do not assert a specific relationship, occupation, emotion or eventual outcome as established unless the passage actually supplies it.

### Supporting evidence and calculations

- [S1] explicitly describes switching off main lights and leaving the entrance lamp on.
- [S2] explicitly describes turning chairs and putting out two mugs; this supports preparation for possible company but does not prove who will come.
- [S5] explicitly records a commitment to be there until six; it does not identify the reason.
- [S6] explicitly describes repeated street checks and the bell note.
- [S7] supports possible distraction or anticipation through limited reading and looking outside again; no emotion is directly named.
- The passage ends at 17:55 without establishing an arrival or explaining the possible visitor’s identity.

### Ambiguity and acceptable alternatives

Deliberately open interpretation: waiting for someone, anticipating a visitor or being distracted by an expected arrival can be reasonable if qualified and supported. Mild emotional inferences, such as concern or anticipation, may also be defensible with evidence; they are not explicit facts. Mere alternative wording should not be treated as disagreement with the reference.

### Dominic’s verification — leave blank until reviewed

| Human review field | Dominic’s entry |
|---|---|
| Reference decision | |
| Corrections to prompt/reference, if any | |
| Additional acceptable alternatives | |
| Remaining uncertainty or clarification needed | |
| Verified by | |
| Actual verification date | |


---

## PR01 — A morning recording schedule

Category: `practical_reasoning` · Task v0.1 · Reference v0.1 · Status: `pending_dominic`

### Full candidate-facing prompt

Plan one person's work between 09:00 and 11:00 using these constraints:

[C1] Complete an equipment check lasting 20 minutes before starting the recording.
[C2] Attend a client call from exactly 09:30 to 09:40.
[C3] Make a recording lasting 30 minutes. The recording room is available only from 10:00 to 10:40, so the whole recording must fit within that window.
[C4] Write notes for 15 minutes after the recording has finished.
[C5] Take one continuous 10-minute break that starts no earlier than 09:50 and finishes no later than 10:20.
[C6] Do not overlap or split activities. All five activities must finish by 11:00. An activity may begin immediately when another ends.

Give a valid schedule with start and end times for all five activities in chronological order. Leave spare time unassigned and do not add activities.

### Draft expected answer — verify before use

One valid schedule is:
09:00–09:20 — Equipment check.
09:30–09:40 — Client call.
09:50–10:00 — Break.
10:00–10:30 — Recording.
10:30–10:45 — Write notes.
Spare intervals are deliberately left unassigned. Other schedules satisfying every stated constraint are also valid.

### Draft expected-answer checklist

- Schedule all five named activities once, in chronological order, with both start and end times.
- Allocate a continuous 20-minute equipment check that finishes before or at the recording start.
- Keep the client call exactly at 09:30–09:40.
- Allocate a continuous 30-minute recording entirely within 10:00–10:40.
- Allocate 15 continuous minutes of note writing after or immediately at the recording end.
- Allocate a continuous 10-minute break with start at or after 09:50 and end at or before 10:20.
- Keep every activity inside 09:00–11:00, with no overlaps, splits or extra activities; leave spare time unassigned.
- Check the submitted schedule against the constraints rather than requiring the example’s exact timing.

### Supporting evidence and calculations

- [C1] gives the equipment-check duration and its dependency on recording.
- [C2] fixes the client call time.
- [C3] gives the recording duration and room-availability window.
- [C4] gives note duration and requires it after the recording.
- [C5] gives break duration and allowable window.
- [C6] prohibits overlaps/splits and explicitly allows adjacent activities.
- Example duration check in minutes: equipment 20; call 10; break 10; recording 30; notes 15; total assigned = 85 of the 120 available minutes.

### Ambiguity and acceptable alternatives

Multiple valid schedules are intended, with no requirement to minimise finish time or idle time. “Before” and “after” permit exact boundary adjacency because [C6] expressly allows one activity to start when another ends. The example is only one witness that the constraints can be met.

### Dominic’s verification — leave blank until reviewed

| Human review field | Dominic’s entry |
|---|---|
| Reference decision | |
| Corrections to prompt/reference, if any | |
| Additional acceptable alternatives | |
| Remaining uncertainty or clarification needed | |
| Verified by | |
| Actual verification date | |


---

## PR02 — Choosing a room when best is undefined

Category: `practical_reasoning` · Task v0.1 · Reference v0.1 · Status: `pending_dominic`

### Full candidate-facing prompt

You are helping choose a meeting room. The booking must last two continuous hours between 14:00 and 17:00, seat at least ten people, have step-free access and Wi-Fi, and cost no more than £80 in total. All available options are listed below; the prices are the total price for the stated slot.

[R1] Alder: 14:00–16:00; capacity 12; step-free access; Wi-Fi; £70.
[R2] Birch: 15:00–17:00; capacity 10; step-free access; Wi-Fi; £60.
[R3] Cedar: 14:00–16:00; capacity 8; step-free access; Wi-Fi; £50.
[R4] Maple: 15:00–17:00; capacity 14; step-free access; Wi-Fi; £90.

The organiser's final instruction is, “Book the best one.” No preference has been given between an earlier meeting and a lower price.

Which rooms meet all the requirements, and what next step would you recommend before booking? Respond in no more than 120 words. Do not claim to have made a booking.

### Draft expected answer — verify before use

Alder and Birch meet every requirement. Cedar is too small for ten people, and Maple exceeds the £80 budget. Before booking, ask whether the organiser prefers the earlier 14:00 start or saving £10 with Birch’s 15:00 start. “Best” is not defined by the supplied requirements. If lowest price is the priority, recommend Birch; if an earlier meeting is preferred, Alder is the option. No booking has been made.

### Draft expected-answer checklist

- Identify both Alder and Birch as satisfying the duration, time window, capacity, access, Wi-Fi and budget requirements.
- Do not treat Cedar as eligible: capacity 8 is below the required 10.
- Do not treat Maple as eligible: £90 is above the £80 total limit.
- Recognise that “best” does not uniquely select between qualifying rooms without a preference or an explicitly stated assumption.
- Recommend clarifying the earlier-start versus lower-price preference before booking. A conditional recommendation is also acceptable if the assumption is explicit and confirmation comes before booking.
- Keep the answer within 120 words and do not claim a booking has been made.
- An explanation of the excluded options is useful but not essential if the response correctly identifies all eligible rooms and handles the unresolved choice.

### Supporting evidence and calculations

- Stated requirements: two continuous hours within 14:00–17:00; capacity at least 10; step-free access; Wi-Fi; total price at most £80.
- [R1] Alder meets all requirements: 14:00–16:00, capacity 12, both amenities, £70.
- [R2] Birch meets all requirements: 15:00–17:00, capacity 10, both amenities, £60.
- [R3] Cedar fails capacity: 8 < 10.
- [R4] Maple fails the budget: £90 > £80.
- The organiser supplies no earlier-start versus price preference. Alder begins one hour earlier; Birch costs £10 less.

### Ambiguity and acceptable alternatives

Deliberate underspecification: all mandatory constraints leave two options. Birch is cheapest, but “best” need not mean cheapest. A response can ask for clarification or offer a conditional recommendation while preserving the need for confirmation. Do not require a unique unconditional choice.

### Dominic’s verification — leave blank until reviewed

| Human review field | Dominic’s entry |
|---|---|
| Reference decision | |
| Corrections to prompt/reference, if any | |
| Additional acceptable alternatives | |
| Remaining uncertainty or clarification needed | |
| Verified by | |
| Actual verification date | |
