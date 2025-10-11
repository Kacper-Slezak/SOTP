
# Commit Convention

A consistent commit message convention is used in this project to maintain a clear and readable Git history. This approach makes it easier to understand changes, review project history, and automate tasks like generating changelogs.

This convention is based on the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Structure

Each commit message consists of a **header**, an optional **body**, and an optional **footer**.

```
<type>(<scope>): <subject>
<BLANK LINE>
[optional body]
<BLANK LINE>
[optional footer]
```

-----

### Header

The header is the most important part of the commit message and has a specific format: `<type>(<scope>): <subject>`

#### **`<type>` (Required)**

This describes the kind of change that the commit contains. The allowed types are:

* **feat**: A new feature for the user.
* **fix**: A bug fix for the user.
* **docs**: Changes to documentation only.
* **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
* **refactor**: A code change that neither fixes a bug nor adds a feature.
* **perf**: A code change that improves performance.
* **test**: Adding missing tests or correcting existing tests.
* **build**: Changes that affect the build system or external dependencies (e.g., `package.json`, `Dockerfile`).
* **ci**: Changes to our CI/CD configuration files and scripts (e.g., GitHub Actions workflows).
* **chore**: Other changes that don't modify source code or test files (e.g., updating `.gitignore`).

#### **`<scope>` (Optional)**

The scope provides additional contextual information and is contained within parentheses. It can be the name of the module, component, or part of the codebase affected by the change.

Examples: `api`, `frontend`, `auth`, `collectors`, `db`

#### **`<subject>` (Required)**

The subject contains a short, concise description of the change.

* Use the imperative, present tense: "add" not "added" or "adds".
* Don't capitalize the first letter.
* Do not end the subject line with a period.

-----

### Body (Optional)

The body is used to provide more detailed information about the commit. Use it to explain the "what" and "why" of the change, not the "how".

* Separate the body from the subject with a blank line.
* Use multiple paragraphs if needed.

-----

### Footer (Optional)

The footer is used to reference issues from your issue tracker (like GitHub Issues) or to note breaking changes.

* **Breaking Changes**: Start with `BREAKING CHANGE:` followed by a detailed description of the change, the justification, and migration notes.
* **Referencing Issues**: Use keywords like `Closes`, `Fixes`, or `Resolves` followed by the issue number. For example: `Closes #123`.

-----

## Examples

### Good Commit Messages

```
feat(api): add user registration endpoint
```

```
fix(frontend): correct validation on login form
```

```
refactor(auth): simplify token generation logic

The previous implementation was overly complex and difficult to test.
This change simplifies the flow without altering the final output.
```

```
docs(readme): update setup instructions and add troubleshooting section
```

```
chore: add .env.example to .gitignore
```

```
feat(collectors): implement snmp collector for cisco devices

This commit introduces a new SNMP collector with support for basic
CPU, memory, and interface metrics on Cisco IOS devices.

Closes #42
```

```
perf(db): add index to users table for faster email lookups
```

### Bad Commit Messages

```d
updated stuff
```

Too vague, wrong format.

```
fix: Fixed a bug
```

*(Capitalized subject, past tense, not descriptive)*

```
feat: add login functionality and also fix the header styling
```

A single commit should address a single concern.
