## User Stories

### US1: Add a task (must-have)
As a user, I want to add a new task so that I can keep track of things I need to do.

**Tasks:**

Create the Task model; build the add form in the template; handle the POST in task_list view

**Acceptance criteria:**

- A text box and "Add" button are visible on the main page.
- Submitting a title creates the task and it appears in the list.
- The page reloads with the form cleared.

### US2: View all tasks (must-have)

As a user, I want to see all my tasks on one page so that I know what's outstanding.

**Tasks:**

Write the task_list view; create the task_list.html template; loop over tasks with {% for %}.

**Acceptance criteria:**

- All saved tasks are displayed when I open the home page.
- Each task shows its title.
- Tasks are still there after refreshing the page or restarting the server.

### US3: Mark a task as complete (must-have)

As a user, I want to mark a task as done so that I can see my progress.

**Tasks:** 

Add the completed field; write the toggle_task view and URL; add the "Done" link.

**Acceptance criteria:**

- Clicking "Done" marks the task complete.
- Completed tasks appear with a strikethrough.
- The change is saved in the database.

### US4: Undo a completed task (should-have)

As a user, I want to mark a completed task as not done so that I can fix mistakes.

**Tasks:** 

Reuse the toggle view; show "Undo" when a task is complete.

**Acceptance criteria:**

- Completed tasks show an "Undo" link instead of "Done".
- Clicking it removes the strikethrough and marks the task incomplete.

### US5: Delete a task (must-have)

As a user, I want to delete a task so that my list doesn't fill up with things I no longer need.

**Tasks:**

Write the delete_task view and URL; add the "Delete" link.

**Acceptance criteria:**

- Clicking "Delete" removes the task from the list and the database.
- Other tasks are not affected.
- Deleting a task that doesn't exist shows a 404 page rather than crashing.

### US6: See a message when the list is empty (should-have)

As a new user, I want to see a friendly message when I have no tasks so that I know the app is working.

**Tasks:** add the {% empty %} block to the template.

**Acceptance criteria:**

- "No tasks yet!" shows when there are zero tasks.
- The message disappears once a task is added.
- Extension stories

### US7: Prevent empty tasks (should-have)

As a user, I want the app to reject blank tasks so that my list stays meaningful.

**Tasks:** keep the required attribute on the input; add a server-side check that strips whitespace; optionally show an error message.

**Acceptance criteria:**

- A task made up only of spaces is not saved.
- No blank rows appear in the list.

### US8: Edit a task (must-have)

As a user, I want to change a task's title so that I can fix typos or update details.

**Tasks:** write an edit_task view and URL; create an edit template with a pre-filled form; add an "Edit" link.

**Acceptance criteria:**

### US9: See newest and incomplete tasks first (should-have)

As a user, I want unfinished tasks at the top so that I can focus on what's left.

**Tasks:** order the queryset by completed, then -created_at.

**Acceptance criteria:**

- Incomplete tasks always appear above completed ones.
- Within each group, the newest task is first.


### US10: Set a due date (could-have)

As a user, I want to give a task a due date so that I know what's urgent.

**Tasks:** add a due_date field to the model; run migrations; add a date input to the form; display the date in the list.

**Acceptance criteria:**

- The due date is optional.
- A task with a due date shows it next to the title.
- Overdue incomplete tasks are visibly highlighted (e.g. red text).

### US11: Manage tasks through the admin panel (could-have)

As an admin, I want to manage tasks from Django's admin site so that I can fix or clean up data easily.

**Tasks:** register Task in admin.py; create a superuser; set list_display to show title and completed status.

**Acceptance criteria:**

- I can log in at /admin/.
- I can view, add, edit, and delete tasks there.
- The list shows each task's title and status.

### US12: Use the app on a phone (could-have)

As a user, I want the list to look good on a small screen so that I can use it anywhere.

**Tasks:** add the viewport meta tag; use flexible widths in the CSS; test using browser dev tools.

**Acceptance criteria:**

No horizontal scrolling on a 375px-wide screen.
Buttons and links are big enough to tap.

### US13: Categorise Tasks (could-have)

As a user, I want to assign categories to my tasks, so that I can organise different types of tasks.

**Tasks:**

- Assign a category

- Change a category

- Save/display the category

**Acceptance criteria:**

- User can assign a category when creating a task

- User can change the category when editing a task

- Selected category is saved

- Category is displayed with the task

### US14: Filter Options (could-have)

As a user, I want to filter my tasks by category, so that I can focus on a particular group of tasks.

**Tasks:**

- Filter by category

- Filter by priority

- Return to all tasks

**Acceptance criteria:**

- User can select a category

- Only tasks belonging to the selected category are displayed

- User can return to viewing all tasks

### US15: Prioritise Tasks (could-have)

As a user, I want to assign and organise tasks by priority, so that I can focus on the most important tasks first.

**Tasks:**

- Define priority levels such as High, Medium and Low

- Add priority field to the Task model

- Add priority selection to create and edit forms

- Display task priority

**Acceptance criteria:**

- User can assign a priority when creating a task

- User can change the priority when editing a task

- Priority is saved with the task

- Priority is clearly displayed

### US16: Intuitive Navigation (must-have)

As a user, I want the application to be simple and intuitive to navigate, so that I can quickly add, view, edit and delete my tasks.

**Tasks:**

- Create consistent site navigation

- Provide clear navigation to task management features

- Add clear navigation back to task list

- Ensure navigation links and buttons are clearly labelled

**Acceptance criteria:**

- User can easily access the task list

- User can easily access the Add Task page

- Edit and delete controls are clearly identifiable

- User can return to the task list after creating or editing a task

### US17: Clear Guidance and Feedback (must-have)

As a user, I want clear guidance and feedback when using the application, so that I know what information to enter and whether my actions have been successful.

**Tasks:**

- Add helpful labels, placeholders or help text to input fields

- Add warning and error messages where appropriate

- Add confirmation messages after successful actions

- Make messages clear and easy to understand

- Ensure messages are displayed consistently throughout the application

**Acceptance criteria:**

- Input fields clearly indicate what information the user should enter

- Required fields are clearly identified

- A clear warning or error message is displayed when appropriate

- Confirmation messages are displayed after successful actions

- Messages clearly explain what has happened

- Messages are displayed consistently across the application

- Messages are easy to notice and understand