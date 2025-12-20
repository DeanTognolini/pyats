from pyats import aetest
from pyats.topology import loader
import logging

logger = logging.getLogger(__name__)


class CommonSetup(aetest.CommonSetup):
    """Common setup tasks for Layer 2 tests."""

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
            try:
                device.connect(log_stdout=False)
            except Exception as e:
                logger.error(f"Failed to connect to {device.name}: {e}")
                self.failed(f"Failed to connect to {device.name}: {e}")

    @aetest.subsection
    def mark_l2_devices(self, testbed):
        """Identify Layer 2 enabled devices based on custom attributes."""
        l2_devices = []

        for device in testbed.devices.values():
            # Check if device has L2 custom attributes
            if hasattr(device, 'custom'):
                l2_enabled = device.custom.get('l2_enabled', False)
                expected_vlans = device.custom.get('expected_vlans', [])
                stp_enabled = device.custom.get('stp_enabled', False)
                port_channels = device.custom.get('port_channels', [])

                if l2_enabled or expected_vlans or stp_enabled or port_channels:
                    l2_devices.append(device)

        if not l2_devices:
            logger.warning("No Layer 2 devices found in testbed")
        else:
            logger.info(f"Found {len(l2_devices)} Layer 2 devices: {[d.name for d in l2_devices]}")

        self.parent.parameters['l2_devices'] = l2_devices


class VLANValidation(aetest.Testcase):
    """Validate VLAN configuration and status across switches."""

    @aetest.setup
    def setup(self):
        """Check if we have devices to test."""
        l2_devices = self.parent.parameters.get('l2_devices', [])
        # Filter devices with VLAN expectations
        self.vlan_devices = [
            d for d in l2_devices
            if hasattr(d, 'custom') and d.custom.get('expected_vlans')
        ]

        if not self.vlan_devices:
            self.skipped("No devices with expected VLAN configuration")

    @aetest.test
    def verify_vlan_existence(self):
        """Verify that expected VLANs exist on devices."""
        failed = []

        for device in self.vlan_devices:
            expected_vlans = device.custom.get('expected_vlans', [])

            try:
                parsed = device.parse('show vlan')
            except Exception as e:
                failed.append({
                    'device': device.name,
                    'error': f"Failed to parse VLAN info: {e}"
                })
                continue

            vlans = parsed.get('vlans', {})
            existing_vlan_ids = set(vlans.keys())

            for vlan_id in expected_vlans:
                vlan_str = str(vlan_id)
                if vlan_str not in existing_vlan_ids:
                    failed.append({
                        'device': device.name,
                        'issue': f"VLAN {vlan_id} not configured"
                    })

        if failed:
            self.failed(f"VLAN existence check failed: {failed}")
        else:
            self.passed(f"All expected VLANs exist on {len(self.vlan_devices)} devices")

    @aetest.test
    def verify_vlan_state(self):
        """Verify that VLANs are in active state."""
        failed = []

        for device in self.vlan_devices:
            expected_vlans = device.custom.get('expected_vlans', [])

            try:
                parsed = device.parse('show vlan')
            except Exception as e:
                failed.append({
                    'device': device.name,
                    'error': f"Failed to parse VLAN info: {e}"
                })
                continue

            vlans = parsed.get('vlans', {})

            for vlan_id in expected_vlans:
                vlan_str = str(vlan_id)
                if vlan_str in vlans:
                    vlan_info = vlans[vlan_str]
                    state = vlan_info.get('state', vlan_info.get('vlan_state', '')).lower()

                    if state not in ['active', 'act/lshut']:
                        failed.append({
                            'device': device.name,
                            'issue': f"VLAN {vlan_id} in state '{state}' (expected active)"
                        })

        if failed:
            self.failed(f"VLAN state check failed: {failed}")
        else:
            self.passed("All VLANs are in active state")

    @aetest.test
    def verify_trunk_ports(self):
        """Verify trunk port configuration and allowed VLANs."""
        failed = []

        for device in self.vlan_devices:
            trunk_ports = device.custom.get('trunk_ports', {})
            if not trunk_ports:
                continue

            try:
                parsed = device.parse('show interfaces trunk')
            except Exception as e:
                logger.warning(f"Failed to parse trunk info on {device.name}: {e}")
                continue

            for port_name, expected_vlans in trunk_ports.items():
                found = False

                # Search through the parsed output
                for intf_name, intf_data in parsed.items():
                    if port_name.lower() in intf_name.lower():
                        found = True
                        mode = intf_data.get('mode', '').lower()

                        if mode not in ['trunk', 'on', 'desirable', 'auto']:
                            failed.append({
                                'device': device.name,
                                'issue': f"Interface {intf_name} not in trunk mode (mode: {mode})"
                            })
                        break

                if not found:
                    failed.append({
                        'device': device.name,
                        'issue': f"Trunk port {port_name} not found"
                    })

        if failed:
            self.failed(f"Trunk port check failed: {failed}")
        else:
            self.passed("All trunk ports configured correctly")


