import pymc as pm
import kabuki
from kabuki import Parameter

class Regression(kabuki.Hierarchical):
    def __init__(self, data, **kwargs):
        super(Regression, self).__init__(data, **kwargs)

        self.params = [Parameter('beta', lower=-100, upper=100, init=0),
                       Parameter('sigma', lower=1e-8, upper=100, init=.1),
                       Parameter('like', is_bottom_node=True)]

    def get_bottom_node(self, param, params):
        if param.name == 'like':
            # Create likelihood
            return pm.Normal(param.full_name,
                             mu=params['mu'],
                             tau=params['sigma']**-2,
                             value=param.data['value'],
                             observed=True)

        else:
            print "Not found."
