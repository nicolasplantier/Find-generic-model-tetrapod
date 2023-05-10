"""
This algorithm concatenates the previous csv files to give the final model with the probability map. 
"""


import functions as f 
import constants as c 

def run(): 
    current_dir = f.os.getcwd()
    parent_dir = f.os.path.dirname(current_dir)
    path_to_tetrapods_csv = f.os.path.join(parent_dir, "create_generic_model", "results", "csv_files")
    list_tetrapods_csv = f.os.listdir(path_to_tetrapods_csv)
    try : 
        list_tetrapods_csv.remove(".DS_Store")
    except:
        pass

    new_fit = []
    for superposed_tetrapod_name in list_tetrapods_csv: 
        new_fit.append(f.np.loadtxt(fname = f.os.path.join(path_to_tetrapods_csv, superposed_tetrapod_name)))
    
    point_cloud = new_fit[0]
    for point_cloud_new in new_fit[1:]:
        point_cloud = f.np.concatenate((point_cloud, point_cloud_new), axis = 0) 
    
    list_l = []

    print("This algorithm concatenates the previous csv files to give the final model with the probability map.")

    # Implementing the kd_tree 
    tree = f.spatial.KDTree(point_cloud)
    neighbors = tree.query_ball_point(x = point_cloud, r = c.RADIUS)
    for element in neighbors:
        list_l.append(len(element))
    array_colors = f.np.array(list_l)
    df = f.pd.DataFrame(data = point_cloud, columns = ['x', 'y', 'z'])
    df['colors'] = array_colors

    las_file_path = f.os.path.join(parent_dir, "init.las")
    las_1 = f.laspy.read(las_file_path) 
    las = f.laspy.create(point_format=las_1.header.point_format, file_version=las_1.header.version)
    header = las.header
    header.point_count = len(df)
    rap_x = las_1.X[0]/las_1.x[0]
    rap_y = las_1.y[0]/las_1.y[0]
    rap_z = las_1.z[0]/las_1.z[0]
    las.points.X = df['x']*rap_x
    las.points.Y = df['y']*rap_y
    las.points.Z = df['z']*rap_z
    las.points.x = df['x']
    las.points.y = df['y']
    las.points.z = df['z']
    las.add_extra_dim(f.laspy.ExtraBytesParams(name="density",type=f.np.float64,description="More classes available"))
    las.points.density[:] = df['colors']
    las.write(f.os.path.join(current_dir, "results", "density_model.las"))




if __name__ == "__main__": 
    run()