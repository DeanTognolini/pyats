# Layer 3 Tests

This directory is for Layer 3 (Network Layer) validation tests.

## Potential Test Cases

- **Routing Tables**: Verify routing table entries and next-hops
- **BGP**: Validate BGP peering, route advertisements, and attributes
- **OSPF**: Check OSPF neighbors, areas, and LSDBs
- **EIGRP**: Verify EIGRP neighbors and topology tables
- **Static Routes**: Validate static routing configuration
- **VRF**: Verify VRF configuration and route leaking
- **Route Redistribution**: Check redistribution between protocols
- **Prefix Lists/Route Maps**: Validate routing policies
- **IP Reachability**: Ping/traceroute tests between endpoints

## Getting Started

1. Create a test script: `test_layer3.py` or separate files per protocol
2. Create job files in `jobs/` as needed
3. Add your testbed with L3 topology in `testbeds/`
4. Consider creating subdirectories for complex setups:
   - `layer3/bgp/`
   - `layer3/ospf/`
   - `layer3/eigrp/`

## Example Structure

```python
from pyats import aetest

class BGPValidation(aetest.Testcase):
    @aetest.test
    def check_bgp_neighbors(self, testbed):
        # Your test logic here
        pass
```
