from pyats import aetest
from pyats.topology import loader
import logging
import re

logger = logging.getLogger(__name__)


class CommonSetup(aetest.CommonSetup):
    """Common setup tasks for MPLS core validation."""

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
    def mark_mpls_routers(self, testbed):
        """Identify MPLS-enabled routers in the testbed."""
        self.parent.parameters['mpls_routers'] = []
        for device in testbed.devices.values():
            # Check if device has mpls_role custom attribute
            mpls_role = device.custom.get('mpls_role')
            if mpls_role in ['P', 'PE', 'P-PE']:
                self.parent.parameters['mpls_routers'].append(device)
                logger.info(f"{device.name} marked as MPLS {mpls_role} router")


class LdpNeighbors(aetest.Testcase):
    """Verify LDP neighbor relationships."""

    @aetest.setup
    def setup(self, mpls_routers):
        """Verify we have MPLS routers to test."""
        if not mpls_routers:
            self.skipped("No MPLS-enabled routers found in testbed")

    @aetest.test
    def verify_ldp_neighbors(self, mpls_routers):
        """Verify all expected LDP neighbors are operational."""
        failed_devices = []

        for device in mpls_routers:
            logger.info(f"Checking LDP neighbors on {device.name}...")

            # Get expected LDP neighbors from custom attributes
            expected_neighbors = device.custom.get('ldp_neighbors', [])

            if not expected_neighbors:
                logger.warning(f"{device.name} has no expected LDP neighbors defined")
                continue

            try:
                # Parse LDP neighbor output
                output = device.parse('show mpls ldp neighbor')

                # Extract operational neighbors
                operational_neighbors = []
                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'peers' in vrf_data:
                            for peer_id, peer_data in vrf_data['peers'].items():
                                # State is nested under label_space_id
                                if 'label_space_id' in peer_data:
                                    for ls_id, ls_data in peer_data['label_space_id'].items():
                                        state = ls_data.get('state', '').lower()
                                        if state == 'oper':
                                            operational_neighbors.append(peer_id)
                                            break  # Only need to check once per peer

                # Verify all expected neighbors are operational
                missing_neighbors = set(expected_neighbors) - set(operational_neighbors)

                if missing_neighbors:
                    failed_devices.append({
                        'device': device.name,
                        'missing': list(missing_neighbors),
                        'operational': operational_neighbors
                    })
                    logger.error(f"{device.name}: Missing LDP neighbors: {missing_neighbors}")
                else:
                    logger.info(f"{device.name}: All LDP neighbors operational ✓")

            except Exception as e:
                logger.error(f"Failed to check LDP neighbors on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"LDP neighbor issues found: {failed_devices}")


class MplsLabels(aetest.Testcase):
    """Verify MPLS label bindings."""

    @aetest.setup
    def setup(self, mpls_routers):
        """Verify we have MPLS routers to test."""
        if not mpls_routers:
            self.skipped("No MPLS-enabled routers found in testbed")

    @aetest.test
    def verify_label_bindings(self, mpls_routers):
        """Verify MPLS label bindings exist for critical prefixes."""
        failed_devices = []

        for device in mpls_routers:
            logger.info(f"Checking MPLS label bindings on {device.name}...")

            # Get critical prefixes that must have labels
            critical_prefixes = device.custom.get('critical_prefixes', [])

            if not critical_prefixes:
                logger.info(f"{device.name}: No critical prefixes defined, checking general MPLS forwarding")

            try:
                # Parse MPLS forwarding table
                output = device.parse('show mpls forwarding-table')

                # Check if we have any label bindings at all
                if 'vrf' not in output or not output['vrf']:
                    failed_devices.append({
                        'device': device.name,
                        'issue': 'No MPLS forwarding entries found'
                    })
                    logger.error(f"{device.name}: No MPLS forwarding entries!")
                    continue

                # If critical prefixes specified, verify they have labels
                if critical_prefixes:
                    missing_labels = []
                    for prefix in critical_prefixes:
                        found = False
                        for vrf, vrf_data in output['vrf'].items():
                            if 'local_label' in vrf_data:
                                for label, label_data in vrf_data['local_label'].items():
                                    # Key is 'outgoing_label_or_vc' in actual output
                                    outgoing_label_or_vc = label_data.get('outgoing_label_or_vc', {})
                                    for out_label, out_data in outgoing_label_or_vc.items():
                                        if 'prefix_or_tunnel_id' in out_data:
                                            # Prefix is the KEY, not a nested value
                                            for pfx in out_data['prefix_or_tunnel_id'].keys():
                                                # Match prefix with or without CIDR notation
                                                # e.g., "10.29.252.185" should match "10.29.252.185/32"
                                                if pfx.startswith(prefix.rstrip('/')):
                                                    found = True
                                                    break
                                        if found:
                                            break
                                if found:
                                    break
                            if found:
                                break

                        if not found:
                            missing_labels.append(prefix)

                    if missing_labels:
                        failed_devices.append({
                            'device': device.name,
                            'missing_labels': missing_labels
                        })
                        logger.error(f"{device.name}: Missing labels for: {missing_labels}")
                    else:
                        logger.info(f"{device.name}: All critical prefixes have labels ✓")
                else:
                    # Just verify MPLS is operational
                    logger.info(f"{device.name}: MPLS forwarding operational ✓")

            except Exception as e:
                logger.error(f"Failed to check MPLS labels on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"MPLS label issues found: {failed_devices}")


class OspfNeighbors(aetest.Testcase):
    """Verify OSPF neighbor relationships."""

    @aetest.setup
    def setup(self, mpls_routers):
        """Verify we have MPLS routers to test."""
        if not mpls_routers:
            self.skipped("No MPLS-enabled routers found in testbed")

    @aetest.test
    def verify_ospf_neighbors(self, mpls_routers):
        """Verify all expected OSPF neighbors are in FULL state."""
        failed_devices = []

        for device in mpls_routers:
            logger.info(f"Checking OSPF neighbors on {device.name}...")

            # Get expected OSPF neighbors from custom attributes
            expected_neighbors = device.custom.get('ospf_neighbors', [])

            if not expected_neighbors:
                logger.warning(f"{device.name} has no expected OSPF neighbors defined")
                continue

            try:
                # Parse OSPF neighbor output
                output = device.parse('show ip ospf neighbor')

                # Extract FULL state neighbors
                full_neighbors = []

                # Handle simple output format (interfaces -> neighbors)
                if 'interfaces' in output:
                    for intf, intf_data in output['interfaces'].items():
                        if 'neighbors' in intf_data:
                            for nbr, nbr_data in intf_data['neighbors'].items():
                                state = nbr_data.get('state', '').upper()
                                # State is typically "FULL/  -" or "FULL/DR", etc.
                                if state.startswith('FULL'):
                                    full_neighbors.append(nbr)

                # Handle complex VRF output format (for multi-VRF setups)
                elif 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'instance' in af_data:
                                    for instance, inst_data in af_data['instance'].items():
                                        if 'areas' in inst_data:
                                            for area, area_data in inst_data['areas'].items():
                                                if 'interfaces' in area_data:
                                                    for intf, intf_data in area_data['interfaces'].items():
                                                        if 'neighbors' in intf_data:
                                                            for nbr, nbr_data in intf_data['neighbors'].items():
                                                                state = nbr_data.get('state', '').upper()
                                                                if state.startswith('FULL'):
                                                                    full_neighbors.append(nbr)

                # Verify all expected neighbors are FULL
                missing_neighbors = set(expected_neighbors) - set(full_neighbors)

                if missing_neighbors:
                    failed_devices.append({
                        'device': device.name,
                        'missing': list(missing_neighbors),
                        'full_neighbors': full_neighbors
                    })
                    logger.error(f"{device.name}: Missing OSPF neighbors in FULL state: {missing_neighbors}")
                else:
                    logger.info(f"{device.name}: All OSPF neighbors in FULL state ✓")

            except Exception as e:
                logger.error(f"Failed to check OSPF neighbors on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"OSPF neighbor issues found: {failed_devices}")


class LoopbackConnectivity(aetest.Testcase):
    """Verify P router loopback connectivity."""

    @aetest.setup
    def setup(self, mpls_routers):
        """Build list of P router loopbacks to test."""
        self.p_routers = [device for device in mpls_routers
                          if device.custom.get('mpls_role') in ['P', 'P-PE']]

        if not self.p_routers:
            self.skipped("No P routers found in testbed")

    @aetest.test
    def verify_loopback_reachability(self, testbed):
        """Verify all P router loopbacks are reachable from each PE router."""
        failed_tests = []

        # Get PE routers as source
        pe_routers = [device for device in testbed.devices.values()
                      if device.custom.get('mpls_role') in ['PE', 'P-PE']]

        if not pe_routers:
            logger.warning("No PE routers found to test connectivity from")
            return

        # Get loopback IPs for all P routers
        target_loopbacks = {}
        for p_router in self.p_routers:
            loopback_ip = p_router.custom.get('loopback0_ip')
            if loopback_ip:
                target_loopbacks[p_router.name] = loopback_ip
            else:
                logger.warning(f"{p_router.name}: No loopback0_ip defined in custom attributes")

        if not target_loopbacks:
            self.skipped("No P router loopback IPs defined")

        # Test connectivity from each PE to each P router loopback
        for pe_router in pe_routers:
            logger.info(f"Testing loopback connectivity from {pe_router.name}...")

            for p_name, loopback_ip in target_loopbacks.items():
                # Remove subnet mask if present
                target_ip = loopback_ip.split('/')[0]

                try:
                    # Execute ping
                    result = pe_router.ping(target_ip, count=5)

                    if not result:
                        failed_tests.append({
                            'source': pe_router.name,
                            'target': p_name,
                            'target_ip': target_ip,
                            'result': 'FAILED'
                        })
                        logger.error(f"{pe_router.name} → {p_name} ({target_ip}): FAILED")
                    else:
                        logger.info(f"{pe_router.name} → {p_name} ({target_ip}): SUCCESS ✓")

                except Exception as e:
                    logger.error(f"Ping failed from {pe_router.name} to {target_ip}: {e}")
                    failed_tests.append({
                        'source': pe_router.name,
                        'target': p_name,
                        'target_ip': target_ip,
                        'error': str(e)
                    })

        if failed_tests:
            self.failed(f"Loopback connectivity failures: {failed_tests}")


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
