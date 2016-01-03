import warnings
warnings.filterwarnings("ignore")

from openmdao.api import Component, Group, Problem, IndepVarComp
from openmdao.api import ScipyOptimizer

import numpy as np

from parser import parse_data

from solar import Panels, Batteries, DataSource, Costs
from make_plot import make_plot

class GreenhouseLoads(Component):
    def __init__(self, n):
        super(GreenhouseLoads, self).__init__()
        self.n = n

        self.add_param("cell_temperature", np.zeros(self.n), units="degF")
        self.add_param("ambient_temperature", np.zeros(self.n), units="degF")
        self.add_param("hour", np.zeros(self.n), units="h")
        self.add_param("day", np.zeros(self.n), units="d")
        self.add_param("weekday", np.zeros(self.n))
        self.add_param("month", np.zeros(self.n), units="mo")
        self.add_param("irradiance", np.zeros(self.n))
        self.add_param("wind", np.zeros(self.n), units="m/s")
        self.add_param("P_base", np.zeros(self.n), units="W")
        self.add_param("P_generated", np.zeros(self.n), units="W")

        self.add_output("P_consumption_direct", np.zeros(self.n), units="W")
        self.add_output("P_consumption", np.zeros(self.n), units="W")

    def solve_nonlinear(self, p, u, r):
        # reset power load values for each execution
        u['P_consumption'] = np.zeros(self.n)
        
        # constant background load - microcontroller 3 W
        u['P_consumption'] += 3

        # run a 15 W cooling fan as a direct load when ambient temp > 60
        # between april and october
        idx = np.where((p['P_generated'] >= 15) & 
                       (p['ambient_temperature'] >= 60) &
                       (p['month'] >= 4) & 
                       (p['month'] <= 10))
        u['P_consumption'][idx] += 15
        u['P_consumption_direct'][idx] += 15

        # water pumps irrigate every day at noon between april and october
        # 5 gallons moved per day
        idx = np.where((p['hour'] == 12) & 
                       (p['month'] >= 4) & 
                       (p['month'] <= 10))
        pump_power = 5.0 / 200.0 * 50.0
        u['P_consumption'][idx] += pump_power

        # constant trickle charging of tool batteries, 6 W
        u['P_consumption'] += 6

        # On-demand full charging 80 W for 1 hour 
        # once per week on saturday at 5pm, between March and October
        idx = np.where((p['hour'] == 17) & 
                       (p['month'] >= 3) & 
                       (p['month'] <= 10) &
                       (p['weekday'] == 6))
        u['P_consumption'][idx] += 80.0


class Greenhouse(Group):

    def __init__(self):
        super(Greenhouse, self).__init__()
        self.add("data", DataSource())
        n = self.data.n

        params = (
            ('panels_array_power', 100.0, {'units' : 'W'}),
            ('power_capacity', 50.0, {'units' : 'W*h'}),
        )
        self.add('des_vars', IndepVarComp(params))


        self.add("panels", Panels(n))
        self.add("batteries", Batteries(n))
        self.add("loads", GreenhouseLoads(n))
        self.add("cost", Costs())

        self.connect("des_vars.panels_array_power", ["panels.array_power", "cost.array_power"])
        self.connect("des_vars.power_capacity", ["batteries.power_capacity", "cost.power_capacity"])

        self.connect("data.P_base", ["panels.P_base", "loads.P_base"])
        self.connect("data.ambient_temperature", "loads.ambient_temperature")
        self.connect("data.cell_temperature", "loads.cell_temperature")
        self.connect("data.wind", "loads.wind")
        self.connect("data.irradiance", "loads.irradiance")
        self.connect("data.hour", "loads.hour")
        self.connect("data.day", "loads.day")
        self.connect("data.weekday", "loads.weekday")
        self.connect("data.month", "loads.month")

        self.connect("panels.P_generated", ["batteries.P_generated", "loads.P_generated"])
        self.connect("loads.P_consumption", "batteries.P_consumption")


if __name__ == "__main__":
    import pylab

    top = Problem()
    top.root = Greenhouse()
    top.root.fd_options['force_fd'] = True
    top.root.fd_options['step_size'] = 1.0
    
    top.setup(check=False)

    top['des_vars.panels_array_power'] = 350.0
    top['des_vars.power_capacity'] = 12*100

    top.run()
    fig = make_plot(top)

    pylab.show()


