# pyATS Network Testing Framework

**A template repository for automated network testing with Cisco pyATS**

This is a ready-to-use template for building automated network validation test suites. Clone it for each network project or change you need to test, customize the testbed and tests, and validate your network infrastructure with confidence.

## 🎯 Purpose

This template provides a **scalable foundation** for pyATS-based network testing projects. It comes pre-configured with:

- ✅ **Organized structure** for multiple test categories (Layer 1, 2, 3, security, compliance, etc.)
- ✅ **Example Layer 1 tests** validating physical connectivity, optics, errors, and CDP
- ✅ **Flexible job runners** to execute single or multiple test suites
- ✅ **Docker support** for consistent execution environments
- ✅ **CI/CD automation** with GitHub Actions
- ✅ **Production-ready configuration** with logging, reporting, and error handling

**Clone this repository for each network project to maintain test code alongside your infrastructure changes.**

---

## 🚀 Quick Start

### 1. Clone the Template

```bash
git clone <this-repo-url> my-network-project
cd my-network-project
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install pyATS and dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
vim .env

# Load environment variables
export $(cat .env | xargs)
```

### 4. Configure Your Network

Edit `testbeds/testbed.yaml` with your device details:

```yaml
devices:
  router1:
    os: iosxe
    type: router
    credentials:
      default:
        username: '%ENV{PYATS_USERNAME}'
        password: '%ENV{PYATS_PASSWORD}'
    connections:
      defaults:
        class: unicon.Unicon
      cli:
        protocol: ssh
        ip: 192.168.1.1

topology:
  router1:
    interfaces:
      GigabitEthernet1:
        link: router1-router2
        speed: 1000
        duplex: full
```

### 5. Run Tests

```bash
# Run all test suites
pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs ./reports/

# Run specific test suite (Layer 1)
pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml --html-logs ./reports/

# View reports
open reports/TaskLog.html
```

---

## 📁 Repository Structure

```
.
├── jobs/                       # Job orchestration files
│   ├── run_all.py             # Execute all test suites
│   └── run_layer1.py          # Execute Layer 1 tests
│
├── tests/                      # Test suites by category
│   ├── layer1/                # Physical layer validation
│   │   ├── test_layer1.py     # Link status, optics, errors, CDP
│   │   └── __init__.py
│   ├── layer2/                # Data link layer (placeholder)
│   │   └── README.md          # Guide for adding L2 tests
│   └── layer3/                # Network layer (placeholder)
│       └── README.md          # Guide for adding L3 tests
│
├── testbeds/                   # Network topology definitions
│   ├── testbed.yaml           # Example testbed
│   └── README.md
│
├── configs/                    # Configuration files
│   └── logging_config.yaml    # Logging configuration
│
├── reports/                    # Test reports (generated)
├── archive/                    # pyATS archives (generated)
├── logs/                       # Log files (generated)
│
├── .github/workflows/          # CI/CD automation
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Compose configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── README.md                   # This file
├── TEMPLATE_USAGE.md           # Detailed usage guide
└── SAMPLE_OUTPUT.md            # Example test outputs
```

---

## 📋 Included Test Suites

### Layer 1 Validation (Included)

The template includes a complete Layer 1 test suite (`tests/layer1/test_layer1.py`) that validates:

| Test | Description | Failure Example |
|------|-------------|----------------|
| **Link Status** | Verifies interfaces are up/up | `router1:Gi1 is up/down` |
| **Optical Levels** | Validates RX power within SFP thresholds | `RX -12.5 dBm (expected -9.5 to 2.0)` |
| **Interface Errors** | Checks for CRC, input, output errors | `[245 in, 45 CRC]` |
| **Speed/Duplex** | Validates configuration matches expected | `speed 100 != 1000` |
| **MTU** | Verifies MTU settings | `MTU 1400 != 1500` |
| **CDP Neighbors** | Confirms topology matches expectations | `CDP neighbor sw1 != router2` |

**Supported SFP Types:**
- SFP-10G-SR, SFP-10G-LR, SFP-10G-ER
- SFP-1G-SX, SFP-1G-LX

### Layer 2 & Layer 3 (Placeholders)

The `tests/layer2/` and `tests/layer3/` directories include README files with:
- Suggested test cases (VLANs, STP, BGP, OSPF, etc.)
- Code examples and patterns
- Getting started guides

