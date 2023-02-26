"""
This .py creates the functions that we will use to calculate the planity measure of our patches.
"""

import pandas as pd
import numpy as np
import math
from constants import PX_SIZE
from statsmodels.formula.api import ols 
import random as rd 
from tqdm import tqdm
import laspy 
import os 



def create_voxel_column(df : pd.DataFrame) -> pd.DataFrame:
    
    """
    This function takes a dataframe and return the same dataframe where we created a column saying to which voxel each point belongs.

    Args : 
        df : the dataframe where we want to know to which voxel each point belongs (pd.Dataframe)

    Returns : 
        df_intermediate : the same one with the column saying to which voxel each point belongs to (pd.Dataframe)
    """

    xmax, xmin = np.max(df['x']), np.min(df['x'])
    ymax, ymin = np.max(df['y']), np.min(df['y'])
    zmax, zmin = np.max(df['z']), np.min(df['z'])
    N_x = math.floor((xmax - xmin)/PX_SIZE)
    N_y = math.floor((ymax - ymin)/PX_SIZE)
    N_z = math.floor((zmax - zmin)/PX_SIZE)
    indexs = df.index
    df_intermediate = df.copy()

    # Let's know where each point belongs (voxel number)
    df_intermediate['i'] = (N_x*((df['x'] - xmin)/(xmax - xmin))).astype(np.int64)
    df_intermediate['j'] = (N_y*((df['y'] - ymin)/(ymax - ymin))).astype(np.int64)
    df_intermediate['k'] = (N_z*((df['z'] - zmin)/(zmax - zmin))).astype(np.int64)
    df_intermediate['index'] = df_intermediate.index
    df_intermediate['voxel'] = (df_intermediate['i'] + df_intermediate['j']*(10**(np.log10(N_x)//1 + 1)) + df_intermediate['k']*(10**(np.log10(N_x)//1 + np.log10(N_y)//1 + 2))).astype(np.int64)
    
    return df_intermediate

# ---- ---- ---- ---- 

def planity_measure_df(df : pd.DataFrame) -> float:
    """
    This function takes points which belong to the same voxel as input and gives the absolute error : distance to the regression plane of theses points.
    This function could be better : instead of setting arbitrary limit for the planity measure of a vector that is on the edge of an object (vertical edge), we could use the distribution of planity measures.

    Args : 
        df : The dataframe where each row corresponds to a point (Dataframe)
    
    Returns : 
        planity_measure : The planity measure of this voxel ie the absolute distance of these points to the resgression plane
    """
    if len(df) < 3: # If the number of points is too little then there are not enough points to create a plane : the planity measure is set to 0. 
        planity_measure = 0
    else :    
        regress_plane = ols("z ~ x + y", df).fit()
        d, a, b = regress_plane._results.params
        c = -1
        normal = np.array([a,b,c])
        normal = normal/np.linalg.norm(normal)
        norm_vect_horizontal = np.linalg.norm([a,b])
        if norm_vect_horizontal > 2:  # if the normal vector is more or less colinear to the x,y plane then we are on the edge of an object, certainly a tetrapod
            value = rd.randint(1,4)
            if value == 1 or value == 2 or value == 3:
                planity_measure = rd.random()*(0.04-0.02) + 0.02  # We are on a tetrapod and its real mesure is somewhere around here. 
            else : 
                planity_measure = rd.random()*(0.07-0.04) + 0.04
        else : 
            cos_theta = np.abs(normal[2])
            z_predict = regress_plane.predict(df)
            dist_table = cos_theta*(np.abs(z_predict - df['z']))
            dist_table_max = dist_table.copy()
            ids = []
            for k in range(len(df)//5): 
                id_max = dist_table_max.idxmax(axis = 0)
                ids.append(id_max)
                dist_table_max.drop(index = id_max)
            dist_table.loc[ids] = 100*dist_table[ids]
            planity_measure = dist_table.std()

    return planity_measure