# Layer 3 Tests

This directory is for Layer 3 (Network Layer) validation tests.

## Available Test Suites

### MPLS Core Tests (`test_mpls_core.py`)

Comprehensive MPLS core network validation including:

1. **LDP Neighbor Verification** - Validates LDP neighbor adjacencies are operational
2. **MPLS Label Validation** - Verifies label bindings for critical prefixes
3. **OSPF Neighbor Verification** - Checks OSPF neighbors are in FULL state
4. **P Router Loopback Connectivity** - Tests reachability to P router loopbacks

## Potential Additional Test Cases

- **Routing Tables**: Verify routing table entries and next-hops
- **BGP**: Validate BGP peering, route advertisements, and attributes
- **EIGRP**: Verify EIGRP neighbors and topology tables
- **Static Routes**: Validate static routing configuration
- **VRF**: Verify VRF configuration and route leaking
- **Route Redistribution**: Check redistribution between protocols
- **Prefix Lists/Route Maps**: Validate routing policies

## MPLS Test Configuration

### Required Testbed Custom Attributes

For MPLS core tests, devices must have the following custom attributes defined:

```yaml
devices:
  PE1:
    custom:
      mpls_role: PE                    # Role: P, PE, or P-PE
      loopback0_ip: 10.0.0.1/32       # Loopback IP for connectivity tests
      ldp_neighbors:                   # Expected LDP neighbor router IDs
        - 10.0.0.2
        - 10.0.0.3
      ospf_neighbors:                  # Expected OSPF neighbor IPs
        - 192.168.1.2
        - 192.168.2.2
      critical_prefixes:               # Prefixes that must have MPLS labels (optional)
        - 10.0.0.0/24
        - 172.16.0.0/16

  P1:
    custom:
      mpls_role: P
      loopback0_ip: 10.0.0.2/32
      ldp_neighbors:
        - 10.0.0.1
        - 10.0.0.3
      ospf_neighbors:
        - 192.168.1.1
        - 192.168.3.1
```

### MPLS Roles

| Role | Description | Tests Applied |
|------|-------------|---------------|
| `PE` | Provider Edge router | LDP, OSPF, loopback connectivity |
| `P` | Provider (core) router | LDP, OSPF, labels, loopback connectivity |
| `P-PE` | Combined P and PE functions | All MPLS tests |

### Running MPLS Tests

```bash
# Run all Layer 3 tests (including MPLS)
pyats run job jobs/run_all.py --testbed testbeds/mpls_testbed.yaml

# Run only MPLS tests
pyats run job jobs/run_layer3.py --testbed testbeds/mpls_testbed.yaml

# Run MPLS test directly
pyats run testscript tests/layer3/test_mpls_core.py --testbed testbeds/mpls_testbed.yaml
```

### Test Output

Each test will report:
- ✓ **PASS**: All validations successful
- ✗ **FAIL**: Issues found with detailed error information
- ⊘ **SKIP**: Test not applicable (e.g., no MPLS routers in testbed)

Example failure output:
```
LDP neighbor issues found: [
  {
    'device': 'PE1',
    'missing': ['10.0.0.5'],
    'operational': ['10.0.0.2', '10.0.0.3']
  }
]
```

## Getting Started (Other L3 Tests)

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
