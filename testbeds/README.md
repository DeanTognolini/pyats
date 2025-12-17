# Testbed Files

This directory contains pyATS testbed files that define your network topology and device connections.

## Overview

Testbed files are YAML documents that describe:
- **Devices**: Network equipment with connection details
- **Topology**: How devices are interconnected
- **Credentials**: Authentication information (use environment variables)
- **Custom Attributes**: Test-specific metadata (SFP types, expected values, etc.)

## Files

- `testbed.yaml` - Example testbed with Layer 1 topology
- Add your own testbed files here for different projects

## Best Practices

1. **One testbed per project**: Clone this repo for each network project
2. **Use environment variables**: Never hardcode credentials
3. **Document topology**: Add comments explaining the network design
4. **Version control**: Track testbed changes with git
5. **Naming convention**: Use descriptive names (e.g., `datacenter-core.yaml`, `branch-routers.yaml`)

## Template Structure

```yaml
devices:
  device-name:
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
  device-name:
    interfaces:
      GigabitEthernet1:
        link: device1-device2
        # Layer 1 test attributes
        speed: 1000              # Expected interface speed (Mbps)
        duplex: full             # Expected duplex mode (full/half)
        mtu: 1500                # Expected MTU size
        sfp_type: SFP-10G-SR     # SFP type for optical threshold validation
```

## Custom Attributes for Layer 1 Tests

The Layer 1 test suite uses custom attributes defined in the topology section to validate interface configurations and optical levels.

### Interface Attributes

| Attribute | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `link` | string | **Yes** | Link name (must match on both ends) | `router1-router2` |
| `speed` | integer | No | Expected interface speed in Mbps | `1000`, `10000`, `100000` |
| `duplex` | string | No | Expected duplex mode | `full`, `half` |
| `mtu` | integer | No | Expected MTU size in bytes | `1500`, `9000` |
| `sfp_type` | string | No | SFP module type for optical validation | `SFP-10G-SR`, `SFP-1G-LX` |

### SFP Types and Optical Thresholds

The `sfp_type` attribute enables optical power level validation. When specified, the Layer 1 tests will check that the RX (receive) optical power falls within the acceptable range for that SFP type.

**Supported SFP Types:**

| SFP Type | Technology | RX Min (dBm) | RX Max (dBm) | Typical Distance |
|----------|------------|--------------|--------------|------------------|
| `SFP-10G-SR` | 10G Short Range | -9.5 | 2.0 | 300m MMF |
| `SFP-10G-LR` | 10G Long Range | -14.4 | 0.5 | 10km SMF |
| `SFP-10G-ER` | 10G Extended Range | -15.8 | -1.0 | 40km SMF |
| `SFP-1G-SX` | 1G Short Range | -17.0 | 0.0 | 550m MMF |
| `SFP-1G-LX` | 1G Long Range | -19.0 | -3.0 | 10km SMF |

**Example with SFP Types:**

```yaml
topology:
  core-router-1:
    interfaces:
      TenGigabitEthernet1/0/1:
        link: core1-core2-10g
        speed: 10000
        duplex: full
        mtu: 9000
        sfp_type: SFP-10G-LR      # Long range 10G fiber

      GigabitEthernet1/0/10:
        link: core1-access1
        speed: 1000
        duplex: full
        mtu: 1500
        sfp_type: SFP-1G-SX       # Short range 1G fiber

  core-router-2:
    interfaces:
      TenGigabitEthernet1/0/1:
        link: core1-core2-10g
        speed: 10000
        duplex: full
        mtu: 9000
        sfp_type: SFP-10G-LR      # Must match on both ends
```

**How Optical Validation Works:**

1. Test reads the `sfp_type` from the interface definition
2. Looks up the min/max RX power thresholds for that SFP type
3. Executes `show controllers optics <interface>` on the device
4. Extracts the RX power level from the output
5. Validates: `rx_min <= actual_rx_power <= rx_max`
6. Fails if power is outside acceptable range (indicates fiber issues, distance mismatch, or failing optics)

**When to Use sfp_type:**

- ✅ Fiber optic connections where you want to validate signal strength
- ✅ Critical links where optical degradation could indicate problems
- ✅ Long-distance links where attenuation matters
- ✅ After fiber cleaning, replacement, or maintenance
- ❌ Skip for copper interfaces (not applicable)
- ❌ Skip if optical monitoring is not important for your use case

### Adding Custom SFP Types

To add support for additional SFP types, edit `tests/layer1/test_layer1.py`:

```python
SFP_THRESHOLDS = {
    'SFP-10G-SR': {'rx_min': -9.5, 'rx_max': 2.0},
    'SFP-10G-LR': {'rx_min': -14.4, 'rx_max': 0.5},
    'SFP-10G-ER': {'rx_min': -15.8, 'rx_max': -1.0},
    'SFP-1G-SX': {'rx_min': -17.0, 'rx_max': 0.0},
    'SFP-1G-LX': {'rx_min': -19.0, 'rx_max': -3.0},
    # Add your custom SFP type here:
    'QSFP-40G-SR4': {'rx_min': -10.0, 'rx_max': 2.4},
}
```

Consult your SFP vendor documentation for the correct RX power sensitivity ranges.

## See Also

- Official pyATS testbed documentation: https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html
- Testbed file examples in the main README.md
