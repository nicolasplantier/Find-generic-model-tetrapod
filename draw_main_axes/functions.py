# Import libraries
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import os 
from tqdm import tqdm
import pandas as pd 
import laspy 

import constants as c 

def create_main_axes_file(text : str, path_to_main_axe : str) -> list:
    """
    Creates the file where one can find the main axes of a tetrapod with the same format as input.
    
    Args : 
        text : the file of the input axes (str)
        path_to_main_axe : the path where one wants to write the new axes (str)
    
    Returns : 
        plot_list : the list with the center of gravity of all axes and directions (list)
    """

    plot_list = []
    n_lines = len(text)
    text_line = text[0]
    n = eval(text_line[text_line.find("npoints=")+8:text_line.find(", ")])
    a = eval(text_line[text_line.find("a=")+2:text_line.find("),")+1])
    b = eval(text_line[text_line.find("b=")+2:]) 
    plot_list.append([np.array(list(a)), np.array(list(b))])

    with open(path_to_main_axe, 'w') as the_file:
        the_file.write(text_line)

    for k in range(1,n_lines):
        text_line = text[k]
        new_n = eval(text_line[text_line.find("npoints=")+8:text_line.find(", ")])
        new_a = eval(text_line[text_line.find("a=")+2:text_line.find("),")+1])
        new_b = eval(text_line[text_line.find("b=")+2:]) 

        intermediate_array = np.linalg.norm((np.array(plot_list)[:,1]-np.array(list(new_b))), axis = 1)
        intermediate_array_2 = np.linalg.norm((np.array(plot_list)[:,0]-np.array(list(new_a))), axis = 1)
        mask_direction = all((intermediate_array > 1))
        mask_center_gravity = all((intermediate_array_2 > 30))

        mask_n_points = (new_n > 15)

        if mask_direction and mask_n_points and mask_center_gravity:
            plot_list.append([np.array(list(new_a)), np.array(list(new_b))])
            with open(path_to_main_axe, 'a') as the_file:
                the_file.write(f"{text_line}")
        
    return plot_list


# ------------------------------------------------------------------------------------------------------------------------


def remove_too_little(path_to_main_axe : str) -> None:
    """
    Removes axes of tetrapods without enough axes. (less than 2 excluded)

    Args : 
        path_to_main_axe : the file we want to check the number of lines

    Returns : 
        None
    """
    new_text = open(path_to_main_axe).readlines()
    n_lines = len(new_text)
    if n_lines < 2:
        os.remove(path_to_main_axe)


# ------------------------------------------------------------------------------------------------------------------------


def draw_figure(number_model : str, 
                x : list, 
                y : list, 
                z : list, 
                plot_list : list, 
                path_fig : str) -> None:
    """
    This function draws the axes found (all axes, not only the main axes) to show them on a picture. 

    Args : 
        number_model : The number of model of the tetrapod (str)
        x : list of x coordinates of the points found inside an axis (list)
        y : list of y coordinates of the points found inside an axis (list)
        z : list of z coordinates of the points found inside an axis (list)
        plot_list : each element corresponds to an axis and has two elements, a is the direction of the axis, b is the center of mass (list)
        path_fig : path to register te fig (str)

    Returns : 
        None 
    """
    fig = plt.figure()
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
    
    for element in plot_list:
        a = element[0]
        b = element[1]/10
        vect_list = []
        for k in range (25*10): 
                vect_list.append(a+k*b)
        for k in range (25*10): 
                vect_list.append(a-k*b)
        vect_list = np.array(vect_list)
        sctt = ax.scatter3D(vect_list[:,0], vect_list[:,1], vect_list[:,2],
                        alpha = 0.8,
                        color = 'red',
                        marker ='^',
                        s = 4)

    plt.title(f"Axes found inside the tetrapod {number_model}")
    ax.set_xlabel('X-axis', fontweight ='bold')
    ax.set_ylabel('Y-axis', fontweight ='bold')
    ax.set_zlabel('Z-axis', fontweight ='bold')
    ax.set_xlim(0,100)
    ax.set_ylim(0,100)
    ax.set_zlim(0,100)
    fig.colorbar(sctt, ax = ax, shrink = 0.5, aspect = 5)
    plt.savefig(path_fig, dpi = 300)


# ------------------------------------------------------------------------------------------------------------------------


