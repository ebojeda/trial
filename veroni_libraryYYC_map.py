import numpy as np
import pandas as pd
import scipy.spatial as spatial
import matplotlib.pyplot as plt
import matplotlib.path as path
import matplotlib as mpl
import smopy


#import data file
df = pd.read_csv('Calgary_Public_Library_Locations_and_Hours.csv')

#data file contains name of library, postal code, square_feet, phone_nmber, business hours (monday to sunday), and adress, which includes GPS coordinates 
print(df)

#We can select the column of interest 
#For instance, to select the posta code, in column 2
post_code = df[df.columns[1:]]
#print(post_code)


#or to select the library names
#Now to select the library names
library_names = df[ df.columns[0] ]
#print(library_names)

#For this exercise we need the last column, which contains latitud and longitud of each location
#in pandas there are different ways to extract data of columns

#opc_1
loc_opc1 = df.ix[:,-2] 
print(type(loc_opc1))

#or opc_2
loc_opc2 = df[ df.columns[-2]]
print(type(loc_opc2))

address = df.Address.str.split('\n+\(|\)')


loc = []
for index in range(len(address)):
	loc.append(address[index][1].split(','))
	#print(address[index][1])

lat = []
lon = []
new_loc = []

for i in loc:
	lat.append(float(i[0]))
	lon.append(float(i[1]))

	new_loc.append( (i[0],[1]) )


box = [min(lat), min(lon), max(lat), max(lon)]

print(box)

m = smopy.Map(box, z=len(address))
m.show_ipython()


