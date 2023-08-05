
def fair_scale(weight, wmpairs):
    """
    Fair resizing algorithm. 
    A weight and a list of (weight, min_weight) pairs is provided. The result is a list
    of calculated weights that add up to weight, but are no smaller than their specified
    min_weight's.

    >>> fair_scale(.7, ((.3, .2), (.5, .1)))
    [0.26249999999999996, 0.43749999999999994]
    >>> fair_scale(.5, ((.3, .2), (.5, .1)))
    [0.20000000000000001, 0.29999999999999999]
    >>> fair_scale(.4, ((.3, .2), (.5, .1)))
    [0.20000000000000001, 0.20000000000000001]
    """
    # List of new weights
    n = [0] * len(wmpairs)
    # Values that have been assigned their min_weight end up in this list:
    skip = [False] * len(wmpairs)
    while True:
        try:
            f = weight / sum(a[0] for a, s in zip(wmpairs, skip) if not s)
        except ZeroDivisionError:
            f = 0
        for i, (w, m) in enumerate(wmpairs):
            if skip[i]:
                continue
            n[i] = w * f
            if n[i] < m:
                n[i] = m
                weight -= m
                skip[i] = True
                break
        else:
            break # quit while loop
    return n


print fair_scale(.7, ((.3, .2), (.5, .1)))
print fair_scale(.5, ((.3, .2), (.5, .1)))
print fair_scale(.4, ((.3, .2), (.5, .1)))
print fair_scale(.3, ((.3, .2), (.5, .1)))
print fair_scale(.3, ((.3, .2), (.5, .1), (.5, .1), (.5, .1)))
