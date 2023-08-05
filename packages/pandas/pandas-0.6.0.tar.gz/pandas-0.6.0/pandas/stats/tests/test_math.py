import pandas.stats.math as math
import numpy as np

def test_rank():
    x = np.zeros(10)
    assert(math.rank(x) == 0)
    x = np.ones(10)
    assert(math.rank(x) == 1)

def test_inv():
    # test singular matrix
    math.inv(np.ones((3, 3)))

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)


