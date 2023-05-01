"""
The aim of the file is to create the edges of the image of the tetrapods in order to prepare the data for the watershed algorithm. 
"""

import functions as f
import constants as c 

def run(): 
    current_path = f.os.getcwd()
    parent_path = f.os.path.dirname(current_path)
    path_patches_classified = f.os.path.join(parent_path, f"planity_calculator", 'results')
    list_patches_names = (f.os.listdir(path_patches_classified))
    try : 
        list_patches_names.remove(".DS_Store")
    except: 
        pass

    print("Starting the algorithm to find out the edges for the image : input of the watershed algorithm that will segment the 3D point cloud.")
    print("You can follow how the work goes with the following bar : ")

    for filename in f.tqdm(list_patches_names):
        file_number = filename[25:-4]
        las = f.laspy.read(f.os.path.join(parent_path, f"planity_calculator", 'results', filename)) 
        n = len(las.x)
        x_scaled = f.np.array(las.x)
        y_scaled = f.np.array(las.y) 
        z_scaled = f.np.array(las.z)
        np_coords_3d = f.np.concatenate((x_scaled.reshape((n,1)), y_scaled.reshape((n,1)), z_scaled.reshape((n,1)), f.np.array(las.points.planity[:].tolist()).reshape((n,1))), axis = 1)
        df_coords_3d = f.pd.DataFrame(data=np_coords_3d, columns=['x', 'y', 'z', 'planity']) 

        # All the points that have a planity measure that is too high are fixed to lower value
        max_value = 0.70 #We fix it at 0.7 (empirical measure)
        mask = (df_coords_3d['planity'] > max_value)
        index = df_coords_3d[mask].index
        df_coords_3d.loc[index, 'planity'] = max_value

        # We now create the final image
        cvs = f.ds.Canvas(plot_width = c.PLOT_SIZE, plot_height = c.PLOT_SIZE)
        agg = cvs.points(df_coords_3d, 'x', 'y', agg = f.ds.reductions.mean('planity'))
        agg_array = f.np.asarray(agg)
        f.np.nan_to_num(agg_array, copy=False)

        # We then apply a maximum function to avoid black pixels : it reduces the size of the shape but makes better the classification algorithm
        agg_array = f.scipy.ndimage.maximum_filter(input  = agg_array, size = c.KERNEL_SIZE_MAX, mode = 'constant') 
        agg_array[agg_array <= 0.0001] = f.np.max(agg_array)

        # We save the txt representing the image 
        path_table_image = f.os.path.join(parent_path, f"tables_images", f"table_image_{file_number}.txt")
        f.np.savetxt(path_table_image, agg_array)

        # And we save the image so we can see it 
        f.plt.imshow(agg_array, cmap = 'jet')
        path_image_edges = f.os.path.join(current_path, f"results", f"image_edges_{file_number}.png")
        f.plt.savefig(path_image_edges, dpi = 400)
    
if __name__ == "__main__": 
    run()