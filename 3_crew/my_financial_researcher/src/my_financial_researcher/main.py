#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from .crew import MyFinancialResearcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the financial researcher crew
    """

    inputs = {
        'company': 'Interglobe Aviation'
    }
    result = MyFinancialResearcher().crew().kickoff(inputs=inputs)
    print(result.raw)

if __name__ == '__main__':
    run()