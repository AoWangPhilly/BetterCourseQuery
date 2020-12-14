import pandas as pd
import numpy as np
import os
import glob

class TMSQuery():
    def __init__(self):
        pass
    
if __name__ == '__main__':
    fall = os.path.join('DREXEL', 'FALL', 'Col of Computing & Informatics', 'CS.csv')
    df = pd.read_csv(fall);
    print(df)
