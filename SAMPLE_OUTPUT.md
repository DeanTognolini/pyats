# Sample Test Output and Reports

This document shows example outputs from the pyATS Layer 1 validation tests to help you understand what to expect when running the test suite.

## Table of Contents

- [Console Output](#console-output)
- [Test Results Summary](#test-results-summary)
- [HTML Report Structure](#html-report-structure)
- [JSON Report Structure](#json-report-structure)
- [Common Failure Scenarios](#common-failure-scenarios)

---

## Console Output

### Successful Test Run

```
2025-12-17T14:30:00: %EASYPY-INFO: Starting job run: Layer 1 Validation
2025-12-17T14:30:00: %EASYPY-INFO: Runinfo directory: /home/user/pyats/archive/25-Dec_14:30:00.123456
2025-12-17T14:30:00: %EASYPY-INFO: --------------------------------------------------------------------------------

2025-12-17T14:30:01: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:01: %SCRIPT-INFO: |                            Starting common setup                             |
2025-12-17T14:30:01: %SCRIPT-INFO: +------------------------------------------------------------------------------+

2025-12-17T14:30:01: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:01: %SCRIPT-INFO: |                   Starting subsection check_env_vars                         |
2025-12-17T14:30:01: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:01: %SCRIPT-INFO: The result of subsection check_env_vars is => PASSED

2025-12-17T14:30:01: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:01: %SCRIPT-INFO: |                 Starting subsection connect_to_devices                       |
2025-12-17T14:30:01: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:02: %UNICON-INFO: +++ router1 with via 'cli': executing command 'show version' +++
2025-12-17T14:30:03: %UNICON-INFO: +++ router1 with via 'cli': connection established successfully +++
2025-12-17T14:30:04: %UNICON-INFO: +++ router2 with via 'cli': executing command 'show version' +++
2025-12-17T14:30:05: %UNICON-INFO: +++ router2 with via 'cli': connection established successfully +++
2025-12-17T14:30:05: %SCRIPT-INFO: The result of subsection connect_to_devices is => PASSED

2025-12-17T14:30:05: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:05: %SCRIPT-INFO: |                         Starting testcase LinkHealth                         |
2025-12-17T14:30:05: %SCRIPT-INFO: +------------------------------------------------------------------------------+

2025-12-17T14:30:05: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:05: %SCRIPT-INFO: |                          Starting section setup                              |
2025-12-17T14:30:05: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:05: %SCRIPT-INFO: The result of section setup is => PASSED

2025-12-17T14:30:05: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:05: %SCRIPT-INFO: |                    Starting test check_link_status                           |
2025-12-17T14:30:05: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:08: %SCRIPT-INFO: Passed reason: All 2 links are up/up
2025-12-17T14:30:08: %SCRIPT-INFO: The result of test check_link_status is => PASSED

2025-12-17T14:30:08: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:08: %SCRIPT-INFO: |                Starting test check_link_optical_levels                       |
2025-12-17T14:30:08: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:12: %SCRIPT-INFO: Passed reason: All link optical levels OK
2025-12-17T14:30:12: %SCRIPT-INFO: The result of test check_link_optical_levels is => PASSED

2025-12-17T14:30:12: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:12: %SCRIPT-INFO: |                     Starting test check_link_errors                          |
2025-12-17T14:30:12: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:15: %SCRIPT-INFO: Passed reason: No errors on any links
2025-12-17T14:30:15: %SCRIPT-INFO: The result of test check_link_errors is => PASSED

2025-12-17T14:30:15: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:15: %SCRIPT-INFO: |                  Starting test check_link_speed_duplex                       |
2025-12-17T14:30:15: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:18: %SCRIPT-INFO: Passed reason: All link speed/duplex settings OK
2025-12-17T14:30:18: %SCRIPT-INFO: The result of test check_link_speed_duplex is => PASSED

2025-12-17T14:30:18: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:18: %SCRIPT-INFO: |                       Starting test check_link_mtu                           |
2025-12-17T14:30:18: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:20: %SCRIPT-INFO: Passed reason: All link MTU settings OK
2025-12-17T14:30:20: %SCRIPT-INFO: The result of test check_link_mtu is => PASSED

2025-12-17T14:30:20: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:20: %SCRIPT-INFO: |                       Starting test check_link_cdp                           |
2025-12-17T14:30:20: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:24: %SCRIPT-INFO: Passed reason: All CDP neighbors match topology
2025-12-17T14:30:24: %SCRIPT-INFO: The result of test check_link_cdp is => PASSED

2025-12-17T14:30:24: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:24: %SCRIPT-INFO: |                      Starting common cleanup                                 |
2025-12-17T14:30:24: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:25: %SCRIPT-INFO: The result of common cleanup is => PASSED

2025-12-17T14:30:25: %EASYPY-INFO: --------------------------------------------------------------------------------
2025-12-17T14:30:25: %EASYPY-INFO: Job finished successfully
2025-12-17T14:30:25: %EASYPY-INFO:
2025-12-17T14:30:25: %EASYPY-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:25: %EASYPY-INFO: |                               Test Results                                   |
2025-12-17T14:30:25: %EASYPY-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:30:25: %EASYPY-INFO:   Number of PASSED     : 13
2025-12-17T14:30:25: %EASYPY-INFO:   Number of FAILED     : 0
2025-12-17T14:30:25: %EASYPY-INFO:   Number of SKIPPED    : 0
2025-12-17T14:30:25: %EASYPY-INFO:   Total Number         : 13
2025-12-17T14:30:25: %EASYPY-INFO: +------------------------------------------------------------------------------+
```

### Test Run with Failures

```
2025-12-17T14:35:15: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:35:15: %SCRIPT-INFO: |                    Starting test check_link_status                           |
2025-12-17T14:35:15: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:35:18: %SCRIPT-ERROR: Failed reason: Links not up/up: router1-router2: router2:GigabitEthernet1 is up/down
2025-12-17T14:35:18: %SCRIPT-INFO: The result of test check_link_status is => FAILED

2025-12-17T14:35:18: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:35:18: %SCRIPT-INFO: |                Starting test check_link_optical_levels                       |
2025-12-17T14:35:18: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:35:22: %SCRIPT-ERROR: Failed reason: Optical levels out of range: router1-router2: router1:GigabitEthernet1 RX -12.5 dBm (expected -9.5 to 2.0)
2025-12-17T14:35:22: %SCRIPT-INFO: The result of test check_link_optical_levels is => FAILED

2025-12-17T14:35:22: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:35:22: %SCRIPT-INFO: |                     Starting test check_link_errors                          |
2025-12-17T14:35:22: %SCRIPT-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:35:25: %SCRIPT-ERROR: Failed reason: Links with errors: router1-legacy: router1:GigabitEthernet2 [245 in, 45 CRC]
2025-12-17T14:35:25: %SCRIPT-INFO: The result of test check_link_errors is => FAILED

2025-12-17T14:35:30: %EASYPY-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:35:30: %EASYPY-INFO: |                               Test Results                                   |
2025-12-17T14:35:30: %EASYPY-INFO: +------------------------------------------------------------------------------+
2025-12-17T14:35:30: %EASYPY-INFO:   Number of PASSED     : 10
2025-12-17T14:35:30: %EASYPY-INFO:   Number of FAILED     : 3
2025-12-17T14:35:30: %EASYPY-INFO:   Number of SKIPPED    : 0
2025-12-17T14:35:30: %EASYPY-INFO:   Total Number         : 13
2025-12-17T14:35:30: %EASYPY-INFO: +------------------------------------------------------------------------------+
```

---

## Test Results Summary

After each run, pyATS generates a detailed summary. Here's what each section means:

### Result Codes

| Code | Meaning | Description |
|------|---------|-------------|
| **PASSED** | Success | Test completed successfully with all validations passing |
| **FAILED** | Failure | Test found issues that need attention |
| **SKIPPED** | Skipped | Test was not executed (e.g., no links defined) |
| **ERRORED** | Error | Test encountered an unexpected error during execution |
| **BLOCKED** | Blocked | Test could not run due to a prerequisite failure |

### Summary Breakdown

```
+------------------------------------------------------------------------------+
|                               Test Results                                   |
+------------------------------------------------------------------------------+
  Number of PASSED     : 10    # Tests that completed successfully
  Number of FAILED     : 3     # Tests that found issues
  Number of SKIPPED    : 0     # Tests that were skipped
  Number of ERRORED    : 0     # Tests that encountered errors
  Number of BLOCKED    : 0     # Tests blocked by prerequisites
  Total Number         : 13    # Total tests executed
+------------------------------------------------------------------------------+
```

---

## HTML Report Structure

When you run with `--html-logs ./reports/`, pyATS generates an interactive HTML report.

### Report Location

```
reports/
├── TaskLog.html                    # Main interactive report
├── TaskLog.{timestamp}.html        # Timestamped copy
└── {timestamp}/
    ├── job.results.json            # Machine-readable results
    ├── layer1_tests.html           # Detailed test script report
    └── connection_logs/            # Device connection logs
        ├── router1.log
        └── router2.log
```

### HTML Report Features

The HTML report includes:

1. **Executive Summary**
   - Overall pass/fail status
   - Test execution timeline
   - Device inventory

2. **Test Case Details**
   - Individual test results
   - Passed/failed criteria
   - Execution time per test

3. **Device Logs**
   - Complete command output
   - Connection logs
   - Parser information

4. **Interactive Features**
   - Expandable/collapsible sections
   - Search functionality
   - Filtering by result type
   - Direct links to failures

### Sample HTML Report View

```
┌─────────────────────────────────────────────────────────────┐
│ pyATS Test Report - Layer 1 Validation                     │
│ Job: Layer 1 Validation                                     │
│ Status: ✓ PASSED    Duration: 25.4s    Date: 2025-12-17   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Test Summary:                                               │
│   ✓ CommonSetup                                      PASSED │
│   ✓ LinkHealth                                       PASSED │
│     ✓ setup                                          PASSED │
│     ✓ check_link_status                              PASSED │
│     ✓ check_link_optical_levels                      PASSED │
│     ✓ check_link_errors                              PASSED │
│     ✓ check_link_speed_duplex                        PASSED │
│     ✓ check_link_mtu                                 PASSED │
│     ✓ check_link_cdp                                 PASSED │
│   ✓ CommonCleanup                                    PASSED │
│                                                             │
│ Device Summary:                                             │
│   ✓ router1 (192.168.1.1)                           PASSED  │
│   ✓ router2 (192.168.1.2)                           PASSED  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## JSON Report Structure

When you run with `--json-logs ./reports/`, pyATS generates JSON output for programmatic processing.

### Sample JSON Report

```json
{
  "job": {
    "name": "Layer 1 Validation",
    "start_time": "2025-12-17T14:30:00.123456",
    "end_time": "2025-12-17T14:30:25.654321",
    "runtime": "25.53",
    "result": "Passed"
  },
  "tasks": {
    "layer1_tests": {
      "result": "Passed",
      "start_time": "2025-12-17T14:30:01.000000",
      "end_time": "2025-12-17T14:30:25.000000",
      "sections": {
        "common_setup": {
          "result": "Passed",
          "subsections": {
            "check_env_vars": {"result": "Passed"},
            "connect_to_devices": {"result": "Passed"}
          }
        },
        "LinkHealth": {
          "result": "Passed",
          "tests": {
            "check_link_status": {
              "result": "Passed",
              "reason": "All 2 links are up/up"
            },
            "check_link_optical_levels": {
              "result": "Passed",
              "reason": "All link optical levels OK"
            },
            "check_link_errors": {
              "result": "Passed",
              "reason": "No errors on any links"
            },
            "check_link_speed_duplex": {
              "result": "Passed",
              "reason": "All link speed/duplex settings OK"
            },
            "check_link_mtu": {
              "result": "Passed",
              "reason": "All link MTU settings OK"
            },
            "check_link_cdp": {
              "result": "Passed",
              "reason": "All CDP neighbors match topology"
            }
          }
        }
      }
    }
  }
}
```

---

## Common Failure Scenarios

### 1. Link Down

**Console Output:**
```
%SCRIPT-ERROR: Failed reason: Links not up/up: router1-router2: router2:GigabitEthernet1 is up/down
```

**What it means:** The interface is administratively up but the line protocol is down, indicating a Layer 1 or Layer 2 issue.

**Troubleshooting:**
- Check physical cable connection
- Verify the remote end is up
- Check for speed/duplex mismatches
- Verify no error disable state

---

### 2. Optical Power Out of Range

**Console Output:**
```
%SCRIPT-ERROR: Failed reason: Optical levels out of range: router1-router2: router1:GigabitEthernet1 RX -12.5 dBm (expected -9.5 to 2.0)
```

**What it means:** The received optical power is below the acceptable threshold for the SFP type.

**Troubleshooting:**
- Check fiber connection and cleanliness
- Verify correct fiber type (single-mode vs multi-mode)
- Check for fiber bends or damage
- Verify SFP is properly seated
- Consider fiber length and attenuation

---

### 3. Interface Errors

**Console Output:**
```
%SCRIPT-ERROR: Failed reason: Links with errors: router1-legacy: router1:GigabitEthernet2 [245 in, 45 CRC]
```

**What it means:** The interface has accumulated input and CRC errors.

**Troubleshooting:**
- Check for duplex mismatches
- Verify cable quality (replace if needed)
- Check for EMI/electrical interference
- Review interface error trends over time
- Consider clearing counters and monitoring

---

### 4. Speed/Duplex Mismatch

**Console Output:**
```
%SCRIPT-ERROR: Failed reason: Speed/duplex mismatches: router1-router2: router1:GigabitEthernet1 [speed 100 != 1000, duplex half != full]
```

**What it means:** The configured speed/duplex doesn't match expectations.

**Troubleshooting:**
- Configure both sides with matching settings
- Verify auto-negotiation is working
- Check for manual configuration overrides
- Review switch port configuration

---

### 5. MTU Mismatch

**Console Output:**
```
%SCRIPT-ERROR: Failed reason: MTU mismatches: router1-router2: router1:GigabitEthernet1 MTU 1400 != 1500
```

**What it means:** The interface MTU doesn't match the expected value.

**Troubleshooting:**
- Verify MTU configuration on both ends
- Check if jumbo frames are required
- Review VLAN and tunnel overhead requirements
- Ensure consistent MTU across the path

---

### 6. CDP Neighbor Mismatch

**Console Output:**
```
%SCRIPT-ERROR: Failed reason: CDP mismatches: router1-router2: router1:GigabitEthernet1 CDP neighbor switch1 != router2
```

**What it means:** The discovered CDP neighbor doesn't match the expected topology.

**Troubleshooting:**
- Verify physical cabling matches documentation
- Check testbed.yaml topology definition
- Ensure CDP is enabled on both ends
- Verify you're connected to the correct port

---

### 7. Connection Failure

**Console Output:**
```
%SCRIPT-ERROR: Failed reason: Missing required environment variables: PYATS_USERNAME, PYATS_PASSWORD
```

**What it means:** Required credentials are not set.

**Troubleshooting:**
- Export environment variables before running
- Verify .env file is sourced
- Check credentials are correct
- Ensure network connectivity to devices

---

## Tips for Interpreting Results

1. **Look for Patterns**: Multiple failures on the same device or link often indicate a common root cause

2. **Check Timestamps**: Failures at similar times might indicate a network event

3. **Review Logs**: The HTML report includes full device output for debugging

4. **Compare Runs**: Track results over time to identify degradation

5. **Use JSON for Automation**: Parse JSON reports for integration with monitoring systems

6. **Archive Results**: Keep historical reports for trend analysis and compliance

---

## Generating Reports

### HTML Report
```bash
pyats run job layer1_job.py --testbed testbed.yaml --html-logs ./reports/
```

### JSON Report
```bash
pyats run job layer1_job.py --testbed testbed.yaml --json-logs ./reports/
```

### Both Formats
```bash
pyats run job layer1_job.py --testbed testbed.yaml --html-logs ./reports/ --json-logs ./reports/
```

### Custom Archive Location
```bash
pyats run job layer1_job.py --testbed testbed.yaml \
  --archive-dir ./archive/$(date +%Y-%m-%d) \
  --html-logs ./reports/
```
