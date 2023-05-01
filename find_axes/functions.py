import numpy as np 
import pandas as pd
from statsmodels.formula.api import ols  
import os 
from tqdm import tqdm 
import datashader as ds 
import laspy
import matplotlib.pyplot as plt 
import multiprocessing

current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)

import sys 
sys.path.append(parent_dir)

from edges_calculator import constants as c_edges
import constants as c 
m = c.M



def create_3d_image(m : int) -> pd.DataFrame:
    """
    This function creates a 3d image : a column voxel is added as well as i,j,k columns
    
    Args : 
        m : The integer of the size of the cube (int)
    
    Returns : 
        df_image_3d : The corresponding 3d image of size : m*m*m. Each line corresponds to a voxel (pd.DataFrame)
    """
    pixels_list = []
    i_table = np.arange(0, m)
    j_table = (np.arange(0, m)*(10**(np.log10(m)//1 + 1))).astype(np.int64)
    k_table = (np.arange(0, m)*(10**(np.log10(m)//1 + np.log10(m)//1 + 2))).astype(np.int64)
    X, Y, Z = np.meshgrid(i_table, j_table, k_table)
    df_image_3d = pd.DataFrame(np.array(X+Y+Z).flatten(), columns=['voxel']).astype(np.int64)

    cent = 10**(np.log10(m)//1 + np.log10(m)//1 + 2)
    diz = 10**(np.log10(m)//1 + 1)
    unit = 1
    df_image_3d['i'] = ((df_image_3d['voxel'] - cent*(df_image_3d['voxel']//cent) - diz*((df_image_3d['voxel'] - cent*(df_image_3d['voxel']//cent))//diz))//unit).astype(np.int64)
    df_image_3d['j'] = ((df_image_3d['voxel'] - cent*(df_image_3d['voxel']//cent))//diz).astype(np.int64)
    df_image_3d['k'] = (df_image_3d['voxel']//cent).astype(np.int64)
    return df_image_3d



def create_voxel_column_constant(df : pd.DataFrame, m :int, df_coords_3d : pd.DataFrame) -> pd.DataFrame: 
    """
    Create the voxel column as well as the i,j,k columns. Each triplet (i,j,k) is unique and corresponds to one unique voxel. 

    Args : 
        df : input dataframe, with x,y,z columns (pd.DataFrame)
        m : integer for the size of the final 3d image (int)
        df_coords_3d : values we use to calculate i,j,k columns (pd.DataFrame)

    Returns : 
        df : the same dataframe as before, but with these new : i,j,k,voxel columns (pd.DataFrame)
    """
    xmin = df['x'].min()
    xmax = df['x'].max()
    ymin = df['y'].min()
    ymax = df['y'].max()
    zmin = df['z'].min()
    zmax = df['z'].max()
    df['i'] = (m*((df_coords_3d['x'] - xmin)/(xmax - xmin))).astype(np.int64)
    df['j'] = (m*((df_coords_3d['y'] - ymin)/(ymax - ymin))).astype(np.int64)
    df['k'] = (m*((df_coords_3d['z'] - zmin)/(zmax - zmin))).astype(np.int64)
    df['index'] = df.index
    df['voxel'] = (df['i'] + df['j']*(10**(np.log10(m)//1 + 1)) + df['k']*(10**(np.log10(m)//1 + np.log10(m)//1 + 2))).astype(np.int64)
    return df




def vect_plan(df : pd.DataFrame, delta : float) -> float:
    """
    This function takes points in the same voxel and returns the norm of the vector on the x,y plan
    
    Args : 
        df : The dataframe with point belonging to the same voxel (pd.DataFrame)
    
    Returns : 
        norm : the norm of the vector in the x,y plane (float)

    """
    if len(df) < 3:
        normal = np.nan
    else :    
        regress_plane = ols("z ~ x + y", df).fit()
        d, a, b = regress_plane._results.params
        c = -1
        normal = np.array([a,b,c])
        normal = delta*(normal/np.linalg.norm(normal))
    norm = np.round(normal,5)
    return norm




def calculate_delta(df : pd.DataFrame) -> tuple :
    """
    Calculate delta for a given dataframe
    """
    xmin = df['x'].min()
    xmax = df['x'].max()
    ymin = df['y'].min()
    ymax = df['y'].max()
    zmin = df['z'].min()
    zmax = df['z'].max()
    delta = np.round(min((xmax-xmin)/m, (ymax-ymin)/m, (zmax-zmin)/m), 2) # This is the approximate size of a voxel (delta x delta x delta)
    xsize = (xmax-xmin)/m
    ysize = (ymax-ymin)/m
    zsize = (zmax-zmin)/m
    return delta, xsize, ysize, zsize



def create_voxel_list(df, xsize, ysize, zsize, limit_beginning = False):
    """
    This function will calculate all the voxels that we be touched by the vector planity.
    The i,j,k coordinates are the coordinates of the point where we calculated the vector_planity. 
    """
    # We first add the i,j,k columns
    df['voxel'] = df.index
    cent = 10**(np.log10(m)//1 + np.log10(m)//1 + 2)
    diz = 10**(np.log10(m)//1 + 1)
    unit = 1
    df['i'] = ((df['voxel'] - cent*(df['voxel']//cent) - diz*((df['voxel'] - cent*(df['voxel']//cent))//diz))//unit).astype(np.int64)
    df['j'] = ((df['voxel'] - cent*(df['voxel']//cent))//diz).astype(np.int64)
    df['k'] = (df['voxel']//cent).astype(np.int64)
    df.drop('voxel', axis = 1, inplace = True)

    # We first need to convert the vector_planity in (x,y,z) to (i,j,k)
    df['dn_x'] = df.loc[:, 'dx']/xsize
    df['dn_y'] = df.loc[:, 'dy']/ysize
    df['dn_z'] = df.loc[:, 'dz']/zsize
    df.drop('dx', axis = 1, inplace = True)
    df.drop('dy', axis = 1, inplace = True)
    df.drop('dz', axis = 1, inplace = True)

    # We will just add the first 2, that is the i,j,k method
    """n = 2
    for k in range(1,n+1):
        df[f"next_voxel_{k}_i"] = (df[f"i"] + k*df['dn_x']).astype(np.int64)
        df[f"next_voxel_{k}_j"] = (df[f"j"] + k*df['dn_y']).astype(np.int64)
        df[f"next_voxel_{k}_k"] = (df[f"k"] + k*df['dn_z']).astype(np.int64)"""

    # We will just add the first 2, that is the voxel method
    n = 30
    for k in range(1,n+1):
        mask_i = (0 <= df[f"i"] + k*df['dn_x']) & (df[f"i"] + k*df['dn_x']<= m) #we need to be careful that we are still inside the cube in the x direction
        mask_j = (0 <= df[f"j"] + k*df['dn_y']) & (df[f"j"] + k*df['dn_y']<= m) #we need to be careful that we are still inside the cube in the y direction
        mask_k = (0 <= df[f"k"] + k*df['dn_z']) & (df[f"k"] + k*df['dn_z']<= m) #we need to be careful that we are still inside the cube in the z direction
        mask = mask_i & mask_j & mask_k
        df[f"voxel_{k}"] = -1
        df.loc[mask,f"voxel_{k}"] = ((df[mask][f"i"] + k*df[mask]['dn_x']).astype(np.int64)*unit + (df[mask][f"j"] + k*df[mask]['dn_y']).astype(np.int64)*diz + (df[mask][f"k"] + k*df[mask]['dn_z']).astype(np.int64)*cent).astype(np.int64)
    if limit_beginning:  # It is very important in the case edges of the tetrapod we are looking at are not clearly defined. 
        for k in range(1,12):
            df[f"voxel_{k}"] = -1
    for k in range(2,n+1):
        mask = (df[f"voxel_{k}"] == df[f"voxel_{k-1}"])
        df.loc[mask,f"voxel_{k}"] = -1
    arr = np.unique(np.array(df.iloc[:,6:6+n]), return_counts=True)
    voxels = arr[0]
    counts = arr[1]
    df_voxel_counts = pd.DataFrame(index=voxels, data = counts, columns=['counts'])
    return df, df_voxel_counts