**Add your own tests following these patterns!**

---

## 🐳 Docker Usage

### Build Image

```bash
docker build -t pyats-network-tests .
```

### Run Tests in Container

```bash
# Interactive mode
docker run -it --rm \
  -v $(pwd)/testbeds:/app/testbeds:ro \
  -v $(pwd)/reports:/app/reports \
  -e PYATS_USERNAME="${PYATS_USERNAME}" \
  -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
  pyats-network-tests

# Direct execution
docker run --rm \
  -v $(pwd)/testbeds:/app/testbeds:ro \
  -v $(pwd)/reports:/app/reports \
  -e PYATS_USERNAME="${PYATS_USERNAME}" \
  -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
  pyats-network-tests \
  pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs /app/reports/
```

### Docker Compose

```bash
# Run interactively
docker-compose run --rm pyats-tests

# Run all tests
docker-compose run --rm pyats-tests \
  pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs /app/reports/
```

---

## 🔧 Adding Your Own Tests

### Example: Adding BGP Validation

1. **Create test file** (`tests/layer3/test_bgp.py`):

```python
from pyats import aetest

class BGPValidation(aetest.Testcase):
    @aetest.test
    def check_bgp_neighbors(self, testbed):
        failed = []
        for device in testbed.devices.values():
            device.connect(log_stdout=False)
            bgp = device.parse('show bgp summary')

            for neighbor, data in bgp['neighbor'].items():
                if data['state'] != 'Established':
                    failed.append(f"{device.name}: {neighbor} state is {data['state']}")

        if failed:
            self.failed(f"BGP neighbors down: {'; '.join(failed)}")
        else:
            self.passed("All BGP neighbors Established")
```

2. **Create job file** (`jobs/run_bgp.py`):

```python
from pyats.easypy import run

def main(runtime):
    runtime.job.name = 'BGP Validation'
    run(testscript='tests/layer3/test_bgp.py', runtime=runtime)
```

3. **Run your tests**:

```bash
# Run BGP tests specifically
pyats run job jobs/run_bgp.py --testbed testbeds/testbed.yaml

# Or run all tests (auto-discovers your new test)
pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml
```

**See [TEMPLATE_USAGE.md](./TEMPLATE_USAGE.md) for more examples and patterns.**

---

## ⚙️ Configuration

### Environment Variables

Set in `.env` file:

```bash
# Required
PYATS_USERNAME=admin
PYATS_PASSWORD=your-password

# Optional
PYATS_LOG_LEVEL=INFO
PYATS_REPORT_DIR=./reports
PYATS_HTML_REPORTS=true
PYATS_JSON_REPORTS=false
PYATS_TEST_SUITES=layer1,layer3  # Specific suites for run_all.py
```

### Testbed Configuration

The testbed YAML defines:
- **Devices**: Connection details, OS type, credentials
- **Topology**: Interface mappings, links, expected configurations
- **Custom Attributes**: SFP types, speed/duplex, MTU, etc.

See `testbeds/README.md` and official docs: https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html

---

## 📊 Test Reports

### HTML Reports

Generate with `--html-logs`:

```bash
pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs ./reports/
```

Features:
- Interactive web interface
- Expandable test details
- Device connection logs
- Searchable and filterable
- Direct links to failures

### JSON Reports

Generate with `--json-logs` for programmatic parsing:

```bash
pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --json-logs ./reports/
```

See [SAMPLE_OUTPUT.md](./SAMPLE_OUTPUT.md) for examples of test outputs and report structures.

---

## 🔄 CI/CD Integration

The included GitHub Actions workflow (`.github/workflows/pyats-validation.yml`) provides:

- ✅ **Code linting** (flake8, pylint, black)
- ✅ **YAML validation** (testbeds, configs)
- ✅ **Docker build testing**
- ✅ **Syntax validation** for all tests
- ✅ **Security scanning** (safety, bandit)

Runs automatically on PRs and pushes to main.

**Optional**: Uncomment the `network-testing` job to run actual tests against network devices (requires secrets configuration).

---

## 🎓 Use Cases

### 1. Pre-Change Validation

```bash
# Before network change
pyats run job jobs/run_all.py --testbed testbeds/production.yaml \
  --html-logs ./reports/pre-change/

# Make your change

# After network change
pyats run job jobs/run_all.py --testbed testbeds/production.yaml \
  --html-logs ./reports/post-change/

# Compare results
```

