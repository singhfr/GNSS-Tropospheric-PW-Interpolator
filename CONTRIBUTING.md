# Contributing to GNSS Tropospheric PW Interpolator

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### Types of Contributions

We welcome the following types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve or add documentation
- **Testing**: Add test cases or improve test coverage
- **Performance**: Optimize existing code

### Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/gnss-dashboard.git
   cd gnss-dashboard
   ```

2. **Set up Development Environment**
   ```bash
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend setup
   cd ../frontend
   pnpm install
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Guidelines

### Code Style

**Python (Backend & ML)**
- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [flake8](https://flake8.pycqa.org/) for linting
- Add type hints for all function parameters and return values

```bash
# Format code
black app/ ml/

# Check linting
flake8 app/ --max-line-length=100 --ignore=E203,W503
```

**TypeScript/React (Frontend)**
- Use [Prettier](https://prettier.io/) for code formatting
- Follow [ESLint](https://eslint.org/) rules
- Use TypeScript for all new code
- Follow React best practices

```bash
# Format and lint
pnpm lint
pnpm format
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add forecast validation endpoint
fix(ml): resolve GPR training memory issue
docs(readme): update installation instructions
test(backend): add unit tests for interpolation service
```

## 🧪 Testing

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest tests/ -v --cov=app
```

**ML Tests:**
```bash
cd backend
pytest tests/test_ml.py -v
```

**Integration Tests:**
```bash
docker-compose up --build -d
# Run integration tests
docker-compose down
```

### Writing Tests

- Write unit tests for all new functions
- Include integration tests for API endpoints
- Test edge cases and error conditions
- Maintain test coverage above 90%

**Test Structure:**
```python
def test_function_name():
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_result
```

## 📝 Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Use Google-style docstrings for Python
- Include parameter types and descriptions
- Provide usage examples for complex functions

**Python Docstring Example:**
```python
def interpolate_pw(data: pd.DataFrame, model_type: str = "gpr") -> List[GridPoint]:
    """
    Interpolate precipitable water values across a spatial grid.
    
    Args:
        data: DataFrame containing GNSS observations
        model_type: Type of interpolation model ("gpr", "idw")
        
    Returns:
        List of GridPoint objects with interpolated values
        
    Raises:
        ValueError: If data is empty or invalid
        
    Example:
        >>> data = load_gnss_data()
        >>> points = interpolate_pw(data, model_type="gpr")
    """
```

### API Documentation

- Update OpenAPI schemas for new endpoints
- Include request/response examples
- Document error responses
- Test documentation with Swagger UI

## 🚀 Pull Request Process

### Before Submitting

1. **Update Tests**: Add or update tests for your changes
2. **Run Tests**: Ensure all tests pass locally
3. **Update Documentation**: Update relevant documentation
4. **Check Code Style**: Run linters and formatters
5. **Test Integration**: Verify your changes work with Docker

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process

1. **Automated Checks**: CI pipeline runs automatically
2. **Code Review**: At least one maintainer review required
3. **Testing**: All tests must pass
4. **Documentation**: Documentation must be updated
5. **Approval**: Maintainer approval required for merge

## 🐛 Reporting Issues

### Bug Reports

Use the bug report template and include:

- **Environment**: OS, Python version, browser
- **Steps to Reproduce**: Clear step-by-step instructions
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: If applicable
- **Logs**: Relevant error messages or logs

### Feature Requests

Use the feature request template and include:

- **Problem**: What problem does this solve?
- **Solution**: Proposed solution or implementation
- **Alternatives**: Alternative solutions considered
- **Additional Context**: Screenshots, mockups, etc.

## 🏗️ Architecture Guidelines

### Backend (FastAPI)

- Use dependency injection for services
- Implement proper error handling
- Follow REST API conventions
- Use Pydantic models for validation
- Keep business logic in service classes

### Frontend (React)

- Use functional components with hooks
- Implement proper error boundaries
- Follow React best practices
- Use TypeScript for type safety
- Keep components small and focused

### ML Components

- Document model assumptions and limitations
- Include model evaluation metrics
- Version trained models
- Provide clear training procedures
- Handle edge cases gracefully

## 📊 Performance Guidelines

### Backend Performance

- Use async/await for I/O operations
- Implement proper caching strategies
- Optimize database queries
- Profile code for bottlenecks
- Use background tasks for long operations

### Frontend Performance

- Implement lazy loading for components
- Optimize bundle size
- Use React.memo for expensive components
- Minimize re-renders
- Implement proper loading states

### ML Performance

- Optimize model inference time
- Use appropriate data structures
- Implement model caching
- Profile memory usage
- Consider model quantization

## 🌍 Internationalization

Currently, the project supports English only. Contributions for internationalization are welcome:

- Use i18n libraries (react-i18next for frontend)
- Externalize all user-facing strings
- Support RTL languages
- Consider cultural differences in data presentation

## 📦 Dependency Management

### Adding Dependencies

**Backend:**
```bash
pip install new-package
pip freeze > requirements.txt
```

**Frontend:**
```bash
pnpm add new-package
# or for dev dependencies
pnpm add -D new-package
```

### Guidelines

- Keep dependencies minimal
- Use well-maintained packages
- Check for security vulnerabilities
- Document why new dependencies are needed
- Update dependencies regularly

## 🔒 Security

### Security Guidelines

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Implement proper authentication/authorization
- Follow OWASP security guidelines

### Reporting Security Issues

Please report security vulnerabilities privately to the maintainers. Do not create public issues for security problems.

## 📞 Getting Help

### Communication Channels

- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Code Reviews**: Technical discussions
- **Documentation**: Check the wiki and README

### Mentorship

New contributors are welcome! If you need help getting started:

1. Look for issues labeled "good first issue"
2. Ask questions in GitHub Discussions
3. Join our community calls (if applicable)
4. Reach out to maintainers for guidance

## 🏆 Recognition

Contributors are recognized in:

- README.md contributors section
- Release notes for significant contributions
- GitHub contributor statistics
- Special mentions for outstanding contributions

Thank you for contributing to the GNSS Tropospheric PW Interpolator! 🙏
