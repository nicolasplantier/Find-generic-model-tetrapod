"""
This algorithm finds the feet of the tetrapods and remove the outliers. 
"""

import functions as f 
import constants as c 

import sys 
path_to_main_axes = f.os.path.dirname(f.os.getcwd())
sys.path.append(path_to_main_axes)
from draw_main_axes import functions as f_main_axes

def run():
    current_dir = f.os.getcwd()
    parent_dir = f.os.path.dirname(current_dir)
    path_to_main_axes = f.os.path.join(parent_dir, "find_axes_cpp", "results", "axes_tetrapods_all", "main_axes")
    list_axes = f.os.listdir(path_to_main_axes)
    try : 
        list_axes.remove(".DS_Store")
    except:
        pass 

    print("This algorithm finds the feet of the tetrapods and remove outliers.")
    print(f"Estimate time : {int((10*len(list_axes))//60)} minutes and {int(((10*len(list_axes)))%60)} seconds")
    print("You can follow how the work goes with the following bar : ")

    for main_axes_name in f.tqdm(list_axes):
        file_number = main_axes_name[10:-4]
        path = f.os.path.join(parent_dir, "create_models", "results", f"tetrapod_model_{file_number}.las")
        df_coords_3d, las = f.read_las_file(path)

        path_to_main_axe = f.os.path.join(parent_dir, "find_axes_cpp", "results", "axes_tetrapods_all", "main_axes")
        path_main_axes_tetrapod = f.os.path.join(path_to_main_axe, main_axes_name)

        plot_list = f_main_axes.get_plot_list(path_main_axes_tetrapod)
        plot_list = f.convert_to_ijk(plot_list, df_coords_3d)

        df_coords_3d = f.find_feet_tetrapod(plot_list, df_coords_3d, file_number)
        df_coords_3d = f.delete_useless_points(df_coords_3d)
    
        path_tetrapod_with_feet = f.os.path.join(current_dir, "results", "tetrapods_with_feet", f"model_with_feet_{file_number}.las")
        f.write_tetrapods_with_feet(df_coords_3d, path_tetrapod_with_feet, las)
    
    
if __name__ == "__main__": 
    run()