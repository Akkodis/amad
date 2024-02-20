import math


def average_sweep(spans: list, sweeps: list):
    """
    Calculate the average sweep angle from a list of span lengths and sweep angles.

    Parameters
    ----------
    spans : list
        A list of numeric values representing the lengths of each span.
    sweeps : list or float
        A list of numeric values representing the sweep angles for each span, or a single float value representing the average sweep angle.

    Returns
    -------
    float
        The average sweep angle calculated from the input spans and sweeps.

    Raises
    ------
    TypeError
        If the input sweeps is not a list for multiple spans.

    Notes
    -----
    If the input sweeps is a list, the function calculates the average sweep angle by summing the displacements of each span and dividing by the total length of all spans. If the input sweeps is a single float value, it is returned as is.

    The displacement for each span is calculated as the tangent of the sweep angle in radians multiplied by the
    length of the span. The average sweep angle is then calculated by taking the arctangent of the ratio of total
    displacement to the length of the last span, converted to degrees.
    """
    if isinstance(sweeps, list):
        displacement = 0.0
        spans_abs = [spans[0]]
        spans_abs.extend(list(spans[i] - spans[i - 1] for i in range(1, len(spans))))

        for span, sweep in zip(spans_abs, sweeps):
            displacement = displacement + math.tan(math.radians(sweep)) * span

        av_sweep = math.degrees(math.atan(displacement / spans[-1]))

    else:
        av_sweep = sweeps

    return av_sweep


if __name__ == "__main__":
    spans = [8.62, 34.32]
    sweeps = [31.5, 23.5]

    print(average_sweep(spans, sweeps))
    print(average_sweep([10.0], [5.0]))
    print(average_sweep(10.0, 5.0))
    print(average_sweep([10], 5.0))
