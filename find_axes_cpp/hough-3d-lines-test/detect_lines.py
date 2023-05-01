# Import libraries
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

data = np.genfromtxt('point_cloud_main_axe2.dat',
                    dtype=np.int64,
                    delimiter=',')


# Creating dataset
z = data[:,2]
x = data[:,0]
y = data[:,1]
 
# Creating figure
fig = plt.figure(figsize = (16, 9))
ax = plt.axes(projection ="3d")
   
# Add x, y gridlines
ax.grid(b = True, color ='grey',
        linestyle ='-.', linewidth = 0.3,
        alpha = 0.2)
 
 
# Creating color map
my_cmap = plt.get_cmap('hsv')
 


# Creating plot
sctt = ax.scatter3D(x, y, z,
                    alpha = 0.8,
                    #c = (x + y + z),
                    #cmap = my_cmap,
                    marker ='^',
                    s = 0.8)
 

# adding the line plot
# creatin plot_list :
plot_list = []
plot_list.append([np.array([30.392045,48.193182,71.215909]), np.array([0.297233,-0.022309,-0.954544])])
plot_list.append([np.array([73.487179,50.166667,40.948718]), np.array([0.988559,0.074275,-0.131279])])
plot_list.append([np.array([28.981481,20.944444,30.740741]), np.array([0.308055,0.822309,0.478446])])
plot_list.append([np.array([26.525000,65.150000,29.700000]), np.array([0.474501,-0.699134,0.534846])])
for element in plot_list:
        a = element[0]
        b = element[1]/10
        vect_list = []
        for k in range (30*10): 
                vect_list.append(a+k*b)
        for k in range (30*10): 
                vect_list.append(a-k*b)
        vect_list = np.array(vect_list)
        sctt = ax.scatter3D(vect_list[:,0], vect_list[:,1], vect_list[:,2],
                        alpha = 0.8,
                        color = 'red',
                        marker ='^',
                        s = 4)

plt.title("Axes found inside the tetrapod")
ax.set_xlabel('X-axis', fontweight ='bold')
ax.set_ylabel('Y-axis', fontweight ='bold')
ax.set_zlabel('Z-axis', fontweight ='bold')
ax.set_xlim(0,100)
ax.set_ylim(0,100)
ax.set_zlim(0,100)
#fig.colorbar(sctt, ax = ax, shrink = 0.5, aspect = 5)

# show plot
plt.show()