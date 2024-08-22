import math

def calculate_trajectory(weapon, data, **kwargs):
    # Extract weapon properties with default fallback values
    initial_speed = weapon.get('initial_speed', 0)
    drag_coefficient = weapon.get('drag_coefficient', 0.47)  # Default drag coefficient
    bullet_weight = weapon.get('bullet_weight', 0) / 1000  # Convert grams to kilograms
    bullet_diameter = weapon.get('bullet_diameter', 0) / 1000  # Convert millimeters to meters
    ballistic_coefficient = weapon.get('ballistic_coefficient', 1)

    # Environmental conditions
    altitude = kwargs.get('altitude', weapon.get('altitude', 0))
    temperature = kwargs.get('temperature', 15)
    humidity = kwargs.get('humidity', 50)
    wind_speed = kwargs.get('wind_speed', data.get('wind_speed', 0))
    wind_angle = kwargs.get('wind_angle', data.get('wind_angle', 0))
    spin_drift = kwargs.get('spin_drift', True)
    coriolis_effect = kwargs.get('coriolis_effect', True)
    latitude = kwargs.get('latitude', 0)  # Default latitude to 0 if not provided

    # Convert latitude and wind angle from degrees to radians
    latitude_radians = math.radians(latitude)
    wind_angle_radians = math.radians(wind_angle)

    # Adjusted constants
    gravity = 9.81  # Acceleration due to gravity in m/s^2
    air_density = 1.225 * (1 - 0.0065 * altitude / 288.15) ** 5.2561 * (1 - (humidity / 100) * 0.00367)
    angle = math.radians(kwargs.get('angle', weapon.get('default_angle', 45)))

    # Adjusted initial speed and drag
    adjusted_speed = initial_speed * (air_density / 1.225) * ((273.15 + temperature) / 293.15) ** 0.5

    # Time step for calculations
    time_step = 0.01
    elapsed_time = 0
    start_x, start_y = 0, 0

    # Calculate the cross-sectional area of the bullet
    cross_sectional_area = math.pi * (bullet_diameter / 2) ** 2

    # Initialize lists to store trajectory points
    trajectory_points = []

    while True:
        # Velocity components with drag, air density, and dynamic forces
        velocity_x = adjusted_speed * math.cos(angle) - (
                0.5 * drag_coefficient * air_density * cross_sectional_area * abs(
            adjusted_speed * math.cos(angle)) ** 2 / bullet_weight)
        velocity_y = (adjusted_speed * math.sin(angle) - (gravity * elapsed_time)) - (
                0.5 * drag_coefficient * air_density * cross_sectional_area * abs(
            adjusted_speed * math.sin(angle)) ** 2 / bullet_weight)

        # Apply wind effects
        wind_effect_x = wind_speed * math.cos(wind_angle_radians) * elapsed_time
        wind_effect_y = wind_speed * math.sin(wind_angle_radians) * elapsed_time

        # Apply Coriolis effect and spin drift if enabled
        coriolis_x = 0
        coriolis_y = 0
        if coriolis_effect:
            coriolis_x = 2 * 7.2921e-5 * elapsed_time * velocity_y * math.sin(latitude_radians)
            coriolis_y = 2 * 7.2921e-5 * elapsed_time * velocity_x * math.sin(latitude_radians)

        spin_drift_effect = 0
        if spin_drift:
            spin_drift_effect = 0.0001 * elapsed_time

        x = start_x + (velocity_x + wind_effect_x + coriolis_x + spin_drift_effect) * elapsed_time
        y = start_y - ((velocity_y + wind_effect_y + coriolis_y) * elapsed_time - (0.5 * gravity * elapsed_time ** 2))

        # Update trajectory points with display data
        trajectory_points.append({
            'x': x,
            'y': y,
            'velocity_x': velocity_x,
            'velocity_y': velocity_y,
            'time': elapsed_time,
        })

        # Break the loop when the bullet hits the ground
        if y <= 0:
            break

        # Increment time
        elapsed_time += time_step

    return trajectory_points
