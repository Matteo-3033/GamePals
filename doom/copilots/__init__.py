import math

from doom import Math


def proximity_factor(monster: dict[str, any]) -> float:
    """
    Returns the proximity factor of a Monster, based on their distance on the screen (from the crosshair)
    and their 3D distance (from the player).
    The factor is the most when the enemy is the furthest, either on the screen or in 3D.
    """
    distance_on_screen = math.hypot(monster['relativeAngle'], monster['relativePitch'])
    distance_3d = monster['distance']
    p1 = Math.exponential_mapping(distance_on_screen, (0, max(distance_on_screen, 60)), (0, 1), p=0.25)
    p2 = Math.exponential_mapping(distance_3d, (0, max(distance_3d, 1000)), (0, 1), p=0.25)
    p = min(p1, p2)
    return p