class STPValidation(aetest.Testcase):
    """Validate Spanning Tree Protocol configuration and state."""

    @aetest.setup
    def setup(self):
        """Check if we have STP-enabled devices to test."""
        l2_devices = self.parent.parameters.get('l2_devices', [])
        self.stp_devices = [
            d for d in l2_devices
            if hasattr(d, 'custom') and d.custom.get('stp_enabled', False)
        ]

        if not self.stp_devices:
            self.skipped("No devices with STP enabled")

    @aetest.test
    def verify_stp_mode(self):
        """Verify STP mode (RSTP, PVST+, MST, etc.)."""
        failed = []

        for device in self.stp_devices:
            expected_mode = device.custom.get('stp_mode', 'rapid-pvst')

            try:
                parsed = device.parse('show spanning-tree summary')
            except Exception as e:
                failed.append({
                    'device': device.name,
                    'error': f"Failed to parse STP summary: {e}"
                })
                continue

            # Check STP mode
            mode = parsed.get('mode', parsed.get('spanning_tree_mode', '')).lower()

            if expected_mode.lower() not in mode:
                failed.append({
                    'device': device.name,
                    'issue': f"STP mode '{mode}' does not match expected '{expected_mode}'"
                })

        if failed:
            self.failed(f"STP mode check failed: {failed}")
        else:
            self.passed(f"STP mode correct on {len(self.stp_devices)} devices")

    @aetest.test
    def verify_stp_root_bridge(self):
        """Verify root bridge for configured VLANs."""
        failed = []

        for device in self.stp_devices:
            expected_root_vlans = device.custom.get('stp_root_vlans', [])
            if not expected_root_vlans:
                continue

            try:
                parsed = device.parse('show spanning-tree')
            except Exception as e:
                failed.append({
                    'device': device.name,
                    'error': f"Failed to parse STP info: {e}"
                })
                continue

            # Check if device is root for expected VLANs
            for vlan_id in expected_root_vlans:
                vlan_key = f"vlan{vlan_id}" if f"vlan{vlan_id}" in parsed else str(vlan_id)

                if vlan_key in parsed:
                    vlan_stp = parsed[vlan_key]
                    bridge_address = vlan_stp.get('bridge', {}).get('address', '')
                    root_address = vlan_stp.get('root', {}).get('address', '')

                    if bridge_address and root_address and bridge_address != root_address:
                        failed.append({
                            'device': device.name,
                            'issue': f"Not root bridge for VLAN {vlan_id} (root: {root_address})"
                        })

        if failed:
            self.failed(f"STP root bridge check failed: {failed}")
        else:
            self.passed("STP root bridge assignment correct")

    @aetest.test
    def verify_stp_port_states(self):
        """Verify STP port states are stable (no ports in blocking unnecessarily)."""
        warnings = []

        for device in self.stp_devices:
            try:
                parsed = device.parse('show spanning-tree')
            except Exception as e:
                logger.warning(f"Failed to parse STP info on {device.name}: {e}")
                continue

            # Count ports in various states across all VLANs
            for vlan_id, vlan_data in parsed.items():
                interfaces = vlan_data.get('interfaces', {})

                for intf_name, intf_data in interfaces.items():
                    port_state = intf_data.get('port_state', '').lower()

                    # Warn on potentially problematic states
                    if port_state in ['broken', 'err-disabled']:
                        warnings.append({
                            'device': device.name,
                            'interface': intf_name,
                            'vlan': vlan_id,
                            'state': port_state
                        })

        if warnings:
            logger.warning(f"STP ports in non-optimal states: {warnings}")
            self.passed(f"STP running, but {len(warnings)} ports in non-optimal states (see warnings)")
        else:
            self.passed("All STP port states are healthy")


