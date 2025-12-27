# Layer 2 Tests

This directory contains validation tests for Layer 2 (Data Link Layer) protocols and configurations.

## Available Test Suites

### 1. Spanning Tree Protocol (STP)
**File:** `test_stp.py`

This suite validates the stability and configuration of the Spanning Tree Protocol across all switches in the testbed.

- **Global Status**: Verifies STP is enabled and reports the mode (e.g., MST, PVST, RPVST).
- **Root Bridge**: Checks that a root bridge is identified for each instance/VLAN and logs root priority/MAC.
- **Interface States**: Validates that interfaces have valid STP roles (Root, Designated, Alternate) and statuses (Forwarding, Blocking, Learning).

## Usage

### Running Layer 2 Tests
You can execute the full Layer 2 suite using the provided job file:

```bash
pyats run job jobs/run_layer2.py --testbed testbeds/testbed.yaml
```

### Running Specific STP Tests
To run just the STP test file directly:

```bash
python tests/layer2/test_stp.py --testbed testbeds/testbed.yaml
```

## Future Test Cases

We plan to add the following validations in the future:

- **VLAN Configuration**: Verify VLAN assignments and trunking
- **Port Channels/LACP**: Verify link aggregation and LACP state
- **MAC Address Tables**: Check MAC learning and table consistency
- **Storm Control**: Validate broadcast/multicast/unicast storm thresholds
- **Port Security**: Verify port security configuration and violations
- **LLDP/CDP**: Comprehensive neighbor discovery validation (Basic CDP check exists in Layer 1)
