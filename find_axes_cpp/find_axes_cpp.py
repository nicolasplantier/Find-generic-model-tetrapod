import functions as f
import constants as c 
from subprocess import Popen, PIPE

if __name__ == "__main__": 
    current_dir = f.os.getcwd()
    parent_dir = f.os.path.dirname(current_dir)

    path_to_cpp = f.os.path.join(current_dir, 'hough-3d-lines')
    path_to_points = f.os.path.join(parent_dir, "find_points_axes", "results", "points_on_axes")

    list_filename_points = f.os.listdir(path_to_points)
    try : 
        list_filename_points.remove(".DS_Store")
    except: 
        pass

    out_parent_dir = output_dir = f.os.path.join(current_dir, "results", "axes_tetrapods_all", "axes") 

    for filename in f.tqdm(list_filename_points): 
        input_dir = f.os.path.join(f"./input", filename)
        output_dir = f.os.path.join(out_parent_dir, f"axes_model_{filename[27:-4]}.dat") 

        f.os.chdir(path_to_cpp)
        completed_process = f.subprocess.run(f"./hough3dlines {input_dir} -o ./output/axes_model_{filename[27:-4]}.dat", shell = True, text=True, stdout=f.subprocess.PIPE)

        with open(output_dir, "w") as output_file: 
            with open(f"./output/axes_model_{filename[27:-4]}.dat", "r") as input_file: 
                output_file.write(input_file.read())
        