"""
pyATS Job File - Run Layer 2 Test Suite

This job runner executes the Layer 2 validation tests (STP, etc).

Usage:
  pyats run job jobs/run_layer2.py --testbed testbeds/testbed.yaml
"""

from pyats.easypy import run
import os

def main(runtime):
    runtime.job.name = 'Layer 2 Validation'

    # Run STP Tests
    run(
        testscript='tests/layer2/test_stp.py',
        runtime=runtime,
        taskid='stp_validation'
    )
    
    # Can add more L2 tests here in the future
