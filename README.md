# Accessing from SIGCSE
### Automated Support for Flexible Extensions
*Poster Link*
Jordan Schwartz, Madison Bohannan, Jacob Yim, Yuerou Tang, Dana Benedicto, Charisse Liu, Armando Fox, Lisa Yan, and Narges Norouzi. 2024.
Automated Support for Flexible Extensions. In Proceedings of the 55th ACM Technical Symposium on Computer Science Education V. 2 (SIGCSE 2024), March 20–23, 2024, Portland, OR, USA. ACM, New York, NY, USA, 2 pages.
https://doi.org/10.1145/3626253.3635628

### Supporting Mastery Learning with Flexible Extensions
*Poster Link*
Yuerou Tang, Jacob Yim, Jordan Schwartz, Madison Bohannan, Dana Benedicto, Charisse Liu, Armando Fox, Lisa Yan, and Narges Norouzi. 2024.
Supporting Mastery Learning with Flexible Extensions. In Proceedings of the 55th ACM Technical Symposium on Computer Science Education V. 2 (SIGCSE 2024), March 20–23, 2024, Portland, OR, USA. ACM, New York, NY, USA,
2 pages. https://doi.org/10.1145/3626253.3635615

# The CS 161 Extension Pipeline

The CS 161 Extensions Pipeline is a lightweight framework designed for tracking, approving, and managing extension requests in medium and large classes (e.g. N > 50). It's optimized for courses in the EECS department at UC Berkeley, but is extensible to other departments and universities.

At a high level, this pipeline consists of:

