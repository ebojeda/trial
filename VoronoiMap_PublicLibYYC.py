import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.path as path
import matplotlib as mpl
from scipy.spatial import Voronoi, voronoi_plot_2d
import smopy

"""
Voroni diagram calculated for a set of coordinates using public libraries location 
in the City of Calgary. Map visualization using PolyCollection.
Output file in .png format (OpenStreetMap overlapped by Voronoi tesellation).
"""

__author__ = "Estefania Barreto-Ojeda"
version = 1.0


def import_data(csv_file):
 	""" Extract latitude and longitude of each location (index) """
 	return pd.read_csv(csv_file)

def extract_coords(dframe):
	""" Define location by latitude and longitude """
	
	loc = dframe["Location"].str.strip('()').str.split(',', expand=True).rename(columns={0:"Lat", 1:"Lon"})
	latitude = loc['Lat'].values.astype(float)
	longitude = loc['Lon'].values.astype(float)

	return latitude, longitude

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


def new_locs(latitude, longitude):
	"""Compute Voronoi tessellation"""

	# # List Comprehension to array of [lat, lon] for each location
	new_locations = [ [latitude[i], longitude[i]] for i in range(len(longitude))]  
	new_locations = np.asarray(new_locations).astype(float)

	return new_locations

def plot_voronoi(box, latitude, longitude, new_loc):
	"""Retrive Map and plot Voronoi Diagram. 
	Final figure exported as .png """

	# Retrieve map
	m = smopy.Map(box, z=11) 

	vor = Voronoi(new_locs(latitude, longitude))

	regions, vertices = voronoi_finite_polygons_2d(vor)
	#Define Color Map for each cuadrantt
	cmap = plt.cm.Set3
	cuadrants = len(longitude)
	colors_cuadrants = cmap( np.linspace(0, 1., cuadrants))[:, :3]
	colors = .85 * np.random.rand(len(longitude),3)

	# Define each cuadrant to plot
	cells = [m.to_pixels(vertices[region]) for region in regions]

	# Generate Figure and save as png (low format)
	fig = plt.figure()
	x,y = m.to_pixels(new_loc[:,0], new_loc[:,1])
	fig = m.show_mpl(figsize=(9,9))
	fig.add_collection( mpl.collections.PolyCollection(cells, facecolors = colors, edgecolors='k', alpha=0.3, linewidth=1.5))
	fig.plot(x,y, 'ok', ms=5)
	plt.savefig("VoronoiMap_PublicLibYYC.png", format='png')

	return 0

def main ():
	
	input_file = 'Calgary_Public_Library_Locations_and_Hours.csv'
	
	#import data
	df = import_data(input_file)

	#extract latitude and longitude
	lat, lon = extract_coords(df)
	
	# Define box to retrive OpenStreetMap
	box = [lat.min(), lon.min(), lat.max(), lon.max()]
	
	# Plot
	plot_voronoi( box, lat, lon, new_locs(lat, lon) )

	return 0


if __name__ == "__main__":
	main()





