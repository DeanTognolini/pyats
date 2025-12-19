"""
pyATS Job File for MPLS Core Validation

Executes the MPLS core test suite to validate:
- LDP neighbor adjacencies
- OSPF neighbor relationships (for MPLS underlay)
- P router loopback connectivity
- LSP path establishment

Usage:
  Basic:
    pyats run job jobs/run_mpls.py --testbed testbeds/mpls_testbed.yaml

  With HTML reports:
    pyats run job jobs/run_mpls.py --testbed testbeds/mpls_testbed.yaml --html-logs ./reports/

  With JSON reports:
    pyats run job jobs/run_mpls.py --testbed testbeds/mpls_testbed.yaml --json-logs ./reports/

  Debug mode:
    pyats run job jobs/run_mpls.py --testbed testbeds/mpls_testbed.yaml --loglevel DEBUG
"""

from pyats.easypy import run
import os
import logging

logger = logging.getLogger(__name__)

TESTSCRIPT = 'tests/layer3/test_mpls_core.py'


def main(runtime):
    """
    Main job function for MPLS core validation.

    This job executes the MPLS core test suite which validates:
    - LdpNeighbors: LDP adjacency verification
    - OspfNeighbors: OSPF neighbor state (MPLS underlay)
    - LoopbackConnectivity: P router loopback reachability
    - LspPath: LSP establishment for critical destinations
    """
    runtime.job.name = 'MPLS Core Validation'

    # Get report directory from environment or use default
    report_dir = os.environ.get('PYATS_REPORT_DIR', './reports')

    # Enable HTML reports if specified via environment
    if os.environ.get('PYATS_HTML_REPORTS', '').lower() == 'true':
        runtime.html_logs = report_dir

    # Enable JSON reports if specified via environment
    if os.environ.get('PYATS_JSON_REPORTS', '').lower() == 'true':
        runtime.json_logs = report_dir

    # Verify test script exists
    if not os.path.exists(TESTSCRIPT):
        logger.error(f'Test script not found: {TESTSCRIPT}')
        return

    logger.info('Executing MPLS core validation test suite...')

    run(
        testscript=TESTSCRIPT,
        runtime=runtime,
        taskid='mpls_core',
    )

    logger.info('MPLS core validation complete')
