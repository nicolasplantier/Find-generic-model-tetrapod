"""
This algorithm finds the generic model of tetrapods. 
"""


import functions as f 
import constants as c 

import sys 
path = f.os.path.dirname(f.os.getcwd())
sys.path.append(path)
from clean_tetrapods import functions as f_clean_tetrapods

def run():
    current_dir = f.os.getcwd()
    parent_dir = f.os.path.dirname(current_dir)
    path_to_main_axes = f.os.path.join(parent_dir, "find_axes_cpp", "results", "axes_tetrapods_all", "main_axes")
    list_main_axes = f.os.listdir(path_to_main_axes)[:41]

    # First we find which one is the best tetrapod to do the global registration on
    file_number_3_axes, best_tetrapod_number = f.find_the_best_tetrapod(parent_dir)
    try : 
        list_main_axes.remove(f"main_axes_{best_tetrapod_number}.dat") # We remove it so we do not do a registration on himself. 
    except:
        pass
    try : 
        list_main_axes.remove(".DS_Store")
    except:
        pass

    print("This algorithm finds the generic model of tetrapods.")
    print(f"Estimate time : {int((15*len(list_main_axes))//60)} minutes and {int(((15*len(list_main_axes)))%60)} seconds")
    print("You can follow how the work goes with the following bar : ")


    # We take the coordinates of the points of this tetrapod
    path_to_las_file = f.os.path.join(parent_dir, "clean_tetrapods", "results", "tetrapods_with_feet", f"model_with_feet_{best_tetrapod_number}.las")
    df_coords_3d_init, las, np_coords_3d_init= f_clean_tetrapods.read_las_file(path_to_las_file, return_np_coords= True) # init for initialization 
    axes_list = f.find_axes(best_tetrapod_number, path_to_main_axes)
    center, direction = f.find_center(axes_list, df_coords_3d_init)
    center_2, direction_2 = f.find_center(axes_list, df_coords_3d_init, new_axis = True)

    for axes_tetrapods in f.tqdm(list_main_axes):
        tetrapod_number = axes_tetrapods[10:-4]
        path_to_las_file = f.os.path.join(parent_dir, "clean_tetrapods", "results", "tetrapods_with_feet", f"model_with_feet_{tetrapod_number}.las")
        df_coords_3d, las, np_coords_3d= f_clean_tetrapods.read_las_file(path_to_las_file, return_np_coords= True)
        

        # First, we do the global registration without any rotation 
        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=5,
                                                                point_to_point= True)
        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=2,
                                                                point_to_point= True)
        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=0.05,
                                                                point_to_point= True)
        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=0.02,
                                                                point_to_point= True,)
        
        path_to_save_csv = f.os.path.join(current_dir, "results", "csv_files", f"new_fit_{tetrapod_number}_0.csv")
        f.np.savetxt(fname = path_to_save_csv, X = np_coords_3d)


        # Now we do a rotation and than, global registration with a more little thershold
        mesh = f.examples.download_cow()
        mesh.points = np_coords_3d
        rot = mesh.copy()
        rot.rotate_vector(vector=direction, angle=120, point=center)
        np_coords_3d = f.np.asarray(rot.points)

        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=0.1,
                                                                point_to_point= True,)
        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=0.01,
                                                                point_to_point= True,)
        path_to_save_csv = f.os.path.join(current_dir, "results", "csv_files", f"new_fit_{tetrapod_number}_1.csv")
        f.np.savetxt(fname = path_to_save_csv, X = np_coords_3d)


        # Now we do a rotation and than, global registration with a more little thershold
        mesh = f.examples.download_cow()
        mesh.points = np_coords_3d
        rot = mesh.copy()
        rot.rotate_vector(vector=direction, angle=120, point=center)
        np_coords_3d = f.np.asarray(rot.points)

        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=0.1,
                                                                point_to_point= True,)
        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=0.01,
                                                                point_to_point= True,)
        path_to_save_csv = f.os.path.join(current_dir, "results", "csv_files", f"new_fit_{tetrapod_number}_2.csv")
        f.np.savetxt(fname = path_to_save_csv, X = np_coords_3d)

        
        """ # Now we do a rotation around the second axis 
        mesh = f.examples.download_cow()
        mesh.points = np_coords_3d
        rot = mesh.copy()
        rot.rotate_vector(vector=direction_2, angle=130, point=center_2)
        np_coords_3d = f.np.asarray(rot.points)
        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=0.1,
                                                                point_to_point= True,)
        np_coords_3d_init, np_coords_3d = f.global_registration(np_coords_3d_init,
                                                                np_coords_3d, 
                                                                threshold=0.01,
                                                                point_to_point= True,
                                                                draw_final_registration=True)
        path_to_save_csv = f.os.path.join(current_dir, "results", "csv_files", f"new_fit_{tetrapod_number}_2.csv")
        f.np.savetxt(fname = path_to_save_csv, X = np_coords_3d) """


if __name__ == "__main__": 
    run()



