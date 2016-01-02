import warnings
warnings.filterwarnings("ignore")

from openmdao.api import Problem
from basic import Basic
from make_plot import make_plot
import os
import pylab

import unittest


class TestRun(unittest.TestCase):

    def test_basic(self):
        top = Problem()
        top.root = Basic()
        top.setup(check=False)

        top['loads.P_constant'] = 1

        top['des_vars.panels_array_power'] = 100
        top['des_vars.power_capacity'] = 30

        top.run()

        soc_min = top['batteries.SOC'].min()
        self.assertAlmostEqual(0.433333124802, soc_min)

    def test_plot(self):
        top = Problem()
        top.root = Basic()
        top.setup(check=False)

        top['loads.P_constant'] = 10

        top['des_vars.panels_array_power'] = 300
        top['des_vars.power_capacity'] = 420

        top.run()

        fig = make_plot(top)
        fig.savefig("test_fig.png", format="png", bbox_inches='tight', 
               pad_inches=0)

        assert os.path.exists("test_fig.png")
        try:
            os.remove("test_fig.png")
        except:
            pass

if __name__ == "__main__":
    unittest.main()