### 2. Continuous Monitoring

Run tests on a schedule (cron, systemd timer, etc.) to detect drift:

```bash
0 */6 * * * cd /path/to/tests && pyats run job jobs/run_all.py \
  --testbed testbeds/production.yaml --html-logs ./reports/$(date +\%Y\%m\%d-\%H\%M)/
```

### 3. Project-Specific Testing

Clone this template for each project:

```bash
# Project 1: Data center migration
git clone <template> dc-migration-tests
cd dc-migration-tests
# Add migration-specific tests

# Project 2: Branch upgrade
git clone <template> branch-upgrade-tests
cd branch-upgrade-tests
# Add upgrade validation tests
```

### 4. Multi-Vendor Networks

```bash
# Create testbeds for different vendors
testbeds/
  ├── cisco-core.yaml
  ├── arista-leaf.yaml
  └── juniper-edge.yaml

# Run against all
for tb in testbeds/*.yaml; do
  pyats run job jobs/run_all.py --testbed $tb --html-logs ./reports/$(basename $tb .yaml)/
done
```

---

## 🛠️ Troubleshooting

### Connection Issues
- **Problem**: Can't connect to devices
- **Solution**: Check IP/port, verify credentials, ensure SSH is enabled, test with `ssh user@device`

### Parser Errors
- **Problem**: `ParserNotFound` errors
- **Solution**: Verify OS type in testbed matches device, update pyATS: `pip install -U pyats[full]`

### Missing Test Discovery
- **Problem**: `run_all.py` doesn't find tests
- **Solution**: Ensure files match pattern `tests/*/test_*.py` and have proper Python syntax

### Docker Networking
- **Problem**: Container can't reach network devices
- **Solution**: Use host networking: `docker run --network host ...`

See [TEMPLATE_USAGE.md](./TEMPLATE_USAGE.md#troubleshooting) for more troubleshooting tips.

---

## 📚 Documentation

- **[TEMPLATE_USAGE.md](./TEMPLATE_USAGE.md)** - Comprehensive guide for using this template
- **[SAMPLE_OUTPUT.md](./SAMPLE_OUTPUT.md)** - Example test outputs and reports
- **[testbeds/README.md](./testbeds/README.md)** - Testbed configuration guide
- **[tests/layer2/README.md](./tests/layer2/README.md)** - Layer 2 test ideas
- **[tests/layer3/README.md](./tests/layer3/README.md)** - Layer 3 test ideas

### External Resources

- [pyATS Documentation](https://developer.cisco.com/docs/pyats/)
- [pyATS Getting Started](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/)
- [Genie Parser Library](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/)
- [pyATS Community Forum](https://community.cisco.com/t5/pyats/bd-p/5672j-disc-pyats)

---

## 🤝 Contributing

This is a template repository - fork it and customize for your needs!

If you develop useful test patterns or improvements:
1. Keep your project-specific code in your fork
2. Consider contributing generic improvements back to the template
3. Share your experiences with the community

---

## 📝 License

See [LICENSE](./LICENSE) file for details.

---

## ✨ Features Summary

| Feature | Status |
|---------|--------|
| Layer 1 Tests | ✅ Included |
| Layer 2 Tests | 📝 Placeholder |
| Layer 3 Tests | 📝 Placeholder |
| Multi-vendor Support | ✅ Yes (IOS, XE, XR, NXOS, ASA, Junos) |
| Docker Support | ✅ Included |
| CI/CD Pipeline | ✅ GitHub Actions |
| HTML Reports | ✅ Included |
| JSON Reports | ✅ Included |
| Logging Configuration | ✅ Included |
| Environment Management | ✅ .env support |
| Documentation | ✅ Comprehensive |

---

## 🚦 Getting Started Checklist

- [ ] Clone this template for your project
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure credentials in `.env`
- [ ] Update `testbeds/testbed.yaml` with your devices
- [ ] Run example Layer 1 tests
- [ ] Review test results in HTML report
- [ ] Add your own test suites
- [ ] Integrate with your change management process
- [ ] Configure CI/CD for your repository

**Ready to validate your network? Let's go! 🚀**

For detailed instructions, see [TEMPLATE_USAGE.md](./TEMPLATE_USAGE.md).
