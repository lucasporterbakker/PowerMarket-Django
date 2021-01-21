from datetime import datetime, date
from calendar import monthrange


# MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# NUM_DAYS_PER_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
# SOLAR_FLUX = [.93, 1.7, 1.95, 2.99, 3.42, 3.26, 3.52, 3.04, 2.41, 1.88, 1.15, .67, 2.24]  # kWh/m2/day.

# -----------------------------------------------------------------------------
#   Solar potential
# -----------------------------------------------------------------------------

'''
def calc_monthly_energy_output(area):
    """
    Calculates estimate of monthly energy output for a given panel area.
    :param area: panel area, for a simple estimation equal to the selected area.
    :return: monthly energy output [:12]
    """
    l = .15  # Phil says: Efficiency of solar panels.
    system_losses = .14  # Default value from NREL PVWatts v5 software.

    monthly_energy_output = []  # kWh/month

    for idx, month in enumerate(MONTHS):
        monthly_energy_output.append(area * SOLAR_FLUX[idx] * l * (1 - system_losses) * NUM_DAYS_PER_MONTH[idx])

    return monthly_energy_output
'''


ENERGY_PRICE_MAP = {
    'United Kingdom': {
        # GBP/kWh.
        'default': 0.1054,
    },
    'India': {
        # INR/kWh.
        # Last update: May 18, 2017.
        'default': 6.50,
        'AP': 6.82,  # Andhra Pradesh
        'AS': 5.78,  # Assam
        'BR': 6.42,  # Bihar
        'CT': 6.63,  # Chhatisgarh
        'DL': 8.78,  # Delhi
        'GA': 4.36,  # Goa
        'GJ': 5.64,  # Gujarat
        'HR': 6.83,  # Haryana
        'HP': 6.15,  # Himachal Pradesh
        'JK': 4.37,  # Jammu and Kashmir
        'KA': 7.11,  # Karnataka
        'KL': 6.30,  # Kerala
        'MP': 7.54,  # Madhya Pradesh
        'MH': 9.00,  # Maharastra
        'ML': 7.79,  # Meghalaya
        'OR': 6.29,  # Orissa
        'PB': 8.46,  # Punjab
        'RJ': 7.86,  # Rajasthan
        'TN': 6.77,  # Tamilnadu
        'UP': 8.17,  # Uttar Pradesh
        'UT': 4.56,  # Uttrakhand
        'WB': 8.57,  # West Bengal
    }
}


def get_energy_price(annual_energy, country='United Kingdom', state=None):
    """
    Returns the energy price for a given annual consumption in the given country (and state).
    :param annual_energy: annual energy consumption in kWh.
    :param country: country where energy is consumed.
    :param state: state in in which energy is consumed (optional).
    
    :return: average energy price in local currency.
    """
    if not state:
        state = 'default'
    try:
        energy_price = ENERGY_PRICE_MAP[country][state]
    except KeyError:
        try:
            energy_price = ENERGY_PRICE_MAP[country]['default']
        except KeyError:
            energy_price = ENERGY_PRICE_MAP['United Kingdom']['default']
    # print('energy price:', energy_price)
    return energy_price


def get_fit_rate(annual_energy, country='United Kingdom', target_date=None):
    """
    Returns FiT (Feed-in Tariff) for a given annual energy consumption in a given country.
    :param annual_energy: annual energy consumption in kWh.
    :param country: country where energy is consumed.
    :param target_date: date for which FiT rate should be returned.
    :return: fit tariff in local currency.
    """
    fit_rate = 0

    if country == 'United Kingdom':
        # http://www.solarpowerportal.co.uk/news/breaking_government_sets_future_feed_in_tariff_rate_1404
        if not target_date:
            # If no date is given use the current date.
            target_date = datetime.now().date()

        # FiT subsidies stop in 2019.
        if target_date > date(year=2019, month=1, day=1):
            return 0

        # Calculate FiT rate.
        date0 = date(year=2016, month=1, day=1)
        dm = target_date.month - date0.month + 12 * (target_date.year - date0.year)

        if annual_energy < 10e3:
            fit_rate = 0.0439
            degression_rate = 0.0007
        elif annual_energy < 50e3:
            fit_rate = 0.0459
            degression_rate = 0.000675
        elif annual_energy < 250e3:
            fit_rate = 0.027
            degression_rate = 0.000617
        elif annual_energy < 1e6:
            fit_rate = 0.0227
            degression_rate = 0.000608
        else:
            fit_rate = 0.0087
            degression_rate = 0.000583

        # Apply quarterly degression.
        fit_rate -= degression_rate * int(dm / 3)
        if fit_rate < 0:
            fit_rate = 0

    # print('fit_rate:', fit_rate)
    return fit_rate


