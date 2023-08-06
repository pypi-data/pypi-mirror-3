import benchmark

import math

# Source
# http://stackoverflow.com/questions/327002/which-is-faster-in-python-x-5-or-math-sqrtx

class Benchmark_Sqrt(benchmark.Benchmark):

    each = 100

    def setUp(self):
        self.size = 25000

    def test_pow_operator(self):
        for i in xrange(self.size):
            z = i**.5
    
    def test_pow_function(self):
        for i in xrange(self.size):
            z = pow(i, .5)
    
    def test_sqrt_function(self):
        for i in xrange(self.size):
            z = math.sqrt(i)

class Benchmark_Sqrt2(Benchmark_Sqrt):

    label = "Benchmark Sqrt on a larger range"
    
    each = 50
    
    def setUp(self):
        self.size = 750000


if __name__ == '__main__':
    benchmark.main(format="markdown") 
    # could have written benchmark.main(each=50)

#    Benchmark Report
#    ================
#
#    Benchmark Sqrt
#    --------------
#
#             name | rank | runs |             mean |                sd
#    --------------|------|------|------------------|------------------
#     pow operator |    1 |  100 | 0.00398081541061 | 0.000712735404794
#    sqrt function |    2 |  100 | 0.00518546819687 | 0.000691936907173
#     pow function |    3 |  100 | 0.00728440284729 |  0.00133268917025
#
#    Benchmark Sqrt on a larger range
#    --------------------------------
#
#             name | rank | runs |           mean |               sd
#    --------------|------|------|----------------|-----------------
#     pow operator |    1 |   50 | 0.112720785141 | 0.00579241912336
#    sqrt function |    2 |   50 | 0.152897367477 |  0.0075897918245
#     pow function |    3 |   50 | 0.211021671295 |  0.0139702154247
#
#    Each of the above 450 runs were run in random, non-consecutive order by
#    `benchmark` v0.1.2 (http://jspi.es/benchmark) with Python 2.7.1
#    Darwin-11.3.0-x86_64 on 2012-04-17 16:39:10.
