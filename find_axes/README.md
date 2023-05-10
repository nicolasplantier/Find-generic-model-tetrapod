# Find axes algorithm 

Now that we have access to different instances of tetrapods, we need to identify the axes.   
This algorithm find a 3D probability map : high probabilities meaning that a point has a high probability to belong to one of the axes of a tetrapod.

## Input

- `create_models` : the models found in the previous algorithm, in the `results` file

## Output 

- `echographie_tetrapods_all` : images corresponding to the 3D probability map over a few heights
- `echographie_tetrapods_all_csv` : same images but over every heights, and stored into a .csv file

Here is an overview of the final result.  

https://github.com/nicolasplantier/Find-generic-model-tetrapod/assets/91543973/e23945ac-e024-49f4-a71b-2ae30a5cb188

