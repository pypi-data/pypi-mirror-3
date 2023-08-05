# mcint/integrate.py

import itertools

def integrate(integrand, sampler, measure=1.0, n=100):
    samples = list(itertools.islice(sampler(), n))
    # Compute the sum of samples
    ss = sum(samples)
    # Return answer
    return measure * ss / n
