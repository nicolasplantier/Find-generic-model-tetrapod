import numpy as np 
import laspy
import pandas as pd 
import os 
import constants as c 
import matplotlib.pyplot as plt 
from tqdm import tqdm

import sys 
path = os.path.dirname(os.getcwd())
sys.path.append(path)
from planity_calculator import functions as f_planity_calculator



def read_las_file(path: str, return_np_coords: bool = False) -> pd.DataFrame:
    """
    This function return the df_coords_3d dataframe corresponding to the las file in the path. 

    Args : 
        path : the path to the las file (str)
        return_np_coords : if we want the corresponding numpy array (bool)

    Returns:
        df_coords_3d : the coordinates of the pints of this las file (pd.DataFrame)
        las : the corresponding las file (laspy)
    """ 

    las = laspy.read(path) 
    n = len(las.x)

    # shift the data to simplify
    x_scaled = np.array(las.x) - np.array(las.x).min()
    y_scaled = np.array(las.y) -  np.array(las.y).min()
    z_scaled = np.array(las.z) 

    # Create the dataframe
    np_coords_3d = np.concatenate((x_scaled.reshape((n,1)), y_scaled.reshape((n,1)), z_scaled.reshape((n,1))), axis = 1)
    df_coords_3d = pd.DataFrame(data=np_coords_3d, columns=['x', 'y', 'z'])

    if return_np_coords: 
        return df_coords_3d, las, np_coords_3d

    return df_coords_3d, las 


# ------------------------------------------------------------------------------------------------------------------------------------------------


def convert_to_ijk(plot_list: list, df_coords_3d: pd.DataFrame) -> list:
    """
    This functions converts the well known plot_list from x,y,z coordinates to i,j,k.

    Args : 
        plot_list : (list)
        df_coords_3d : (pd.DataFrame)

    Returns : 
        plot_list : the same list but in the i,j,k coordinate system 
    """

    xmin = df_coords_3d['x'].min()
    xmax = df_coords_3d['x'].max()
    ymin = df_coords_3d['y'].min()
    ymax = df_coords_3d['y'].max()
    zmin = df_coords_3d['z'].min()
    zmax = df_coords_3d['z'].max()

    for tuple in plot_list:
        tuple[0][0] = xmin + (xmax - xmin)*(tuple[0][0]/c.M)
        tuple[1][0] = (xmax - xmin)*(tuple[1][0]/c.M)

        tuple[0][1] = ymin + (ymax - ymin)*(tuple[0][1]/c.M)
        tuple[1][1] = (ymax - ymin)*(tuple[1][1]/c.M)

        tuple[0][2] = zmin + (zmax - zmin)*(tuple[0][2]/c.M)
        tuple[1][2] =  (zmax - zmin)*(tuple[1][2]/c.M)
    
    return plot_list


# ------------------------------------------------------------------------------------------------------------------------------------------------


