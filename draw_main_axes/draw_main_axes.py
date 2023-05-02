import functions as f 
import constants as c 


def run(): 
    fig = f.plt.figure()
    plot = 0
    current_path = f.os.getcwd()
    parent_path = f.os.path.dirname(current_path)
    path_to_points = f.os.path.join(parent_path, "find_points_axes", "results", "points_on_axes")
    list_dir_points = f.os.listdir(path_to_points)
    try :
        list_dir_points.remove(".DS_Store")
    except:
        pass

    print("This algorithm draws the axes found inside the tetrapods creating new .las files")
    print(f"Estimate time : {int((0.25*len(list_dir_points))//60)} minutes and {int(((0.25*len(list_dir_points)))%60)} seconds")
    print("You can follow how the work goes with the following bar : ")

    for filename in f.tqdm(list_dir_points):
        plot += 1
        dir_points = f.os.path.join(path_to_points, filename)
        data = f.np.genfromtxt(dir_points,
                            dtype=f.np.int64,
                            delimiter=',')
        
        try : 
            # Creating dataset
            z = data[:,2]
            x = data[:,0]
            y = data[:,1]

            number_model = filename[27:-4] # something like 2_0 
            path_to_axe = f.os.path.join(parent_path, "find_axes_cpp", "results", "axes_tetrapods_all", "axes", f"axes_model_{number_model}.dat")
            path_to_main_axe = f.os.path.join(parent_path, "find_axes_cpp", "results", "axes_tetrapods_all", "main_axes", f"main_axes_{number_model}.dat")
            path_fig = f.os.path.join(current_path, "results", "draw_axes", f"fig_axes_tetrapods_{number_model}.png")
            text = open(path_to_axe).readlines()

            plot_list = f.create_main_axes_file(text, path_to_main_axe) # This create the main_axes file 
            f.remove_too_little(path_to_main_axe)
            f.draw_figure(number_model, x, y, z, plot_list, path_fig)
        except:
            pass

    
def run2(): 
    current_path = f.os.getcwd()
    parent_path = f.os.path.dirname(current_path)
    path_to_main_axe = f.os.path.join(parent_path, "find_axes_cpp", "results", "axes_tetrapods_all", "main_axes")
    list_main_axes = f.os.listdir(path_to_main_axe)
    try : 
        list_main_axes.remove(".DS_Store")
    except:
        pass

    for filename in f.tqdm(list_main_axes):
        file_number = filename[10:-4]
        path_tetrapod = f.os.path.join(parent_path, "create_models", "results", f"tetrapod_model_{file_number}.las")
        las = f.laspy.read(path_tetrapod) 
        n = len(las.x)

        # shift the data to simplify
        x_scaled = f.np.array(las.x) - f.np.array(las.x).min()
        y_scaled = f.np.array(las.y) -  f.np.array(las.y).min()
        z_scaled = f.np.array(las.z) 

        # Create the dataframe
        np_coords_3d = f.np.concatenate((x_scaled.reshape((n,1)), y_scaled.reshape((n,1)), z_scaled.reshape((n,1))), axis = 1)
        df_coords_3d = f.pd.DataFrame(data=np_coords_3d, columns=['x', 'y', 'z']) 

        # Now get the plot list 
        path_main_axes_tetrapod = f.os.path.join(path_to_main_axe, filename)
        plot_list = f.get_plot_list(path_main_axes_tetrapod)

        # Now get the points on the axes 
        df_axes_plot = f.create_axes_as_points(plot_list)
        df_coords_3d = f.add_points_axes_to_dfcoods(df_coords_3d, df_axes_plot)

        path_to_las = f.os.path.join(current_path, "results", "models_with_axes", f"model_with_axes_{file_number}.las")
        f.create_las_with_axes(path_to_las, las, df_coords_3d)




if __name__ == "__main__": 
    run()
    run2()