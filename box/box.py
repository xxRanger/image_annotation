from collections import namedtuple

# box = (Point, Point)

Point = namedtuple('Point', ['x', 'y'])

def box_overlap(b1, b2):
    # a box position is a named tuple (Point,Point)  (left bottom, right upper)
    if not isinstance(b1, tuple) and not isinstance(b2, tuple):
        raise Exception("b1 and b2 should be tuple")

    left_x = max(b1[0].x, b2[0].x)
    right_x = min(b1[1].x, b2[1].x)

    bottom_y = max(b1[0].y, b2[0].y)
    upper_y = min(b1[1].y, b2[1].y)

    return (Point(left_x, bottom_y), Point(right_x, upper_y))


def box_area(b):
    if not isinstance(b, tuple):
        raise Exception("box should be tuple")
    if b[1].x <= b[0].x or b[1].y <= b[0].y:
        area = 0
    else:
        area = (b[1].x - b[0].x) * (b[1].y - b[0].y)
    return area