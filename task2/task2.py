import re
import collections
import argparse

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits import mplot3d
except ImportError as err:
    print('Please, install numpy and matplotlib:\n'
          '  pip install numpy, matplotlib')
    raise


def give_values(text: str) -> tuple or None:
    """Returns values from a given text as a named 2-tuple.

    :param text: string from the given file;
    :return: 2-tuple (sphere, line) in which:
        sphere.center - sphere center coordinates;
        sphere.radius - sphere radius;
        line.point1 - coordinates of first point;
        line.point2 - coordinates of second point.

    """

    match_sphere_center = re.search(r"center: \[(.*?)\]", text)
    match_sphere_radius = re.search(r"radius: ([\d.]*)", text)
    match_line_coords = re.search(r"line: {\[(.*?)\], \[(.*?)\]}", text)

    if not (
        match_sphere_center and match_sphere_radius and match_line_coords
    ):
        return None

    sphere_center = tuple(map(float, match_sphere_center[1].split(',')))
    sphere_radius = float(match_sphere_radius[1])
    line_coords = (
        tuple(map(float, match_line_coords[1].split(','))),
        tuple(map(float, match_line_coords[2].split(','))),
    )

    line = collections.namedtuple('Line', ('point1', 'point2'))
    sphere = collections.namedtuple('Sphere', ('center', 'radius'))
    given = collections.namedtuple('Given', ('sphere', 'line'))

    return given(
        sphere(sphere_center, sphere_radius),
        line(*line_coords)
    )


def give_size(point1: tuple, point2: tuple, precision: float) -> int:
    """Returns the size of the array according to the precision.

    :param point1: tuple of coordinates of the first point: (x, y, z);
    :param point2: tuple of coordinates of the second point: (x, y, z);
    :param precision: collision detection precision;
    :return: integer array size.

    """

    diff = lambda points: abs(points[0] - points[1])
    max_diff = max(map(diff, zip(point1, point2)))

    return round(max_diff / precision) + 1


def give_line_arrays(point1: tuple, point2: tuple, size: int) -> tuple:
    """Returns a 3-tuple arrays of points for axes x, y, z.

    Points in arrays are formed with an interval of a given precision.

    :param point1: tuple of coordinates of the first point: (x, y, z);
    :param point2: tuple of coordinates of the second point: (x, y, z);
    :param size: array size;

    :return: 3-tuple arrays of point for axes x, y, z.

    """

    return (
        np.linspace(point1[0], point2[0], size),
        np.linspace(point1[1], point2[1], size),
        np.linspace(point1[2], point2[2], size)
    )


def give_sphere_arrays(center: tuple, radius: float, size: int) -> tuple:
    """Returns a 3-tuple arrays of points for axes x, y, z.

    :param center: tuple of coordinates of sphere center: (x, y, z)
    :param radius: float radius of sphere;
    :param size: array size;
    :return: 3-tuple arrays of point for axes x, y, z.

    """

    size = complex(0, size//100)
    im = size if size.imag > 100 else 100j

    u, v = np.mgrid[0:2*np.pi:im, 0:np.pi:im/2]
    x = center[0] + radius * np.cos(u) * np.sin(v)
    y = center[1] + radius * np.sin(u) * np.sin(v)
    z = center[2] + radius * np.cos(v)

    return x, y, z


def give_collisions(
        line_arrays: tuple, sphere: tuple, precision: float) -> np.array:
    """Returns a list of collisions.

    :param line_arrays: 3-tuple of line point arrays;
    :param sphere: a named tuple of the sphere's center
        coordinates and its radius;
    :param precision: collision detection precision;
    :return: np.array of coordinates of collision points
        of sphere and line.

    """

    line_coords = np.concatenate(
        [
            line_arrays[0][:, np.newaxis],
            line_arrays[1][:, np.newaxis],
            line_arrays[2][:, np.newaxis],
        ],
        axis=1
    )

    normal = np.sqrt(((line_coords - sphere.center) ** 2).sum(axis=1))
    condition = abs(normal - sphere.radius) < precision/2

    collisions = []
    for coords in line_coords[condition]:
        if collisions and all(abs(coords - collisions[-1]) < precision):
            collisions.pop()
        collisions.append(coords)

    return collisions


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.usage = f"task2.py [path_to_given] [-p precision]"
    parser.add_argument(
        'given', action='store', type=str, help='path to given')
    parser.add_argument(
        '-p', '--precision', action='store', type=str, default=0.001,
        help='collision detection precision [default=0.01]'
    )
    args = parser.parse_args()

    with open(args.given) as f:
        text = f.read().strip()
    given = give_values(text)

    if given is None:
        print('Wrong data')
    else:
        precision = float(args.precision)
        sphere, line = given
        size = give_size(line.point1, line.point2, precision)
        line_arrays = give_line_arrays(line.point1, line.point2, size)
        sphere_arrays = give_sphere_arrays(sphere.center, sphere.radius, size)

        collisions = give_collisions(line_arrays, sphere, precision)
        if collisions:
            for coords in collisions:
                print(np.array2string(coords, separator=',', precision=2))
        else:
            print('Коллизий не найдено')

        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.plot_surface(*sphere_arrays, color='blue', alpha=0.5)
        ax.plot3D(*line_arrays, color='green')

        for point in collisions:
            ax.plot3D(*point, marker='o', color='red')

        plt.show()
