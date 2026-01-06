# Contributing to UAV-Satellite Event Analysis

First off, thank you for considering contributing to EVENT! It's people like you that make this project a great tool for the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Guidelines](#coding-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, use the bug report template and include as many details as possible.

**Good Bug Reports Include:**
- A clear, descriptive title
- Exact steps to reproduce the problem
- Expected vs. actual behavior
- Screenshots or logs
- Your environment details (OS, Docker version, EVENT version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Use the feature request template and provide:
- A clear use case and motivation
- Proposed solution with examples
- Alternative approaches considered
- Any mockups or diagrams if applicable

### Code Contributions

1. **Find an Issue**: Look for issues labeled `good first issue` or `help wanted`
2. **Discuss First**: For major changes, open an issue first to discuss your approach
3. **Fork & Branch**: Fork the repo and create a feature branch
4. **Code**: Implement your changes following our coding guidelines
5. **Test**: Write tests and ensure all tests pass
6. **Document**: Update relevant documentation
7. **Submit PR**: Create a pull request with a clear description

## 🛠️ Development Setup

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for local development)
- Node.js 18+ (for dashboard development)
- Git

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/EVENT.git
cd EVENT

# Add upstream remote
git remote add upstream https://github.com/lenchoajema/EVENT.git

# Create environment file
cp .env.example .env

# Start services
docker-compose up -d

# Run tests
docker-compose exec api pytest tests/
```

### Development Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and test
# ... edit files ...
docker-compose restart api  # Restart affected services
pytest tests/  # Run tests

# Commit with descriptive messages
git add .
git commit -m "feat: Add awesome new feature"

# Keep your branch updated
git fetch upstream
git rebase upstream/main

# Push to your fork
git push origin feature/your-feature-name
```

### Running Tests Locally

```bash
# All tests
docker-compose exec api pytest tests/ -v

# Specific test file
docker-compose exec api pytest tests/test_api.py -v

# With coverage
docker-compose exec api pytest tests/ --cov=app --cov-report=html

# Integration tests
./tests/integration_test.sh
```

### Local Development (Without Docker)

```bash
# Install dependencies
cd services/api
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://mvp:mvp@localhost:5432/mvp"
export REDIS_URL="redis://localhost:6379"

# Run API locally
uvicorn app.main:app --reload --port 8000

# Dashboard
cd services/dashboard
npm install
npm start
```

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines (Black for Python, ESLint for JS)
- [ ] Self-reviewed your code
- [ ] Added comments for complex logic
- [ ] Updated documentation
- [ ] Added tests for new features
- [ ] All tests pass
- [ ] No new linting errors
- [ ] Updated CHANGELOG.md if applicable

### PR Guidelines

1. **Title**: Use conventional commit format
   - `feat: Add new feature`
   - `fix: Resolve bug in X`
   - `docs: Update README`
   - `refactor: Improve code structure`
   - `test: Add tests for Y`

2. **Description**: Use the PR template and provide:
   - Clear description of changes
   - Link to related issues
   - Testing evidence (screenshots, logs)
   - Breaking changes if any

3. **Size**: Keep PRs focused and reasonably sized
   - Large PRs are harder to review
   - Consider breaking into smaller PRs

4. **Reviews**: Address reviewer feedback promptly
   - Be open to suggestions
   - Explain your reasoning if you disagree

### Merge Requirements

- All CI checks must pass
- At least one approval from a maintainer
- No unresolved review comments
- Up-to-date with main branch

## 📝 Coding Guidelines

### Python (Backend)

```python
# Use Black for formatting
black services/api/app/

# Use isort for imports
isort services/api/app/

# Type hints are encouraged
def process_alert(alert_id: int) -> Dict[str, Any]:
    """Process a satellite alert.
    
    Args:
        alert_id: The unique identifier for the alert
        
    Returns:
        Dictionary containing processing results
    """
    pass

# Use descriptive variable names
uav_battery_level = 85  # Good
x = 85  # Bad

# Keep functions focused and small
# Prefer composition over deep nesting
```

### JavaScript/React (Frontend)

```javascript
// Use ESLint and Prettier
npm run lint
npm run format

// Use functional components and hooks
const Dashboard = () => {
  const [missions, setMissions] = useState([]);
  
  useEffect(() => {
    fetchMissions();
  }, []);
  
  return <div>...</div>;
};

// PropTypes or TypeScript for type safety
Dashboard.propTypes = {
  apiUrl: PropTypes.string.isRequired
};
```

### General Best Practices

- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It
- **Comments**: Explain *why*, not *what*
- **Error Handling**: Always handle errors gracefully
- **Security**: Never commit secrets, use environment variables
- **Logging**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)

## 🧪 Testing Guidelines

### Test Coverage

- Aim for >80% code coverage
- All new features must have tests
- Bug fixes should include regression tests

### Test Structure

```python
# tests/test_feature.py
import pytest
from app.main import app

class TestFeature:
    """Tests for feature X."""
    
    def test_happy_path(self):
        """Test the normal, expected flow."""
        # Arrange
        data = {"key": "value"}
        
        # Act
        result = process(data)
        
        # Assert
        assert result["status"] == "success"
    
    def test_error_handling(self):
        """Test error cases."""
        with pytest.raises(ValueError):
            process(None)
```

### Test Types

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

## 📚 Documentation Guidelines

### Code Documentation

```python
def calculate_uav_route(
    start: Tuple[float, float],
    end: Tuple[float, float],
    obstacles: List[Obstacle]
) -> List[Waypoint]:
    """Calculate optimal UAV route using A* algorithm.
    
    Computes a collision-free path from start to end position,
    avoiding known obstacles and minimizing distance.
    
    Args:
        start: Starting coordinates (lat, lon)
        end: Destination coordinates (lat, lon)
        obstacles: List of obstacles to avoid
        
    Returns:
        List of waypoints forming the route
        
    Raises:
        RouteNotFoundError: If no valid route exists
        
    Example:
        >>> route = calculate_uav_route(
        ...     start=(45.0, -122.0),
        ...     end=(45.1, -122.1),
        ...     obstacles=[]
        ... )
        >>> len(route) > 0
        True
    """
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): Add endpoint for multi-UAV coordination

Implements new /api/v1/swarms endpoint for managing
UAV swarm missions with collision avoidance.

Closes #42
```

## 🏷️ Labels

We use labels to organize issues and PRs:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to docs
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority-high`: Critical issues
- `priority-low`: Nice to have
- `wontfix`: This will not be worked on

## 🎯 Project Roadmap

See [CHANGELOG.md](CHANGELOG.md) for planned features in upcoming releases.

## ❓ Questions?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review [existing issues](https://github.com/lenchoajema/EVENT/issues)
- Start a [discussion](https://github.com/lenchoajema/EVENT/discussions)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to EVENT! 🚀
