# pyATS Network Testing Template - Usage Guide

This repository is designed as a **template** for pyATS network testing projects. Clone it for each new network project or change you need to test.

## Quick Start

### 1. Clone the Template

```bash
# Clone for your specific project
git clone <this-repo-url> my-network-project
cd my-network-project

# Remove the original remote (optional)
git remote remove origin

# Add your own remote
git remote add origin <your-repo-url>
```

### 2. Set Up Your Environment

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your credentials
vim .env

# Source the environment variables
set -a; source .env; set +a
```

### 3. Configure Your Testbed

```bash
# Edit the testbed file or create a new one
vim testbeds/testbed.yaml

# Or copy and customize for your network
cp testbeds/testbed.yaml testbeds/my-network.yaml
```

### 4. Run Existing Tests

```bash
# Run all test suites
pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs ./reports/

# Run specific test suite
pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml --html-logs ./reports/
```

---

## Repository Structure

```
.
├── jobs/                    # Job files (test orchestrators)
│   ├── run_all.py          # Runs all test suites
│   └── run_layer1.py       # Runs Layer 1 tests only
│
├── tests/                   # Test suites organized by category
│   ├── layer1/             # Physical layer tests
│   │   ├── __init__.py
│   │   └── test_layer1.py
│   ├── layer2/             # Data link layer tests (placeholder)
│   │   └── README.md
│   └── layer3/             # Network layer tests (placeholder)
│       └── README.md
│
├── testbeds/               # Network topology definitions
│   ├── testbed.yaml        # Example testbed
│   └── README.md
│
├── configs/                # Configuration files
│   └── logging_config.yaml
│
├── reports/                # Test reports (created at runtime)
├── archive/                # pyATS archives (created at runtime)
├── logs/                   # Log files (created at runtime)
│
├── .github/workflows/      # CI/CD automation
│   └── pyats-validation.yml
│
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
└── .gitignore              # Git ignore patterns
```

---

## Common Workflows

### Workflow 1: Using Existing Tests (Layer 1)

If you just need to validate physical layer connectivity:

1. **Configure testbed** with your devices in `testbeds/testbed.yaml`
2. **Define topology** including interfaces, links, expected speeds, etc.
3. **Set credentials** in `.env` file
4. **Run Layer 1 tests**:
   ```bash
   pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml --html-logs ./reports/
   ```

### Workflow 2: Adding New Test Suites

To add tests for Layer 2, Layer 3, or custom categories:

1. **Create test directory**:
   ```bash
   mkdir -p tests/layer2
   ```

2. **Create test script** (`tests/layer2/test_vlan.py`):
   ```python
   from pyats import aetest

   class VLANValidation(aetest.Testcase):
       @aetest.test
       def check_vlan_config(self, testbed):
           for device in testbed.devices.values():
               device.connect()
               output = device.parse('show vlan')
               # Your validation logic here
               assert len(output['vlans']) > 0
   ```

3. **Create job file** (`jobs/run_layer2.py`):
   ```python
   from pyats.easypy import run

   def main(runtime):
       runtime.job.name = 'Layer 2 Validation'
       run(testscript='tests/layer2/test_vlan.py', runtime=runtime)
   ```

4. **Run your new tests**:
   ```bash
   pyats run job jobs/run_layer2.py --testbed testbeds/testbed.yaml
   ```

The `run_all.py` job will automatically discover and run your new tests!

### Workflow 3: Project-Specific Customization

For a specific network project:

1. **Clone this template** to a project-specific repository
2. **Create custom testbed** in `testbeds/production.yaml`
3. **Add project-specific tests** in `tests/custom/`
4. **Modify existing tests** as needed for your environment
5. **Commit and track changes** in your project repo
6. **Run tests before/after changes**:
   ```bash
   # Before change
   pyats run job jobs/run_all.py --testbed testbeds/production.yaml --html-logs ./reports/before/

   # Make your network change

   # After change
   pyats run job jobs/run_all.py --testbed testbeds/production.yaml --html-logs ./reports/after/

   # Compare results
   ```

---

## Adding New Test Categories

The template is designed to scale. Add new categories beyond Layer 1/2/3:

### Example: Security Tests

```bash
# Create directory
mkdir tests/security

# Create test
cat > tests/security/test_acls.py << 'EOF'
from pyats import aetest

class ACLValidation(aetest.Testcase):
    @aetest.test
    def check_acls(self, testbed):
        # Your ACL validation logic
        pass
EOF

# Create job (optional - run_all.py will find it automatically)
cat > jobs/run_security.py << 'EOF'
from pyats.easypy import run

def main(runtime):
    runtime.job.name = 'Security Validation'
    run(testscript='tests/security/test_acls.py', runtime=runtime)
EOF
```

### Example: Compliance Tests

```bash
mkdir tests/compliance

cat > tests/compliance/test_config_standards.py << 'EOF'
from pyats import aetest

class ConfigCompliance(aetest.Testcase):
    @aetest.test
    def check_ntp_servers(self, testbed):
        expected_ntp = ['10.1.1.1', '10.1.1.2']
        for device in testbed.devices.values():
            device.connect()
            ntp_config = device.parse('show ntp associations')
            # Validate NTP configuration
            pass
EOF
```

---

## Docker Usage

### Build and Run

```bash
# Build image
docker build -t my-network-tests .

# Run interactively
docker run -it --rm \
  -v $(pwd)/testbeds:/app/testbeds:ro \
  -v $(pwd)/reports:/app/reports \
  -e PYATS_USERNAME="${PYATS_USERNAME}" \
  -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
  my-network-tests

