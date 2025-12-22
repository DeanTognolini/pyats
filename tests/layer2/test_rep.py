"""
REP (Resilient Ethernet Protocol) Health Check Test Suite
==========================================================

This test suite validates REP health and parameters across network devices.

REP (Resilient Ethernet Protocol) is a Cisco proprietary Layer 2 protocol
that provides fast convergence for ring topologies, preventing loops while
maintaining backup paths.

Testcases:
    - RepSegmentHealth: Verify REP segments are operational
    - RepNeighborHealth: Verify REP neighbors are properly discovered
    - RepTopologyHealth: Verify REP topology is consistent
    - RepBlockedPortHealth: Verify appropriate ports are blocked
    - RepInterfaceHealth: Verify REP interfaces are operational

Required Custom Attributes:
    rep_enabled: bool - Whether device runs REP (default: True if rep_segment_id defined)
    rep_segment_id: int - Expected REP segment ID
    rep_interfaces: list - Expected REP-enabled interfaces
    rep_role: str - Expected REP role (edge, intermediate, primary-edge, etc.)
    rep_expected_neighbors: list - Expected REP neighbor interfaces
    rep_blocked_ports: list - Expected blocked REP ports (for edge nodes)

Example testbed configuration:
    devices:
      SW1:
        custom:
          rep_enabled: true
          rep_segment_id: 1
          rep_role: "primary-edge"
          rep_interfaces:
            - GigabitEthernet1/0/1
            - GigabitEthernet1/0/2
          rep_expected_neighbors:
            - GigabitEthernet1/0/2
          rep_blocked_ports:
            - GigabitEthernet1/0/1
"""

from pyats import aetest
from pyats.topology import loader
import logging
import re

logger = logging.getLogger(__name__)


