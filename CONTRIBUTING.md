# Contributing

Thanks for contributing to Spixi-AI-Chatbot. Please follow these guidelines to make collaboration smooth.

1. Branches & PRs
- Branch from `master` using descriptive names: `feature/<name>` or `fix/<short-desc>`.
- Open a pull request against `master` and include a short description of the change and rationale.

2. Commit messages
- Use imperative, present-tense messages: `Add feature`, `Fix bug`.
- Include issue number when relevant: `Fix #123: ...`.

3. Code style
- Follow `.editorconfig`. C# uses 4-space indent. Python uses 4-space indent and Black formatting.
- Run `dotnet format` and `black .` locally before opening a PR.

4. Tests
- Add tests for new functionality. Python tests go under `tests/` and use `pytest`.

5. Security
- Do not commit secrets, keys, or wallet files. If you accidentally commit secrets follow the repository's security policy and coordinate with maintainers.
