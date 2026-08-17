# Contributing Guidelines

This guide describes the team's development and contribution workflow.

## Development Setup

1. Fork the repository (optional but recommended for external contributors).
2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```
3. Follow the setup instructions for each folder:
   - `backend/` — Python/FastAPI
   - `web/` — React
   - `mobile/` — Flutter
4. Copy `.env.example` to `.env` and fill in the required keys (Gemini API,
   Google Maps, database, and so on).

### Pre-commit Hooks

The project uses pre-commit hooks to automatically check code quality before creating commits.

Install pre-commit:

```bash
pip install pre-commit
```
Enable the hooks for the repository:

```bash
pre-commit install
```

Run the checks manually:
```bash
pre-commit run
```

## Branch Naming

Choose clear, lowercase names separated by hyphens.

| Type          | Pattern                       | Example                       |
| ------------- | ----------------------------- | ----------------------------- |
| Feature       | `feature/<short-description>` | `feature/user-authentication` |
| Bug Fix       | `bugfix/<short-description>`  | `bugfix/login-validation`     |
| Documentation | `docs/<short-description>`    | `docs/update-readme`          |
| Chore         | `chore/<short-description>`   | `chore/update-dependencies`   |

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) so commit
history is consistent and easy to understand. Write each commit as a short,
imperative summary of one logical change.

Use this format:

```text
<type>(optional-scope): <short description>
```

Common types include `feat` for features, `fix` for bug fixes, `docs` for
documentation, `test` for tests, `refactor` for code restructuring, and `chore`
for maintenance or configuration.

Examples:

```text
feat(auth): add user login
fix: validate login credentials
docs: update setup instructions
test(api): add user login tests
refactor(auth): simplify token validation
chore: update dependencies
```

Keep descriptions concise, lowercase, and in the imperative mood. For breaking
changes, add `!` after the type or scope. For example:

```text
feat(api)!: change login response format
```

## Coding Standards & Testing

- Backend (Python): Follow PEP 8. Use `black` for formatting and `ruff` for
  linting.
- Web (React): Follow ESLint and Prettier rules.
- Mobile (Flutter): Run `flutter analyze` and `flutter format`.
- Write tests for new features and bug fixes.
- All tests must pass before creating a Pull Request.

## Pull Requests

Open a PR against `main` when the work is ready for review.

- Follow the PR template.
- Clearly describe the change and its motivation.
- Reference every related issue (for example, `fixes #12` or `relates to #12`).
- State the testing performed.

## Continuous Integration

The project uses GitHub Actions to automatically validate Pull Requests before merging.

CI checks are executed when a Pull Request is created or updated.

### Backend CI

The backend workflow performs:

- Dependency installation
- Ruff lint check
- Ruff formatting check
- Backend tests using pytest

### Web CI

The web workflow performs:

- Dependency installation
- ESLint check
- Prettier formatting check
- Frontend tests using Vitest
- Production build verification

A Pull Request must pass the required CI checks before it can be merged.

## Code Review

At least one team member must review and approve every PR before it is merged.

Reviewers should verify the requirements, implementation quality, and relevant
tests. Address all required changes before merging.

## Merging

- Get at least one approval from a team member.
- Do not push directly to `main`.
- Ensure all required checks pass.
- Delete the feature branch after merging.

## Issues

Use GitHub Issues to track features, bugs, development tasks, and documentation work.

- Use the appropriate issue template.
- Check for duplicates before opening an issue.
- A feature can include multiple related issues; complete them in the same
  feature branch when appropriate.
