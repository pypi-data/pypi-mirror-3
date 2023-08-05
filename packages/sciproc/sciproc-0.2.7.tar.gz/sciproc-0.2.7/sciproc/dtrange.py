from datetime import datetime, timedelta

# redefine range() to make it work with datetimes
def dtrange(*args):
    if len(args) != 3:
        return range(*args)
    start, stop, step = args
    if start < stop:
        cmp = lambda a, b: a < b
        inc = lambda a: a + step
    else:
        cmp = lambda a, b: a > b
        inc = lambda a: a - step
    output = [start]
    while cmp(start, stop):
        start = inc(start)
        output.append(start)

    return output
