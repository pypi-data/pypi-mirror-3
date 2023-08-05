========================
 Monte Carlo integrator
========================

This package provides a Monte Carlo integrator which can be used to evaluate
multi-dimensional integrals. The results are numerical approximations which are
dependent on the use of random number generation.

Example 1
=========

In this example we compute :math:`\int_0^1 x^2 dx`::

    import mcint
    import random
    
    def integrand(x): # Describe the function being integrated
        return (x**2)
    
    def sampler(): # Describe how Monte Carlo samples are taken
        while True:
            yield random.random()
    
    result, error = mcint.integrate(integrand, sampler(), measure=1.0, n=100)
    
    print "The integral of x**2 between 0 and 1 is approximately", result

The second argument to the integrate() function should be an iterable
expression, in this case it is a generator. We could do away with this sampler
using the following::

    result, error = mcint.integrate(integrand, iter(random.random, -1), measure=1.0, n=100)

This creates an iterable object from the random.random() function which will
continuously call random.random() until it returns -1 (which it will never do as
it returns values between 0.0 and 1.0.

Example 2
=========

In this example we compute :math:`\int_0^1 \int_0^\sqrt{1-y^2} x^2+y^2 dx dy`::

    import mcint
    import random
    import math
    
    def integrand(x):
        return (x[0]**2 + x[1]**2)
    
    def sampler():
        while True:
            y = random.random()
            x = random.random()
            if x**2+y**2 <= 1:
                yield (x,y)
    
    result, error = mcint.integrate(integrand, sampler(), measure=math.pi/4)
