"""
Thpppt your heart out
"""

import warnings

with warnings.catch_warnings() as wr:
    warnings.filterwarnings("ignore", category = SyntaxWarning)
    from thpppt import main

if __name__ == '__main__':
    main()
