import numpy as np


def rounded_rect(l, b, r, t, radius=1, n_arc=8) -> list[list]:
    """
    From: ChatGPT
    Generate a set of points representing a rounded rectangle with specified dimensions and
    corner radius.

    The function calculates the rounded rectangle by defining arcs for the corners and
    combining these arcs into a closed polygon. The rounded corners are generated using
    circular arcs, parameterized by angle values, and combined into a single list of points
    defining the rectangle.

    Parameters:
        l (float): The x-coordinate of the left side of the rectangle.
        b (float): The y-coordinate of the bottom side of the rectangle.
        r (float): The x-coordinate of the right side of the rectangle.
        t (float): The y-coordinate of the top side of the rectangle.
        radius (float): The radius of the rounded corners. Default is 1.
        n_arc (int): The number of points used to approximate each rounded corner arc.
            Default is 8.

    Returns:
        list[list[float, float]]: A list of points representing the closed polygon of the
            rounded rectangle. Each point is a pair [x, y] with the coordinates of a vertex.
    """
    # Rectangle points (Ecken)
    points = []
    # Bottom Left Arc
    bl = [(l+radius + radius*np.cos(theta), b+radius + radius*np.sin(theta))
          for theta in np.linspace(np.pi, 1.5*np.pi, n_arc)]
    # Bottom Right Arc
    br = [(r-radius + radius*np.cos(theta), b+radius + radius*np.sin(theta))
          for theta in np.linspace(1.5*np.pi, 2*np.pi, n_arc)]
    # Top Right Arc
    tr = [(r-radius + radius*np.cos(theta), t-radius + radius*np.sin(theta))
          for theta in np.linspace(0, 0.5*np.pi, n_arc)]
    # Top Left Arc
    tl = [(l+radius + radius*np.cos(theta), t-radius + radius*np.sin(theta))
          for theta in np.linspace(0.5*np.pi, np.pi, n_arc)]
    # Combine arcs (im Uhrzeigersinn)
    points = bl + br + tr + tl
    # Polygon muss geschlossen werden
    points.append(points[0])
    return [list(point) for point in points]