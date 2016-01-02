import warnings
warnings.filterwarnings("ignore")

from openmdao.api import Problem
from lib.basic import Basic
from lib.make_plot import make_plot

import pylab
import click

@click.command()
@click.option('-data', default=None, help='NREL Data file(s) for your location. Separate file names by comma.')
@click.option('-o', default="result.png", help='Output figure file name (png format)')
@click.option('--efficiency', default=0.95, prompt='Power conversion efficiency',
              help='Power conversion efficiency')
@click.option('--panel_watt', default=100.0, prompt='Total rated panel power (Watt)',
              help='Total rated panel power for your system (Watt)')
@click.option('--battery_capacity', default = 50*12.0, prompt='Total battery power capacity (Watt-hr)',
              help='Total battery power capacity for your system (Watt-hr)')

@click.option('--power_use_constant', default=0.0, prompt='Constant background power load (Watt)',
              help='Constant background power load (Watt)')
@click.option('--power_use_daytime', default = 0.0, prompt='Daytime power load (Watt)',
              help='Daytime power load (Watt). This is added on top of the background power use, during daylight hours.')
@click.option('--power_use_nighttime', default=0.0, prompt='Nighttime power load (Watt)',
              help='Nighttime power load (Watt). This is added on top of the background power use, during night time hours.')
@click.option('--power_use_direct', default=0.0, prompt='Direct load (Watt)',
              help='Direct load (Watt). This is load that will be applied only when the available PV power can match it (ie. during the day in direct sunlight)')
@click.option('--direct_min_temp', default=-40.0, prompt='Direct load min temperature (Deg. F)',
              help='Direct load min temperature (Deg. F). The direct load value will only be applied if the ambient temperature is above this optional level. Useful for direct solar water pumps, etc.')


@click.option('--start_time', default=0.0, prompt='Start time cut-off (hour 0-23)',
              help='Start time cut-off (hour 0-23). Collected PV power before this hour is set to zero. Used to model obstruction at dawn.')
@click.option('--end_time', default=23.0, prompt='End time cut-off (hour 0-23)',
              help='End time cut-off (hour 0-23). Collected PV power after this hour is set to zero. Used to model obstruction at dusk')

def hello(data, efficiency, battery_capacity, panel_watt, power_use_daytime, 
          power_use_nighttime, power_use_constant, start_time, end_time, o,
          power_use_direct, direct_min_temp):
    """Solar calculation application"""

    if data != None:
        data = data.split(",")

    top = Problem()
    top.root = Basic(start_time=start_time, end_time=end_time, fns=data,
                     efficiency = efficiency)
    top.setup(check=False)

    top['loads.P_constant'] = power_use_constant
    top['loads.P_daytime'] = power_use_daytime
    top['loads.P_nighttime'] = power_use_nighttime
    top['loads.P_direct'] = power_use_direct
    top['loads.switch_temp'] = direct_min_temp

    top['des_vars.panels_array_power'] = panel_watt
    top['des_vars.power_capacity'] = battery_capacity

    fig = make_plot(top)

    fig.savefig(o, format=o.split(".")[-1], bbox_inches='tight', 
               pad_inches=0)

if __name__ == '__main__':
    hello()