"""
pyATS Job File for OSPF Health Validation

Usage:
  Basic:
    pyats run job jobs/run_ospf.py --testbed testbeds/testbed.yaml

  With HTML reports:
    pyats run job jobs/run_ospf.py --testbed testbeds/testbed.yaml --html-logs ./reports/

  With JSON reports:
    pyats run job jobs/run_ospf.py --testbed testbeds/testbed.yaml --json-logs ./reports/

  With both reports:
    pyats run job jobs/run_ospf.py --testbed testbeds/testbed.yaml --html-logs ./reports/ --json-logs ./reports/

  Debug mode:
    pyats run job jobs/run_ospf.py --testbed testbeds/testbed.yaml --loglevel DEBUG
"""

from pyats.easypy import run
import os
import logging

logger = logging.getLogger(__name__)


def main(runtime):
    """
    Main job function for OSPF health validation.

    This job executes only the OSPF neighbor verification test from the
    MPLS core test suite, checking that all expected OSPF neighbors are
    in FULL state.
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

    logger.info('Running OSPF neighbor verification...')

    # Run only the OSPF test from the MPLS core suite
    run(
        testscript='tests/layer3/test_mpls_core.py',
        runtime=runtime,
        taskid='ospf_health_check',
        test_case='OspfNeighbors',
    )

    logger.info('OSPF health validation complete')
