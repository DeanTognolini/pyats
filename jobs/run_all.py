"""
pyATS Job File - Run All Test Suites

This job runner executes all available test suites in the repository.
It will automatically discover and run tests from:
- tests/layer1/
- tests/layer2/
- tests/layer3/
- Any other test directories you add

Usage:
  Basic:
    pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml

  With HTML reports:
    pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs ./reports/

  With JSON reports:
    pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --json-logs ./reports/

  With both reports:
    pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs ./reports/ --json-logs ./reports/

  Run specific test suites only:
    export PYATS_TEST_SUITES="layer1,layer3"
    pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml

  Debug mode:
    pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --loglevel DEBUG
"""

from pyats.easypy import run
import os
import glob


def main(runtime):
    """
    Main job function that runs all test suites.

    This job will:
    1. Discover all test_*.py files in tests/ subdirectories
    2. Execute each test suite sequentially
    3. Generate consolidated reports

    Environment Variables:
        PYATS_TEST_SUITES: Comma-separated list of test suites to run (e.g., "layer1,layer3")
        PYATS_REPORT_DIR: Directory for reports (default: ./reports)
        PYATS_HTML_REPORTS: Enable HTML reports (true/false)
        PYATS_JSON_REPORTS: Enable JSON reports (true/false)
    """
    runtime.job.name = 'Network Validation - All Test Suites'

    # Get report directory from environment or use default
    report_dir = os.environ.get('PYATS_REPORT_DIR', './reports')

    # Enable HTML reports if specified via environment
    if os.environ.get('PYATS_HTML_REPORTS', '').lower() == 'true':
        runtime.html_logs = report_dir

    # Enable JSON reports if specified via environment
    if os.environ.get('PYATS_JSON_REPORTS', '').lower() == 'true':
        runtime.json_logs = report_dir

    # Check if specific test suites are requested
    test_suites_env = os.environ.get('PYATS_TEST_SUITES', '')
    if test_suites_env:
        # Run only specified test suites
        requested_suites = [suite.strip() for suite in test_suites_env.split(',')]
        test_scripts = []
        for suite in requested_suites:
            pattern = f'tests/{suite}/test_*.py'
            test_scripts.extend(glob.glob(pattern))
    else:
        # Auto-discover all test scripts
        test_scripts = glob.glob('tests/*/test_*.py')

    if not test_scripts:
        runtime.log.warning('No test scripts found!')
        runtime.log.warning('Make sure your test files follow the pattern: tests/<category>/test_*.py')
        return

    runtime.log.info(f'Found {len(test_scripts)} test suite(s) to execute:')
    for script in sorted(test_scripts):
        runtime.log.info(f'  - {script}')

    # Execute each test suite
    for testscript in sorted(test_scripts):
        # Extract test suite name for better logging
        suite_name = testscript.split('/')[-2] if '/' in testscript else 'unknown'

        runtime.log.info(f'Executing {suite_name} test suite...')

        run(
            testscript=testscript,
            runtime=runtime,
            taskid=f'{suite_name}_tests'
        )

    runtime.log.info('All test suites completed!')
