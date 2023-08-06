# Sample configurable:
from IPython.config.configurable import Configurable
from IPython.utils.traitlets import *

class Model(Configurable):
    name = Unicode(u'defaultname', config=True)
    model_type = String('kabuki.Regression')
    data = String('data.csv')
    depends_on = Dict()
    kwargs = Dict()
    samples = Int(5000)
    burn = Int(1000)
    thin = Int(3)

