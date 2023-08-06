import unittests
import kabuki
import kabuki.regression
import numpy as np
import pandas as pd

class TestRegression(unittests.UnitTest):
    def __init__(self, *args, **kwargs):
        super(TestRegression, self).__init__(*args, **kwargs)

        # Generate data
        subjs = 10
        samples_per_group = 200
        group_mean = 0.
        group_sigma = 1.
        group_beta = 1.

        #index = pd.MultiIndex()
        samples = pd.DataFrame(subjs*samples_per_group, {'subj_idx': int, 'value': np.float32})
        for subj in range(subjs):


