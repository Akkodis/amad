def lifting_area(spans, taper_ratios, root_chord: float):
    """
    Calculate the area of a lifting surface.

    Parameters
    ----------
    spans : list or float
        If a list, it represents the span lengths of each section of the lifting surface.
        If a float, it represents the total span length of the lifting surface.
    taper_ratios : list or float
        If a list, it represents the taper ratios of each section of the lifting surface.
        If a float, it represents the taper ratio of the lifting surface.
    root_chord : float
        The root chord length of the lifting surface.

    Returns
    -------
    float
        The area of the lifting surface.

    Raises
    ------
    None
    """
    if isinstance(spans, list):
        area_lifting_surface = 0.0
        spans_abs = [spans[0]]
        spans_abs.extend(list(spans[i] - spans[i - 1] for i in range(1, len(spans))))

        for span, taper_ratio in zip(spans_abs, taper_ratios):
            area_lifting_surface = (
                area_lifting_surface
                + 0.5 * (root_chord + (taper_ratio * root_chord)) * span
            )

    else:
        area_lifting_surface = 0.5 * (root_chord + (taper_ratios * root_chord)) * spans

    return area_lifting_surface


if __name__ == "__main__":
    spans = 20.0
    taper_ratios = 0.5
    root_chord = 3.0
    print(lifting_area(spans, taper_ratios, root_chord))

    spans = [10, 20]
    taper_ratios = [0.5, 0.5]
    print(lifting_area(spans, taper_ratios, root_chord))
