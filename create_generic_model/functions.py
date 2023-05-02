import os 
from tqdm import tqdm 
import matplotlib.pyplot as plt 
import numpy as np 
import open3d as o3d 
import copy 
import constants as c 
import pandas as pd 
import pyvista as pv
from pyvista import examples


import sys 
path = os.path.dirname(os.getcwd())
sys.path.append(path)
from clean_tetrapods import functions as f_clean_tetrapods


def find_the_best_tetrapod(parent_dir):
    # First, we have to find the tetrapods with 3 axes 
    path_to_main_axes = os.path.join(parent_dir, "find_axes_cpp", "results", "axes_tetrapods_all", "main_axes")
    list_main_axes = os.listdir(path_to_main_axes)
    try : 
        list_main_axes.remove(".DS_Store")
    except:
        pass

    file_number_3_axes = []
    for file_axes_name in list_main_axes: 
        with open(os.path.join(path_to_main_axes, file_axes_name)) as f:
            list_axes = f.readlines()
            if len(list_axes) > 3:
                file_number_3_axes.append(file_axes_name[10:-4])
    best_tetrapod_number = file_number_3_axes[0]
    max_n_points = 0

    # Second, we take the one we the biggest number of points 
    for file_number in file_number_3_axes:
        path_to_las_file = os.path.join(parent_dir, "clean_tetrapods", "results", "tetrapods_with_feet", f"model_with_feet_{file_number}.las")
        df_coords_3d, las = f_clean_tetrapods.read_las_file(path_to_las_file)
        if len(df_coords_3d) >= max_n_points:
            best_tetrapod_number = file_number
            max_n_points = len(df_coords_3d)
    return file_number_3_axes, best_tetrapod_number



def find_axes(tetrapod_number, path_to_main_axes):
    axes_list = []
    text = open(os.path.join(path_to_main_axes, f"main_axes_{tetrapod_number}.dat")).readlines()
    n_lines = len(text)
    text_line = text[0]
    n = eval(text_line[text_line.find("npoints=")+8:text_line.find(", ")])
    a = eval(text_line[text_line.find("a=")+2:text_line.find("),")+1])
    b = eval(text_line[text_line.find("b=")+2:]) 
    axes_list.append([np.array(list(a)), np.array(list(b))])
    for line in text[1:]:
        n = eval(line[line.find("npoints=")+8:line.find(", ")])
        a = eval(line[line.find("a=")+2:line.find("),")+1])
        b = eval(line[line.find("b=")+2:]) 
        axes_list.append([np.array(list(a)), np.array(list(b))])
    return axes_list



def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp],
                                    zoom=0.7,
                                    front=[0.9288, -0.2951, -0.2242],
                                    # lookat=[1.6784, 2.0612, 1.4451],
                                    lookat=[0.,0.,0.],
                                    up=[-0.3402, -0.9189, -0.1996])
    

def global_registration(np_coords_3d_init, 
                        np_coords_3d, 
                        threshold, 
                        point_to_point = True, 
                        point_to_plane = False,
                        draw_init_registration = False,
                        draw_final_registration = False): 
    point_cloud_one = np_coords_3d_init
    point_cloud_two = np_coords_3d

    pcd1 = o3d.geometry.PointCloud()
    pcd2 = o3d.geometry.PointCloud()

    pcd1.points = o3d.utility.Vector3dVector(point_cloud_one)
    pcd2.points = o3d.utility.Vector3dVector(point_cloud_two)
    
    pcd1.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius = 0.1, max_nn = 100))
    demo_icp_pcds = o3d.data.DemoICPPointClouds()
    source = pcd1
    target = pcd2
    trans_init = np.asarray([[1., 0., 0., 0.],
                            [0., 1., 0., 0.],
                            [0., 0., 1., 0.], 
                            [0., 0., 0., 1.]])
    
    if draw_init_registration: 
        draw_registration_result(target, source, trans_init)

    if point_to_point: 
        reg_p2l = o3d.pipelines.registration.registration_icp(
            target, source, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPoint())
    elif point_to_plane: 
        reg_p2l = o3d.pipelines.registration.registration_icp(
            target, source, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPlane())
    
    if draw_final_registration:
        draw_registration_result(target, source, reg_p2l.transformation)

    
    return(np_coords_3d_init, np.asarray(target.transform(reg_p2l.transformation).points))





def find_center(axes_list, df_coords_3d_init, new_axis = False):
    df_axes_plot = pd.DataFrame(columns = ['i','j','k']) 
    if new_axis :
        element = axes_list[1]
    else : 
        element = axes_list[0] 
    a = element[0]
    b = element[1]/100
    vect_list = []
    for k in range (c.LEN_AX*100): 
            vect_list.append(a+k*b)
    for k in range (c.LEN_AX*100): 
            vect_list.append(a-k*b)
    vect_list = np.array(vect_list)

    df_vect_list =  pd.DataFrame(data = vect_list, columns = ['i', 'j', 'k'])
    df_axes_plot = pd.concat([df_axes_plot, df_vect_list], axis = 0)

    xmin = df_coords_3d_init['x'].min()
    xmax = df_coords_3d_init['x'].max()
    ymin = df_coords_3d_init['y'].min()
    ymax = df_coords_3d_init['y'].max()
    zmin = df_coords_3d_init['z'].min()
    zmax = df_coords_3d_init['z'].max()

    df_axes_plot['x']  = xmin+ (xmax - xmin)*(df_axes_plot['i']/c.M)
    df_axes_plot['y']  = ymin+ (ymax - ymin)*(df_axes_plot['j']/c.M)
    df_axes_plot['z']  = zmin+ (zmax - zmin)*(df_axes_plot['k']/c.M)

    max_index = df_coords_3d_init.index.max()
    df_axes_plot.index = np.arange(max_index+1, max_index+1 + len(df_axes_plot))
    df_points_to_add = pd.DataFrame(data = df_axes_plot[['x','y','z']], columns = ['x', 'y', 'z'])
    df_coords_3d_init = pd.concat([df_coords_3d_init, df_points_to_add], axis = 0)

    center = df_points_to_add.iloc[len(df_points_to_add)//2,:]
    direction = (df_points_to_add.iloc[len(df_points_to_add)-1, :] - df_points_to_add.iloc[len(df_points_to_add)//2, :])/(len(df_points_to_add)//2)

    return center, direction