"""
pyATS Job File for Layer 3 Validation

Usage:
  Basic:
    pyats run job jobs/run_layer3.py --testbed testbeds/mpls_testbed.yaml

  With HTML reports:
    pyats run job jobs/run_layer3.py --testbed testbeds/mpls_testbed.yaml --html-logs ./reports/

  With JSON reports:
    pyats run job jobs/run_layer3.py --testbed testbeds/mpls_testbed.yaml --json-logs ./reports/

  With both reports:
    pyats run job jobs/run_layer3.py --testbed testbeds/mpls_testbed.yaml --html-logs ./reports/ --json-logs ./reports/

  Debug mode:
    pyats run job jobs/run_layer3.py --testbed testbeds/mpls_testbed.yaml --loglevel DEBUG
"""

from pyats.easypy import run
import os
import glob
import logging

logger = logging.getLogger(__name__)


def main(runtime):
    """
    Main job function for Layer 3 validation.

    This job executes all Layer 3 test suites which validate:
    - MPLS Core (LDP neighbors, labels, OSPF, loopback connectivity, LSP paths)
    - Additional Layer 3 tests as they are added
    """
    runtime.job.name = 'Layer 3 Validation'

    # Get report directory from environment or use default
    report_dir = os.environ.get('PYATS_REPORT_DIR', './reports')

    # Enable HTML reports if specified via environment
    if os.environ.get('PYATS_HTML_REPORTS', '').lower() == 'true':
        runtime.html_logs = report_dir

    # Enable JSON reports if specified via environment
    if os.environ.get('PYATS_JSON_REPORTS', '').lower() == 'true':
        runtime.json_logs = report_dir

    # Find all Layer 3 test scripts
    test_scripts = glob.glob('tests/layer3/test_*.py')

    if not test_scripts:
        logger.warning('No Layer 3 test scripts found in tests/layer3/')
        return

    logger.info(f'Found {len(test_scripts)} Layer 3 test suite(s) to execute:')
    for script in sorted(test_scripts):
        logger.info(f'  - {script}')

    # Run each test script
    for testscript in sorted(test_scripts):
        script_name = testscript.split('/')[-1].replace('test_', '').replace('.py', '')
        logger.info(f'Executing {script_name} test suite...')

        run(
            testscript=testscript,
            runtime=runtime,
            taskid=f'layer3_{script_name}',
        )

    logger.info('Layer 3 validation complete')
