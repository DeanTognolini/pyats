"""
pyATS Job File for OSPF Health Validation

Executes the OSPF health check test suite to validate:
- OSPF process health and configuration
- OSPF neighbor relationships
- OSPF interface status
- OSPF database consistency
- OSPF routes in routing table

Usage:
  Basic:
    pyats run job jobs/run_ospf.py --testbed testbeds/ospf_testbed.yaml

  With HTML reports:
    pyats run job jobs/run_ospf.py --testbed testbeds/ospf_testbed.yaml --html-logs ./reports/

  With JSON reports:
    pyats run job jobs/run_ospf.py --testbed testbeds/ospf_testbed.yaml --json-logs ./reports/

  Debug mode:
    pyats run job jobs/run_ospf.py --testbed testbeds/ospf_testbed.yaml --loglevel DEBUG
"""

from pyats.easypy import run
import os
import logging

logger = logging.getLogger(__name__)

TESTSCRIPT = 'tests/layer3/test_ospf_health.py'


def main(runtime):
    """
    Main job function for OSPF health validation.

    This job executes the OSPF health test suite which validates:
    - OspfProcessHealth: Process status, router ID, SPF timing
    - OspfNeighborHealth: Neighbor states, dead timers
    - OspfInterfaceHealth: Interface status, costs
    - OspfDatabaseHealth: LSA presence, area configuration
    - OspfRouteHealth: Expected routes, route counts
    """
    runtime.job.name = 'OSPF Health Validation'

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

    logger.info('Executing OSPF health validation test suite...')

    run(
        testscript=TESTSCRIPT,
        runtime=runtime,
        taskid='ospf_health',
    )

    logger.info('OSPF health validation complete')
