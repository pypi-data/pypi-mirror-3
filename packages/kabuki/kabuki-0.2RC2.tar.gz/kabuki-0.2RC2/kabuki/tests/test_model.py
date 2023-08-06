import kabuki
import kabuki.generate
import scipy.stats
from kabuki.hierarchical import *
import pymc as pm

# Build a very simple model

class TestModel(Hierarchical):
    def create_params(self):
        loc = pm.Uniform('loc', lower=-10, upper=10)
        var = pm.Uniform('var', lower=1e-8, upper=10)
        subj = pm.Normal('subj', mu=loc, tau=var)
        mu = HNode('mu', subj_knode=subj, group_knode=loc, var_knode=var)

        like_node = pm.Normal('like', mu=subj, tau=1)
        like = HNode('like', is_bottom_node=True, subj_knode=like_node)
        return [mu, like]

normal_like = kabuki.utils.scipy_stochastic(scipy.stats.distributions.norm_gen, name='normal', longname='normal')
data = kabuki.generate.gen_rand_data(normal_like, subjs=4, params={'mu': 0, 'tau':1})[0]

model = TestModel(data)
model.sample(20000)
