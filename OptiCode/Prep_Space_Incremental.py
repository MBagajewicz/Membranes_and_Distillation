#################################################################################################################
# region Nature: Optimization
# # Nature: Trimming by Constraints
# Methodology: Set Trimming Incremental
#################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.1        15-Ago-25        Diego Oliva                New prepare space to increase space from new variables
#################################################################################################################

import numpy as np

def Prep_Space(candidates, space_to_add):
    """
    Expands the candidates matrix with all possible combinations
    of the lists in space_to_add.
    """
    # Create all combinations from space_to_add
    new_spaces = np.meshgrid(*space_to_add, indexing='ij')
    new_combos = np.vstack([arr.ravel() for arr in new_spaces])

    # Expand candidates with new_combos
    # Repeat each row of candidates as many times as there are combinations in new_combos
    expanded_candidates = np.repeat(candidates, new_combos.shape[1], axis=1)

    # Repeat new_combos so it aligns with candidates
    tiled_new_combos = np.tile(new_combos, candidates.shape[1])

    # Concatenate vertically
    final = np.vstack([expanded_candidates, tiled_new_combos])

    return final
