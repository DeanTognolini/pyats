# pyATS Layer 1 Network Validation

A comprehensive Layer 1 validation framework built on Cisco pyATS for automated network infrastructure testing. This tool validates physical layer connectivity, optical levels, error counters, speed/duplex settings, MTU configuration, and CDP neighbor relationships across your network topology.

## Features

- **Link Status Validation**: Verifies both ends of each link are operationally up
- **Optical Power Monitoring**: Validates RX power levels against SFP-specific thresholds
- **Error Detection**: Checks for interface errors (CRC, input/output errors)
- **Configuration Verification**: Validates speed, duplex, and MTU settings
- **Topology Validation**: Confirms CDP neighbors match expected topology
- **Multi-Vendor Support**: Works with IOS, IOS-XE, IOS-XR, NX-OS, ASA, and Junos
- **Containerized**: Docker support for consistent execution environments
- **HTML/JSON Reporting**: Generates detailed test reports

## Supported SFP Types

| SFP Type | RX Min (dBm) | RX Max (dBm) |
|----------|--------------|--------------|
| SFP-10G-SR | -9.5 | 2.0 |
| SFP-10G-LR | -14.4 | 0.5 |
| SFP-10G-ER | -15.8 | -1.0 |
| SFP-1G-SX | -17.0 | 0.0 |
| SFP-1G-LX | -19.0 | -3.0 |

## Prerequisites

- Python 3.11 or higher
- Network devices accessible via SSH
- Device credentials with read access to interface and CDP commands

## Quick Start

### Local Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pyats
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   export PYATS_USERNAME="your-username"
   export PYATS_PASSWORD="your-password"
   ```

4. **Configure your testbed**

   Edit `testbed.yaml` to define your network devices and topology. See [Testbed Configuration](#testbed-configuration) below.

5. **Run the tests**
   ```bash
   pyats run job layer1_job.py --testbed testbed.yaml
   ```

### Docker Installation

1. **Build the image**
   ```bash
   docker build -t pyats-layer1 .
   ```

2. **Run tests in container**
   ```bash
   docker run -it --rm \
     -v $(pwd)/testbed.yaml:/app/testbed.yaml \
     -v $(pwd)/reports:/app/reports \
     -e PYATS_USERNAME="your-username" \
     -e PYATS_PASSWORD="your-password" \
     pyats-layer1 \
     pyats run job layer1_job.py --testbed testbed.yaml --html-logs reports/
   ```

## Testbed Configuration

The `testbed.yaml` file defines your network topology. Here's the structure:

### Device Definition

```yaml
devices:
  router1:
    os: iosxe                    # Device OS: ios, iosxe, iosxr, nxos, asa, junos
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
        ip: 192.168.1.1          # Management IP
        port: 22
        # For legacy devices with older SSH algorithms:
        # ssh_options: -o KexAlgorithms=+diffie-hellman-group1-sha1 -o HostKeyAlgorithms=+ssh-rsa
```

### Topology Definition

```yaml
topology:
  router1:
    interfaces:
      GigabitEthernet1:
        type: ethernet
        link: router1-router2    # Link name (must match on both ends)
        speed: 1000              # Expected speed in Mbps (optional)
        duplex: full             # Expected duplex: full/half (optional)
        mtu: 1500                # Expected MTU (optional)
        sfp_type: SFP-10G-SR     # SFP type for optical checks (optional)
```

**Important**: The `link` name must be identical on both sides of a connection to create a link relationship.

## Usage Examples

### Run all tests
```bash
pyats run job layer1_job.py --testbed testbed.yaml
```

### Run with HTML report
```bash
pyats run job layer1_job.py --testbed testbed.yaml --html-logs ./reports/
```

### Run with JSON output
```bash
pyats run job layer1_job.py --testbed testbed.yaml --json-logs ./reports/
```

### Run specific test case
```bash
python layer1_tests.py --testbed testbed.yaml
```

### Debug mode
```bash
pyats run job layer1_job.py --testbed testbed.yaml --loglevel DEBUG
```

## Test Cases

### 1. Link Status Check
- **Purpose**: Verify all links are operationally up
- **Criteria**: Both ends must show status "up" and line protocol "up"
- **Failure Example**: `router1-router2: router1:Gi1 is up/down`

### 2. Optical Levels Check
- **Purpose**: Validate RX power within acceptable thresholds
- **Criteria**: RX power must be within min/max range for the SFP type
- **Failure Example**: `router1-router2: router1:Gi1 RX -12.3 dBm (expected -9.5 to 2.0)`
- **Note**: Only runs on interfaces with `sfp_type` defined

### 3. Interface Errors Check
- **Purpose**: Detect any interface errors
- **Criteria**: Zero input errors, output errors, and CRC errors
- **Failure Example**: `router1-router2: router1:Gi1 [45 in, 12 CRC]`

### 4. Speed/Duplex Check
- **Purpose**: Verify speed and duplex match expected values
- **Criteria**: Actual values must match topology definition
- **Failure Example**: `router1-router2: router1:Gi1 [speed 100 != 1000]`
- **Note**: Only runs on interfaces with `speed` or `duplex` defined

### 5. MTU Check
- **Purpose**: Verify MTU matches expected value
- **Criteria**: Actual MTU must match topology definition
- **Failure Example**: `router1-router2: router1:Gi1 MTU 1400 != 1500`
- **Note**: Only runs on interfaces with `mtu` defined

### 6. CDP Check
- **Purpose**: Validate CDP neighbors match topology
- **Criteria**: CDP neighbor device and port must match expected topology
- **Failure Example**: `router1-router2: router1:Gi1 CDP neighbor sw1 != router2`
- **Note**: Only runs on point-to-point links (2 interfaces)

## Understanding Test Results

### Pass Example
```
2025-12-17T12:00:00: %AETEST-INFO: +------------------------------------------------------------------------------+
2025-12-17T12:00:00: %AETEST-INFO: |                          Starting section setup                           |
2025-12-17T12:00:00: %AETEST-INFO: +------------------------------------------------------------------------------+
2025-12-17T12:00:00: %AETEST-INFO: The result of section setup is => PASSED