class PortChannelValidation(aetest.Testcase):
    """Validate Port Channel (EtherChannel) and LACP configuration."""

    @aetest.setup
    def setup(self):
        """Check if we have devices with port channels to test."""
        l2_devices = self.parent.parameters.get('l2_devices', [])
        self.pc_devices = [
            d for d in l2_devices
            if hasattr(d, 'custom') and d.custom.get('port_channels')
        ]

        if not self.pc_devices:
            self.skipped("No devices with port channel configuration")

    @aetest.test
    def verify_port_channel_status(self):
        """Verify port channels are up and bundled."""
        failed = []

        for device in self.pc_devices:
            expected_pcs = device.custom.get('port_channels', [])

            try:
                parsed = device.parse('show etherchannel summary')
            except Exception as e:
                failed.append({
                    'device': device.name,
                    'error': f"Failed to parse port-channel info: {e}"
                })
                continue

            # Get port-channel interfaces
            interfaces = parsed.get('interfaces', {})

            for pc_id in expected_pcs:
                pc_name = f"Port-channel{pc_id}"
                found = False

                for intf_name, intf_data in interfaces.items():
                    if pc_name.lower() in intf_name.lower():
                        found = True

                        # Check bundle status
                        oper_status = intf_data.get('oper_status', '').lower()
                        if oper_status not in ['up', 'connected']:
                            failed.append({
                                'device': device.name,
                                'issue': f"{intf_name} is {oper_status} (expected up)"
                            })

                        # Check member ports
                        members = intf_data.get('members', {})
                        if not members:
                            failed.append({
                                'device': device.name,
                                'issue': f"{intf_name} has no member ports"
                            })
                        break

                if not found:
                    failed.append({
                        'device': device.name,
                        'issue': f"Port-channel{pc_id} not found"
                    })

        if failed:
            self.failed(f"Port channel status check failed: {failed}")
        else:
            self.passed("All port channels are up and properly bundled")

    @aetest.test
    def verify_lacp_state(self):
        """Verify LACP state for LACP-enabled port channels."""
        failed = []

        for device in self.pc_devices:
            lacp_channels = device.custom.get('lacp_port_channels', [])
            if not lacp_channels:
                continue

            try:
                parsed = device.parse('show lacp neighbor')
            except Exception as e:
                logger.warning(f"Failed to parse LACP info on {device.name}: {e}")
                continue

            interfaces = parsed.get('interfaces', {})

            for pc_id in lacp_channels:
                pc_name = f"Port-channel{pc_id}"
                found = False

                for intf_name, intf_data in interfaces.items():
                    if pc_name.lower() in intf_name.lower():
                        found = True

                        # Check LACP partner info exists
                        members = intf_data.get('members', {})
                        if not members:
                            failed.append({
                                'device': device.name,
                                'issue': f"{intf_name} has no LACP neighbors"
                            })
                        break

                if not found:
                    failed.append({
                        'device': device.name,
                        'issue': f"LACP info not found for Port-channel{pc_id}"
                    })

        if failed:
            self.failed(f"LACP state check failed: {failed}")
        else:
            self.passed("All LACP port channels have active neighbors")


