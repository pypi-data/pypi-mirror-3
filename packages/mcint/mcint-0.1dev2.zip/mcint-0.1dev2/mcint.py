# mcint/integrate.py

import itertools

def integrate(integrand, sampler, measure=1.0, n=100):
    scale = float(measure/n)
    result = 0.0
    for i in range(n):
        x = sampler().next()
        result += scale * integrand(x)
    # Return answer
    return result
