"""
pyATS Job File for REP (Resilient Ethernet Protocol) Validation

Executes the REP health check test suite to validate:
- REP segment health and configuration
- REP neighbor relationships
- REP topology consistency
- REP blocked port status
- REP interface operational state

Usage:
  Basic:
    pyats run job jobs/run_rep.py --testbed testbeds/rep_testbed.yaml

  With HTML reports:
    pyats run job jobs/run_rep.py --testbed testbeds/rep_testbed.yaml --html-logs ./reports/

  With JSON reports:
    pyats run job jobs/run_rep.py --testbed testbeds/rep_testbed.yaml --json-logs ./reports/

  Debug mode:
    pyats run job jobs/run_rep.py --testbed testbeds/rep_testbed.yaml --loglevel DEBUG
"""

from pyats.easypy import run
import os
import logging

logger = logging.getLogger(__name__)

TESTSCRIPT = 'tests/layer2/test_rep.py'


def main(runtime):
    """
    Main job function for REP health validation.

    This job executes the REP health test suite which validates:
    - RepSegmentHealth: Segment status, role verification
    - RepNeighborHealth: Neighbor discovery and adjacency
    - RepTopologyHealth: Topology completeness, segment ID
    - RepBlockedPortHealth: Blocked port verification
    - RepInterfaceHealth: Interface status and operational state
    """
    runtime.job.name = 'REP Health Validation'

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

    logger.info('Executing REP health validation test suite...')

    run(
        testscript=TESTSCRIPT,
        runtime=runtime,
        taskid='rep_health',
    )

    logger.info('REP health validation complete')
