# Agent Guide for pyATS Network Testing Framework

This document provides guidelines for AI agents and developers working on this pyATS network testing repository. Follow these instructions to ensure code quality, consistency, and successful execution of network tests.

## 🛠️ Build, Lint, and Test Commands

### Environment Setup
The project uses Python 3.11 and standard pip for dependency management.

```bash
# Install dependencies
pip install -r requirements.txt
```

### Linting and Formatting
Strict adherence to linting and formatting standards is required. The project uses `black` for formatting and `flake8`/`pylint` for linting.

```bash
# Format code (Auto-fix)
black jobs/ tests/

# Check formatting (Dry run)
black --check --diff jobs/ tests/

# Run Flake8 Linter (Critical)
# Configuration: max-line-length=120, max-complexity=10
flake8 jobs/ tests/ --count --max-complexity=10 --max-line-length=120 --statistics

# Run Pylint
# Configuration: max-line-length=120, disable specific convention checks (C0114, C0115, C0116)
pylint --exit-zero --max-line-length=120 --disable=C0114,C0115,C0116 jobs/ tests/
```

### Running Tests
Tests are executed using the Cisco pyATS framework. You can run entire suites via job files or individual test scripts.

#### 1. Running via Job File (Recommended for Suites)
Job files (in `jobs/`) orchestrate the execution of test suites.

```bash
# Run all available test suites
pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml

# Run a specific suite (e.g., Layer 1 only)
# Note: jobs/run_layer1.py must exist, or use run_all.py with env var
pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml

# Run specific suites using the generic runner
export PYATS_TEST_SUITES="layer1"
pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml
```

#### 2. Running a Single Test File
For rapid development, you can run individual test files directly if they contain a `if __name__ == '__main__':` block invoking `aetest.main()`.

```bash
# Run a specific test file
python tests/layer1/test_layer1.py --testbed testbeds/testbed.yaml
```

#### 3. Testbed Validation
Always validate YAML syntax before running tests.

```bash
# Validate Testbed YAML
python -c "import yaml; yaml.safe_load(open('testbeds/testbed.yaml'))"

# Validate Loading (Dry Run)
python -c "from pyats.topology import loader; loader.load('testbeds/testbed.yaml')"
```

#### 4. Docker Execution
Ensure code runs in the container environment.

```bash
# Build image
docker build -t pyats-network-tests .

# Run tests in container
docker run --rm -v $(pwd)/testbeds:/app/testbeds:ro pyats-network-tests \
    pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml
```

---

## 📐 Code Style and Conventions

### General Guidelines
- **Python Version**: Target Python 3.11+.
- **Line Length**: 120 characters.
- **Indentation**: 4 spaces.
- **Typing**: Use type hints where helpful, but not strictly enforced unless configured.

### Imports
- Group imports: Standard library first, then third-party (including `pyats`, `unicon`), then local application imports.
- **pyATS Imports**:
  ```python
  from pyats import aetest
  from pyats.topology import loader
  from pyats.easypy import run
  ```

### Naming Conventions
- **Variables/Functions**: `snake_case` (e.g., `interface_status`, `check_errors`).
- **Classes**: `CamelCase` (e.g., `CommonSetup`, `BGPValidation`).
- **Test Methods**: Must be decorated with `@aetest.test`, `@aetest.setup`, or `@aetest.cleanup`.
- **Files**:
  - Tests: `tests/<category>/test_<name>.py`
  - Jobs: `jobs/run_<name>.py`

### Testing Structure (pyATS/AEtest)
Follow the standard `aetest` structure:
1.  **CommonSetup**: Connect to devices, verify basic environment.
2.  **Testcases**: Group related tests (e.g., `InterfaceChecks`, `RoutingChecks`).
3.  **Tests**: Individual validation steps.
4.  **CommonCleanup**: Disconnect and teardown.

**Example Pattern:**
```python
from pyats import aetest

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect(self, testbed):
        # Always use log_stdout=False for cleaner logs unless debugging
        testbed.connect(log_stdout=False)

class MyFeatureTest(aetest.Testcase):
    @aetest.test
    def simple_check(self, testbed):
        device = testbed.devices['router1']
        # Use parse() for structured output
        output = device.parse('show version')
        if not output:
             self.failed("Could not parse output")

if __name__ == '__main__':
    # Allow standalone execution
    import argparse
    from pyats.topology import loader
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed', type=loader.load, required=True)
    args, _ = parser.parse_known_args()
    aetest.main(testbed=args.testbed)
```

### Error Handling
- Use `self.failed("Reason")`, `self.passed("Reason")`, `self.skipped("Reason")` inside test methods.
- Do not use bare `assert` statements if you want the test framework to capture the failure gracefully with logs. Use `aetest` methods.
- Wrap connection attempts in `try/except` if connection failures should not abort the entire run (though usually they should in `CommonSetup`).

### Logging
- Use standard `logging`.
- `logger = logging.getLogger(__name__)`.
- Do not print to stdout; use `logger.info()`, `logger.debug()`.

---

## 📂 Directory Structure Rules

- **`jobs/`**: Contains execution scripts (`run_*.py`). Do not put test logic here.
- **`tests/`**: Contains actual test logic. Organize by layer or feature (e.g., `tests/layer1/`).
- **`testbeds/`**: Contains YAML topology files. Do NOT hardcode device credentials in code; use environment variable substitution in YAML (`%ENV{VAR}`).
- **`configs/`**: Static configuration files (logging, etc.).

## 🤖 Working with Files
- **Paths**: Always use relative paths from the project root when importing or referencing files in code (e.g., `tests/layer1/`).
- **Reading Files**: When reading files in agents, always verify the path first.

## 🛡️ Security
- **Credentials**: NEVER commit passwords or keys. Use `.env` files and `os.environ` or pyATS YAML environment substitution.
- **Validation**: Ensure all YAML inputs are validated before use.
