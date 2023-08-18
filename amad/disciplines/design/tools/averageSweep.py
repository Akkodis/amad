import math


def average_sweep(spans: list, sweeps: list):
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
