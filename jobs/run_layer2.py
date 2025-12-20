"""
pyATS Job File for Layer 2 Validation

Usage:
  Basic:
    pyats run job jobs/run_layer2.py --testbed testbeds/testbed.yaml

  With HTML reports:
    pyats run job jobs/run_layer2.py --testbed testbeds/testbed.yaml --html-logs ./reports/

  With JSON reports:
    pyats run job jobs/run_layer2.py --testbed testbeds/testbed.yaml --json-logs ./reports/

  With both reports:
    pyats run job jobs/run_layer2.py --testbed testbeds/testbed.yaml --html-logs ./reports/ --json-logs ./reports/

  Debug mode:
    pyats run job jobs/run_layer2.py --testbed testbeds/testbed.yaml --loglevel DEBUG
"""

from pyats.easypy import run
import os


def main(runtime):
    """
    Main job function for Layer 2 validation.

    This job executes the Layer 2 test suite which validates:
    - VLAN configuration and state
    - Trunk port configuration
    - Spanning Tree Protocol (STP/RSTP)
    - Port Channel/LACP configuration
    - MAC address table learning
    - LLDP neighbor discovery
    """
    runtime.job.name = 'Layer 2 Validation'

    # Get report directory from environment or use default
    report_dir = os.environ.get('PYATS_REPORT_DIR', './reports')

    # Enable HTML reports if specified via environment
    if os.environ.get('PYATS_HTML_REPORTS', '').lower() == 'true':
        runtime.html_logs = report_dir

    # Enable JSON reports if specified via environment
    if os.environ.get('PYATS_JSON_REPORTS', '').lower() == 'true':
        runtime.json_logs = report_dir

    # Run the test script
    run(
        testscript='tests/layer2/test_layer2.py',
        runtime=runtime,
        taskid='layer2_validation'
    )
