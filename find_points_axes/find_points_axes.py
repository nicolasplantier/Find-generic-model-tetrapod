"""
The aim of this file is to extract the points inside the axes using the echography made in "find axes"
"""

import functions as f 
import constants as c 
from constants import M as m 

if __name__ == "__main__": 

    current_dir = f.os.getcwd()
    parent_dir = f.os.path.dirname(current_dir)
    echography_dir = f.os.path.join(parent_dir, f"find_axes", f"results", f"echographie_tetrapods_all_csv")
    list_echographie_files = f.os.listdir(echography_dir)
    try : 
        list_echographie_files.remove(f".DS_Store")
    except :
        pass

    print("This algorithm find the points that belong to the axes of the tetrapods thanks to the results of the 'find axes' algorithm")
    print(f"Estimate time : {int(2.30*len(list_echographie_files)//60)} minutes and {int(2.30*len(list_echographie_files)%60)} seconds")
    print("You can follow how the work goes with the following bar : ")

    for filename in f.tqdm(list_echographie_files):
        file = f.os.path.join(echography_dir, filename)
        df_final_image = f.pd.read_csv(file)
        df_final_image.drop("voxel.1", axis = 1, inplace = True)
        df_final_image.loc[:,'j'] = m - df_final_image.loc[:,'j']

        # Initialisation
        mask = (df_final_image['k'] == 100)
        image = df_final_image[mask]
        cvs = f.ds.Canvas(plot_width=m, plot_height=m)
        agg = cvs.points(image, 'i', 'j', agg = f.ds.reductions.mean('counts'))
        agg_array = f.np.asarray(agg)
        f.np.nan_to_num(agg_array, copy=False)
        agg_array = agg_array.astype(f.np.int64)
        i_max, j_max = f.np.where(agg_array == f.np.max(agg_array))

        p_max_value = f.np.max(agg_array)
        p_i_max, p_j_max = i_max[0], j_max[0] #p for previous 

        X = []
        Y = []
        Y_der = [0]
        axe_points_coordinates = []

        for k in range(99, 0, -1):  # We go layers after layers 
            mask = (df_final_image['k'] == k)
            image = df_final_image[mask]
            cvs = f.ds.Canvas(plot_width=m, plot_height=m)
            agg = cvs.points(image, 'i', 'j', agg = f.ds.reductions.mean('counts'))
            agg_array = f.np.asarray(agg)

            agg_array = agg_array.transpose()
            agg_array = f.np.flip(agg_array, axis = 1)
                
            f.np.nan_to_num(agg_array, copy=False)
            agg_array = agg_array.astype(f.np.int64)
            max_value = f.np.max(agg_array)
            limit_max_value = 0.5*max_value
            if limit_max_value >= 9: # we need to find out for import points that are in an axe 
                i,j = f.np.where(agg_array >= limit_max_value)
                axe_points_coordinates += [[i[l],j[l], k] for l in range(len(i))]

        point_cloud = f.np.array(axe_points_coordinates).astype(f.np.int64)
        result_dir = f.os.path.join(current_dir, f"results", f"points_on_axes", f"point_cloud_{filename[:-4]}.dat")
        result_dir_for_cpp = f.os.path.join(parent_dir, "find_axes_cpp", "hough-3d-lines", "input", f"point_cloud_{filename[:-4]}.dat")
        f.np.savetxt(result_dir, delimiter = ",", X = point_cloud, fmt="%d") # fmt = "%d" to have int 
        f.np.savetxt(result_dir_for_cpp, delimiter = ",", X = point_cloud, fmt="%d") # fmt = "%d" to have int 

    # NB : to execute hough3dlines : "./hough3dlines test -o out" in the hough-3d-lines folder 