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
        # Add test-specific attributes
        speed: 1000
        duplex: full
```

## See Also

- Official pyATS testbed documentation: https://pubhub.devnetcloud.com/media/pyats-getting-started/docs/quickstart/manageconnections.html
- Testbed file examples in the main README.md
