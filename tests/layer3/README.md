# Layer 3 Tests

This directory is for Layer 3 (Network Layer) validation tests.

## Available Test Suites

### MPLS Core Tests (`test_mpls_core.py`)

Comprehensive MPLS core network validation including:

1. **LDP Neighbor Verification** - Validates LDP neighbor adjacencies are operational
2. **OSPF Neighbor Verification** - Checks OSPF neighbors are in FULL state
3. **P Router Loopback Connectivity** - Tests reachability to P router loopbacks
4. **LSP Path Verification** - Validates LSP establishment for critical destinations

### OSPF Health Tests (`test_ospf_health.py`)

Comprehensive OSPF health and parameter validation including:

1. **OspfProcessHealth** - Verifies OSPF process is running and healthy
   - Process existence and configuration
   - Router ID validation
   - SPF timing analysis

2. **OspfNeighborHealth** - Validates OSPF neighbor relationships
   - Neighbor state verification (FULL state)
   - Dead timer monitoring
   - Missing neighbor detection

3. **OspfInterfaceHealth** - Checks OSPF interface status
   - Interface operational state
   - Interface cost validation
   - Expected interface presence

4. **OspfDatabaseHealth** - Validates OSPF database consistency
   - LSA presence verification
   - OSPF area validation
   - Database population check

5. **OspfRouteHealth** - Verifies OSPF routes in routing table
   - Expected route presence
   - Minimum route count validation

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
      critical_lsps:                   # LSP destinations that must be established (optional)
        - 10.0.0.4
        - 10.0.0.5

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
| `PE` | Provider Edge router | LDP, OSPF, LSP paths, loopback connectivity |
| `P` | Provider (core) router | LDP, OSPF, loopback connectivity |
| `P-PE` | Combined P and PE functions | All MPLS tests |

### Running MPLS Tests

```bash
# Run MPLS tests via job file
pyats run job jobs/run_mpls.py --testbed testbeds/mpls_testbed.yaml

# Run MPLS test directly
pyats run testscript tests/layer3/test_mpls_core.py --testbed testbeds/mpls_testbed.yaml

# With HTML reports
pyats run job jobs/run_mpls.py --testbed testbeds/mpls_testbed.yaml --html-logs ./reports/
```

## OSPF Health Test Configuration

### Required Testbed Custom Attributes

For OSPF health tests, devices should have the following custom attributes defined:

```yaml
devices:
  CORE1:
    custom:
      ospf_enabled: true              # Explicitly mark as OSPF-enabled (optional if ospf_neighbors defined)
      ospf_process_id: "1"            # Expected OSPF process ID (optional)
      ospf_router_id: "10.0.0.1"      # Expected OSPF router ID (optional)
      ospf_neighbors:                  # Expected OSPF neighbor IPs (required for neighbor tests)
        - 192.168.1.2
        - 192.168.2.2
      ospf_interfaces:                 # Expected OSPF-enabled interfaces (optional)
        - GigabitEthernet0/0
        - GigabitEthernet0/1
        - Loopback0
      ospf_areas:                      # Expected OSPF areas (optional)
        - "0.0.0.0"
      ospf_expected_routes:            # Routes expected via OSPF (optional)
        - 10.0.0.2/32
        - 172.16.0.0/24
      ospf_min_route_count: 10         # Minimum expected OSPF routes (optional)
      ospf_interface_costs:            # Expected interface costs (optional)
        GigabitEthernet0/0: 1
        GigabitEthernet0/1: 10
```

### Running OSPF Health Tests

```bash
# Run OSPF tests via job file
pyats run job jobs/run_ospf.py --testbed testbeds/ospf_testbed.yaml

# Run OSPF health test directly
pyats run testscript tests/layer3/test_ospf_health.py --testbed testbeds/ospf_testbed.yaml

# With HTML reports
pyats run job jobs/run_ospf.py --testbed testbeds/ospf_testbed.yaml --html-logs ./reports/
```

### OSPF Test Descriptions

| Testcase | Description | Key Validations |
|----------|-------------|-----------------|
| `OspfProcessHealth` | Process status validation | Process running, router ID, SPF timing |
| `OspfNeighborHealth` | Neighbor relationship check | FULL state, dead timers |
| `OspfInterfaceHealth` | Interface status check | Operational state, costs |
| `OspfDatabaseHealth` | Database consistency | LSA presence, area configuration |
| `OspfRouteHealth` | Route table validation | Expected routes, route count |

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
