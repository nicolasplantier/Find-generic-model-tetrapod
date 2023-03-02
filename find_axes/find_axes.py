"""
The aim of this file is to do the echography and extract the main points of this echography. 
It first creates an hypercube from a .las cloudpoints : high values represent voxel where normal vectors (surface of the tetrapod) converge.
"""

import functions as f 
import constants as c 
import matplotlib.pyplot as plt


def run():
    current_dir = f.os.getcwd()
    parent_dir = f.os.path.dirname(current_dir)
    list_tetrapods_files_dir = f.os.path.join(parent_dir, f"create_models", f"results")
    list_tetrapods_files = f.os.listdir(list_tetrapods_files_dir)
    try : 
        list_tetrapods_files.remove(f".DS_Store")
    except : 
        pass

    for filename in f.tqdm(list_tetrapods_files):
        las = f.laspy.read(f.os.path.join(list_tetrapods_files_dir, filename))
        n = len(las.x)

        # shift the data to simplify
        x_scaled = f.np.array(las.x) - f.np.array(las.x).min()
        y_scaled = f.np.array(las.y) -  f.np.array(las.y).min()
        z_scaled = f.np.array(las.z) 

        # Create the dataframe
        np_coords_3d = f.np.concatenate((x_scaled.reshape((n,1)), y_scaled.reshape((n,1)), z_scaled.reshape((n,1))), axis = 1)
        df_coords_3d = f.pd.DataFrame(data=np_coords_3d, columns=['x', 'y', 'z']) 


        # We create the new voxel column as well as i,j,k, index, voxel columns
        delta, xsize, ysize, zsize = f.calculate_delta(df_coords_3d)
        df_coords_3d = f.create_voxel_column_constant(df_coords_3d, c.M, df_coords_3d)
        df_image_3d = f.create_3d_image(c.M)


        # ----------------------------------------------------------------------------------------------------------------

        # We calculate the planity measure in each voxel 
        data = df_coords_3d.groupby(['voxel'], group_keys=True).apply(f.vect_plan, delta)
        data = data.to_frame(name = "planity_vector") # in this dataframe, we have the normal vector for each voxel => we need to calculate 
        data.dropna(inplace = True)

        # just to split the columns 
        data['voxel'] = data.index
        data = (f.pd.concat([data['voxel'], data['planity_vector'].apply(f.pd.Series)], axis = 1).rename(columns = {0: 'dx', 1: 'dy', 2: 'dz'})).drop('voxel', axis = 1)
        data, df_voxel_counts = f.create_voxel_list(data, xsize, ysize, zsize)
        df_image_3d.index = df_image_3d['voxel']
        df_final_image = df_image_3d.join(df_voxel_counts) 
        df_final_image = df_final_image.fillna(0).astype(f.np.int64)

        fig, axes = plt.subplots(3,3,figsize=(10, 6))
        s = 0
        for i in range(3):
            for j in range(3):
                s += 10
                image = df_final_image[df_final_image['k'] == s] 
                cvs = f.ds.Canvas(plot_width=c.M, plot_height=c.M)
                agg = cvs.points(image, 'i', 'j', agg = f.ds.reductions.mean('counts'))
                agg_array = f.np.asarray(agg)
                f.np.nan_to_num(agg_array, copy=False)
                axes[i,j].set_title(f"Cut over the layer number {s}")
                axes[i,j].axis('off')
                axes[i,j].imshow(agg_array, cmap = 'jet')

        dir_images_echography = f.os.path.join(current_dir, "results", f"echographie_tetrapods_all", f"{filename[:-4]}.png")
        plt.savefig(dir_images_echography, dpi = 400)
        dir_csv_echography = f.os.path.join(current_dir,  "results", f"echographie_tetrapods_all_csv", f"{filename[:-4]}.csv")
        df_final_image.to_csv(dir_csv_echography) 

        

if __name__ == "__main__": 
    run()


