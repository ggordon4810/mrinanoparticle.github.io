"""
This file contains the calculations used by app.py.
"""

import numpy as np


def calculate_relaxivity(concentrations, t1_values):

    # Check that concentrations is a list.
    if not isinstance(concentrations, list):
        raise ValueError("Concentrations must be provided as a list.")

    # Check that t1_values is a list.
    if not isinstance(t1_values, list):
        raise ValueError("T1 values must be provided as a list.")

    # Check that concentrations and t1_values have the same length.
    if len(concentrations) != len(t1_values):
        raise ValueError(
            "Each concentration must have a corresponding T1 measurement."
        )

    # Check that there are at least two measurements.
    if len(concentrations) < 2:
        raise ValueError(
            "At least two measurements are required for linear regression."
        )

    # Check that every concentration is zero or greater.
    for concentration in concentrations:
        if concentration < 0:
            raise ValueError(
                "Concentration values must be zero or greater."
            )

    # Check that every T1 value is greater than zero.
    for t1 in t1_values:
        if t1 <= 0:
            raise ValueError(
                "T1 values must be greater than zero."
            )

    # Check that there are at least two different concentrations.
    if len(set(concentrations)) < 2:
        raise ValueError(
            "At least two different concentration values are required."
        )

    # Convert T1 values from milliseconds to seconds.
    t1_seconds = []

    for t1 in t1_values:
        converted_t1 = t1 / 1000
        t1_seconds.append(converted_t1)

    # Calculate R1 values in inverse seconds.
    r1_values = []

    for t1 in t1_seconds:
        r1 = 1 / t1
        r1_values.append(r1)

    # Perform linear regression.
    regression = np.polyfit(
        concentrations,
        r1_values,
        1
    )

    # Store the slope as relaxivity.
    relaxivity = regression[0]

    # Store the y-intercept.
    intercept = regression[1]

    # Calculate predicted R1 values at the measured concentrations.
    predicted_r1_values = []

    for concentration in concentrations:
        prediction = relaxivity * concentration + intercept
        predicted_r1_values.append(prediction)

    # Calculate the average measured R1.
    average_r1 = sum(r1_values) / len(r1_values)

    # Calculate total sum of squares.
    total_sum_squares = 0

    for r1 in r1_values:
        total_sum_squares += (r1 - average_r1) ** 2

    # Calculate residual sum of squares.
    residual_sum_squares = 0

    for i in range(len(r1_values)):
        residual_sum_squares += (
            r1_values[i] - predicted_r1_values[i]
        ) ** 2

    # Calculate R-squared.
    if total_sum_squares == 0:
        r_squared = 1.0
    else:
        r_squared = (
            1 - residual_sum_squares / total_sum_squares
        )

    # Create evenly spaced concentration values for the graph.
    fit_concentrations = np.linspace(
        min(concentrations),
        max(concentrations),
        100
    )

    # Calculate the fitted R1 values for the graph.
    fit_values = []

    for concentration in fit_concentrations:
        fitted_r1 = relaxivity * concentration + intercept
        fit_values.append(fitted_r1)

    # Convert NumPy values to ordinary Python floats and lists.
    relaxivity = float(relaxivity)
    intercept = float(intercept)
    r_squared = float(r_squared)
    fit_concentrations = fit_concentrations.tolist()
    fit_values = [float(value) for value in fit_values]

    # Organize individual measurements.
    measurements = []

    for i in range(len(concentrations)):
        measurement = {
            "concentration": concentrations[i],
            "t1": t1_values[i],
            "r1": r1_values[i]
        }

        measurements.append(measurement)

    # Return all results.
    return {
        "relaxivity": relaxivity,
        "intercept": intercept,
        "r_squared": r_squared,
        "concentrations": concentrations,
        "r1_values": r1_values,
        "fit_concentrations": fit_concentrations,
        "fit_values": fit_values,
        "measurements": measurements
    }