# Run tests directly
docker run --rm \
  -v $(pwd)/testbeds:/app/testbeds:ro \
  -v $(pwd)/reports:/app/reports \
  -e PYATS_USERNAME="${PYATS_USERNAME}" \
  -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
  my-network-tests \
  pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs /app/reports/
```

### Docker Compose

```bash
# Run interactively
docker-compose run --rm pyats-tests

# Run tests
docker-compose run --rm pyats-tests \
  pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs /app/reports/
```

---

## Best Practices

### Testbed Management

1. **One testbed per environment**: Create separate testbeds for dev, staging, prod
2. **Use environment variables**: Never commit credentials
3. **Document topology**: Add comments explaining network design
4. **Version control testbeds**: Track changes alongside code
5. **Validate syntax**: Run `python -c "from pyats.topology import loader; loader.load('testbeds/my-testbed.yaml')"`
6. **Use sfp_type for optical validation**: Add `sfp_type: SFP-10G-LR` to fiber interfaces to validate RX power levels (see `testbeds/README.md` for all supported types)

### Test Organization

1. **Group by layer/function**: Use layer1/, layer2/, security/, compliance/, etc.
2. **One test class per concern**: Don't create monolithic test files
3. **Descriptive names**: Use clear names like `test_bgp_neighbors.py`, not `test1.py`
4. **Reusable helpers**: Create shared utilities in test package `__init__.py`
5. **Document test purpose**: Add docstrings explaining what each test validates

### Running Tests

1. **Always generate reports**: Use `--html-logs` for human-readable results
2. **Archive results**: Keep historical reports for trending
3. **Run before AND after changes**: Establish baseline and validate impact
4. **Use debug mode for troubleshooting**: `--loglevel DEBUG`
5. **Run specific suites during development**: Use individual job files, then `run_all.py` for final validation

### CI/CD Integration

The template includes GitHub Actions workflow that:
- Validates syntax on every PR
- Checks testbed YAML files
- Builds Docker image
- Runs security scans

Customize `.github/workflows/pyats-validation.yml` for your needs.

---

## Environment Variables

Key environment variables (set in `.env`):

```bash
# Required
PYATS_USERNAME=admin              # Device login username
PYATS_PASSWORD=your-password      # Device login password

# Optional
PYATS_ENABLE_PASSWORD=            # Enable password if required
PYATS_LOG_LEVEL=INFO              # Logging verbosity
PYATS_REPORT_DIR=./reports        # Report output directory
PYATS_HTML_REPORTS=true           # Enable HTML reports
PYATS_JSON_REPORTS=false          # Enable JSON reports
PYATS_TEST_SUITES=layer1,layer3   # Specific suites to run with run_all.py
PYATS_MAX_WORKERS=5               # Parallel execution workers
```

---

## Troubleshooting

### Common Issues

**Issue**: Tests can't connect to devices
- **Solution**: Check network connectivity, verify credentials, ensure SSH is enabled

**Issue**: Parser errors
- **Solution**: Verify OS type in testbed, update pyATS: `pip install -U pyats[full]`

**Issue**: Tests not discovered by `run_all.py`
- **Solution**: Ensure files follow pattern `tests/*/test_*.py`

**Issue**: Docker can't access network devices
- **Solution**: Use host networking: `docker run --network host ...`

### Getting Help

1. Check the logs in `logs/` directory
2. Run with `--loglevel DEBUG` for detailed output
3. Review pyATS documentation: https://developer.cisco.com/docs/pyats/
4. Check test-specific README files in `tests/*/`

---

## Examples

### Example 1: Pre-Change Validation

```bash
#!/bin/bash
# pre-change-validation.sh

export $(cat .env | xargs)

echo "Running pre-change validation..."
pyats run job jobs/run_all.py \
  --testbed testbeds/production.yaml \
  --html-logs ./reports/pre-change-$(date +%Y%m%d-%H%M%S) \
  --json-logs ./reports/pre-change-$(date +%Y%m%d-%H%M%S)

echo "Review reports before proceeding with change!"
```

### Example 2: Continuous Monitoring

```bash
#!/bin/bash
# continuous-monitor.sh

while true; do
  echo "Running network validation..."
  pyats run job jobs/run_all.py \
    --testbed testbeds/production.yaml \
    --html-logs ./reports/monitor-$(date +%Y%m%d-%H%M%S)

  echo "Sleeping for 1 hour..."
  sleep 3600
done
```

### Example 3: Multi-Site Testing

```bash
#!/bin/bash
# multi-site-test.sh

for site in testbeds/site-*.yaml; do
  echo "Testing $site..."
  pyats run job jobs/run_all.py \
    --testbed "$site" \
    --html-logs ./reports/$(basename $site .yaml)-$(date +%Y%m%d)
done
```

---

## Next Steps

1. **Customize your testbed** in `testbeds/testbed.yaml`
2. **Run the example Layer 1 tests** to verify everything works
3. **Add your own test suites** following the patterns above
4. **Integrate with your workflow** (CI/CD, change management, etc.)
5. **Share and reuse** - this template makes it easy to maintain consistency across projects

## Resources

- [pyATS Documentation](https://developer.cisco.com/docs/pyats/)
- [Genie Parser Library](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/)
- [pyATS Forum](https://community.cisco.com/t5/pyats/bd-p/5672j-disc-pyats)
- [Example Tests](./tests/)
- [Sample Output](./SAMPLE_OUTPUT.md)
