from __future__ import division

import numpy as np
from copy import copy

def _add_noise(params, check_valid_func=None, bounds=None, noise=.1, exclude_params=()):
    """Add individual noise to each parameter.

        :Arguments:
            params : dict
                Parameter names and values

        :Optional:
            check_valid_func : function <default lambda x: True>
                Function that takes as input the parameters as kwds
                and returns True if param values are admissable.
            bounds : dict <default={}>
                Dict containing parameter names and
                (lower, upper) value for valid parameter
                range.
            noise : float <default=.1>
                Standard deviation of random gaussian
                variable to add to each parameter.
            exclude_params : tuple <default=()>
                Do not add noise to these parameters.

        :Returns:
            params : dict
                parameters with noise added.

    """

    def normal_rand(mu, sigma):
        if sigma == 0:
            return mu
        else:
            return np.random.normal(loc=mu, scale=sigma)

    def sample_value(param, value):
        if np.isscalar(noise):
            param_noise = noise
        else:
            param_noise = noise.get(param, 0)

        if param in bounds:
            while True:
                sampled_value = normal_rand(value, param_noise)
                if sampled_value >= bounds[param][0] and sampled_value <= bounds[param][1]:
                    return sampled_value
        else:
            return normal_rand(value, param_noise)

    if bounds is None:
        bounds = {}

    if check_valid_func is None:
        check_valid_func = lambda **params: True

    # Sample parameters until accepted
    while True:
        params_cur = copy(params)

        for param, value in params_cur.iteritems():
            if param not in exclude_params:
                params_cur[param] = sample_value(param, value)

        if check_valid_func(**params_cur):
            return params_cur

def gen_rand_data(Stochastic, params, size=50, subjs=1, subj_noise=.1, exclude_params=(),
                  column_name='data', check_valid_func=None, bounds=None, seed=None):
    """Generate a random dataset using a user-defined random distribution.

    :Arguments:
        Stochastic : a pymc stochastic class of the target distribution (e.g., pymc.Normal)
        params : dict
            Parameters to use for data generation. Two options possible:
                * {'param1': value, 'param2': value2}
                * {'condition1': {'param1': value, 'param2': value2},
                   'condition2': {'param1': value3, 'param2': value4}}
            In the second case, the dataset is generated with multiple conditions
            named after the key and will be sampled using the corresponding parameters.

    :Optional:
        size : int <default: 50>
            How many values to sample for each condition for each subject.
        subjs : int <default: 1>
            How many subjects to generate data from. Individual subject parameters
            will be normal distributed around the provided parameters with variance
            subj_noise if subjs > 1. If only one subject is simulated no noise is added.
        subj_noise : float or dictionary <default: .1>
            How much to perturb individual subj parameters.
            if float then each parameter will be sampled from a normal distribution with std of subj_noise.
            if dictionary then only parameters that are keys of subj_noise will be sampled, and the std of the sampling
            distribution will be the value associated with them.
        exclude_params : tuple <default ()>
            Do not add noise to these parameters.
        check_valid_func : function <default lambda x: True>
            Function that takes as input the parameters as kwds
            and returns True if param values are admissable.
        bounds : dict <default={}>
            Dict containing parameter names and
            (lower, upper) value for valid parameter
            range.
        column_name : str <default='data'>
            What to name the data column.

    :Returns:
        data : numpy structured array
            Will contain the columns 'subj_idx', 'condition' and 'data' which contains
            the random samples.
        subj_params : dict mapping condition to list of individual subject parameters
            Tries to be smart and will return direct values if there is only 1 subject
            and no dict if there is only 1 condition.

    """
    from itertools import product

    # Check if only dict of params was passed, i.e. no conditions
    if not isinstance(params[params.keys()[0]], dict):
        params = {'none': params}


    subj_params = {}
    dtype = Stochastic('temp', size=2, **(params.values()[0])).dtype
    if seed is not None:
        np.random.seed(seed)

    idx = list(product(range(subjs), params.keys(), range(size)))
    data = np.array(idx, dtype=[('subj_idx', np.int32), ('condition', 'S20'), (column_name, dtype)])

    for condition, param in params.iteritems():
        subj_params[condition] = []
        for subj_idx in range(subjs):
            if subjs > 1:
                # Sample subject parameters from a normal around the specified parameters
                subj_param = _add_noise(param, noise=subj_noise,
                                        check_valid_func=check_valid_func,
                                        bounds=bounds,
                                        exclude_params=exclude_params)
            else:
                subj_param = param
            subj_params[condition].append(subj_param)
            samples_from_dist = Stochastic('temp', size=size, **subj_param).value
            idx = (data['subj_idx'] == subj_idx) & (data['condition'] == condition)
            data[column_name][idx] = np.array(samples_from_dist, dtype=dtype)

    # Remove list around subj_params if there is only 1 subject
    if subjs == 1:
        for key, val in subj_params.iteritems():
            subj_params[key] = val[0]

    # Remove dict around subj_params if there is only 1 condition
    if len(subj_params) == 1:
        subj_params = subj_params[subj_params.keys()[0]]

    return data, subj_params