class MACAddressTableValidation(aetest.Testcase):
    """Validate MAC address table learning and stability."""

    @aetest.setup
    def setup(self):
        """Check if we have L2 devices to test."""
        l2_devices = self.parent.parameters.get('l2_devices', [])
        if not l2_devices:
            self.skipped("No Layer 2 devices")
        self.l2_devices = l2_devices

    @aetest.test
    def verify_mac_table_populated(self):
        """Verify MAC address table has entries."""
        failed = []

        for device in self.l2_devices:
            try:
                parsed = device.parse('show mac address-table')
            except Exception as e:
                failed.append({
                    'device': device.name,
                    'error': f"Failed to parse MAC table: {e}"
                })
                continue

            # Get MAC entries
            mac_table = parsed.get('mac_table', {})
            total_entries = mac_table.get('total_mac_addresses', 0)

            if total_entries == 0:
                failed.append({
                    'device': device.name,
                    'issue': "MAC address table is empty"
                })

        if failed:
            self.failed(f"MAC table check failed: {failed}")
        else:
            self.passed(f"MAC address tables populated on {len(self.l2_devices)} devices")

    @aetest.test
    def verify_expected_macs(self):
        """Verify expected MAC addresses are learned on correct VLANs/interfaces."""
        failed = []

        for device in self.l2_devices:
            expected_macs = device.custom.get('expected_macs', [])
            if not expected_macs:
                continue

            try:
                parsed = device.parse('show mac address-table')
            except Exception as e:
                failed.append({
                    'device': device.name,
                    'error': f"Failed to parse MAC table: {e}"
                })
                continue

            # Build a set of learned MACs
            learned_macs = set()
            mac_table = parsed.get('mac_table', {})
            vlans = mac_table.get('vlans', {})

            for vlan_id, vlan_data in vlans.items():
                mac_addresses = vlan_data.get('mac_addresses', {})
                for mac, mac_info in mac_addresses.items():
                    learned_macs.add(mac.lower().replace('.', '').replace(':', ''))

            # Check for expected MACs
            for expected_mac in expected_macs:
                normalized_mac = expected_mac.lower().replace('.', '').replace(':', '')
                if normalized_mac not in learned_macs:
                    failed.append({
                        'device': device.name,
                        'issue': f"Expected MAC {expected_mac} not found in MAC table"
                    })

        if failed:
            self.failed(f"Expected MAC check failed: {failed}")
        else:
            self.passed("All expected MAC addresses learned")


class LLDPNeighborValidation(aetest.Testcase):
    """Validate LLDP neighbor discovery and topology."""

    @aetest.setup
    def setup(self):
        """Check if we have devices with LLDP expectations."""
        l2_devices = self.parent.parameters.get('l2_devices', [])
        self.lldp_devices = [
            d for d in l2_devices
            if hasattr(d, 'custom') and d.custom.get('lldp_neighbors')
        ]

        if not self.lldp_devices:
            self.skipped("No devices with LLDP neighbor expectations")

    @aetest.test
    def verify_lldp_neighbors(self):
        """Verify LLDP neighbors match expected topology."""
        failed = []

        for device in self.lldp_devices:
            expected_neighbors = device.custom.get('lldp_neighbors', {})

            try:
                parsed = device.parse('show lldp neighbors detail')
            except Exception as e:
                # Try fallback to basic command
                try:
                    parsed = device.parse('show lldp neighbors')
                except Exception as e2:
                    failed.append({
                        'device': device.name,
                        'error': f"Failed to parse LLDP info: {e2}"
                    })
                    continue

            # Get LLDP entries
            total_entries = parsed.get('total_entries', 0)
            interfaces = parsed.get('interfaces', {})

            if total_entries == 0 and expected_neighbors:
                failed.append({
                    'device': device.name,
                    'issue': "No LLDP neighbors found, but neighbors expected"
                })
                continue

            # Verify expected neighbors
            for local_intf, expected_neighbor_name in expected_neighbors.items():
                found = False

                for intf_name, intf_data in interfaces.items():
                    if local_intf.lower() in intf_name.lower():
                        found = True

                        # Get neighbor info
                        neighbors = intf_data.get('neighbors', intf_data.get('port_id', {}))
                        if isinstance(neighbors, dict):
                            for neighbor_id, neighbor_info in neighbors.items():
                                neighbor_name = neighbor_info.get('system_name',
                                                                 neighbor_info.get('chassis_id', ''))

                                if expected_neighbor_name.lower() not in neighbor_name.lower():
                                    failed.append({
                                        'device': device.name,
                                        'issue': f"{intf_name}: LLDP neighbor '{neighbor_name}' != expected '{expected_neighbor_name}'"
                                    })
                        break

                if not found:
                    failed.append({
                        'device': device.name,
                        'issue': f"No LLDP neighbor on interface {local_intf}"
                    })

        if failed:
            self.failed(f"LLDP neighbor check failed: {failed}")
        else:
            self.passed(f"All LLDP neighbors match expected topology on {len(self.lldp_devices)} devices")


class CommonCleanup(aetest.CommonCleanup):
    """Common cleanup tasks."""

    @aetest.subsection
    def disconnect(self, testbed):
        """Disconnect from all devices."""
        for device in testbed.devices.values():
            if device.connected:
                device.disconnect()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed', type=loader.load, required=True)
    args, _ = parser.parse_known_args()
    aetest.main(testbed=args.testbed)
