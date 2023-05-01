"""
The aim of this file is to create the instances of tetrapods found in the cloud point (in all patches).
"""

import functions as f 
import constants as c 

import sys 
path_to_segmentation = f.os.path.dirname(f.os.getcwd())
sys.path.append(path_to_segmentation)
from segmentation import functions as f_segm


def run():

    print("This algorithm takes the results of the watershed algorithm to create the different instances of the generic model that we can find")

    current_dir = f.os.getcwd()
    parent_dir = f.os.path.dirname(current_dir)
    
    dfs_finals = f.os.path.join(parent_dir, f"ajaccio_patches_classified_dataframes")
    list_df_finals = f.os.listdir(dfs_finals)
    try : 
        list_df_finals.remove(f".DS_Store")
    except : 
        pass 

    print(f"Estimate time : {int(3.81*len(list_df_finals)//60)} minutes and {int(3.81*len(list_df_finals)%60)} seconds")
    print("You can follow how the work goes with the following bar : ")
    
    n_tot_tetrapods = 0
    for filepath in f.tqdm(list_df_finals):
        df_final = f.pd.read_csv(f.os.path.join(dfs_finals, filepath))
        patch_number = filepath[9:-4]
        tetrapods_mask = {}
        patch_dir = f.os.path.join(parent_dir, f"tetrapods_mask_all", f"patch_{patch_number}")
        for filename in f.os.listdir(patch_dir):
            tetrapods_mask[filename] = f.np.loadtxt(f.os.path.join(patch_dir, filename))

        # We now convert the point in the dataframe to points in the image 
        df_image = f_segm.create_df_image(df_final)
        
        # We change the classification value 
        df_image = f.change_classification_value(df_image, tetrapods_mask)
        n_tetrapods = len(tetrapods_mask)
        n_tot_tetrapods += n_tetrapods

        directory_tetrapod_models = f.os.path.join(current_dir, f"results")
        for i in range(n_tetrapods):
            df_final2 = df_final.copy()
            df_final2 = df_final2.merge(df_image[df_image.loc[:, f"classification_tetra_{i}"] == 1], how='inner', on='pixel')
            las = f_segm.create_las(df_final=df_final2, classification=False)
            las.write(f.os.path.join(directory_tetrapod_models, f"tetrapod_model_{patch_number}_{i}.las"))

    print(f"We have found a total of {n_tot_tetrapods} tetrapods !")

if __name__ == "__main__": 
    run()