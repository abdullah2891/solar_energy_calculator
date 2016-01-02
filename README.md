Solar energy budget calculator
===============================

This is a python code that implements a power budget model for the sizing and
analysis of ground-based photo-voltaic energy systems, included battery storage.

The core of this code is a model which implements a transient power balance
calculation, culminating in a time integration of a battery bank state-of-charge over time. This model was written using NASA's OpenMDAO framework, and makes use of data from
the U.S. Department of Energy's National Renewable Energy Laboratory (NREL).
This model is contained in `solar.py`. The file `basic.py` includes an example
model of powered loads and overall problem specification. This is used to 
make the end-user command line interface problem, `run.py`

Requirements
---------------
- Python 2.7 or 3.4 or higher
- Numpy, scipy, matplotlib 
- [OpenMDAO 1.0](https://github.com/OpenMDAO/OpenMDAO) or greater: `pip install openmdao`

Summary of end-user application
---------------------
This application allows the user to visualize the performance of a photovoltaic 
energy collection and storage system based on a variety of parameters:
    - Physical location
    - PV array size (in rated watts)
    - Battery bank size (in Watt-hours)
    - Load specification (constant, daytime, or night time)

Using location-based data, the time series model then simulates one-year of 
operation of the described system, on an hour-by-hour basis. Below is an example
of the figure produced for a 100w panel + 360 Watt-hour battery system powering a constant 5 Watt load (lights, sensors, etc.):

This transient analysis is what differentiates this code from other solar energy calculators.

Limitations and assumptions:
------------
- The array is assumed to be non-tracing and pointed and tilted based on the values given in the downloaded NREL data (see below). An active-tracing or manual re-tilted array can be expected to extract more energy over time.
- The described model is entirely based in simple power balancing. Losses due DC-DC conversion, transmission loss or power inversion are not modeled. In fact, you'll notice that panel vs battery vs load voltages are not parameterized at all. Thus efficiency losses in conversion and transmission must be taken account into the load specification. For example, an MPPT controller would be expected to make better use of a voltage mis-match between the panels and the rest of the system than a PWM controller.
- Similarly, a battery charge/discharge curve isn't simulated in the state-of-charge integration - it is a simple power balance. In other words, the state of charge computed is NOT a percent of a nominal amp-hour rating (the usual definition of SOC), but of the user-set watt-hour value. The SOC calculation does not take into account charge/discharge rate limitations or dynamics based on a specific battery chemistry.
- In a real-world setting, your effective solar line-of-sight may be limited due to objects on the horizon (trees, other structures, etc.) The NREL data, to my best understanding, is based on unobstructed line-of-sight, which may not be the case especially at the very beginning and very end of the day where solar illumination is transitioning. However, I have included options for hard cut-off times to be set to model a real-world situation (see examples).

Usage and examples
====================

To use the user application, run `python run.py` with the following options:

```
Usage: run.py [OPTIONS]

  Solar calculation application

Options:
  -data TEXT                   NREL Data file(s) for your location. Separate
                               file names by comma.
  -o TEXT                      Output figure file name (png format)
  --efficiency FLOAT           Power conversion efficiency
  --panel_watt FLOAT           Total rated panel power for your system (Watt)
  --battery_capacity FLOAT     Total battery power capacity for your system
                               (Watt-hr)
  --power_use_constant FLOAT   Constant background power load (Watt)
  --power_use_daytime FLOAT    Daytime power load (Watt). This is added on top
                               of the background power use, during daylight
                               hours.
  --power_use_nighttime FLOAT  Nighttime power load (Watt). This is added on
                               top of the background power use, during night
                               time hours.
  --power_use_direct FLOAT     Direct load (Watt). This is load that will be
                               applied only when the available PV power can
                               match it (i.e.. during the day in direct
                               sunlight)
  --direct_min_temp FLOAT      Direct load min temperature (Deg. F). The
                               direct load value will only be applied if the
                               ambient temperature is above this optional
                               level. Useful for direct solar water pumps,
                               etc.
  --start_time FLOAT           Start time cut-off (hour 0-23). Collected PV
                               power before this hour is set to zero. Used to
                               model obstruction at dawn.
  --end_time FLOAT             End time cut-off (hour 0-23). Collected PV
                               power after this hour is set to zero. Used to
                               model obstruction at dusk
  --help                       Show this message and exit.
```
This produces the figure like the one shown in the previous section.
If you don't specify a particular variable, you will be prompted to enter one. Press
enter to accept the shown default value.

Th NREL data may be collected by running their [PVWATTS calculator application](http://pvwatts.nrel.gov/).
You'll be asked to first specify your location (by address, zip code, or other), then in the following screens you will be asked to specify parameters for a residential PV system. You can just take all of the defaults for this, then click through to the last screen. On the last screen, scroll down and click the "Download Hourly Results" file, a CSV file with hourly climate and solar illumination and PV collection data for your location. The parameters in the above model can scale these values as needed to model a larger or smaller PV system. The headers of the CSV show system and environmental assumptions.

NREL data also contains wind information that could potentially be used for wind turbine sizing for a hybrid solar-wind system in the future.

Example: Tiny panel w/ LiPo battery and LED light
-------------------------------------------------
Consider setting up a [5.2 W panel](https://www.sparkfun.com/products/9241) with a [2000 mAh LiPo battery](https://www.sparkfun.com/products/8483), controlled via a [small MPPT controller](https://www.sparkfun.com/products/12885). We'll plan to use this to power a 0.1 W LED.

So the power capacity of the battery is: 2Ah * 3.7V = 7.4 Wh, and we can run our model with:

`python run.py -data data/cleveland.csv --panel_watt 5.2 --battery_capacity 7.4 --power_use_constant 0.1`

Here, I used the NREL CSV data file for my location (in the vicinity of Cleveland, OH). This gives the resulting figure:

![Example 1](images/result_ex1.png)

Looking at summary information at the top: The model predicts that the system, run continuously, will never discharge the LiPo battery below 79.99%, reached during the winter (as expected). Over the simulated year, It is also noted that a total of 7kWh of energy can be collected by the panel in its location, with 6kWh net collectible (total collectible minus LED energy use). 

The first subplot shows that we are unlikely to ever really get 5.2 W out of the panel. Over the course of the day, we get anywhere from 1 W to about 4 W. Also, the large amount of green (net) collectible energy shows that our load isn't using a large percentage of it most of the time during daylight hours.

The second subplot shows that we can collect from 5 to 30 Wh energy every day from the panel (blue trace). The green trace subtracts off the LED load power, which is generally only 2-4 Wh less than the power that can be collected.

The third subplot shows ambient temperature variation over the year, 0 to 100 F transition over the course of the year. This doesn't tell us much here, but future versions of this model will allow this to be taken into account for battery charge characteristics, temperature-dependent load specifications, etc. 

The last subplot shows that the battery SOC oscillates pretty regularly with the day-night cycles, with the night period being getting longer in the winter. Again, no major surprises here. 

Overall, not discharging the battery below about 80% is pretty good, and would preserve the life of the battery very well over time.

Example: Tiny panel w/ LiPo battery and LED light V.2
----------------------------------------------------
Let's rerun the last example, but this time let's only run the LED at night, but run an Arduino 3.3v mini Pro constantly. I estimate that the Arduino will consume about 0.05 A * 3.7 V = 0.185 W

Let's also set the model to only count daylight hours between 10am and 3pm (due to shadowing from trees around my area).

We would then run:
`python run.py -data data/cleveland.csv --panel_watt 5.2 --battery_capacity 7.4 --power_use_constant 0.185 --power_use_nighttime 0.1 --start_time 10 --end_time 15`

which gives:
![Example 1](images/result_ex2.png)


The first subplot shows that the net hourly power is generally dips further into the negative (during the night hours, naturally).

The second subplot shows that in the winter, the net power collected over each day is often in the negative (there is a horizontal black line on both subplots that shows the Wh = 0 level). The gap between the total collectible energy and net collected is noticeably wider.

So overall, we see that while the panel can still technically collect 3 kWh more over the year than is consumed, the battery can no longer keep the system running continuously anymore due to collection and storage deficiencies during the winter months. Because of this, the battery reaches full discharge several times. 

While it bounces back and recharges typically within a day in our model, in reality most batteries have a very hard time recovering from complete discharges. To successfully design this as real-world hands-off system, we would need to re-run this model with higher panel wattages, greater battery capacities, or reducing load specifications until the depth of discharge is a more reasonable level. A low-voltage disconnect should also be used as a backup measure, or in a case where the system doesn't really need to run continuously without any interruption. Numerical optimization could be used to help squeeze performance out of the margins while keeping a lid on costs.


Example: Solar water pump & night spotlight
-------------------------------------------------------
Next will be the design of a solar water pumping station with night light.
For this, a 30W DC water pump will be powered only when at least 30W of solar power is available from the array, and only when the ambient temperature is greater than 32 Deg F. A constant background draw of 0.5W will also be made for sensors and microelectronics, and 4W will be used to power a small LED outdoor light.

At 30W, this pump can move 3 liters per minute, or about 47 gallons per hour.

We can run this with:

`python run.py -data data/cleveland.csv --panel_watt 100 --battery_capacity 420 --power_use_nighttime 4 --power_use_constant 0.5 --power_use_direct 30 --direct_min_temp 32`

Which gives:
![Example 1](images/result_ex3.png)

The black line in the second subplot shows when the direct-load pump comes on, which is a bit sporadic. It looks as though in the summer months, we get about 250 Wh worth of energy directed into the pump at the needed condition (30W PV available, > 32 degrees), which would correspond to about 391 pumped gallons per day. In the winter, the pump is practically hibernated. We also see that we get a total of about 45 kWh powered to the pump over the course of the year, which corresponds to about 70,000 gallons of pumped water.
Battery SOC is not adversely affected by the daytime pump operation, and has an acceptable discharge depth of 80% occurring in the winter. 

Experimenting with the model shows that SOC is much more sensitive to the constant background loads than the pump load level, since the logic of the model will not operate the pump unless the PV can support it. Interestingly, for a fixed PV array and battery size, the directly load power level (the pump wattage) that maximizes total energy delivered to the pump over the year is not directly intuitive - setting it very low does not deliver as much cumulative power, while setting it too high does not turn it on often enough. For a 100W panel + 420 Wh battery, a 30W pump seems to have about the maximum annual energy you can put to use - around 45 kWh. 

Experimenting with it a bit: 
    - with a 18W pump its 40 kWh over the year, with a 73% minimum battery SOC level
    - with a 30W pump (same run above) its 45 kWh with 80% minimum SOC
    - with a 50W pump you get 29 kWh , with 80% minimum SOC

Assuming that the total amount of water that you can pump over a year is directly correlated to the total energy delivered to it, It's a pretty interesting design space with non-trivial constraints (especially when you consider the battery).


Example: Whole-House residential grid-tie system
-------------------------------------------------
For this, a PV array will be sized to negate the electrical power usage of an average
home. Battery SOC will be neglected, and it will be assumed that it is a grid-tie system.

The average american home uses [about 911 kWh of energy per month](https://www.eia.gov/tools/faqs/faq.cfm?id=97&t=3). I'll bump this up to 1000 kWh to make it a nice round number, and to take into account inverter losses.

1000 kWh per month corresponds to about a constant power draw of 1370 W.
Let's analyze a 9.5 kilowatt PV system: 

`python run.py -data data/cleveland.csv --panel_watt 9500 --power_use_constant 1370`

![Example 1](images/result_ex4.png)

For this, the summary data at the top of the figure is probably the most informative: a 9.5Kw allows this home to break even with their electrical usage, with a small estimated 608 kWh net surplus (collectible power - loads).

Unlike the other examples, the net surplus wattage amount is actually
collected and used - in this case, sold to the utility company. In the grid-tie setup, AC power from the grid effectively plays the role that the DC batteries played in the previous models. If you oversize the array (say, with a 15kW system) you can see the amount of power that can be sold back. In this case, it would be about 6648 kWh net over the year, which at a value of $0.22 per kWh would be about $1462.00 worth of energy. 

Of course, off-setting the initial investment is another issue entirely!

Example: merging multiple NREL data sets
-----------------------------------------

Multiple NREL data sets collected from the PVWATTS tool can be used for a single run by passing each of them to `run.py`, separated by commas. The data is then concatenated to produce a model that then simulates multiple years of operation.

For example, if we wanted to run an 300W panel + 800Wh battery + 12.5 W constant load analysis, but include data from weather stations from Cleveland, Akron, and Mansfield OH together, we would first gather the CSV data for each of those stations separately, then run:

`python run.py -data lib/data/cleveland.csv,lib/data/akron.csv,lib/data/mansfield.csv --panel_watt 300 --battery_capacity 800 --power_use_constant 12.5 --start_time 10 --end_time 15`

which gives:

![Example 1](images/result_ex6.png)

More customization
==========================
You can create a much more customized model than would be possible with the command-line application by directly implementing your own OpenMDAO model that uses the components in `solar.py`. For example, see `greenhouse.py`, which implements a load component with temperature and time-of-day logic. The data source component that parses the NREL data also provides solar cell temperature, wind speed values, solar irradiance, and hour of day information.


Future plans
==================
There are a lot of possible improvements and enhancements:
 
 - Modelling of system voltage matching and PWM vs. MPPT controller technologies
 - More sophisticated battery component with voltage estimation and temperature dependant discharge curves and charge charectorisitics
 - Include estimation of PV, battery, and load currents, which (together with voltage drop estimation) could be used to size wiring.
 - Create a version of the `basic` model that allows for battery SOC-dependant load calculations. For example, maybe I would like to implement a load that only powers when the battery SOC is above a certain percentage. The power draw of some loads may also change based on battery voltage, which is tied to battery SOC (such as an unregulated voltage supplied to an LED). This would introduce an implicit cycle: Loads -> BatterySOC -> Loads [...] that would have to be converged with a numerical solver. OpenMDAO is designed to recognize and converge implicit models like this automatically, though they are more computationally expensive than direct feed-forward only models. 
 - Implementation of numerical derivatives using OpenMDAO's derivative API. This will allow for fast and efficient numerical optimization, even on extremely large design spaces, particularly when coupled with other codes. For instance, one could use it to optimize a power load schedule over time with respect to battery, thermal, cost, or operational constraints, etc.
 - Components for wind energy collection
