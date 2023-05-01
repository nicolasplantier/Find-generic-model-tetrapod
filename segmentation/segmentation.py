import functions as f 
import constants as c 

"""
The aim of the file is to do the segmentation using wathershed algorithm. 
Many results can be found in the current directory. 
"""

def run(): 
    current_path = f.os.getcwd()
    parent_path = f.os.path.dirname(current_path)
    path_tables = f.os.path.join(parent_path, f"tables_images")
    list_tables = f.os.listdir(path_tables)

    print("We are now implementing the watershed algorithm : we are segmenting the 3D point clouds")
    print(f"Estimate time : {int(9.26*len(list_tables)//60)} minutes and {int(9.26*len(list_tables)%60)} seconds")
    print("You can follow how the work goes with the following bar : ")

    for filename in f.tqdm(list_tables):

        # Create the file where we will put all the masks for each patch 
        newpath = f.os.path.join(parent_path, f"tetrapods_mask_all", f"patch_{filename[12:-4]}")
        if not f.os.path.exists(newpath):
            f.os.makedirs(newpath)

        # importing the scalar 2D field 
        fpath = f.os.path.join(parent_path, "tables_images", filename)
        array = f.np.loadtxt(fpath)

        gradient, markers, labels = f.create_useful_informations(array)
        f.plt.imsave(arr = gradient, cmap = 'jet', dpi = 400, fname= f.os.path.join(current_path, f"gradients", f"gradient_{filename[:-4]}.png"))
        f.plt.imsave(arr = markers, cmap = 'jet', dpi = 400, fname= f.os.path.join(current_path, f"markers", f"marker_{filename[:-4]}.png"))
        f.plt.imsave(arr = labels, cmap = 'jet', dpi = 400, fname= f.os.path.join(current_path, f"labels", f"label_{filename[:-4]}.png"))

        #select the biggest ones that might be tetrapods
        labels_sizes = f.np.array([(labels == i).sum() for i in range(labels.max())])
        tetra_indices = list(f.np.where((labels_sizes>50000) & (labels_sizes<140000))[0])
        tetrapods = []
        for i in tetra_indices:
            shadow = (labels == i)
            #get rid of the background parts
            if (shadow[0,0] != 1) & (shadow[0,-1] != 1) & (shadow[-1,-1] != 1) & (shadow[-1,0] != 1):
                tetrapods.append(shadow)
        for i in range(len(tetrapods)):
            tetrapod_path = f.os.path.join(parent_path, f"tetrapods_mask_all", f"patch_{filename[12:-4]}/{filename[:-4]}_tetrapod_mask{i}")
            f.np.savetxt(tetrapod_path, tetrapods[i])


# ------------------------------------------------------------------------------------------------------------------------

# -------------------- This is the second part of the segmentation : coloring the patches --------------------------------

# ------------------------------------------------------------------------------------------------------------------------


    print("All tetrapods are found, now we just put colors on the different patches")
    filepaths = f.os.path.join(parent_path, f"ajaccio_patches_classified_dataframes")
    my_list_patches_classified = f.os.listdir(filepaths)
    try : 
        my_list_patches_classified.remove(".DS_Store")
    except : 
        pass 
    print(f"Estimate time : {int(4.27*len(list_tables)//60)} minutes and {int(4.27*len(list_tables)%60)} seconds")
    print("You can follow how the work goes with the following bar : ")
    for filepath in f.tqdm(my_list_patches_classified):
        df_final = f.pd.read_csv(f.os.path.join(parent_path, f"ajaccio_patches_classified_dataframes", filepath))
        patch_number = filepath[9:-4]
        tetrapods_mask = {}
        for filename in f.os.listdir(f.os.path.join(parent_path, f"tetrapods_mask_all", f"patch_{patch_number}")):
            tetrapods_mask[filename] = f.np.loadtxt(f.os.path.join(parent_path, f"tetrapods_mask_all", f"patch_{patch_number}", filename))

        # We now convert the point in the dataframe to points in the image 
        df_image = f.create_df_image(df_final)

        # We change the classification value on the final cloud point
        df_final = f.change_classification_value(tetrapods_mask, df_image, df_final)

        # We now create the new las file reprensenting this classified cloud point
        las = f.create_las(df_final)

        # And we write a new file 
        las.write(f.os.path.join(current_path, f"ajaccio_patches_classified_colors", f"3d_patch_classified_final_{patch_number}.las"))

if __name__ == "__main__":
    run()
    