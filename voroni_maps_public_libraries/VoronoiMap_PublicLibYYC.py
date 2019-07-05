import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.path as path
import matplotlib as mpl
from scipy.spatial import Voronoi, voronoi_plot_2d
import smopy


def import_data(csv_file):
 	""" Extract latitude and longitude of each location (index) """
 	return pd.read_csv(csv_file)

def extract_coords(dframe):
	""" Define location by latitude and longitude """
	
	loc = df["Location"].str.strip('()').str.split(',', expand=True).rename(columns={0:"Lat", 1:"Lon"})
	lat = loc['Lat'].values.astype(float)
	lon = loc['Lon'].values.astype(float)

	return lat, lon

def voronoi_finite_polygons_2d(vor, radius=None):
	""" Define new regions and new vertices """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)



def main ():
	
	input_file = 'Calgary_Public_Library_Locations_and_Hours.csv'
	df = import_data(input_file)

	return 0

main()

# # List Comprehension to array of [lat, lon] for each location
# new_loc = [ [lat[i], lon[i]] for i in range(len(lon))]  
# new_loc = np.asarray(new_loc).astype(float)


# # Define box to retrive OpenStreetMap
# box = [lat.min(), lon.min(), lat.max(), lon.max()]


# # Retrieve map
# m = smopy.Map(box, z=11) 


# # Compute Voronoi tessellation
# vor = Voronoi(new_loc)
# regions, vertices = voronoi_finite_polygons_2d(vor)


# # Plot
# cmap = plt.cm.Set3
# cuadrants = len(lon)
# colors_cuadrants = cmap( np.linspace(0, 1., cuadrants))[:, :3]
# colors = .85 * np.random.rand(len(lon),3)

# # Define each cuadrant to plot
# cells = [m.to_pixels(vertices[region]) for region in regions]


# fig = plt.figure()
# x,y = m.to_pixels(new_loc[:,0], new_loc[:,1])
# fig = m.show_mpl(figsize=(9,9))
# fig.add_collection( mpl.collections.PolyCollection(cells, facecolors = colors, edgecolors='k', alpha=0.3, linewidth=1.5))
# fig.plot(x,y, 'ok', ms=5)
# plt.savefig("VoronoiMap_PublicLibYYC.png", format='png')

