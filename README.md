# Generation of a Generic tetrapod model from photogrammetric point clouds of breakwaters
This code implements the algorithm described in :
> N. Plantier, A. Li, S. Travadel, "Generation of a Generic tetrapod model from photogrammetric point clouds of breakwaters", 2023

Please, cite this article when using the code. 

## Source Files

Please, execute the algorithms in this order. 

- `planity_calculator.py` in `planity_calculator`  
Main program that implements the "flatness_measure" algorithm described in the paper.  

- `edges_calculator.py` in `edges_calculator`   
Main program that prepares the input of the watershed algorithm that will segment the 3D point cloud. It computes the edges of the 2D projection of the flatness measure. 

## Installation 
