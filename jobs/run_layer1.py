"""
pyATS Job File for Layer 1 Validation

Usage:
  Basic:
    pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml

  With HTML reports:
    pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml --html-logs ./reports/

  With JSON reports:
    pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml --json-logs ./reports/

  With both reports:
    pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml --html-logs ./reports/ --json-logs ./reports/

  Debug mode:
    pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml --loglevel DEBUG
"""

from pyats.easypy import run
import os


def main(runtime):
    """
    Main job function for Layer 1 validation.

    This job executes the Layer 1 test suite which validates:
    - Link status (up/up verification)
    - Optical power levels
    - Interface errors
    - Speed/duplex configuration
    - MTU settings
    - CDP neighbor verification
    """
    runtime.job.name = 'Layer 1 Validation'

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
        testscript='tests/layer1/test_layer1.py',
        runtime=runtime,
    )
