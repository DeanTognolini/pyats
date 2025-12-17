from pyats import aetest
from pyats.topology import loader

# Optical thresholds by SFP type (dBm)
SFP_THRESHOLDS = {
    'SFP-10G-SR': {'rx_min': -9.5, 'rx_max': 2.0},
    'SFP-10G-LR': {'rx_min': -14.4, 'rx_max': 0.5},
    'SFP-10G-ER': {'rx_min': -15.8, 'rx_max': -1.0},
    'SFP-1G-SX': {'rx_min': -17.0, 'rx_max': 0.0},
    'SFP-1G-LX': {'rx_min': -19.0, 'rx_max': -3.0}
}

class CommonSetup(aetest.CommonSetup):
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
            device.connect(log_stdout=False)

class LinkHealth(aetest.Testcase):
    """Verify link health across both ends: status, optics, errors, speed/duplex, MTU, CDP."""

    @aetest.setup
    def setup(self, testbed):
        """Build list of links."""
        self.links = list(testbed.links)
        if not self.links:
            self.skipped("No links defined in testbed topology")

    def _get_interface_data(self, device, intf_name):
        """Parse and return interface data."""
        parsed = device.parse(f'show interfaces {intf_name}')
        return parsed.get(intf_name, {})

    @aetest.test
    def check_link_status(self, testbed):
        """Verify both ends of each link are up/up."""
        failed_links = []

        for link in self.links:
            link_ok = True
            link_details = []

            for intf in link.interfaces:
                device = intf.device
                intf_name = intf.name
                intf_data = self._get_interface_data(device, intf_name)

                oper_status = intf_data.get('oper_status', '').lower()
                line_protocol = intf_data.get('line_protocol', '').lower()

                if oper_status != 'up' or line_protocol != 'up':
                    link_ok = False
                    link_details.append(f"{device.name}:{intf_name} is {oper_status}/{line_protocol}")

            if not link_ok:
                failed_links.append(f"{link.name}: {', '.join(link_details)}")

        if failed_links:
            self.failed(f"Links not up/up: {'; '.join(failed_links)}")
        else:
            self.passed(f"All {len(self.links)} links are up/up")

    @aetest.test
    def check_link_optical_levels(self, testbed):
        """Verify RX power within acceptable range on both ends."""
        failed_links = []

        for link in self.links:
            link_details = []

            for intf in link.interfaces:
                device = intf.device
                intf_name = intf.name
                intf_obj = device.interfaces.get(intf_name)

                sfp_type = getattr(intf_obj, 'sfp_type', None) if intf_obj else None
                if not sfp_type:
                    continue  # Skip interfaces without sfp_type

                thresholds = SFP_THRESHOLDS.get(sfp_type)
                if not thresholds:
                    continue

                try:
                    parsed = device.parse(f'show controllers optics {intf_name}')
                except Exception:
                    continue

                intf_data = parsed.get(intf_name, {})
                optics = intf_data.get('optics', {})
                rx_power = optics.get('rx_power', optics.get('receive_power'))

                if rx_power is None:
                    continue

                rx_power = float(rx_power)
                if not (thresholds['rx_min'] <= rx_power <= thresholds['rx_max']):
                    link_details.append(
                        f"{device.name}:{intf_name} RX {rx_power} dBm "
                        f"(expected {thresholds['rx_min']} to {thresholds['rx_max']})"
                    )

            if link_details:
                failed_links.append(f"{link.name}: {', '.join(link_details)}")

        if failed_links:
            self.failed(f"Optical levels out of range: {'; '.join(failed_links)}")
        else:
            self.passed("All link optical levels OK")

    @aetest.test
    def check_link_errors(self, testbed):
        """Check for errors on both ends of each link."""
        failed_links = []

        for link in self.links:
            link_details = []

            for intf in link.interfaces:
                device = intf.device
                intf_name = intf.name
                intf_data = self._get_interface_data(device, intf_name)
                counters = intf_data.get('counters', {})

                errors = []
                for error_type, key in [('in', 'in_errors'), ('out', 'out_errors'), ('CRC', 'in_crc_errors')]:
                    count = counters.get(key, 0)
                    if count > 0:
                        errors.append(f"{count} {error_type}")

                if errors:
                    link_details.append(f"{device.name}:{intf_name} [{', '.join(errors)}]")

            if link_details:
                failed_links.append(f"{link.name}: {', '.join(link_details)}")

        if failed_links:
            self.failed(f"Links with errors: {'; '.join(failed_links)}")
        else:
            self.passed("No errors on any links")

    @aetest.test
    def check_link_speed_duplex(self, testbed):
        """Verify speed and duplex match expected values on both ends."""
        failed_links = []

        for link in self.links:
            link_details = []

            for intf in link.interfaces:
                device = intf.device
                intf_name = intf.name
                intf_obj = device.interfaces.get(intf_name)

                expected_speed = getattr(intf_obj, 'speed', None) if intf_obj else None
                expected_duplex = getattr(intf_obj, 'duplex', None) if intf_obj else None

                if not expected_speed and not expected_duplex:
                    continue  # No expectations defined

                intf_data = self._get_interface_data(device, intf_name)
                actual_speed = intf_data.get('bandwidth', intf_data.get('speed'))
                actual_duplex = intf_data.get('duplex_mode', intf_data.get('duplex', '')).lower()

                mismatches = []
                if expected_speed and actual_speed != expected_speed:
                    mismatches.append(f"speed {actual_speed} != {expected_speed}")
                if expected_duplex and actual_duplex != expected_duplex.lower():
                    mismatches.append(f"duplex {actual_duplex} != {expected_duplex}")

                if mismatches:
                    link_details.append(f"{device.name}:{intf_name} [{', '.join(mismatches)}]")

            if link_details:
                failed_links.append(f"{link.name}: {', '.join(link_details)}")

        if failed_links:
            self.failed(f"Speed/duplex mismatches: {'; '.join(failed_links)}")
        else:
            self.passed("All link speed/duplex settings OK")

    @aetest.test
    def check_link_mtu(self, testbed):
        """Verify MTU matches expected value on both ends."""
        failed_links = []

        for link in self.links:
            link_details = []

            for intf in link.interfaces:
                device = intf.device
                intf_name = intf.name
                intf_obj = device.interfaces.get(intf_name)

                expected_mtu = getattr(intf_obj, 'mtu', None) if intf_obj else None
                if not expected_mtu:
                    continue

                intf_data = self._get_interface_data(device, intf_name)
                actual_mtu = intf_data.get('mtu')

                if actual_mtu != expected_mtu:
                    link_details.append(f"{device.name}:{intf_name} MTU {actual_mtu} != {expected_mtu}")

            if link_details:
                failed_links.append(f"{link.name}: {', '.join(link_details)}")

        if failed_links:
            self.failed(f"MTU mismatches: {'; '.join(failed_links)}")
        else:
            self.passed("All link MTU settings OK")

    @aetest.test
    def check_link_cdp(self, testbed):
        """Verify CDP neighbors match expected topology."""
        failed_links = []

        for link in self.links:
            if len(link.interfaces) != 2:
                continue  # CDP check only makes sense for point-to-point links

            intf_a, intf_b = link.interfaces
            link_details = []

            for local_intf, remote_intf in [(intf_a, intf_b), (intf_b, intf_a)]:
                device = local_intf.device
                local_name = local_intf.name

                try:
                    parsed = device.parse('show cdp neighbors detail')
                except Exception:
                    link_details.append(f"{device.name}: CDP parse failed")
                    continue

                # Find CDP entry for this interface
                expected_neighbor = remote_intf.device.name
                expected_port = remote_intf.name
                found = False

                for idx, neighbor in parsed.get('index', {}).items():
                    local_interface = neighbor.get('local_interface', '')
                    if local_name.lower() in local_interface.lower():
                        cdp_neighbor = neighbor.get('device_id', '').split('.')[0]  # Strip domain
                        cdp_port = neighbor.get('port_id', '')

                        if expected_neighbor.lower() not in cdp_neighbor.lower():
                            link_details.append(
                                f"{device.name}:{local_name} CDP neighbor {cdp_neighbor} != {expected_neighbor}"
                            )
                        elif expected_port.lower() not in cdp_port.lower():
                            link_details.append(
                                f"{device.name}:{local_name} CDP port {cdp_port} != {expected_port}"
                            )
                        found = True
                        break

                if not found:
                    link_details.append(f"{device.name}:{local_name} no CDP neighbor found")

            if link_details:
                failed_links.append(f"{link.name}: {', '.join(link_details)}")

        if failed_links:
            self.failed(f"CDP mismatches: {'; '.join(failed_links)}")
        else:
            self.passed("All CDP neighbors match topology")

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self, testbed):
        for device in testbed.devices.values():
            if device.connected:
                device.disconnect()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed', type=loader.load, required=True)
    args, _ = parser.parse_known_args()
    aetest.main(testbed=args.testbed)