def find_feet_tetrapod(plot_list: list, 
                       df_coords_3d: pd.DataFrame, 
                       file_number: str) -> pd.DataFrame:
    """
    This function finds the feet inside a tetrapod and calculate a planity measure inside of them for all points.
    
    Args : 
        plot_list : the list of all directions + centers of gravity (list)
        df_coords_3d : the dataFrame with all coordinates of points
        file_number : the number of the file (str)
    
    Returns :
        df_coords_3d : the Dataframe with the feet and the corresponding classification and planity measure (pd.DataFrame)
    """ 

    fig, axes = plt.subplots(1,len(plot_list),figsize=(6, 6))
    df_coords_3d['classification'] = 0 
    df_coords_3d['planity_final'] = 0 
    for n_axe, axe in enumerate(plot_list): #We project the points axis after axis 
        b = axe[0]
        u = axe[1]/np.linalg.norm(axe[1]) 

        df_coords_3d[f"x_distance_axe_{n_axe}"] = (df_coords_3d['y']-b[1])*u[2] - (df_coords_3d['z'] - b[2])*u[1]
        df_coords_3d[f"y_distance_axe_{n_axe}"] = (df_coords_3d['z']-b[2])*u[0] - (df_coords_3d['x'] - b[0])*u[2]
        df_coords_3d[f"z_distance_axe_{n_axe}"] = (df_coords_3d['x']-b[0])*u[1] - (df_coords_3d['y'] - b[1])*u[0]
        df_coords_3d[f"distance_axe_{n_axe}"] = np.sqrt(df_coords_3d[f"x_distance_axe_{n_axe}"]**2 + df_coords_3d[f"y_distance_axe_{n_axe}"]**2 + df_coords_3d[f"z_distance_axe_{n_axe}"]**2)
        # values, bins = np.histogram(df_coords_3d[f"distance_axe_{n_axe}"], bins=300)

        axes[n_axe].set_title(f"This is the histogram for tetrapod number {file_number} in axis number {n_axe}", fontsize = 10)
        axes[n_axe].set_xlabel(f"Density / distance")
        axes[n_axe].set_ylabel("Density")
        values, bins = np.histogram(df_coords_3d[f"distance_axe_{n_axe}"], bins=300)
        axes[n_axe].plot(bins[20:-1],values[20:]/bins[20:-1]**2)  
        bins = bins[:-1]

        values = values/bins**2


        """
        We estimate the approximate radius of a tetrapod at 0.75. 
        To find the local minima (the rapartition that corresonds to a planar surface), we thus find out the minimum value before 0.75 (before 0.6 for instance)
        The local minimum is usually around 0.27. 
        """
        mask = bins > 0.2
        index_max = np.argmax(values[mask])

        local_max = values[mask][index_max]
        bin_max = bins[mask][index_max]

        min_value = 0.15*local_max # We can change this value to get bigger foot

        mask = (bins < bin_max) | (values > min_value)

        dist_min = bins[mask][-1] 
        mask_distance_axe = df_coords_3d[f"distance_axe_{n_axe}"] < dist_min
        

        df_coords_3d[f"distance_center_gravity_{n_axe}"] = np.sqrt((df_coords_3d['x'] - b[0])**2 + (df_coords_3d['y'] - b[1])**2 + (df_coords_3d['z'] - b[2])**2)
        mask_distance_center_gravity_axe = df_coords_3d[f"distance_center_gravity_{n_axe}"] < 1


        df_coords_3d.loc[mask_distance_axe & mask_distance_center_gravity_axe,"classification"] = n_axe+1

        
        # Now we add a planity_measure in each foot 
        lala = df_coords_3d[mask_distance_axe & mask_distance_center_gravity_axe].copy(deep = True)
        df_intermediate = f_planity_calculator.create_voxel_column(lala)

        data = df_intermediate.groupby(['voxel'], group_keys=True).apply(f_planity_calculator.planity_measure_df)
        data = data.to_frame(name = "planity_measure")
        data.index = data.index.astype(np.int64)
        df_final = pd.merge(df_intermediate, data, left_on='voxel', right_index=True)
        df_final.index = df_final['index']
        df_final.sort_index(inplace = True)

        df_coords_3d.loc[mask_distance_axe & mask_distance_center_gravity_axe,"planity_final"] = df_final['planity_measure']
    
    return df_coords_3d


# ------------------------------------------------------------------------------------------------------------------------------------------------


def delete_useless_points(df_coords_3d: pd.DataFrame) -> pd.DataFrame:
    """
    Here to delete the useless points, the ones that do not belong to a foot or that have a too high planity measure. 
    
    Args : 
        df_coords_3d : all the points (pd.DataFrame)
    Returns :
        df_coords_3d : the new dataframe without certain points (pd.DataFrame)
    """

    # deleting points that do not have the right planity measure 
    to_delete = df_coords_3d[df_coords_3d['planity_final'] > 0.2].index
    df_coords_3d.drop(index=to_delete, inplace = True)
        
    # deleting points that do not belong to a single foot 
    to_delete = df_coords_3d[df_coords_3d['classification'] == 0].index
    df_coords_3d.drop(index=to_delete, inplace = True)

    return df_coords_3d


# ------------------------------------------------------------------------------------------------------------------------------------------------


def write_tetrapods_with_feet(df_coords_3d: pd.DataFrame,
                            path_tetrapod_with_feet: str, 
                            las : laspy) -> None:
    """
    Writes the new las file : with feet and without all the useless points.

    Args : 
        df_coords_3d : the points to add (pd.DataFrame)
        path_tetrapod_with_feet : where we want to write the new file (str)
        las : the initial las file (laspy)

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

    filter_las.add_extra_dim(laspy.ExtraBytesParams(name="classif",type=np.float64,description="More classes available"))
    filter_las.points.classif[:] = df_coords_3d['classification']
    filter_las.add_extra_dim(laspy.ExtraBytesParams(name="planity",type=np.float64,description="More classes available"))
    filter_las.points.planity[:] = df_coords_3d['planity_final']
    filter_las.write(path_tetrapod_with_feet)