2025-12-17T12:00:01: %AETEST-INFO: +------------------------------------------------------------------------------+
2025-12-17T12:00:01: %AETEST-INFO: |                      Starting test check_link_status                      |
2025-12-17T12:00:01: %AETEST-INFO: +------------------------------------------------------------------------------+
2025-12-17T12:00:05: %AETEST-INFO: Passed reason: All 2 links are up/up
2025-12-17T12:00:05: %AETEST-INFO: The result of test check_link_status is => PASSED
```

### Failure Example
```
2025-12-17T12:00:10: %AETEST-INFO: +------------------------------------------------------------------------------+
2025-12-17T12:00:10: %AETEST-INFO: |                   Starting test check_link_optical_levels                 |
2025-12-17T12:00:10: %AETEST-INFO: +------------------------------------------------------------------------------+
2025-12-17T12:00:15: %AETEST-ERROR: Failed reason: Optical levels out of range: router1-router2: router1:GigabitEthernet1 RX -12.5 dBm (expected -9.5 to 2.0)
2025-12-17T12:00:15: %AETEST-INFO: The result of test check_link_optical_levels is => FAILED
```

## CI/CD Integration

This repository includes GitHub Actions workflows for automated testing:

- **PR Validation**: Runs on all pull requests to validate changes
- **Scheduled Testing**: Can run on a schedule for continuous monitoring
- **Test Reports**: Generates and uploads HTML reports as artifacts

See `.github/workflows/pyats-validation.yml` for configuration.

## Project Structure

```
.
├── layer1_job.py           # pyATS job file (entry point)
├── layer1_tests.py         # Test suite with all validation logic
├── testbed.yaml            # Network topology definition
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore patterns
├── logging_config.yaml     # Logging configuration
└── reports/                # Test reports directory (created at runtime)
```

## Troubleshooting

### Connection Issues

**Problem**: `ConnectionError: Failed to connect to device`

**Solutions**:
- Verify IP address and port in testbed.yaml
- Check network connectivity: `ping <device-ip>`
- Verify SSH is enabled on the device
- Check credentials are correct
- For legacy devices, add SSH options (see testbed.yaml template)

### Parser Errors

**Problem**: `ParserNotFound: Could not find parser for command`

**Solutions**:
- Verify the OS type is correct in testbed.yaml
- Update pyATS to the latest version: `pip install -U pyats[full]`
- Check device is running a supported OS version

### Authentication Failures

**Problem**: `Authentication failed`

**Solutions**:
- Verify environment variables are set: `echo $PYATS_USERNAME`
- Check credentials have proper permissions
- Try connecting manually via SSH to verify credentials

### Missing Optical Data

**Problem**: Tests skip optical checks even with `sfp_type` defined

**Solutions**:
- Verify the command `show controllers optics <interface>` works on your device
- Some devices use different commands - check pyATS parser support
- Ensure the interface actually has an SFP installed

## Advanced Configuration

### Custom Logging

Edit `logging_config.yaml` to customize log levels and formats:

```yaml
loggers:
  pyats:
    level: INFO
  unicon:
    level: WARNING
```

### Parallel Execution

Run tests across multiple devices in parallel:

```bash
pyats run job layer1_job.py --testbed testbed.yaml --max-workers 5
```

### Custom Thresholds

To modify optical thresholds, edit `SFP_THRESHOLDS` in `layer1_tests.py`:

```python
SFP_THRESHOLDS = {
    'CUSTOM-SFP': {'rx_min': -10.0, 'rx_max': 3.0},
}
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-feature`
3. Make your changes and add tests
4. Run the test suite to ensure everything passes
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/my-new-feature`
7. Submit a pull request

## License

See LICENSE file for details.

## Resources

- [pyATS Documentation](https://developer.cisco.com/docs/pyats/)
- [pyATS Getting Started Guide](https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/)
- [Genie Parser Documentation](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/)
- [Unicon Connection Library](https://developer.cisco.com/docs/unicon/)

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the pyATS community forums
