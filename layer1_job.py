"""
pyATS Job File for Layer 1 Validation
Run with: pyats run job layer1_job.py --testbed testbed.yaml
"""

from pyats.easypy import run


def main(runtime):
    runtime.job.name = 'Layer 1 Validation'

    run(
        testscript='layer1_tests.py',
        runtime=runtime,
    )
