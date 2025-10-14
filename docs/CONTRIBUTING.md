# Contributing to SOTP

This document outlines the development workflow for the SOTP project. Following these guidelines ensures our work is consistent, visible, and efficient.

## Our Workflow: From "To Do" to "Done"

All work is tracked through GitHub Issues and managed on our Project board. The entire lifecycle of a task is automated based on specific actions.

### Step 1: Taking a Task

1.  **Find a Task:** Go to the Project board and look for an issue in the "To Do" column.
2.  **Assign it to Yourself:** Open the issue and in the "Assignees" panel on the right, assign it to yourself.
3.  **Move:** This action is our signal that work has begun. **The issue should be move to the "In Progress" column on our board.**

### Step 2: Development

1.  **Create a Branch:** From the `develop` branch, create a new feature branch. The branch name **must** follow this convention: `type/issue-number/short-description`.
    * `type` can be `feat`, `fix`, `build`, `docs`, etc.
    * **Example:** `feat/15/add-device-form-ui`

2.  **Code and Commit:** Work on the task in your development environment. Commit your changes regularly.
    * Commit messages **must** follow our [Commit Convention](/.github/COMMIT_COVENCTIONS.md).
    * **Example:** `git commit -m "feat(ui): create device form component"`

### Step 3: Review and Merge

1.  **Create a Pull Request:** When your work is complete, push your branch and open a Pull Request (PR) against the `develop` branch.
    * Fill out the PR template, describing your changes.
    * **Crucially, link the issue your PR resolves** by writing `Closes #15` in the description. This will automatically close the issue when the PR is merged.

2.  **CI & Code Review:**
    * Our CI pipeline will automatically run tests. All checks must pass.
    * At least one other team member must review and approve your changes.

3.  **Merge:**
    * Once approved, a project lead will merge the PR.
    * **The issue will automatically move to the "Done" column on our board.**

This workflow ensures that our project board is always an accurate reflection of our progress.  