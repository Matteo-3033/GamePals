import math


def polar_to_cartesian(rho: float, theta: float) -> tuple[float, float]:
    return rho * math.cos(theta), rho * math.sin(theta)


def linear_mapping(x: float, range1: tuple[float, float], range2: tuple[float, float]) -> float:
    """
    Returns the linear mapping of the value x from range1 to range2
    """
    (x1, x2) = range1
    (y1, y2) = range2

    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)


def exponential_mapping(x: float, range1: tuple[float, float], range2: tuple[float, float], p: float) -> float:
    """
    Returns the exponential mapping of the value x from range1 to range2.
    The parameter p controls the steepness of the curve
    """
    (x1, x2) = range1
    (y1, y2) = range2

    return y1 + (y2 - y1) * (((x - x1) / (x2 - x1)) ** p)

def proximity_factor(monster: dict[str, any]) -> float:
    """
    Returns the proximity factor of a Monster, based on their distance on the screen (from the crosshair)
    and their 3D distance (from the player).
    The factor is the most when the enemy is the furthest, either on the screen or in 3D.
    """
    distance_on_screen = math.hypot(monster['relativeAngle'], monster['relativePitch'])
    distance_3d = monster['distance']
    p1 = exponential_mapping(distance_on_screen, (0, max(distance_on_screen, 60)), (0, 1), p=0.25)
    p2 = exponential_mapping(distance_3d, (0, max(distance_3d, 1000)), (0, 1), p=0.25)
    p = min(p1, p2)
    return p