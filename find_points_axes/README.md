# Find points axes 

This algorithm finds out the points on that are likely to belong to the axes of a tetrapod. 

## Input
- `echographie_tetrapods_all_csv` in `results` of `find_axes`: the 3D probability maps of points inside tetrapods instances

## Output 
- `point_cloud_{filename[:-4]}.dat"` : list of coordinates of the points that belong to the axes 