def analyze_dls(
    z_average_nm,
    pdi,
    intensity_size_nm=None,
    volume_size_nm=None,
    number_size_nm=None
):

    # Check that z_average_nm is not None.
    if z_average_nm is None:
        raise ValueError("A Z-average value is required.")

    # Check that pdi is not None.
    if pdi is None:
        raise ValueError("A PDI value is required.")

    # Check that z_average_nm is greater than zero.
    if z_average_nm <= 0:
        raise ValueError(
            "The Z-average must be greater than zero."
        )

    # Check that pdi is zero or greater.
    if pdi < 0:
        raise ValueError(
            "The PDI must be zero or greater."
        )

    # Check each optional size value.
    # Only validate the value if it was provided.
    if (
        intensity_size_nm is not None
        and intensity_size_nm <= 0
    ):
        raise ValueError(
            "The intensity size must be greater than zero."
        )

    if (
        volume_size_nm is not None
        and volume_size_nm <= 0
    ):
        raise ValueError(
            "The volume size must be greater than zero."
        )

    if (
        number_size_nm is not None
        and number_size_nm <= 0
    ):
        raise ValueError(
            "The number size must be greater than zero."
        )

    # Create an empty list for interpretation sentences.
    interpretation_parts = []

    # Classify the distribution based on PDI.
    if pdi <= 0.10:
        interpretation_parts.append(
            "The sample has a uniform "
            "size distribution."
        )

    elif pdi <= 0.20:
        interpretation_parts.append(
            "The sample has a relatively uniform "
            "size distribution."
        )

    elif pdi <= 0.30:
        interpretation_parts.append(
            "The sample has a moderately disperse "
            "size distribution."
        )

    else:
        interpretation_parts.append(
            "The sample has a broad"
            "size distribution."
        )

    # By default, recommend the Z-average.
    recommended_value = "Z-Average"

    # Explain what the Z-average represents.
    interpretation_parts.append(
        "The Z-average is the primary DLS measurement because "
        "it represents the weighted mean "
        "diameter of the particles."
    )

    # Compare the intensity size with the Z-average.
    if intensity_size_nm is not None:
        absolute_difference = abs(
            intensity_size_nm - z_average_nm
        )

        percent_difference = (
            absolute_difference / z_average_nm
        ) * 100

        if percent_difference >= 50:
            interpretation_parts.append(
                "The intensity size differs substantially from "
                "the Z-average, there may be an excess of large particles."
            )

        elif percent_difference > 10:
            interpretation_parts.append(
                "The intensity size is moderately different from "
                "the Z-average. Consider examining the volume and "
                "number distributions."
            )

        else:
            interpretation_parts.append(
                "The intensity size is similar to the Z-average, "
                "large particles have minimal effect on the size."
            )

    # Compare the volume size with the Z-average.
    if volume_size_nm is not None:
        absolute_difference = abs(
            volume_size_nm - z_average_nm
        )

        percent_difference = (
            absolute_difference / z_average_nm
        ) * 100

        if percent_difference >= 50:
            interpretation_parts.append(
                "The volume size differs substantially from the "
                "Z-average. Consider retesting the sample as they should be somewhat similar."
            )

        elif percent_difference > 10:
            interpretation_parts.append(
                "The volume size is moderately different from the "
                "Z-average. Consider reporting the Z-average."
            )

        else:
            interpretation_parts.append(
                "The volume size is similar to the Z-average, you can report either."
            )

    # Compare the number size with the Z-average.
    if number_size_nm is not None:
        absolute_difference = abs(
            number_size_nm - z_average_nm
        )

        percent_difference = (
            absolute_difference / z_average_nm
        ) * 100

        if percent_difference >= 50:
            interpretation_parts.append(
                "The number size differs substantially from the "
                "Z-average, there may be a lot of small particles in your sample"
            )

        elif percent_difference > 10:
            interpretation_parts.append(
                "The number size is moderately different from the "
                "Z-average. Consider looking at other measurements for more information."
            )

        else:
            interpretation_parts.append(
                "The number size is similar to the Z-average, you can report either."
            )

    # Warn against relying on one average for highly polydisperse samples.
    if pdi > 0.30:
        recommended_value = "Review Full Distribution"

        interpretation_parts.append(
            "Because the PDI is moderately high, your sample has a broad size distribution."
        )

    # Combine all interpretation sentences into one string.
    interpretation = " ".join(interpretation_parts)

    # Return the results.
    return {
        "recommended_value": recommended_value,
        "interpretation": interpretation
    }

