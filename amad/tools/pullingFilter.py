def pulling_filter(inwards, outwards, exceptions=[]):
    """
    Generates a filtered list of parameters based on the following rules:
    `Outwards` with the suffix `_out`
    All `inwards` except for those with corresponding `outwards` suffixed with `_out`

    Parameters
    ----------
    inwards : list
        CoSApp list of inwards (`system_name.inwards`)
    outwards : list
        CoSApp list of outwards (`system_name.outwards`)
    """

    # outwards where _out is present
    filtered_outwards = [out for out in outwards if "_out" in out]

    # all inwards except the _out related ones
    root_outwards = [out.removesuffix("_out") for out in filtered_outwards]
    filtered_inwards = [inw for inw in inwards if inw not in root_outwards]

    all_pulling = filtered_inwards + filtered_outwards

    for exception in exceptions:
        try:
            all_pulling.remove(exception)
        except ValueError:
            next

    return all_pulling
