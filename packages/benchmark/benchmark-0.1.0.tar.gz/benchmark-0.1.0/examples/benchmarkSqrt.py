import benchmark

import math

# Source
# http://stackoverflow.com/questions/327002/which-is-faster-in-python-x-5-or-math-sqrtx

class Benchmark_Sqrt(benchmark.Benchmark):
    
    def test_pow_operator(self):
        for i in xrange(750000):
            z = i**.5
    
    def test_pow_function(self):
        for i in xrange(750000):
            z = pow(i, .5)
    
    def test_sqrt_function(self):
        for i in xrange(750000):
            z = math.sqrt(i)

if __name__ == '__main__':
    benchmark.main(each=50, format="markdown")

#  Benchmark Report
#  ================
#  
#  Benchmark Sqrt
#  --------------
#  
#           name | rank | runs |           mean |               sd
#  --------------|------|------|----------------|-----------------
#   pow operator |    1 |   50 | 0.113651094437 | 0.00709087316343
#  sqrt function |    2 |   50 | 0.151987323761 | 0.00658830515608
#   pow function |    3 |   50 | 0.223314394951 |  0.0133163421349
#  
#  The functions above were run in random, nonconsecutive order by 
#  `benchmark` v0.1.0 (http://jspi.es/benchmark) with Python 2.7.1
#  Darwin-11.3.0-x86_64 on 2012-04-16 17:42:19.