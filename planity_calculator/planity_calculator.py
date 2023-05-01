"""
In this file, we just read the patches and add a new dimension : the planity measure. 
We also create the corresponding .csv file where we added the planity_measure column, very important for the next step. 
"""

import functions as f 
import constants as c 


def run(): 
    file_number = 0 
    current_path = f.os.getcwd()
    parent_path = f.os.path.dirname(current_path)
    path_patches = f.os.path.join(parent_path, f"ajaccio_patches")

    list_patches_names = (f.os.listdir(path_patches))
    try : 
        list_patches_names.remove(".DS_Store")
    except: 
        pass
    number_of_file = len(list_patches_names)

    print(f"Starting to calculate the planity measure for {number_of_file} different patches")
    print("You can follow how the work goes with the following bar : ")

    for filename in f.tqdm(list_patches_names):
        file_number += 1 
        patch_path = f.os.path.join(path_patches, filename)
        las = f.laspy.read(patch_path) 
        n = len(las.x)

        # Shifting the data to simplify
        x_scaled = f.np.array(las.x) - f.np.array(las.x).min()
        y_scaled = f.np.array(las.y) -  f.np.array(las.y).min()
        z_scaled = f.np.array(las.z) 

        # Creating the dataframe with the coordinates
        np_coords_3d = f.np.concatenate((x_scaled.reshape((n,1)), y_scaled.reshape((n,1)), z_scaled.reshape((n,1))), axis = 1)
        df_coords_3d = f.pd.DataFrame(data = np_coords_3d, columns=['x', 'y', 'z']) 

        # Creating the dataframe with the coordinates and the corresponding voxel
        df_intermediate = f.create_voxel_column(df_coords_3d)
        
        # We calculate the planity measure in each voxel 
        data = df_intermediate.groupby(['voxel'], group_keys=True).apply(f.planity_measure_df)
        data = data.to_frame(name = "planity_measure")
        data.index = data.index.astype(f.np.int64)
        df_final = f.pd.merge(df_intermediate, data, left_on='voxel', right_index=True)
        df_final.index = df_final['index']
        df_final.sort_index(inplace = True)

        las.add_extra_dim(f.laspy.ExtraBytesParams(name="planity",type=f.np.float64,description="More classes available"))
        las.points.planity[:] = df_final['planity_measure']

        # We save the dataframe file
        path_classified_patch_dataframe = f.os.path.join(parent_path, f"ajaccio_patches_classified_dataframes", f"df_final_{file_number}.csv")
        df_final.to_csv(path_classified_patch_dataframe) 

        # We save the .las file 
        path_classified_patch = f.os.path.join(f"results", f"3d_patch_classified_test_{file_number}.las")
        las.write(path_classified_patch)
       

if __name__ == "__main__": 
    run()