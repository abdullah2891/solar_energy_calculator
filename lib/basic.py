import warnings
warnings.filterwarnings("ignore")

from openmdao.api import Component, Group, Problem, IndepVarComp

import numpy as np

from parser import parse_data

from solar import Panels, Batteries, DataSource, Costs
from make_plot import make_plot

class BasicLoads(Component):
    """
    A very basic PV solar load component. Has constant power draws, and direct loading.
    """
    def __init__(self, n):
        super(BasicLoads, self).__init__()
        self.n = n

        self.add_param("P_constant", 0.0, units="W")
        self.add_param("P_direct", 0.0, units="W")
        self.add_param("P_daytime", 0.0, units="W")
        self.add_param("P_nighttime", 0.0, units="W") 
        self.add_param("switch_temp", 0.0, units="degF")

        self.add_param("P_generated", np.zeros(self.n), units="W")
        self.add_param("cell_temperature", np.zeros(self.n), units="degF")
        self.add_param("ambient_temperature", np.zeros(self.n), units="degF")
        self.add_param("hour", np.zeros(self.n), units="h")
        self.add_param("irradiance", np.zeros(self.n))
        self.add_param("wind", np.zeros(self.n), units="m/s")
        self.add_param("P_base", np.zeros(self.n), units="W")
        self.add_output("P_consumption", np.zeros(self.n), units="W")
        self.add_output("P_consumption_direct", np.zeros(self.n), units="W")


    def solve_nonlinear(self, p, u, r):
        # constant background consumption
        u['P_consumption'] = np.zeros(self.n)
        u['P_consumption'] += p['P_constant']

        # daytime - based on PV
        idx = np.where(p['P_base'] >= 0.01)
        u['P_consumption'][idx] += p['P_daytime']

        # nightime - based on irradiance
        idx = np.where(p['irradiance'] < 10.0)
        u['P_consumption'][idx] += p['P_nighttime']

        # direct load - based on available power
        idx = np.where((p['P_generated'] >= p['P_direct']) & (p['ambient_temperature'] >= p['switch_temp']))
        u['P_consumption'][idx] += p['P_direct']
        u['P_consumption_direct'][idx] += p['P_direct']



class Basic(Group):
    """
    Simple solar PV model. Collects all components, and establishes data 
    relationships.
    """
    def __init__(self, start_time=10, end_time=15, fns=None, efficiency = 0.95):
        super(Basic, self).__init__()
        
        # add NREL data parsing component
        self.add("data", DataSource(start_time=start_time, end_time=end_time, 
            fns=fns, efficiency = efficiency))
        n = self.data.n

        # Not necessary at this point, but the variables exposed here can be
        # used later for numerical optimization (or anything that makes use
        # of model total derivative calculations)
        params = (
            ('panels_array_power', 100.0, {'units' : 'W'}),
            ('power_capacity', 50.0, {'units' : 'W*h'}),
        )
        self.add('des_vars', IndepVarComp(params))

        # PV panel component
        self.add("panels", Panels(n))
        # Battery component
        self.add("batteries", Batteries(n))
        # Load component
        self.add("loads", BasicLoads(n))
        # Cost component
        self.add("cost", Costs())   

        # Data relationships
        self.connect("des_vars.panels_array_power", ["panels.array_power", "cost.array_power"])
        self.connect("des_vars.power_capacity", ["batteries.power_capacity", "cost.power_capacity"])

        self.connect("data.P_base", ["panels.P_base", "loads.P_base"])
        self.connect("data.ambient_temperature", "loads.ambient_temperature")
        self.connect("data.cell_temperature", "loads.cell_temperature")
        self.connect("data.wind", "loads.wind")
        self.connect("data.irradiance", "loads.irradiance")
        self.connect("data.hour", "loads.hour")

        self.connect("panels.P_generated", ["batteries.P_generated", "loads.P_generated"])
        self.connect("loads.P_consumption", "batteries.P_consumption")


if __name__ == "__main__":
    import pylab

    top = Problem()
    top.root = Basic(start_time=0, end_time=23)
    
    top.setup(check=False)

    top['loads.P_constant'] = 0.1
    top['loads.P_daytime'] = 0.0
    top['loads.P_nighttime'] = 0.0
    top['loads.P_direct'] = 0.0
    top['loads.switch_temp'] = 0.0

    top['des_vars.panels_array_power'] = 5.2 # Watts
    top['des_vars.power_capacity'] = 3.7*2 # Watt-hours

    top.run()
    
    fig = make_plot(top)

    pylab.show()



