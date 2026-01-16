#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from .crew import MyStockPicker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the research crew
    """

    inputs = {
        'sector': 'Consumption and FMCG'
    }

    result = MyStockPicker().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== Final Decision ===\n\n")
    print(result.raw)

if __name__ == "__main__":
    run()