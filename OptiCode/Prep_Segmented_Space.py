##################################################################################################################
#region Titles and Header
# Nature: Matrix with all combinations of discrete variables Construction
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0       31-Jan-2025       Alice Peccini              Proposed

##################################################################################################################
# INPUT: No inputs allowed
##################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete this file !!!!!
#endregion
##################################################################################################################

##################################################################################################################
#region Import Library
import numpy as np
#endregion
##################################################################################################################

##################################################################################################################
#region Call this function to create a Matrix with all posible combinations among your discrete variables
def Segment_Space(candidates,var_list, segmentation_variable, variables_per_segment, segment_correction):

    # Identifying segmentation variable
    seg_var_index = var_list.index(segmentation_variable)

    # Identifying discretized values for segmentation variable present in the matrix of candidates
    unique_values = np.unique(candidates[seg_var_index, :])     

    # Creating segmented intervals for segmentation variable
    num_segments = max(1, len(unique_values) // variables_per_segment)     
    intervals = np.array_split(unique_values, num_segments)

    # Concatenation of last two intervals if needed per correction factor given
    if len(intervals) > 1 and len(intervals[-1]) < variables_per_segment*segment_correction:
        intervals[-2] = np.concatenate([intervals[-2], intervals[-1]])
        intervals = intervals[:-1]

    # Generating segmented candidates:
    segmented_candidates = []

    for interval in intervals:
        mask = np.isin(candidates[seg_var_index, :], interval)
        segmented_candidates.append(candidates[:,mask])

    return segmented_candidates

#endregion
##################################################################################################################