# Importations 
import numpy as np 
import matplotlib.pyplot as plt 
from scipy import ndimage as ndi
from skimage.morphology import disk
from skimage.segmentation import watershed, inverse_gaussian_gradient
from skimage.filters import rank
from skimage.util import img_as_ubyte
import time
import os 
from tqdm import tqdm
import pandas as pd 
import laspy
import constants as c

# Some functions
def normalize(array : np.array) -> np.array :
    """
    Takes an array and return the corresponding normalized array.
     
    Args : 
        array : array to normalize (np.array)
    
    Returns : 
        normalize(array) : the corresponding normalized array
    """
    return array/array.max()



def to_255(array : np.array) -> np.array :
    """
    Takes an array and return the corresponding array with value from 0 to 255.
     
    Args : 
        array : array to change (np.array)
    
    Returns : 
        array : the corresponding  array with new values
    """
    return np.uint8(normalize(array)*255)



def for_watershed(array : np.array, exposant : float) -> np.array:
    """
    Takes an array and return the corresponding normalized array.
     
    Args : 
        array : array to normalize (np.array)
    
    Returns : 
        normalize(array) : the corresponding normalized array
    """

    array = normalize(array)
    array = np.power(array,exposant)
    return normalize(array)


def create_useful_informations(array: np.array) -> tuple:
    """
    This functions takes an array and returns the correspondings gradient, markers and labels.

    Args : 
        array : the image that comes from edges_calculator

    Returns : 
        gradient : the gradient of the image (np.array) 
        markers : the markers found in the image (np.array)
        labels : the final labels in the image, after applying the watershed algorithm (np.array)
    """
    gradient = 1 - inverse_gaussian_gradient(array, alpha = 1000, sigma = 3)
    gradient = rank.mean(to_255(gradient), disk(15))
    
    #find best threshold for markers
    def components_sizes(t):
        markers = gradient < t
        markers = ndi.label(markers)[0]
        return [(markers == i).sum() for i in range(markers.max())]
    candidates = range(100,140,2)
    criterions = [sorted(components_sizes(t))[-5]/1000 for t in candidates]
    threshold = candidates[np.argmax(criterions)]

    #watersheding
    markers = gradient < threshold
    markers = ndi.label(markers)[0]
    labels = watershed(gradient, markers)

    return gradient, markers, labels


# ------------------------------------------------------------------------------------------------------------------------

# -------------------- This is the second part of the segmentation : coloring the patches --------------------------------

# ------------------------------------------------------------------------------------------------------------------------

def create_df_image(df_final : pd.DataFrame) -> pd.DataFrame:
    """
    This function creates the image corresponding to the cloud points ie mathematical projection on the x,y plane.

    Args : 
        df_final : the dataframe where each line corresponds to a point (x,y,z coponents) (pd.DataFrame)
    
    Returns : 
        df_image : the corresponding image (pd.DataFrame)
    """ 

    xmin = df_final['x'].min()
    xmax = df_final['x'].max()
    ymin = df_final['y'].min()
    ymax = df_final['y'].max()

    df_final['i'] = (c.M*((df_final['x'] - xmin)/(xmax - xmin))).astype(np.int64)
    df_final['j'] = (c.M*((df_final['y'] - ymin)/(ymax - ymin))).astype(np.int64)
    df_final['pixel'] = df_final['i']*c.M + df_final['j']

    # We create the dataframe representing the image 
    pixels_list = []
    for i in range(1,c.M+1):
        pixels_list += (np.ones(c.M)*i*c.M + np.arange(1, c.M+1)).tolist()
    return pd.DataFrame(np.array(pixels_list), columns=['pixel']).astype(np.int64)



def change_classification_value(tetrapods_mask : dict, df_image : pd.DataFrame, df_final : pd.DataFrame) -> pd.DataFrame: 
    """
    This function change the classification value in the image where we find a tetrapod.

    Args : 
        tetrapods_mask : the dictionary where each element corresponds to a tetrapod 
        df_image : the initial image of the cloud point, projected over the x,y plane (pd.DataFrame)
        df_final : the cloud point (pd.DataFrame)

    Returns : 
        df_final : the new cloud point where the classification has changed where we found a tetrapod (pd.DataFrame)

    """
    i = 0
    final_column_classif = np.zeros(len(df_image))
    for key, value in tetrapods_mask.items():
        df_image[f"classification_tetra_{i}"] = 0
        image_flatten = value.flatten('F').astype(np.int64)
        if len(image_flatten) == len(df_image):
            image_flatten[image_flatten == 1] += i # We put a different classification for each tetrapod
            df_image.loc[:, f"classification_tetra_{i}"] = image_flatten
            final_column_classif += image_flatten
        i += 1
    df_image['classification'] = final_column_classif.astype(np.int64)
    return df_final.merge(df_image, how='inner', on='pixel')


def create_las(df_final : pd.DataFrame, classification = True): 
    """
    This function takes a cloud point and returns the corresponding las file, taking into account the classification scalar field of the cloud point

    Args : 
        df_final : the cloud point with the classification column (pd.DataFrame)
    Returns : 
        las : the corresponding las file with the classification scalar field 

    """
    current_path = os.getcwd()
    parent_path = os.path.dirname(current_path)
    filename = os.path.join(parent_path, f"init.las")
    las = laspy.read(filename)
    
    # We need to change a bit the coordinates
    df_final.loc[:,'x'] += np.array(las.x).min()
    df_final.loc[:,'y'] += np.array(las.y).min()
    rap_x = las.X[0]/las.x[0]
    rap_y = las.y[0]/las.y[0]
    rap_z = las.z[0]/las.z[0]

    filter_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    header = las.header
    header.point_count = len(df_final)
    filter_las = laspy.LasData(header)
    filter_las.points.X = df_final['x']*rap_x
    filter_las.points.Y = df_final['y']*rap_y
    filter_las.points.Z = df_final['z']*rap_z
    filter_las.points.x = df_final['x']
    filter_las.points.y = df_final['y']
    filter_las.points.z = df_final['z']
    if classification: 
        filter_las.add_extra_dim(laspy.ExtraBytesParams(name="tetrapod_classification",type=np.float64,description="More classes available"))
        filter_las.points.tetrapod_classification[:] = df_final['classification']

    return filter_las