- A **[Google Form](https://docs.google.com/forms/d/e/1FAIpQLSdcVhd9WIXn0uegFEX8QVTEEre4oqv5oqQc6bXkNPkG_VIl7g/viewform?usp=sf_link)** that students submit extension requests to.
- A **[Google Sheet](https://docs.google.com/spreadsheets/d/17u8VkAefOeiaW8ryMlC8kid8_HOhu3jN-VhXdYtU75s/edit?usp=sharing)** that collects student extension requests and tracks all extension requests in a master roster.
- **Google Cloud Functions** that contains core business logic that:
  - Receives form data through a simple **Google Apps Script** trigger.
  - Process form data in combination with a student's "record" (which includes DSP status and prior extension requests) to enter either an auto-approval or manual-approval flow.
  - Sends updates to staff through a **Slack Webhook**, enabling simple internal discussion of student cases through Slack threads.
  - Sends updates to students through [bCOP](https://berkeley.service-now.com/kb_view.do?sysparm_article=KB0011937)
  - Optionally publishes assignment extensions to one or more **Gradescope** assignments.
 
This fork of the CS 161 extensions pipeline is managed by Seamless Learning and CDSS staff. There are slight differences between CS 161's version and this version, including which Google Cloud Functions are used.

This README is useful to see how the pipeline works for students and staff. See [GETTING_STARTED.md](GETTING_STARTED.md) to set up the pipeline for your class.

# Background

#### Traditional Flow

Traditionally, courses deal with two types of extensions –

1. **DSP Extensions**, for students with accommodations for assignment extensions
2. **Non-DSP Extensions**, for students facing extenuating or otherwise unforeseen circumstances

Courses traditionally collect extension requests through Google Forms (e.g. ones provided by course managers, like [this one](https://docs.google.com/forms/d/e/1FAIpQLSfrlZXWRdllpkllha9Abfib57qJcKrRfeHHW3kSmA2b3FZ_QA/viewform?usp=sf_link)) or via email. In order to approve these extensions, however, courses (or course managers) need to:

- Read the student's request and categorize it into a DSP or Non-DSP extension.
- Look up whether the student has previously requested assignment extensions.
- Either (a) update the student's requested extensions in a central spreadsheet, or (b) update the student's requested extension on Gradescope/OKPY/PrairieLearn.
- Send an email to the student containing an "Approved" message, with a new due date.

#### Challenges

The traditional flow results in several challenges, including:

- **High potential for human error.** In every manual step, there's a chance for data entry errors that are capable of propagating downstream; in CS 161/CS 61C, we saw a large number of these that arose at the end of the semester when generating final grade reports.
- **Communication difficulties.** For classes that outsource work to course managers, there are three parties with different views on extension data: what course managers see, what course staff see, and what students see. All communication, by default, needs to be inclusive of all three parties; if even one email is two-way instead of three-way, then information is "lost".

- **Delayed processing times.** Because of the number of manual steps required here, it can take several days for students to hear back on whether or not their requests were granted, leaving them in a state of stress and uncertainty.
- **High barriers to requesting extensions.** Because there are so many steps in approving each extension, there's a tendency to write strongly-worded policies discouraging most student extension requests.

The CS 161 Extension Pipeline addresses all of these challenges, significantly **reducing course staff workload** while simultaneously **improving quality-of-life for students**.

# Our Pipeline: Student Workflow

Students request an extension through a Google Form (see an example [here](https://docs.google.com/forms/d/e/1FAIpQLSdcVhd9WIXn0uegFEX8QVTEEre4oqv5oqQc6bXkNPkG_VIl7g/viewform?usp=sf_link)).

**If a student knows which assignments they want to request an extension on,** then they're prompted to select from a list of assignments, and provide a number of days for each extension. They can either enter a single number (which will apply to all assignments that they select), or enter comma-separated numbers (to allow them to request a different number of days for different assignments).

![image-20220127093941023](README.assets/image-20220127093941023.png)

**If a student's working with one or more partners**, then they're asked to enter their partners' emails and SIDs (comma-separated). Their partner(s) will be included in extensions for any assignments that they select which are marked as partner projects.

**If a student doesn't know what assignment they need an extension on,** they can request a meeting with a TA. We've seen this happen for students who have extenuating circumstances, and just need to talk through their situation before deciding upon a specific request.

**If a student's a DSP student with an accommodation for assignment extensions,** they can declare that on the form. (We recommend that all students who fall under this category receive auto-approvals for extension requests fewer than 7 days.)

**When a student's request has been approved (either manually or automatically),** students receive a templated email with their updated assignment deadlines. ![image-20220127094604714](README.assets/image-20220127094604714.png)

**If a class has enabled Gradescope extensions,** students will see extensions reflected in Gradescope automatically after they recieve the email with their updated deadlines, as seen below. This works for one or multiple Gradescope assignments per in-class assignment (so if you have one assignment for code and one for a written PDF, then you can paste both assignment URL's into the `Assignments` tab of the master spreadsheet, and the tool will create extensions on both Gradescope assignments).
![image-20220207124800646](README.assets/image-20220207124800646.png)

...and that's it for students!

# Our Pipeline: Staff Workflow

Staff view all extensions on a master spreadsheet, with two main tabs: a **Form Responses** tab, which contains all form responses from students, and a **Roster** tab, which contains a list of all students in the course, with a column for each assignment. The other tabs are used to set up the pipeline and likely only need to be touched during set up. The **Roster** is color coded and looks like this:

![image-20220127110217827](README.assets/image-20220127110217827.png)

When an extension request comes in, staff first receive a Slack message in a private Slack channel.

---

**<u>If an extension request falls into an auto-approval category,</u>** the message contains a summary of the student's request, as well as a list all of their granted extensions.

![image-20220127095857467](README.assets/image-20220127095857467.png)

When an extension is automatically approved, staff don't need to do anything! 

---

<u>**If an extension request requires manual approval**,</u> the message contains a reason why the request couldn't be auto-approved.

![image-20220127103436782](README.assets/image-20220127103436782.png)

When an extension requires manual approval, staff should read the reason for the extension, and discuss the request (if needed) in the Slack thread, escalating the case to other staff (e.g. instructors) if necessary.

If the extension warrants an approval, staff should:

1. Set the **approval_status** column on the **Roster** to **"Manually Approved".**
2. Set the **email_status** column on the **Roster** to **"In Queue"**.
3. Use the **Actions => Dispatch Emails** menu item to send emails to all students in the queue. This will send emails out to the students in the queue, removing them from the queue as emails are sent, and send an update to Slack when all emails have been sent.

![image-20220127110457234](README.assets/image-20220127110457234.png)

If the extension does not warrant an approval (or staff need more information), staff should:

1. Follow up with the student over email.
2. Clear the **approval_status** column on the **Roster**.
3. Set the **email_status** column on the **Roster** to **Manually Sent**.

---

**<u>If an extension request contains malformed data or any other error occurred,</u>** the message contains a description of the error, along with the entire form response.

![image-20220127100144172](README.assets/image-20220127100144172.png)

When an error occurs, staff should:

1. Correct the error on the **Form Responses** sheet (or, if it was an internal error due to other data misconfiguration - e.g. missing assignments - correct the configuration).
2. Select the **Rerun** checkbox next to any form responses that weren't fully processed.
3. Use the **Actions => Reprocess Form Submissions** menu item to reprocess the failed submissions.

---

**<u>If a student requests a student meeting,</u>** the message contains a description of the student's request.

![image-20220127110739789](README.assets/image-20220127110739789.png)

If, during a student meeting (or through some other channel, like an Ed post), staff would like to grant a student an extension on an assignment, staff should enter the number of days to extend the assignment by directly onto the student record on the **Roster**, and add the student record in the queue for outbound emails. This is a natural "form bypass" case, where a form submission isn't required to grant a student an extension, but these specially-granted extensions are still tracked alongside the rest of the student's extension requests.

---

# Configuration

All configuration values (e.g. API keys, email options) are stored on the spreadsheet itself, in the **"Environment Variable"** tab.

![image-20220127111221248](README.assets/image-20220127111221248.png)

Assignments may be dynamically configured as well, through the **"Assignments"** tab.

![image-20220127111424320](README.assets/image-20220127111424320.png)

# Edge Cases

**<u>In what cases are extensions flagged for human approval?</u>**

These cases are flagged for human approval:

- The student requests a large number of extension days for any single assignment. This threshold is `AUTO_APPROVE_THRESHOLD` and `AUTO_APPROVE_THRESHOLD_DSP` for students with DSP accommodations for assignment extensions.
- The student requests extensions for a large number of assignments. This threshold is `AUTO_APPROVE_ASSIGNMENT_THRESHOLD`.
- The **student record** has "work-in-progress" (e.g. the row on the roster is red or yellow - the student either has an existing pending request or ongoing student meeting).

All other cases are auto-approved! [See here for the logic that handles these cases.](https://github.com/cs161-staff/extensions/blob/master/src/handle_form_submit.py#L63)

**<u>How do I make it so that all extensions (regardless of status) require manual approval?</u>**

If you want tighter control over what's approved, set `AUTO_APPROVE_THRESHOLD` to `0` and `AUTO_APPROVE_THRESHOLD_DSP` to `0`. In this case, it doesn't matter what you set `AUTO_APPROVE_ASSIGNMENT_THRESHOLD` to.

**<u>What if a student submits an extension request with one or more partners?</u>**

Any requested extensions for assignments that are "partner" assignments will apply to the designated partner(s) as well as the student. Both student records will be updated on the **Roster**, and the logic for approval will apply to all partners (e.g. if Partner A submits the form and Partner B has a "work-in-progress" record, then the extension as a whole will be flagged for manual approval).

**<u>Wait, I still have to update the student's due date in OKPY/Gradescope/Prarielearn so that they'll be able to turn in their assignments late, right?</u>**

You could do this (manually) after each extension request, if you'd like. Alternatively, you could set the "late" due date on these assignments to the end of the semester, and use the extension data on the **Roster** during grade compilation (this is what CS 161 & CS 61C do). Students will see their assignments marked as "late", but they'll be able to use the email they received as proof of their granted extension, just in case they notice inconsistencies in their grade reports.

If you're using Gradescope, you can configure the pipeline to input extensions on Gradescope automatically.

**<u>What happens if this thing internally combusts in the middle of the semester?</u>**

While unlikely, this is a very simple failover case: just process form submissions into the **Roster** spreadsheet manually, and send templated emails through something like YAMM.

**<u>What about long-term maintenance?</u>**

Due to the simplicity of this project's architecture (no frontend, configuration is entirely dynamic, etc.), we don't anticipate this project needing a lot of long-term maintenance! And feature requests are simple to add, since the code is well-documented with Python class abstractions.
