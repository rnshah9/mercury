"""     
 Copyright (c) 2019 Cisco Systems, Inc. All rights reserved.
 License at https://github.com/cisco/mercury/blob/master/LICENSE
"""

import numpy as np

###
## Similarity Matching for Fingerprints
#

# ***** Sequence Alignment *****
class SequenceAlignment:
    def __init__(self, similarity, gap_penalty):
        self.map_ = {}
        self.similarity = similarity
        self.gap = float(gap_penalty)

    # Align two sequences, s1 and s2, using the
    #   Needleman-Wunsch Algorithm and return the
    #   score of the best possible alignment
    def align(self, s1, s2):
        F = np.zeros((len(s1)+1, len(s2)+1))
        for i in range(len(s1)+1):
            F[i,0] = self.gap*i
        for i in range(len(s2)+1):
            F[0,i] = self.gap*i
        for i in range(1,len(s1)+1):
            for j in range(1,len(s2)+1):
                match_ = F[i-1,j-1] + self.similarity(s1[i-1], s2[j-1])
                delete_ = F[i-1,j] + self.gap
                insert_ = F[i,j-1] + self.gap
                F[i,j] = max(match_, delete_, insert_)

        return F[len(s1),len(s2)]

# default function: determine the similarity between two elements
def f_similarity(a, b):
    # the two elements match
    if a == b:
        return 1.0
    return 0.0

