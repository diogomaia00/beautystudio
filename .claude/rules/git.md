# Git rules and best practices

# Branch names and purposes

- `main`
    - production-ready branch
    - must always remain stable
    - merge only after feature is fully tested in `dev`
    - direct commits are not allowed
    - every release or deploy should come from this branch

- `dev`
    - integration branch for ongoing development
    - receives completed feature and fix branches
    - used for testing the full application before merging into `main`
    - merge only when a feature or fix branch has finished development
    - direct commits should be avoided unless strictly necessary

- `feat`
    - identifies a feature branch
    - branch name must be `feat/<small-description>`
    - every project feature must be developed in a `feat` branch
    - branch must be created from `dev`
    - merge back into `dev` after completion
    - examples:
        - `feat/create-customer`
        - `feat/update-payments`
        - `feat/add-cache-to-customers-info`

- `fix`
    - identifies a branch to fix a bug
    - branch name must be `fix/<small-description>`
    - every project bug must be fixed in a `fix` branch
    - branch must be created from `dev`
    - merge back into `dev` after testing
    - examples:
        - `fix/change-currency-from-usd-to-eur`
        - `fix/update-client-permissions`

- `chore`
    - identifies a branch to make a small non-feature change
    - branch name must be `chore/<small-description>`
    - used to:
        - update dependency versions
        - fix typos
        - reorganize files
        - improve configuration
        - clean unused code
    - should not introduce business logic changes
    - examples:
        - `chore/update-eslint-config`
        - `chore/remove-unused-imports`
        - `chore/update-readme`

- `refactor`
    - identifies a branch focused on code restructuring
    - branch name must be `refactor/<small-description>`
    - improves readability, maintainability, or architecture
    - must not change external behavior
    - examples:
        - `refactor/simplify-auth-service`
        - `refactor/extract-payment-module`

- `release`
    - optional branch used before deploying to production
    - branch name must be `release/<version>`
    - used to validate final changes before merging into `main`
    - examples:
        - `release/v1.0.0`
        - `release/v2.3.1`

---

# Conventional Commits

## Format

```text
<type>(optional-scope): <description>

[optional-body]

[optional-footer]
```

Example:

```text
feat(auth): add JWT login support
fix(api): handle null response error
docs: update installation guide
```

---

# Rules

* Use lowercase
* Use imperative mood
* Keep message short and clear
* Do not end with a period
* One logical change per commit
* Separate unrelated changes into different commits

---

# Types

## feat

New feature.

```text
feat: add user profile page
```

---

## fix

Bug fix.

```text
fix: resolve login redirect issue
```

---

## doc

Documentation only changes.

```text
doc: update README setup section
```

---

## style

Formatting or style changes without logic changes.

```text
style: format settings file
```

---

## refactor

Code restructuring without changing behavior.

```text
refactor: simplify authentication service
```

---

## perf

Performance improvements.

```text
perf: optimize database queries
```

---

## test

Add or update tests.

```text
test: add unit tests for payments API
```

---

## build

Build system or dependency changes.

```text
build: upgrade django to 5.2
```

---

## ci

CI/CD configuration changes.

```text
ci: add github actions workflow
```

---

## chore

Maintenance tasks not affecting app logic.

```text
chore: clean unused imports
```

---

## revert

Revert previous commit.

```text
revert: revert JWT authentication changes
```

---

# Scope

Optional component or module name.

```text
feat(auth): add oauth login
fix(api): handle timeout errors
```

---

# Breaking Changes

Use `!` for breaking changes.

```text
feat(api)!: remove legacy endpoints
```

Or:

```text
BREAKING CHANGE: authentication now requires tokens
```

---

# Good Examples

```text
feat: add dark mode
fix(users): prevent duplicate emails
docs: improve API examples
refactor(payments): simplify mbway integration
```

---

# Bad Examples
```text
fixed stuff
update
WIP
misc changes
asdf
```

---

# Recommended Commit Size

Prefer:
* small commits
* focused commits
* atomic commits

Avoid:
* huge mixed commits
* unrelated file changes
* committing broken code

---

# Recommended Workflow

```bash
git checkout -b feat/create-user-authentication
git add .
git commit -m "feat(auth): add JWT authentication"
git pull --rebase
git push origin feat/create-user-authentication
```


---

# Good git practices 

- Pull latest changes before starting work
- Rebase feature branches frequently to avoid large conflicts
- Delete merged branches
- Never commit secrets or .env files
- Use .gitignore properly
- Review changed files before committing with `git status` and `git diff`
- Write meaningful commit messages
- Avoid force push on shared branches
- Commit working code whenever possible
- Test changes before merging into dev
- Test integration before merging into main
- Keep pull requests focused on a single purpose
- Avoid committing generated files unless necessary
- Tag important releases
- Squash unnecessary commits before merging
- Prefer rebasing over unnecessary merge commits in a single developer workflow
- Keep documentation updated together with code changes
