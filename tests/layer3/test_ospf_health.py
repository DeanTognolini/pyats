"""
OSPF Health Check Test Suite
=============================

This test suite validates OSPF health and parameters across network devices.

Testcases:
    - OspfProcessHealth: Verify OSPF process is running correctly
    - OspfNeighborHealth: Verify OSPF neighbors are in expected states
    - OspfInterfaceHealth: Verify OSPF interfaces are operational
    - OspfDatabaseHealth: Verify OSPF database consistency
    - OspfRouteHealth: Verify expected OSPF routes are present

Required Custom Attributes:
    ospf_enabled: bool - Whether device runs OSPF (default: True if ospf_neighbors defined)
    ospf_process_id: str - Expected OSPF process ID (optional)
    ospf_router_id: str - Expected OSPF router ID (optional)
    ospf_neighbors: list - Expected OSPF neighbor IP addresses
    ospf_interfaces: list - Expected OSPF-enabled interfaces (optional)
    ospf_expected_routes: list - Expected OSPF routes in routing table (optional)
    ospf_areas: list - Expected OSPF areas (optional)

Example testbed configuration:
    devices:
      R1:
        custom:
          ospf_enabled: true
          ospf_process_id: "1"
          ospf_router_id: "10.0.0.1"
          ospf_neighbors:
            - 192.168.1.2
            - 192.168.2.2
          ospf_interfaces:
            - GigabitEthernet0/0
            - GigabitEthernet0/1
          ospf_areas:
            - "0.0.0.0"
          ospf_expected_routes:
            - 10.0.0.0/24
            - 172.16.0.0/16
"""

from pyats import aetest
from pyats.topology import loader
import logging
import re

logger = logging.getLogger(__name__)


class CommonSetup(aetest.CommonSetup):
    """Common setup tasks for OSPF health validation."""

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
    def mark_ospf_routers(self, testbed):
        """Identify OSPF-enabled routers in the testbed."""
        self.parent.parameters['ospf_routers'] = []
        for device in testbed.devices.values():
            # Device is OSPF-enabled if ospf_enabled is True or ospf_neighbors is defined
            ospf_enabled = device.custom.get('ospf_enabled', False)
            ospf_neighbors = device.custom.get('ospf_neighbors', [])

            if ospf_enabled or ospf_neighbors:
                self.parent.parameters['ospf_routers'].append(device)
                logger.info(f"{device.name} marked as OSPF-enabled router")

        if not self.parent.parameters['ospf_routers']:
            logger.warning("No OSPF-enabled routers found in testbed")


