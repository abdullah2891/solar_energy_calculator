
import pylab
import matplotlib.dates as mdates

import numpy as np
months = mdates.MonthLocator(bymonth=range(0,13,2)) 
monthsFmt = mdates.DateFormatter('%b')

def smooth(trace, cuttoff=15):
    """
    Basic low-pass filter to create trendlines
    """
    n = len(trace)
    trace = np.pad(trace, n, mode='reflect')
    freq = np.fft.rfft(trace)
    freq[3*cuttoff:] = 0.0
    filt = np.fft.irfft(freq).real
    return filt[n:2*n]

def make_plot(top):
    """
    Utility function to produce matplotlib figure
    """
    fig = pylab.figure(figsize=(12, 10))

    dates = np.array(top.root.data.dates)
    SOC = top['batteries.SOC']
    SOC_min = SOC.min()
    idx = np.where(SOC == SOC_min)
    min_date = dates[idx][0]

    cap = top['des_vars.power_capacity']
    panels = top['des_vars.panels_array_power']
    gen = top['panels.P_generated']
    consumed = top['batteries.P_consumption']
    consumed_direct = top['loads.P_consumption_direct']
    idx = np.where(gen >= 0.0)

    avg = smooth(gen[idx])

    day_energy = []
    day_energy_net = []
    day_consumed = []
    day_consumed_direct = []
    days = []
    energy = 0.0
    energy_consumed = 0.0
    energy_net = 0.0
    energy_direct = 0.0
    day = dates[0].date()
    for i, d in enumerate(dates):
        if d.date() == day:
            energy += gen[i]
            energy_consumed += consumed[i]
            energy_net += gen[i] - consumed[i]
            energy_direct += consumed_direct[i]
        else:
            days.append(day)
            day_energy.append(energy)
            day_energy_net.append(energy_net)
            day_consumed.append(energy_consumed)
            day_consumed_direct.append(energy_direct)
            energy = 0.0
            energy_net = 0.0
            energy_consumed = 0.0
            energy_direct = 0
            day = d.date()

    title = """Panel array: %2.2f W rated
Battery Capacity: %2.2f W*h
Battery SOC min: %2.2f %% on %s
Total power collectable: %2.0f kWh, Direct load powered %2.0f kWh, All powered %2.0f kWh, Net surplus: %2.0f kWh
""" % (panels, cap, SOC_min*100.0, min_date.strftime("%B %d"), sum(day_energy)/1000.0, sum(day_consumed_direct)/1000.0, sum(day_consumed)/1000.0, sum(day_energy_net)/1000.0)
    pylab.suptitle(title)
    pylab.subplot(411)
    mx = gen[idx].max()
    scaler, ylabel, ylabel2 = 1, "W", "Wh"
    if mx > 1500:
        scaler, ylabel, ylabel2 = 1000, "kW", "kWh"
    pylab.plot(dates[idx], gen[idx]/scaler, label="Hourly Panel power")
    pylab.plot(dates[idx], gen[idx]/scaler -consumed[idx]/scaler, label="Net")
    pylab.plot([days[0], days[-1]], [0,0], 'k-')

    pylab.ylabel(ylabel)
    pylab.legend()
    #pylab.gca().xaxis.set_major_locator(months)
    #pylab.gca().xaxis.set_major_formatter(monthsFmt)

    pylab.subplot(412)
    pylab.plot(days, np.array(day_energy)/scaler,'b-', linewidth=0.5, label="Panels")
    pylab.plot(days, np.array(day_consumed)/scaler,'r-', linewidth=0.5,label="All Loads")
    pylab.plot(days, np.array(day_consumed_direct)/scaler,'k-', linewidth=0.5,label="Direct Loads")

    pylab.plot([days[0], days[-1]], [0,0], 'k-')
    pylab.ylabel(ylabel2)
    #pylab.gca().xaxis.set_major_locator(months)
    #pylab.gca().xaxis.set_major_formatter(monthsFmt)
    pylab.legend()
        
    pylab.subplot(413)
    temp = top['data.ambient_temperature']*9/5 + 32
    pylab.plot(dates, temp, label="Temp.")
    pylab.plot(dates, smooth(temp), 'k--', linewidth=2)
    pylab.ylabel("F")
    pylab.legend()
    #pylab.gca().xaxis.set_major_locator(months)
    #pylab.gca().xaxis.set_major_formatter(monthsFmt)

    pylab.subplot(414)
    pylab.plot(dates, SOC, label="Battery SOC")
    pylab.plot(dates, smooth(SOC, 25), 'k--', linewidth=2)
    pylab.ylabel("%")
    pylab.legend()
    if SOC_min > 0.97:
        pylab.ylim(-0.1, 1.1)
    else:
        pylab.ylim(SOC_min-0.1, 1.1)
    #pylab.gca().xaxis.set_major_locator(months)
    #pylab.gca().xaxis.set_major_formatter(monthsFmt)


    return fig