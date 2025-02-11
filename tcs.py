import math
import matplotlib.pyplot as plt

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

def convex_hull(points):
    points = sorted(points)
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]

def plot_points_and_hull(points):
    hull = convex_hull(points)

    # Plot points
    x, y = zip(*points)
    plt.scatter(x, y, color="blue", label="Points")

    # Plot the hull
    hull_x, hull_y = zip(*(hull + [hull[0]]))  # Close the hull
    plt.plot(hull_x, hull_y, color="black", label="Convex Hull")

    # Add labels and title
    plt.title("Convex Hull Visualization")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.legend()
    plt.grid(True)

    plt.show()

# Input
points = [(3, 4), (5, 5), (2, 2), (2, 5), (6, 4), (4, 1), (1, 3), (4, 3)]

# Plotting
plot_points_and_hull(points)