class OspfProcessHealth(aetest.Testcase):
    """Verify OSPF process is running and healthy."""

    @aetest.setup
    def setup(self, ospf_routers):
        """Verify we have OSPF routers to test."""
        if not ospf_routers:
            self.skipped("No OSPF-enabled routers found in testbed")

    @aetest.test
    def verify_ospf_process(self, ospf_routers):
        """Verify OSPF process is running on all expected devices."""
        failed_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF process on {device.name}...")

            try:
                # Parse OSPF process information
                output = device.parse('show ip ospf')

                if not output:
                    failed_devices.append({
                        'device': device.name,
                        'issue': 'No OSPF process found'
                    })
                    logger.error(f"{device.name}: No OSPF process running!")
                    continue

                # Extract process information
                processes_found = []

                # Handle VRF-based output structure
                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'instance' in af_data:
                                    for instance_id, inst_data in af_data['instance'].items():
                                        processes_found.append({
                                            'process_id': instance_id,
                                            'router_id': inst_data.get('router_id', 'N/A'),
                                            'vrf': vrf
                                        })

                # Validate expected process ID if specified
                expected_process_id = device.custom.get('ospf_process_id')
                if expected_process_id:
                    process_ids = [p['process_id'] for p in processes_found]
                    if expected_process_id not in process_ids:
                        failed_devices.append({
                            'device': device.name,
                            'issue': f'Expected process ID {expected_process_id} not found',
                            'found_processes': process_ids
                        })
                        logger.error(f"{device.name}: Expected OSPF process {expected_process_id} not found")
                        continue

                # Validate expected router ID if specified
                expected_router_id = device.custom.get('ospf_router_id')
                if expected_router_id:
                    router_ids = [p['router_id'] for p in processes_found]
                    if expected_router_id not in router_ids:
                        failed_devices.append({
                            'device': device.name,
                            'issue': f'Expected router ID {expected_router_id} not found',
                            'found_router_ids': router_ids
                        })
                        logger.error(f"{device.name}: Expected OSPF router ID {expected_router_id} not found")
                        continue

                logger.info(f"{device.name}: OSPF process healthy - {len(processes_found)} instance(s) running")

            except Exception as e:
                logger.error(f"Failed to check OSPF process on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"OSPF process issues found: {failed_devices}")

    @aetest.test
    def verify_ospf_spf_timing(self, ospf_routers):
        """Verify SPF algorithm is not running excessively."""
        warning_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF SPF timing on {device.name}...")

            try:
                output = device.parse('show ip ospf')

                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'instance' in af_data:
                                    for instance_id, inst_data in af_data['instance'].items():
                                        # Check for excessive SPF runs if available
                                        spf_runs = inst_data.get('spf_control', {}).get('spf_runs', 0)
                                        if spf_runs > 1000:  # Threshold for concern
                                            warning_devices.append({
                                                'device': device.name,
                                                'process_id': instance_id,
                                                'spf_runs': spf_runs
                                            })
                                            logger.warning(
                                                f"{device.name}: High SPF run count ({spf_runs}) "
                                                f"may indicate network instability"
                                            )

                logger.info(f"{device.name}: SPF timing check complete")

            except Exception as e:
                logger.warning(f"Could not check SPF timing on {device.name}: {e}")

        if warning_devices:
            logger.warning(f"Devices with high SPF counts: {warning_devices}")
            # This is a warning, not a failure


class OspfNeighborHealth(aetest.Testcase):
    """Verify OSPF neighbor relationships are healthy."""

    @aetest.setup
    def setup(self, ospf_routers):
        """Verify we have OSPF routers to test."""
        if not ospf_routers:
            self.skipped("No OSPF-enabled routers found in testbed")

    @aetest.test
    def verify_ospf_neighbors(self, ospf_routers):
        """Verify all expected OSPF neighbors are in FULL state."""
        failed_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF neighbors on {device.name}...")

            # Get expected OSPF neighbors from custom attributes
            expected_neighbors = device.custom.get('ospf_neighbors', [])

            if not expected_neighbors:
                logger.warning(f"{device.name} has no expected OSPF neighbors defined")
                continue

            try:
                # Parse OSPF neighbor output
                output = device.parse('show ip ospf neighbor')

                # Extract neighbors and their states
                full_neighbors = []
                non_full_neighbors = []

                # Handle simple output format (interfaces -> neighbors)
                if 'interfaces' in output:
                    for intf, intf_data in output['interfaces'].items():
                        if 'neighbors' in intf_data:
                            for nbr, nbr_data in intf_data['neighbors'].items():
                                state = nbr_data.get('state', '').upper()
                                if state.startswith('FULL'):
                                    full_neighbors.append(nbr)
                                else:
                                    non_full_neighbors.append({
                                        'neighbor': nbr,
                                        'state': state,
                                        'interface': intf
                                    })

                # Handle complex VRF output format
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
                                                                else:
                                                                    non_full_neighbors.append({
                                                                        'neighbor': nbr,
                                                                        'state': state,
                                                                        'interface': intf
                                                                    })

                # Verify all expected neighbors are FULL
                missing_neighbors = set(expected_neighbors) - set(full_neighbors)

                if missing_neighbors:
                    failed_devices.append({
                        'device': device.name,
                        'missing': list(missing_neighbors),
                        'full_neighbors': full_neighbors,
                        'non_full_neighbors': non_full_neighbors
                    })
                    logger.error(f"{device.name}: Missing OSPF neighbors in FULL state: {missing_neighbors}")
                else:
                    logger.info(f"{device.name}: All {len(expected_neighbors)} expected OSPF neighbors in FULL state")

            except Exception as e:
                logger.error(f"Failed to check OSPF neighbors on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"OSPF neighbor issues found: {failed_devices}")

    @aetest.test
    def verify_ospf_neighbor_timers(self, ospf_routers):
        """Verify OSPF neighbor dead timers are not near expiration."""
        warning_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF neighbor timers on {device.name}...")

            try:
                output = device.parse('show ip ospf neighbor')

                def check_neighbors(interfaces_dict):
                    """Check neighbor timers in an interfaces dict."""
                    for intf, intf_data in interfaces_dict.items():
                        if 'neighbors' in intf_data:
                            for nbr, nbr_data in intf_data['neighbors'].items():
                                dead_time = nbr_data.get('dead_time', '')
                                # Parse dead time (format: "00:00:35" or similar)
                                if dead_time:
                                    try:
                                        parts = dead_time.split(':')
                                        if len(parts) >= 3:
                                            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                                            if seconds < 10:  # Less than 10 seconds remaining
                                                warning_devices.append({
                                                    'device': device.name,
                                                    'neighbor': nbr,
                                                    'interface': intf,
                                                    'dead_time_remaining': dead_time
                                                })
                                    except (ValueError, IndexError):
                                        pass  # Skip if time format is unexpected

                if 'interfaces' in output:
                    check_neighbors(output['interfaces'])
                elif 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'instance' in af_data:
                                    for instance, inst_data in af_data['instance'].items():
                                        if 'areas' in inst_data:
                                            for area, area_data in inst_data['areas'].items():
                                                if 'interfaces' in area_data:
                                                    check_neighbors(area_data['interfaces'])

                logger.info(f"{device.name}: Neighbor timer check complete")

            except Exception as e:
                logger.warning(f"Could not check neighbor timers on {device.name}: {e}")

        if warning_devices:
            logger.warning(f"Neighbors with low dead timers: {warning_devices}")


class OspfInterfaceHealth(aetest.Testcase):
    """Verify OSPF interfaces are healthy."""

    @aetest.setup
    def setup(self, ospf_routers):
        """Verify we have OSPF routers to test."""
        if not ospf_routers:
            self.skipped("No OSPF-enabled routers found in testbed")

    @aetest.test
    def verify_ospf_interfaces(self, ospf_routers):
        """Verify expected OSPF interfaces are operational."""
        failed_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF interfaces on {device.name}...")

            # Get expected OSPF interfaces from custom attributes
            expected_interfaces = device.custom.get('ospf_interfaces', [])

            if not expected_interfaces:
                logger.info(f"{device.name}: No expected OSPF interfaces defined, skipping interface check")
                continue

            try:
                # Parse OSPF interface output
                output = device.parse('show ip ospf interface')

                # Extract operational interfaces
                operational_interfaces = []

                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'instance' in af_data:
                                    for instance, inst_data in af_data['instance'].items():
                                        if 'areas' in inst_data:
                                            for area, area_data in inst_data['areas'].items():
                                                if 'interfaces' in area_data:
                                                    for intf, intf_data in area_data['interfaces'].items():
                                                        # Check if interface is enabled
                                                        enable = intf_data.get('enable', True)
                                                        state = intf_data.get('state', '').upper()
                                                        if enable and state not in ['DOWN', 'DISABLED']:
                                                            operational_interfaces.append(intf)

                # Normalize interface names for comparison
                normalized_expected = [self._normalize_interface_name(i) for i in expected_interfaces]
                normalized_operational = [self._normalize_interface_name(i) for i in operational_interfaces]

                # Check for missing interfaces
                missing_interfaces = []
                for exp_intf in expected_interfaces:
                    normalized_exp = self._normalize_interface_name(exp_intf)
                    if not any(normalized_exp in norm_op for norm_op in normalized_operational):
                        missing_interfaces.append(exp_intf)

                if missing_interfaces:
                    failed_devices.append({
                        'device': device.name,
                        'missing_interfaces': missing_interfaces,
                        'operational_interfaces': operational_interfaces
                    })
                    logger.error(f"{device.name}: Missing OSPF interfaces: {missing_interfaces}")
                else:
                    logger.info(f"{device.name}: All expected OSPF interfaces operational")

            except Exception as e:
                logger.error(f"Failed to check OSPF interfaces on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"OSPF interface issues found: {failed_devices}")

    def _normalize_interface_name(self, name):
        """Normalize interface names for comparison."""
        # Convert to lowercase and handle common abbreviations
        name = name.lower()
        replacements = {
            'gigabitethernet': 'gi',
            'fastethernet': 'fa',
            'ethernet': 'eth',
            'tengigabitethernet': 'te',
            'twentyfivegige': 'twe',
            'fortygigabitethernet': 'fo',
            'hundredgige': 'hu',
            'loopback': 'lo',
            'vlan': 'vlan',
            'port-channel': 'po',
        }
        for full, abbrev in replacements.items():
            name = name.replace(full, abbrev)
        return name

    @aetest.test
    def verify_ospf_interface_costs(self, ospf_routers):
        """Verify OSPF interface costs are configured correctly."""
        warnings = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF interface costs on {device.name}...")

            # Get expected interface costs from custom attributes
            expected_costs = device.custom.get('ospf_interface_costs', {})

            if not expected_costs:
                logger.info(f"{device.name}: No expected OSPF interface costs defined")
                continue

            try:
                output = device.parse('show ip ospf interface')

                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'instance' in af_data:
                                    for instance, inst_data in af_data['instance'].items():
                                        if 'areas' in inst_data:
                                            for area, area_data in inst_data['areas'].items():
                                                if 'interfaces' in area_data:
                                                    for intf, intf_data in area_data['interfaces'].items():
                                                        if intf in expected_costs:
                                                            actual_cost = intf_data.get('cost', 0)
                                                            expected_cost = expected_costs[intf]
                                                            if actual_cost != expected_cost:
                                                                warnings.append({
                                                                    'device': device.name,
                                                                    'interface': intf,
                                                                    'actual_cost': actual_cost,
                                                                    'expected_cost': expected_cost
                                                                })

                logger.info(f"{device.name}: Interface cost check complete")

            except Exception as e:
                logger.warning(f"Could not check interface costs on {device.name}: {e}")

        if warnings:
            logger.warning(f"OSPF interface cost mismatches: {warnings}")


class OspfDatabaseHealth(aetest.Testcase):
    """Verify OSPF database consistency."""

    @aetest.setup
    def setup(self, ospf_routers):
        """Verify we have OSPF routers to test."""
        if not ospf_routers:
            self.skipped("No OSPF-enabled routers found in testbed")

    @aetest.test
    def verify_ospf_database(self, ospf_routers):
        """Verify OSPF database is populated."""
        failed_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF database on {device.name}...")

            try:
                # Parse OSPF database summary
                output = device.parse('show ip ospf database')

                if not output:
                    failed_devices.append({
                        'device': device.name,
                        'issue': 'Empty OSPF database'
                    })
                    logger.error(f"{device.name}: OSPF database is empty!")
                    continue

                # Check for LSAs in the database
                lsa_count = 0

                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'instance' in af_data:
                                    for instance, inst_data in af_data['instance'].items():
                                        if 'areas' in inst_data:
                                            for area, area_data in inst_data['areas'].items():
                                                # Count different LSA types
                                                # Structure: database -> lsa_types -> {type_num} -> lsas
                                                if 'database' in area_data:
                                                    db = area_data['database']
                                                    if 'lsa_types' in db:
                                                        for lsa_type_num, lsa_type_data in db['lsa_types'].items():
                                                            lsa_count += len(lsa_type_data.get('lsas', {}))

                if lsa_count == 0:
                    failed_devices.append({
                        'device': device.name,
                        'issue': 'No LSAs found in OSPF database'
                    })
                    logger.error(f"{device.name}: No LSAs in OSPF database!")
                else:
                    logger.info(f"{device.name}: OSPF database healthy with {lsa_count} LSAs")

            except Exception as e:
                logger.error(f"Failed to check OSPF database on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"OSPF database issues found: {failed_devices}")

    @aetest.test
    def verify_ospf_areas(self, ospf_routers):
        """Verify expected OSPF areas are present."""
        failed_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF areas on {device.name}...")

            # Get expected areas from custom attributes
            expected_areas = device.custom.get('ospf_areas', [])

            if not expected_areas:
                logger.info(f"{device.name}: No expected OSPF areas defined, skipping area check")
                continue

            try:
                output = device.parse('show ip ospf')

                # Extract areas from the output
                found_areas = []

                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'instance' in af_data:
                                    for instance, inst_data in af_data['instance'].items():
                                        if 'areas' in inst_data:
                                            for area in inst_data['areas'].keys():
                                                found_areas.append(area)

                # Check for missing areas
                missing_areas = set(expected_areas) - set(found_areas)

                if missing_areas:
                    failed_devices.append({
                        'device': device.name,
                        'missing_areas': list(missing_areas),
                        'found_areas': found_areas
                    })
                    logger.error(f"{device.name}: Missing OSPF areas: {missing_areas}")
                else:
                    logger.info(f"{device.name}: All expected OSPF areas present")

            except Exception as e:
                logger.error(f"Failed to check OSPF areas on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"OSPF area issues found: {failed_devices}")


class OspfRouteHealth(aetest.Testcase):
    """Verify OSPF routes are present in routing table."""

    @aetest.setup
    def setup(self, ospf_routers):
        """Verify we have OSPF routers to test."""
        if not ospf_routers:
            self.skipped("No OSPF-enabled routers found in testbed")

    @aetest.test
    def verify_ospf_routes(self, ospf_routers):
        """Verify expected OSPF routes are in the routing table."""
        failed_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF routes on {device.name}...")

            # Get expected routes from custom attributes
            expected_routes = device.custom.get('ospf_expected_routes', [])

            if not expected_routes:
                logger.info(f"{device.name}: No expected OSPF routes defined, skipping route check")
                continue

            try:
                # Parse routing table for OSPF routes
                output = device.parse('show ip route ospf')

                # Extract OSPF routes from the output
                ospf_routes = []

                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'routes' in af_data:
                                    for route, route_data in af_data['routes'].items():
                                        ospf_routes.append(route)

                # Check for missing routes
                missing_routes = []
                for expected_route in expected_routes:
                    # Handle both /32 and /24 style prefixes
                    route_found = False
                    for ospf_route in ospf_routes:
                        # Exact match or prefix match
                        if expected_route == ospf_route or ospf_route.startswith(expected_route.split('/')[0]):
                            route_found = True
                            break
                    if not route_found:
                        missing_routes.append(expected_route)

                if missing_routes:
                    failed_devices.append({
                        'device': device.name,
                        'missing_routes': missing_routes,
                        'found_routes': ospf_routes[:20]  # Limit output
                    })
                    logger.error(f"{device.name}: Missing OSPF routes: {missing_routes}")
                else:
                    logger.info(f"{device.name}: All {len(expected_routes)} expected OSPF routes present")

            except Exception as e:
                logger.error(f"Failed to check OSPF routes on {device.name}: {e}")
                failed_devices.append({
                    'device': device.name,
                    'error': str(e)
                })

        if failed_devices:
            self.failed(f"OSPF route issues found: {failed_devices}")

    @aetest.test
    def verify_ospf_route_count(self, ospf_routers):
        """Verify minimum expected OSPF route count."""
        warning_devices = []

        for device in ospf_routers:
            logger.info(f"Checking OSPF route count on {device.name}...")

            # Get minimum expected route count from custom attributes
            min_route_count = device.custom.get('ospf_min_route_count', 0)

            if min_route_count <= 0:
                continue

            try:
                output = device.parse('show ip route ospf')

                route_count = 0
                if 'vrf' in output:
                    for vrf, vrf_data in output['vrf'].items():
                        if 'address_family' in vrf_data:
                            for af, af_data in vrf_data['address_family'].items():
                                if 'routes' in af_data:
                                    route_count += len(af_data['routes'])

                if route_count < min_route_count:
                    warning_devices.append({
                        'device': device.name,
                        'actual_routes': route_count,
                        'minimum_expected': min_route_count
                    })
                    logger.warning(
                        f"{device.name}: OSPF route count ({route_count}) "
                        f"below minimum expected ({min_route_count})"
                    )
                else:
                    logger.info(f"{device.name}: OSPF route count ({route_count}) meets minimum ({min_route_count})")

            except Exception as e:
                logger.warning(f"Could not check route count on {device.name}: {e}")

        if warning_devices:
            logger.warning(f"Devices with low OSPF route count: {warning_devices}")


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