def get_system_cost(system_size, country='United Kingdom', state=None):
    if country == 'India':
        # print('sys cost india')
        system_cost = get_system_cost_india(system_size)
    else:
        # print('sys cost uk')
        system_cost = get_system_cost_uk(system_size)

    # print('system_cost', system_cost)

    return system_cost


def get_system_cost_uk(system_size):
    """
    Returns average system cost for UK, based on system size.
    Uses the following pricing table:

          0-4kW: 1200 £/kW
         4-10kW: 1100 £/kW
        10-50kW: 1000 £/kW
       50-250kW:  900 £/kW
     250-1000kW:  850 £/kW
    1000-5000kW:  800 £/kW
       > 5000kW:  750 £/kW

    :param system_size: peak performance of the system in kW.
    :return: total system cost in £.
    """
    if system_size < 4:
        cost_per_kw = 1200
    elif system_size < 10:
        cost_per_kw = 1100
    elif system_size < 50:
        cost_per_kw = 1000
    elif system_size < 250:
        cost_per_kw = 900
    elif system_size < 1000:
        cost_per_kw = 850
    elif system_size < 5000:
        cost_per_kw = 800
    else:
        cost_per_kw = 750
    return system_size * cost_per_kw


def get_system_cost_india(system_size):
    """
    Returns average system cost for India, based on system size.
    Uses the following pricing table:
    
    Conversion rate of 84.38 IND / GBP (May 18, 2017).

          0-4kW: 100,000.00 INR/kW 
         4-10kW: 90,000.00 INR/kW
        10-50kW: 80,000.00 INR/kW
       50-250kW: 70,000.00 INR/kW
     250-1000kW: 65,000.00 INR/kW
    1000-5000kW: 60,000.00 INR/kW
       > 5000kW: 55,000.00 INR/kW
       
    :param system_size: peak performance of the system in kW.
    :return: total system cost in £. 
    """
    if system_size < 4:
        cost_per_kw = 90000
    elif system_size < 10:
        cost_per_kw = 80000
    elif system_size < 50:
        cost_per_kw = 70000
    elif system_size < 250:
        cost_per_kw = 65000
    elif system_size < 1000:
        cost_per_kw = 60000
    elif system_size < 5000:
        cost_per_kw = 55000
    else:
        cost_per_kw = 50000
    return system_size * cost_per_kw


def calc_monthly_profit(energy, country='United Kingdom', state=None):
    """
    Calculates estimate of monthly profit (savings + earnings) for a given energy output.
    :param energy: generated energy.
    :param country: country.
    :param state: state.
    :return: savings [:12], earnings[:12]
    """
    now = datetime.now().date()
    month = now.month

    savings = []  # £/month
    earnings = []  # £/month, FiT (Feed-in Tariff)

    annual_energy = sum(energy)

    for idx, e in enumerate(energy):
        if (idx + 1) < month:
            year = 2018
        else:
            year = 2017
        target_date = date(year=year, month=idx + 1, day=1)
        savings.append(get_energy_price(annual_energy, country, state) * e)
        fit_rate = get_fit_rate(annual_energy, country, target_date)
        earnings.append(fit_rate * e)

    return savings, earnings


