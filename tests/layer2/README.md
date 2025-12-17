# Layer 2 Tests

This directory is for Layer 2 (Data Link Layer) validation tests.

## Potential Test Cases

- **VLAN Configuration**: Verify VLAN assignments and trunking
- **STP/RSTP**: Validate spanning tree topology and port states
- **Port Channels/LACP**: Verify link aggregation and LACP state
- **MAC Address Tables**: Check MAC learning and table consistency
- **Storm Control**: Validate broadcast/multicast/unicast storm thresholds
- **Port Security**: Verify port security configuration and violations
- **LLDP/CDP**: Comprehensive neighbor discovery validation

## Getting Started

1. Create a test script: `test_layer2.py`
2. Create a job file in `jobs/`: `run_layer2.py`
3. Add your testbed with L2 topology in `testbeds/`
4. Follow the Layer 1 test pattern for structure

## Example Structure

```python
from pyats import aetest

class VLANValidation(aetest.Testcase):
    @aetest.test
    def check_vlan_config(self, testbed):
        # Your test logic here
        pass
```
