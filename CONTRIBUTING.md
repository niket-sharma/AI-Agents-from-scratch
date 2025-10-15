# Contributing to AI Agents from Scratch

Thank you for your interest in contributing! This document provides guidelines for contributing to this tutorial repository.

## How to Contribute

### Reporting Issues

- **Bugs**: Report bugs via GitHub Issues
- **Documentation**: Report typos, unclear explanations, or missing information
- **Feature Requests**: Suggest new tutorials or improvements

### Types of Contributions

We welcome:

1. **Tutorial Improvements**
   - Fixing typos and errors
   - Clarifying explanations
   - Adding examples
   - Improving code quality

2. **New Tutorials**
   - Advanced agent patterns
   - Real-world use cases
   - Integration with new tools/APIs

3. **Code Examples**
   - Additional agent implementations
   - Tool integrations
   - Example applications

4. **Documentation**
   - Architecture diagrams
   - Concept explanations
   - Troubleshooting guides

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/AI-Agents-from-scratch.git
cd AI-Agents-from-scratch
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Contribution Guidelines

### Code Style

- Follow PEP 8 style guide
- Use descriptive variable names
- Add docstrings to all functions and classes
- Keep functions focused and concise

```python
def good_function_name(parameter: str) -> dict:
    """
    Brief description of what the function does.

    Args:
        parameter: Description of parameter

    Returns:
        Description of return value
    """
    # Implementation
    pass
```

### Documentation

- Use clear, simple language
- Include code examples
- Explain the "why" not just the "how"
- Add diagrams where helpful

### Testing

- Test your code before submitting
- Include test cases for new features
- Ensure existing tests pass

```bash
pytest tests/
```

### Code Formatting

We use Black for code formatting:

```bash
black src/ tutorials/ examples/
```

Check with flake8:

```bash
flake8 src/ tutorials/ examples/
```

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write clear, focused commits
- Follow commit message conventions
- Test your changes

### Commit Message Format

```
type: Short description (50 chars or less)

Longer explanation if needed. Wrap at 72 characters.
Explain what and why, not how.

Fixes #123
```

**Types:**
- `feat`: New feature or tutorial
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add Tutorial 06 on agent evaluation

docs: Fix typo in memory tutorial README

fix: Correct calculator tool division by zero handling
```

### 3. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what changed and why
- Reference to any related issues
- Screenshots (if UI changes)

### 4. Code Review

- Address review feedback promptly
- Be open to suggestions
- Maintain respectful communication

## Tutorial Contribution Guidelines

### Structure

Each tutorial should include:

```
tutorials/XX-topic-name/
├── README.md          # Tutorial instructions
├── code_file.py       # Working code example
├── notebook.ipynb     # Jupyter notebook (optional)
└── exercises/         # Practice exercises (optional)
```

### Tutorial README Template

````markdown
# Tutorial XX: Topic Name

Brief introduction to what this tutorial covers.

## Learning Objectives

- Objective 1
- Objective 2
- Objective 3

## Prerequisites

- List prerequisites

## Time Required

Approximately X minutes

## What You'll Build

Description of what students will create.

## Step 1: Title

Explanation with code examples:

```python
# Code example
```

## Exercises

Practice problems for students.

## What's Next?

Link to next tutorial.
````

### Code Example Guidelines

- Include complete, runnable examples
- Add comments explaining key concepts
- Handle errors gracefully
- Use print statements to show progress
- Keep examples focused on the learning objective

## Example Contribution Guidelines

### Structure

```
examples/
├── example_name/
│   ├── README.md         # Description and usage
│   ├── main.py          # Main implementation
│   ├── requirements.txt  # Specific dependencies
│   └── .env.example     # Environment template
```

### Example README Template

```markdown
# Example Name

Brief description of what this example does.

## Features

- Feature 1
- Feature 2

## Setup

Installation and configuration instructions.

## Usage

How to run the example.

## Architecture

Explanation of how it works.
```

## Documentation Contributions

### What to Document

- Core concepts and terminology
- Architecture decisions
- Design patterns used
- Common pitfalls and solutions
- Best practices

### Documentation Style

- Use clear, simple language
- Define technical terms
- Include examples
- Add cross-references
- Use proper markdown formatting

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on the idea, not the person
- Respect different viewpoints

### Communication

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions

## Recognition

Contributors will be:
- Listed in project contributors
- Credited in release notes
- Acknowledged in documentation

## Questions?

- Check existing issues and discussions
- Create a new issue for bugs
- Start a discussion for questions or ideas
- Tag maintainers if needed (@maintainer-name)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** Every contribution, no matter how small, helps make this resource better for everyone.