def get_plot_list(path_main_axes : str) -> list: 
    """
    This function creates the list with the center of mass and direction of each axe.

    Args : 
        path_main_axes : where we read the main axes (str)
    
    Returns :
        plot_list : where we put them (list)
    
    """
    plot_list = []
    text = open(path_main_axes).readlines()
    n_lines = len(text)
    text_line = text[0]
    a = eval(text_line[text_line.find("a=")+2:text_line.find("),")+1])
    b = eval(text_line[text_line.find("b=")+2:]) 
    plot_list.append([np.array(list(a)), np.array(list(b))])
    for k in range(1,n_lines):
        text_line = text[k]
        new_a = eval(text_line[text_line.find("a=")+2:text_line.find("),")+1])
        new_b = eval(text_line[text_line.find("b=")+2:]) 
        plot_list.append([np.array(list(new_a)), np.array(list(new_b))])
    return plot_list


# ------------------------------------------------------------------------------------------------------------------------


def create_axes_as_points(plot_list : list) -> pd.DataFrame :
    """
    This function takes the previous plot_list and calculate the points around the center of gravity in the direction of the axis.
    It uses the global variable LEN_AX which corresponds to the number of points that we want to represent.

    Args : 
        plot_list : list of center of mass + direction of each axis (list)

    Returns : 
        df_axes_plot : the corresponding points (pd.DataFrame)

    """

    df_axes_plot = pd.DataFrame(columns = ['i','j','k']) 
    for element in plot_list:
        a = element[0]
        b = element[1]/100
        vect_list = []
        for k in range (c.LEN_AX*100): 
                vect_list.append(a+k*b)
        for k in range (c.LEN_AX*100): 
                vect_list.append(a-k*b)
        vect_list = np.array(vect_list)

        df_vect_list =  pd.DataFrame(data = vect_list, columns = ['i', 'j', 'k'])
        df_axes_plot = pd.concat([df_axes_plot, df_vect_list], axis = 0)
    return df_axes_plot


# ------------------------------------------------------------------------------------------------------------------------


def add_points_axes_to_dfcoods(df_coords_3d : pd.DataFrame, df_axes_plot : pd.DataFrame) -> pd.DataFrame: 
    """
    The function takes all the points of a tetrapod and adds the points of the main axes. 

    Args : 
        df_coords_3d : the points of the tetrapod (pd.DataFrame)

    Returns : 
        df_coords_3d : the points of the tetrapod + the points of the main axes (pd.DataFrame)

    """

    xmin = df_coords_3d['x'].min()
    xmax = df_coords_3d['x'].max()
    ymin = df_coords_3d['y'].min()
    ymax = df_coords_3d['y'].max()
    zmin = df_coords_3d['z'].min()
    zmax = df_coords_3d['z'].max()

    df_axes_plot['x']  = xmin + (xmax - xmin)*(df_axes_plot['i']/c.M)
    df_axes_plot['y']  = ymin + (ymax - ymin)*(df_axes_plot['j']/c.M)
    df_axes_plot['z']  = zmin + (zmax - zmin)*(df_axes_plot['k']/c.M)

    max_index = df_coords_3d.index.max()
    df_axes_plot.index = np.arange(max_index+1, max_index+1 + len(df_axes_plot))
    df_points_to_add = pd.DataFrame(data = df_axes_plot[['x','y','z']], columns = ['x', 'y', 'z'])
    df_points_to_add['color'] = 1
    df_coords_3d['color'] = 0
    df_coords_3d = pd.concat([df_coords_3d,df_points_to_add], axis = 0)

    return df_coords_3d


# ------------------------------------------------------------------------------------------------------------------------


def create_las_with_axes(path_to_las :str, las : laspy, df_coords_3d : pd.DataFrame) -> None:
    """
    This function creates the las file with the main axes inside the tetrapod.

    Args : 
        path_to_las : the path to the tetrapod with axes (str)
        las : the initial las file (laspy)
        df_coords_3d : the points of the tetrapod with the main axes 

    Returns : 
        None 
    """

    df_coords_3d.loc[:,'x'] += np.array(las.x).min()
    df_coords_3d.loc[:,'y'] += np.array(las.y).min()
    rap_x = las.X[0]/las.x[0]
    rap_y = las.y[0]/las.y[0]
    rap_z = las.z[0]/las.z[0]

    filter_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    header = las.header
    header.point_count = len(df_coords_3d)
    filter_las = laspy.LasData(header)
    filter_las.points.X = df_coords_3d['x']*rap_x
    filter_las.points.Y = df_coords_3d['y']*rap_y
    filter_las.points.Z = df_coords_3d['z']*rap_z
    filter_las.points.x = df_coords_3d['x']
    filter_las.points.y = df_coords_3d['y']
    filter_las.points.z = df_coords_3d['z']
    filter_las.add_extra_dim(laspy.ExtraBytesParams(name="color",type=np.float64,description="More classes available"))
    filter_las.points.color[:] = df_coords_3d['color']
    filter_las.write(path_to_las)    
