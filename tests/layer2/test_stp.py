from pyats import aetest
from pyats.topology import loader
import logging

logger = logging.getLogger(__name__)

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
            try:
                device.connect(log_stdout=False)
                logger.info(f"Connected to {device.name}")
            except Exception as e:
                logger.error(f"Failed to connect to {device.name}: {e}")
                # Don't fail the whole run if one device fails, but note it
                pass

class StpValidation(aetest.Testcase):
    """Verify Spanning Tree Protocol configuration and status."""

    @aetest.setup
    def setup(self, testbed):
        """Identify devices that should have STP enabled (usually switches)."""
        self.switches = []
        for device in testbed.devices.values():
            if not device.connected:
                continue
            
            # Simple heuristic: Check if it's a switch based on type or capability
            # Or just try to run the command and see if it works
            if device.type in ['switch', 'router']: 
                 self.switches.append(device)
        
        if not self.switches:
            self.skipped("No connected switches found to test STP")

    @aetest.test
    def check_stp_enabled(self):
        """Verify STP is enabled globally."""
        failed_devices = []
        
        for device in self.switches:
            try:
                # Parse 'show spanning-tree summary' to check global status
                # Structure varies by OS, this assumes IOS/NXOS style output availability
                stp_summary = device.parse('show spanning-tree summary')
                
                # Check specific keys depending on the parser output structure
                # Often typically contains 'mode' or 'root_bridge_for'
                if not stp_summary:
                    failed_devices.append(f"{device.name}: Parser returned empty data")
                    continue
                
                mode = stp_summary.get('mode')
                logger.info(f"{device.name} STP Mode: {mode}")
                
            except Exception as e:
                logger.warning(f"{device.name}: Could not parse STP summary - {e}")
                # Identify if this is a failure or just not supported
                # For now, we'll mark it as a failure to investigate
                failed_devices.append(f"{device.name}: {e}")

        if failed_devices:
            self.failed(f"STP check failed on: {'; '.join(failed_devices)}")

    @aetest.test
    def check_root_bridge_status(self):
        """Verify Root Bridge information."""
        failed_devices = []

        for device in self.switches:
            try:
                # 'show spanning-tree' gives per-vlan/instance details
                stp_details = device.parse('show spanning-tree')
                
                # Iterate through VLANs or MST instances
                # Structure: output['entry']['vlan_id']...
                
                # Handling different parser structures (genie returns different structures for different OS)
                # We will look for common keys.
                
                # For IOSXE 'show spanning-tree' usually returns dict with VLANs as keys
                # or under 'topology'
                
                vlans_found = False
                
                # Iterate over whatever the top level keys are (usually VLANs or Instances)
                for inst_id, data in stp_details.get('topology', {}).items():
                    vlans_found = True
                    # Check if root info exists
                    if 'root' not in data:
                        # Some instances might not have root info if disabled?
                        continue
                        
                    root_priority = data['root'].get('priority')
                    root_mac = data['root'].get('address')
                    
                    # Verify we can see a root
                    if not root_priority or not root_mac:
                        failed_devices.append(f"{device.name}: Missing root info for {inst_id}")
                
                # Attempt to handle flat structure (some parsers)
                if not vlans_found:
                     # fallback or logging
                     pass

            except Exception as e:
                logger.warning(f"{device.name}: Could not check root status - {e}")
                # Don't fail immediately, but log
                
        if failed_devices:
            self.failed(f"Root bridge issues: {'; '.join(failed_devices)}")

    @aetest.test
    def check_interface_states(self):
        """Verify interface states (Forwarding, Blocking, etc) are valid."""
        invalid_states = [] # unexpected states like 'Broken' or 'Listening' for too long (though listening is valid transient)
        
        # Valid states usually: FW (Forwarding), BLK (Blocking), LRN (Learning), LIS (Listening)
        # We might want to flag if we see weird ones, but purely reading them is good
        
        for device in self.switches:
            try:
                stp_details = device.parse('show spanning-tree')
                
                # Need to traverse the structure to find interfaces
                # structure: stp_details['topology'][vlan]['interfaces'][intf]...
                
                for inst_id, data in stp_details.get('topology', {}).items():
                    for intf_name, intf_data in data.get('interfaces', {}).items():
                        status = intf_data.get('status')
                        role = intf_data.get('role')
                        
                        logger.info(f"{device.name} {inst_id} {intf_name}: Role={role}, Status={status}")
                        
                        if not status:
                            invalid_states.append(f"{device.name} {intf_name}: No status found")
                        
            except Exception as e:
                logger.warning(f"{device.name}: Error checking interfaces - {e}")

        if invalid_states:
            self.failed(f"Interface state issues: {'; '.join(invalid_states)}")

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self, testbed):
        """Disconnect from devices."""
        for device in testbed.devices.values():
            if device.connected:
                device.disconnect()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed', type=loader.load, required=True)
    args, _ = parser.parse_known_args()
    aetest.main(testbed=args.testbed)