'''
def solar_potential_serialized(area):
    """
    Serializes output of 'calculate_solar_potential' for API.
    :param area: panel area.
    :return: JSON object.
    """
    energy = calc_monthly_energy_output(area)
    savings, earnings = calc_monthly_profit(energy)

    serialized_data = {
        "monthly_data": [],
        "annual_energy": number_format(sum(energy), decimal_pos=0),
        "annual_total_profit": number_format(sum(savings) + sum(earnings), decimal_pos=0)
    }

    for idx, month in enumerate(MONTHS):
        serialized_data["monthly_data"].append({
            "id": idx,
            "month": month,
            "energy": round(energy[idx], 2),
            "savings": round(savings[idx], 2),
            "earnings": round(earnings[idx], 2),
        })

    return serialized_data
'''


# -----------------------------------------------------------------------------
#   Environmental benefits.
# -----------------------------------------------------------------------------

def environmental_benefits_serialized(energy):

    # Calculations and constants from:
    # http://amcleanenergy.com/

    avg_annual_energy_home = 8900  # [kWh]
    avg_annual_energy_lightbulb = 116.8  # [kWh]
    avg_annual_co2_car = 7484.27  # [kg]
    avg_co2_per_energy = 0.61  # [kg]
    co2_per_liter_gasoline = 2.32  # [kg/l]
    annual_offset_per_tree = 50  # [???]
    lifetime_offset_per_tree = 2000

    tons_of_carbon_eliminated_annually = energy * avg_co2_per_energy / 1000  # [mT]
    kg_of_carbon_eliminated_annually = tons_of_carbon_eliminated_annually * 1000  # [kg]
    cars_off_the_road = kg_of_carbon_eliminated_annually / avg_annual_co2_car
    gasoline_equivalent = kg_of_carbon_eliminated_annually / co2_per_liter_gasoline  # [kg]
    tree_equivalent = energy / annual_offset_per_tree
    tree_planting_equivalent = energy / lifetime_offset_per_tree
    homes_powered = energy / avg_annual_energy_home
    lightbulbs_powered = energy / avg_annual_energy_lightbulb

    return {
        "tons_of_carbon_eliminated_annually": tons_of_carbon_eliminated_annually,
        "cars_off_the_road": cars_off_the_road,
        "gasoline_equivalent": gasoline_equivalent,
        "tree_equivalent": tree_equivalent,
        "tree_planting_equivalent": tree_planting_equivalent,
        "homes_powered": homes_powered,
        "lightbulbs_powered": lightbulbs_powered,
    }


# -----------------------------------------------------------------------------
#   Chart JS visualisation.
# -----------------------------------------------------------------------------

def cum_lifetime_timeseries(data):
    now = datetime.now().date()
    year = now.year
    month=now.month

    # get start of next month
    month+=1
    if month>12:
        year+=1
        month=1

    timeseries = []

    for i in range(len(data)):
        num_days = monthrange(year, month)[1]
        dt = datetime(year=year, month=month, day=num_days)
        timeseries.append([str(dt.date()), round(data[i], 0)])
        month+=1
        if month > 12:
            year += 1
            month=1

    return timeseries


def cum_timeseries(data):
    now = datetime.now().date()
    num_days_first_month = monthrange(now.year, now.month)[1]

    rest_of_first_month = (num_days_first_month - now.day) / num_days_first_month * data[now.month - 1]

    # Add rest of current month.
    timeseries = [
        [str(now), 0],
        [str(now.replace(day=num_days_first_month)), round(rest_of_first_month, 0)],
    ]

    dt = None
    cum_sum = rest_of_first_month

    for i in range(11):
        year = now.year
        if (now.month + i) >= 12:
            year += 1
        month = (now.month + i) % 12 + 1
        num_days = monthrange(year, month)[1]
        dt = datetime(year=year, month=month, day=num_days)
        val = data[month - 1]
        cum_sum += val
        timeseries.append([str(dt.date()), round(cum_sum, 0)])

    beginning_of_last_month = [
        str(now.replace(year=now.year + 1)),
        round(num_days_first_month / num_days_first_month * data[now.month - 1] + cum_sum, 0)
    ]
    timeseries.append(beginning_of_last_month)

    return timeseries


