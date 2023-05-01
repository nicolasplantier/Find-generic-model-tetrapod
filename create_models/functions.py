from tqdm import tqdm
import pandas as pd 
import numpy as np 
import os 
import laspy 

def change_classification_value(df_image, tetrapods_mask): 
    final_column_classif = np.zeros(len(df_image))
    i = 0
    for key, value in tetrapods_mask.items():
        df_image[f"classification_tetra_{i}"] = 0
        image_flatten = value.flatten('F').astype(np.int64)
        if len(image_flatten) == len(df_image):
            df_image.loc[:, f"classification_tetra_{i}"] = image_flatten
        i += 1 
    return df_image