class CommonSetup(aetest.CommonSetup):
    """Common setup tasks for REP health validation."""

    @aetest.subsection
    def check_env_vars(self):
        """Verify required environment variables exist."""
        import os
        required_vars = ['PYATS_USERNAME', 'PYATS_PASSWORD']
        missing = [var for var in required_vars if not os.environ.get(var)]
        if missing:
            self.failed(f"Missing required environment variables: {', '.join(missing)}")

    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all devices in testbed."""
        for device in testbed.devices.values():
            logger.info(f"Connecting to {device.name}...")
            try:
                device.connect(log_stdout=False)
            except Exception as e:
                logger.error(f"Failed to connect to {device.name}: {e}")
                self.failed(f"Could not connect to {device.name}")

    @aetest.subsection
    def mark_rep_devices(self, testbed):
        """Identify REP-enabled devices in the testbed."""
        self.parent.parameters['rep_devices'] = []
        for device in testbed.devices.values():
            # Device is REP-enabled if rep_enabled is True or rep_segment_id is defined
            rep_enabled = device.custom.get('rep_enabled', False)
            rep_segment_id = device.custom.get('rep_segment_id')

            if rep_enabled or rep_segment_id is not None:
                self.parent.parameters['rep_devices'].append(device)
                logger.info(f"{device.name} marked as REP-enabled device")

        if not self.parent.parameters['rep_devices']:
            logger.warning("No REP-enabled devices found in testbed")


class RepSegmentHealth(aetest.Testcase):
    """Verify REP segments are operational."""

    @aetest.setup
    def setup(self, rep_devices):
        """Verify we have REP devices to test."""
        if not rep_devices:
            self.skipped("No REP-enabled devices found in testbed")

    @aetest.test
    def verify_rep_segment(self, rep_devices):
        """Verify REP segments are configured and operational."""
        failed_devices = []

        for device in rep_devices:
            logger.info(f"Checking REP segment on {device.name}...")

            try:
                # Try to parse REP topology (pyATS may not have parser)
                # If parser not available, use execute and parse manually
                try:
                    output = device.parse('show rep topology')
                    has_parser = True
                except Exception:
                    # Fall back to execute
                    output = device.execute('show rep topology')
                    has_parser = False

                if not output:
                    failed_devices.append({
                        'device': device.name,
                        'issue': 'No REP topology output'
                    })
                    logger.error(f"{device.name}: No REP topology found!")
                    continue

                # Extract segment information
                if has_parser:
                    # Handle parsed output (structure depends on parser)
                    logger.info(f"{device.name}: REP topology retrieved (parsed)")
                else:
                    # Manual parsing of text output
                    if 'REP Segment' not in output and 'Segment' not in output:
                        failed_devices.append({
                            'device': device.name,
                            'issue': 'No REP segment found in output'
                        })
                        logger.error(f"{device.name}: No REP segment in topology output!")
                        continue

                    # Validate expected segment ID if specified
                    expected_segment_id = device.custom.get('rep_segment_id')
                    if expected_segment_id is not None:
                        segment_pattern = rf'REP\s+Segment\s+{expected_segment_id}\b'
                        if not re.search(segment_pattern, output):
                            failed_devices.append({
                                'device': device.name,
                                'issue': f'Expected REP segment {expected_segment_id} not found',
                                'output_snippet': output[:500]
                            })
                            logger.error(f"{device.name}: Expected REP segment {expected_segment_id} not found")
                            continue

                    logger.info(f"{device.name}: REP segment healthy")

            except Exception as e:
                logger.error(f"Failed to check REP segment on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"REP segment issues found: {failed_devices}")

    @aetest.test
    def verify_rep_role(self, rep_devices):
        """Verify REP role is configured correctly."""
        warning_devices = []

        for device in rep_devices:
            logger.info(f"Checking REP role on {device.name}...")

            # Get expected REP role from custom attributes
            expected_role = device.custom.get('rep_role')

            if not expected_role:
                logger.info(f"{device.name}: No expected REP role defined, skipping role check")
                continue

            try:
                output = device.execute('show rep topology')

                # Look for role indicators in output
                role_found = False
                if expected_role.lower() in ['edge', 'primary-edge']:
                    if 'Primary Edge' in output or 'Edge' in output:
                        role_found = True
                elif expected_role.lower() in ['intermediate', 'transit']:
                    if 'No' in output and 'Edge' not in output:
                        role_found = True

                if not role_found:
                    warning_devices.append({
                        'device': device.name,
                        'expected_role': expected_role,
                        'output_snippet': output[:300]
                    })
                    logger.warning(f"{device.name}: Expected REP role '{expected_role}' not clearly indicated")
                else:
                    logger.info(f"{device.name}: REP role appears correct")

            except Exception as e:
                logger.warning(f"Could not check REP role on {device.name}: {e}")

        if warning_devices:
            logger.warning(f"REP role verification warnings: {warning_devices}")


class RepNeighborHealth(aetest.Testcase):
    """Verify REP neighbor relationships are healthy."""

    @aetest.setup
    def setup(self, rep_devices):
        """Verify we have REP devices to test."""
        if not rep_devices:
            self.skipped("No REP-enabled devices found in testbed")

    @aetest.test
    def verify_rep_neighbors(self, rep_devices):
        """Verify all expected REP neighbors are discovered."""
        failed_devices = []

        for device in rep_devices:
            logger.info(f"Checking REP neighbors on {device.name}...")

            # Get expected REP neighbors from custom attributes
            expected_neighbors = device.custom.get('rep_expected_neighbors', [])

            if not expected_neighbors:
                logger.info(f"{device.name}: No expected REP neighbors defined, checking for any neighbors")

            try:
                output = device.execute('show rep topology')

                # Extract neighbor information from output
                # Look for interface names in the topology
                discovered_neighbors = []

                # Parse for common interface patterns
                interface_patterns = [
                    r'(GigabitEthernet[\d/]+)',
                    r'(Gi[\d/]+)',
                    r'(TenGigabitEthernet[\d/]+)',
                    r'(Te[\d/]+)',
                    r'(Port-channel\d+)',
                    r'(Po\d+)'
                ]

                for pattern in interface_patterns:
                    matches = re.findall(pattern, output)
                    discovered_neighbors.extend(matches)

                # Remove duplicates
                discovered_neighbors = list(set(discovered_neighbors))

                # Normalize interface names for comparison
                def normalize_interface(intf):
                    """Normalize interface name for comparison."""
                    intf = intf.lower()
                    intf = intf.replace('gigabitethernet', 'gi')
                    intf = intf.replace('tengigabitethernet', 'te')
                    intf = intf.replace('port-channel', 'po')
                    return intf

                normalized_discovered = [normalize_interface(i) for i in discovered_neighbors]

                # Verify expected neighbors if specified
                if expected_neighbors:
                    missing_neighbors = []
                    for expected in expected_neighbors:
                        normalized_expected = normalize_interface(expected)
                        if normalized_expected not in normalized_discovered:
                            missing_neighbors.append(expected)

                    if missing_neighbors:
                        failed_devices.append({
                            'device': device.name,
                            'missing_neighbors': missing_neighbors,
                            'discovered_neighbors': discovered_neighbors
                        })
                        logger.error(f"{device.name}: Missing REP neighbors: {missing_neighbors}")
                    else:
                        logger.info(f"{device.name}: All expected REP neighbors present")
                else:
                    # Just verify we have some neighbors
                    if not discovered_neighbors:
                        logger.warning(f"{device.name}: No REP neighbors discovered")
                    else:
                        logger.info(f"{device.name}: REP neighbors discovered: {discovered_neighbors}")

            except Exception as e:
                logger.error(f"Failed to check REP neighbors on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"REP neighbor issues found: {failed_devices}")


class RepTopologyHealth(aetest.Testcase):
    """Verify REP topology is consistent."""

    @aetest.setup
    def setup(self, rep_devices):
        """Verify we have REP devices to test."""
        if not rep_devices:
            self.skipped("No REP-enabled devices found in testbed")

    @aetest.test
    def verify_rep_topology_complete(self, rep_devices):
        """Verify REP topology is complete (no open segments)."""
        failed_devices = []

        for device in rep_devices:
            logger.info(f"Checking REP topology on {device.name}...")

            try:
                output = device.execute('show rep topology')

                # Check for topology health indicators
                if 'Open' in output and 'Segment' in output:
                    # Open segment may indicate problem
                    if re.search(r'Open\s+Segment', output):
                        failed_devices.append({
                            'device': device.name,
                            'issue': 'REP segment is open (may indicate link failure)'
                        })
                        logger.error(f"{device.name}: REP segment is open!")
                        continue

                # Check for "Complete" or "Closed" indicators
                if 'Complete' in output or 'Closed' in output or 'BLK' in output:
                    logger.info(f"{device.name}: REP topology appears complete")
                else:
                    logger.warning(f"{device.name}: REP topology status unclear")

            except Exception as e:
                logger.error(f"Failed to check REP topology on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"REP topology issues found: {failed_devices}")

    @aetest.test
    def verify_rep_segment_id(self, rep_devices):
        """Verify REP segment ID matches expected configuration."""
        failed_devices = []

        for device in rep_devices:
            logger.info(f"Checking REP segment ID on {device.name}...")

            # Get expected segment ID from custom attributes
            expected_segment_id = device.custom.get('rep_segment_id')

            if expected_segment_id is None:
                logger.info(f"{device.name}: No expected REP segment ID defined, skipping")
                continue

            try:
                output = device.execute('show rep topology')

                # Look for segment ID in output
                segment_pattern = rf'REP\s+Segment\s+{expected_segment_id}\b'
                if not re.search(segment_pattern, output, re.IGNORECASE):
                    # Also try numeric pattern
                    numeric_pattern = rf'Segment\s+{expected_segment_id}\b'
                    if not re.search(numeric_pattern, output):
                        failed_devices.append({
                            'device': device.name,
                            'expected_segment_id': expected_segment_id,
                            'output_snippet': output[:500]
                        })
                        logger.error(f"{device.name}: Expected segment ID {expected_segment_id} not found")
                        continue

                logger.info(f"{device.name}: REP segment ID {expected_segment_id} verified")

            except Exception as e:
                logger.error(f"Failed to check REP segment ID on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"REP segment ID issues found: {failed_devices}")


class RepBlockedPortHealth(aetest.Testcase):
    """Verify appropriate REP ports are blocked to prevent loops."""

    @aetest.setup
    def setup(self, rep_devices):
        """Verify we have REP devices to test."""
        if not rep_devices:
            self.skipped("No REP-enabled devices found in testbed")

    @aetest.test
    def verify_blocked_ports(self, rep_devices):
        """Verify expected ports are in blocked state."""
        issues = []

        for device in rep_devices:
            logger.info(f"Checking REP blocked ports on {device.name}...")

            # Get expected blocked ports from custom attributes
            expected_blocked = device.custom.get('rep_blocked_ports', [])

            try:
                output = device.execute('show rep topology')

                # Look for BLK (blocked) indicators
                blocked_ports = []

                # Parse for blocked port indicators
                # Format typically: "Gi1/0/1  BLK" or similar
                blk_pattern = r'((?:Gi|GigabitEthernet|Te|TenGigabitEthernet|Po|Port-channel)[\d/]+)\s+(?:BLK|BLOCKED)'
                matches = re.findall(blk_pattern, output, re.IGNORECASE)
                blocked_ports.extend(matches)

                # Normalize interface names
                def normalize_interface(intf):
                    """Normalize interface name for comparison."""
                    intf = intf.lower()
                    intf = intf.replace('gigabitethernet', 'gi')
                    intf = intf.replace('tengigabitethernet', 'te')
                    intf = intf.replace('port-channel', 'po')
                    return intf

                normalized_blocked = [normalize_interface(i) for i in blocked_ports]

                if expected_blocked:
                    # Verify expected ports are blocked
                    for expected in expected_blocked:
                        normalized_expected = normalize_interface(expected)
                        if normalized_expected not in normalized_blocked:
                            issues.append({
                                'device': device.name,
                                'issue': f'Expected blocked port {expected} not found in blocked state',
                                'blocked_ports': blocked_ports
                            })
                            logger.warning(f"{device.name}: Expected blocked port {expected} not blocked")
                        else:
                            logger.info(f"{device.name}: Port {expected} is correctly blocked")
                else:
                    # Just report what's blocked
                    if blocked_ports:
                        logger.info(f"{device.name}: Blocked ports: {blocked_ports}")
                    else:
                        # For edge nodes, we expect at least one blocked port
                        rep_role = device.custom.get('rep_role', '').lower()
                        if 'edge' in rep_role:
                            issues.append({
                                'device': device.name,
                                'issue': 'No blocked ports found on edge node (expected for loop prevention)'
                            })
                            logger.warning(f"{device.name}: Edge node with no blocked ports detected!")

            except Exception as e:
                logger.error(f"Failed to check blocked ports on {device.name}: {e}")
                issues.append({
                    'device': device.name,
                    'error': str(e)
                })

        if issues:
            logger.warning(f"REP blocked port issues: {issues}")


class RepInterfaceHealth(aetest.Testcase):
    """Verify REP interfaces are operational."""

    @aetest.setup
    def setup(self, rep_devices):
        """Verify we have REP devices to test."""
        if not rep_devices:
            self.skipped("No REP-enabled devices found in testbed")

    @aetest.test
    def verify_rep_interfaces(self, rep_devices):
        """Verify expected REP interfaces are configured and operational."""
        failed_devices = []

        for device in rep_devices:
            logger.info(f"Checking REP interfaces on {device.name}...")

            # Get expected REP interfaces from custom attributes
            expected_interfaces = device.custom.get('rep_interfaces', [])

            if not expected_interfaces:
                logger.info(f"{device.name}: No expected REP interfaces defined, checking for any REP interfaces")

            try:
                # Check interface REP status
                # Try 'show interface rep detail' or 'show rep topology'
                try:
                    output = device.execute('show interface rep detail')
                except Exception:
                    output = device.execute('show rep topology')

                if not output:
                    failed_devices.append({
                        'device': device.name,
                        'issue': 'No REP interface output'
                    })
                    logger.error(f"{device.name}: No REP interface information!")
                    continue

                # Extract interface information
                rep_interfaces = []
                interface_patterns = [
                    r'(GigabitEthernet[\d/]+)',
                    r'(Gi[\d/]+)',
                    r'(TenGigabitEthernet[\d/]+)',
                    r'(Te[\d/]+)',
                    r'(Port-channel\d+)',
                    r'(Po\d+)'
                ]

                for pattern in interface_patterns:
                    matches = re.findall(pattern, output)
                    rep_interfaces.extend(matches)

                # Remove duplicates
                rep_interfaces = list(set(rep_interfaces))

                # Normalize interface names for comparison
                def normalize_interface(intf):
                    """Normalize interface name for comparison."""
                    intf = intf.lower()
                    intf = intf.replace('gigabitethernet', 'gi')
                    intf = intf.replace('tengigabitethernet', 'te')
                    intf = intf.replace('port-channel', 'po')
                    return intf

                normalized_rep = [normalize_interface(i) for i in rep_interfaces]

                if expected_interfaces:
                    # Verify expected interfaces are present
                    missing_interfaces = []
                    for expected in expected_interfaces:
                        normalized_expected = normalize_interface(expected)
                        if normalized_expected not in normalized_rep:
                            missing_interfaces.append(expected)

                    if missing_interfaces:
                        failed_devices.append({
                            'device': device.name,
                            'missing_interfaces': missing_interfaces,
                            'found_interfaces': rep_interfaces
                        })
                        logger.error(f"{device.name}: Missing REP interfaces: {missing_interfaces}")
                    else:
                        logger.info(f"{device.name}: All expected REP interfaces present")
                else:
                    # Just verify we have some REP interfaces
                    if rep_interfaces:
                        logger.info(f"{device.name}: REP interfaces found: {rep_interfaces}")
                    else:
                        logger.warning(f"{device.name}: No REP interfaces detected")

            except Exception as e:
                logger.error(f"Failed to check REP interfaces on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"REP interface issues found: {failed_devices}")

    @aetest.test
    def verify_rep_interface_status(self, rep_devices):
        """Verify REP interfaces are in UP state."""
        failed_devices = []

        for device in rep_devices:
            logger.info(f"Checking REP interface status on {device.name}...")

            # Get expected REP interfaces
            expected_interfaces = device.custom.get('rep_interfaces', [])

            if not expected_interfaces:
                continue

            try:
                # Check each interface status
                for interface in expected_interfaces:
                    try:
                        output = device.execute(f'show interface {interface}')

                        # Check for UP status
                        if 'line protocol is up' not in output.lower():
                            failed_devices.append({
                                'device': device.name,
                                'interface': interface,
                                'issue': 'Interface not in UP state'
                            })
                            logger.error(f"{device.name}: Interface {interface} not UP")
                        else:
                            logger.info(f"{device.name}: Interface {interface} is UP")

                    except Exception as e:
                        logger.warning(f"Could not check status for {interface} on {device.name}: {e}")

            except Exception as e:
                logger.error(f"Failed to check interface status on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"REP interface status issues found: {failed_devices}")


class CommonCleanup(aetest.CommonCleanup):
    """Common cleanup tasks."""

    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        """Disconnect from all devices."""
        for device in testbed.devices.values():
            if device.connected:
                logger.info(f"Disconnecting from {device.name}...")
                device.disconnect()


if __name__ == '__main__':
    import argparse
    from pyats.topology import loader

    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed', type=loader.load)
    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))
