from django.conf import settings

import requests
import math

def pvwatts5_request(
    point,
    area,
    tilt=settings.NREL_DEFAULT_ARRAY_TYPE,
    azimuth=settings.NREL_DEFAULT_AZIMUTH,
    api_key=settings.NREL_API_KEY,
    dataset=settings.NREL_DEFAULT_DATASET,
    module_type=settings.NREL_DEFAULT_MODULE_TYPE,
    system_losses_percent=settings.NREL_DEFAULT_SYSTEM_LOSSES,
    array_type=settings.NREL_DEFAULT_ARRAY_TYPE,
    dc_ac_ratio=settings.NREL_DEFAULT_DC_AC_RATIO,
    gcr=settings.NREL_DEFAULT_GCR,
    inv_eff_percent=settings.NREL_DEFAULT_INV_EFF,
    radius=settings.NREL_DEFAULT_RADIUS,
):
    """
    Computes DC system size from available roof area, generates GET/ request link for NREL PVWatts v5
    and retrieves data from the API via GET/ request..

    Calculator: http://pvwatts.nrel.gov/pvwatts.php
    Documentation: http://www.nrel.gov/docs/fy14osti/62641.pdf

    :param point:
        GEOS point object.

    :param area:
        Available roof area [sqm].

    :param api_key:
        NREL API key.

    :param dataset:
        TMY2 and TMY3 for the US.
        intl for global data.

    :param module_type:
        ID  Type	                        Approximate Efficiency  Module Cover        Temperature Coefficient
        0   Standard (crystalline Silicon)	15%	                    Glass	            -0.47 %/°C
        1   Premium (crystalline Silicon)	19%	                    Anti-reflective	    -0.35 %/°C
        2   Thin film	                    10%	                    Glass	            -0.20 %/°C

    :param system_losses_percent:
        System losses: -5 to 99 [%]

        = 100% × [ 1- ( 1 - 0.02 ) × ( 1 - 0.03 ) × ( 1 - 0.02 ) × ( 1 - 0.02 ) × ( 1 - 0.005 ) × ( 1 - 0.015) ×
        ( 1- 0.01 ) × ( 1 - 0.03) ] = 14%

        Soiling: 2%, Shading: 3%, Snow: 0%, Mismatch: 2%, Wiring: 2%, Connections: 0.5%,
        Light-Induced Degradation: 1.5%, Nameplate Rating: 1%, Age: 0%, Availability: 3%

    :param array_type:
        0: Fixed (open rack)
        1: Fixed (roof mount), default if not specified.
        2: 1-axis tracking
        3: 1-axis backtracking
        4: 2-axis tracking

    :param tilt:
        Tilt of installation [deg].
        Defaults to absolute latitude value if not specified.

    :param azimuth:
        Azimuth of installation [deg].
        Ideally the installation should face south (180°) on the northern hemisphere and north (0°) on the southern.

    :param dc_ac_ratio:
        See description below.

    :param gcr:
        Ground Coverage Ratio. See description below.

    :param inv_eff_percent:
        Inverter efficiency. See description below.

    :param radius:
        Radius to search for a weather station (Phil).

    :return:
        JSON object.
    """

    lat, lon = point.coords

    # Documentation:
    # https://developer.nrel.gov/docs/solar/pvwatts-v5/

    # DC SYSTEM SIZE.
    # ---------------
    # The DC system size is the DC (direct current) power rating of the photovoltaic array in kilowatts (kW)
    # at standard test conditions (STC). PVWatts® can model any size of array, from residential rooftop systems
    # to large ground-mounted power generation systems.
    #
    # The default PV system size is 4 kW. For a system with 16% efficient PV modules, this corresponds to an array
    # area of approximately 25 m² (269 ft²): 4 kW ÷ 1 kW/ m² ÷ 16% = 25 m². This array area is the total module area,
    # not the total area required by the system that might include space between modules and space for inverters and
    # other parts of the system.
    #
    # By default, PVWatts® uses a DC-to-AC size ratio of 1.1 so that the array's DC nameplate size at STC is 1.1 times
    # the inverter's AC (alternating current) size. For example, the default 4 kW system has an array size of 4 DC kW
    # and an inverter size of 3.63 AC kW. The default DC-to-AC ratio value is appropriate for most analyses, but you
    # can can change it under Advanced Parameters.
    #
    # You can either estimate the system size based on the area available for the array, or calculate it from the
    # module nameplate size at STC and number of modules in the array:
    #
    #   Size (kW) = Array Area (m²) × 1 kW/m² × Module Efficiency (%)
    #
    #       or
    #
    #   Size (kW) = Module Nameplate Size (W) × Number of Modules ÷ 1,000 W/kW
    #
    # If you are unsure of the number and size of modules or array area, you can Draw Your System to get a rough
    # estimate based on the area available for the photovoltaic array.
    #
    # Important Note: PVWatts® makes assumptions about the module performance based on the Module Type you choose,
    # and assumes that the module nameplate size is for standard test conditions (STC): Solar irradiance of 1,000 W/m2,
    # cell temperature of 25°C (77°F), and air mass of 1.5. You should not use PVWatts® to model a system with other
    # types of modules, or with a nameplate size for other test conditions.

    solar_irradiance = 1  # [kW/m2]
    panel_efficiency = .15  # Efficiency of the panels.
    system_capacity = math.floor(area/ 1.64) * 0.265   # area/1.64sqm panel size * 265W per panel (typical) - NOT how NREL estimates system capacity from area, but as it says above their Draw Your System is for when you don't know Nameplate size * no. of modules

    # TILT ANGLE.
    # -----------
    # The tilt angle is the angle from horizontal of the photovoltaic modules in the array. For a fixed array,
    # the tilt angle is the angle from horizontal of the array where 0° = horizontal, and 90° = vertical.
    #
    # Designers often use a lower tilt angle to minimize the cost of racking and mounting hardware, or to minimize
    # the risk of wind damage to the array.
    #
    # In general, using a tilt angle greater than the location's latitude favors energy production in the winter and
    # using a tilt angle less than the location's latitude favors energy production in the summer.
    #
    # For a PV array on a building's roof, you may want to choose a tilt angle equal to the roof pitch. Use the table
    # below to convert roof pitch in ratio of rise (vertical) over run (horizontal) to tilt angle.
    #
    #   Roof Pitch (rise/run)	    Tilt Angle (deg)
    #   4/12	                    18.4
    #   5/12	                    22.6
    #   6/12	                    26.6
    #   7/12	                    30.3
    #   8/12	                    33.7
    #   9/12	                    36.9
    #   10/12	                    39.8
    #   11/12	                    42.5
    #   12/12	                    45.0

    if not tilt:
        tilt = abs(lat)
    else:
        tilt=abs(tilt) #Make sure we don't pass a negative tilt!

    # AZIMUTH.
    # --------
    # For a fixed array, the azimuth angle is the angle clockwise from true north describing the direction that
    # the array faces. An azimuth angle of 180° is for a south-facing array, and an azimuth angle of zero degrees
    # is for a north-facing array.
    #
    # The default value is an azimuth angle of 180° (south-facing) for locations in the northern hemisphere and
    # 0° (north-facing) for locations in the southern hemisphere. These values typically maximize electricity
    # production over the year, although local weather patterns may cause the optimal azimuth angle to be slightly
    # more or less than the default values. For the northern hemisphere, increasing the azimuth angle favors afternoon
    # energy production, and decreasing the azimuth angle favors morning energy production. The opposite is true for
    # the southern hemisphere.

    if not azimuth:
        if lat >= 0:
            # Northern hemisphere.
            azimuth = 180
        else:
            # Southern hemisphere.
            azimuth = 0

    # DC / AC RATIO.
    # --------------
    # The DC to AC size ratio is the ratio of the inverter's AC rated size to the array's DC rated size.
    # Increasing the ratio increases the system's output over the year, but also increases the array's cost.
    # The default value is 1.10, which means that a 4 kW system size would be for an array with a 4 DC kW nameplate
    # size at standard test conditions (STC) and an inverter with a 3.63 AC kW nameplate size.
    #
    # For a system with a high DC to AC size ratio, during times when the array's DC power output exceeds the
    # inverter's rated DC input size, the inverter limits the array's power output by increasing the DC operating
    # voltage, which moves the array's operating point down its current-voltage (I-V) curve. PVWatts® models this
    # effect by limiting the inverter's power output to its rated AC size.
    #
    # The default value of 1.10 is reasonable for most systems. A typical range is 1.10 to 1.25, although some
    # large-scale systems have ratios of as high as 1.50. The optimal value depends on the system's location,
    # array orientation, and module cost.

    if not dc_ac_ratio:
        dc_ac_ratio = 1.1  # Default value according to NREL app.

    # GROUND COVERAGE RATIO.
    # ----------------------
    # The ground coverage ratio (GCR) applies only to arrays with one-axis tracking, and is the ratio of module
    # surface area to the area of the ground or roof occupied by the array. A GCR of 0.5 means that when the modules
    # are horizontal, half of the surface below the array is occupied by the array. An array with wider spacing between
    # rows of modules has a lower GCR than one with narrower spacing. A GCR of 1 would be for an array with no space
    # between modules, and a GCR of 0 for infinite spacing between rows. The default value is 0.4, and typical values
    # range from 0.3 to 0.6.
    #
    # PVWatts® uses the GCR value to calculated losses due to shading of neighboring rows of modules in the array.

    if not gcr:
        gcr = 1  # 0.4

    # INVERTER EFFICIENCY.
    # --------------------
    # The inverter's nominal rated DC-to-AC conversion efficiency, defined as the inverter's rated AC power output
    # divided by its rated DC power output. The default value is 96%.

    if not inv_eff_percent:
        inv_eff_percent = 96

    # Construct API URL:
    api_url = (
        'https://developer.nrel.gov/api/pvwatts/v5.json'
        '?api_key={api_key}'
        '&system_capacity={system_capacity}'
        '&dataset={dataset}'
        '&lat={lat}'
        '&lon={lon}'
        '&module_type={module_type}'
        '&losses={losses}'
        '&array_type={array_type}'
        '&tilt={tilt}'
        '&azimuth={azimuth}'
        '&dc_ac_ratio={dc_ac_ratio}'
        # '&gcr={gcr}'
        '&inv_eff={inv_eff}'
        '&radius={radius}'
    ).format(
        api_key=api_key,
        system_capacity=system_capacity,
        dataset=dataset,
        lat=lat,
        lon=lon,
        module_type=module_type,
        losses=system_losses_percent,
        array_type=array_type,
        tilt=tilt,
        azimuth=azimuth,
        dc_ac_ratio=dc_ac_ratio,
        # gcr=gcr,
        inv_eff=inv_eff_percent,
        radius=radius,
    )

    response = requests.get(api_url)
    return response.json()

