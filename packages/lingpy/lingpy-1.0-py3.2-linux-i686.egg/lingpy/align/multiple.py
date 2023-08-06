"""
Basic module for the handling of multiple sequence alignments.
"""

from numpy import array,zeros
from ..data import *
from ..algorithm import *
from ..algorithm.cluster import _neighbor,_upgma,_flat_upgma

class _Multiple(object):
    """
    Basic class for multiple sequence alignment analyses.
    """
    def __init__(
            self,
            seqs,
            merge_vowels = True,
            ):
        
        # store input sequences 
        self.seqs = seqs

        # create a numerical representation of all sequences which reflects the
        # order of both their position and the position of their tokens. Before
        # this can be done, a tokenized version of all sequences has to be
        # created
        self.tokens = []
        self.numbers = []
        for i,seq in enumerate(self.seqs):
            tokens = ipa2tokens(seq,merge_vowels=merge_vowels) 
            self.tokens.append(tokens)
            self.numbers.append(
                    [str(i+1)+'.'+str(j+1) for j in range(len(tokens))]
                    )

        # create dictionary of all unique sequences, this is important, since
        # identical sequences should only be counted once in an alignment,
        # since they otherwise may disturb the analysis or slow it down
        self.uniseqs = {}
        for i,seq in enumerate(self.seqs):
            try:
                self.uniseqs[seq] += [i]
            except:
                self.uniseqs[seq] = [i]

        self._length = len(self.uniseqs)
        
    def __len__(self):
        
        # the length of an alignment is defined as the number of unique
        # sequences present in the alignment

        return self._length

    def __str__(self):
        
        # if alignments are present, print the alignments
        try:
            out = '\t'.join(self.alm_matrix[0])
            for line in self.alm_matrix[1:]:
                out += '\n'+'\t'.join(line)
            return out
        # else, return all sequences
        except:
            out = '\t'.join(self.tokens[0])
            for line in self.tokens[1:]:
                out += '\n'+'\t'.join(line)
            return out

    def __eq__(self,other):

        try:
            return self.alm_matrix == other.alm_matrix
        except:
            return False

    def __getitem__(
            self,
            idx
            ):
        """
        Return specified values.
        """
        try:
            data = idx[1]
            idx = idx[0]
        except:
            data = 'w'
        
        if data == 'w':
            return self.seqs[idx]
        elif data == 'c':
            return self.classes[idx]
        elif data == 't':
            return self.tokens[idx]
        elif data == 'a':
            return self.alm_matrix[idx]

    def _get(
            self,
            number,
            value='tokens',
            error = ('X','-'),
            ):
        """
        Method returns specific values of the class, depending on the index
        which is used.
        """
        
        if number == error[0]:
            return error[1]

        try:

            idxA,idxB = [int(i)-1 for i in number.split('.')]

            if value == 'tokens':
                return self.tokens[idxA][idxB]
            elif value == 'numbers':
                return self.numbers[idxA][idxB]
            elif value == 'classes':
                return self.classes[idxA][idxB]
            elif value == '_classes':
                return self._classes[idxA][idxB]
            elif value == '_sonars':
                return self._sonars[idxA][idxB]
            elif value == '_numbers':
                return self._numbers[idxA][idxB]
            elif value == '_prosodics':
                return self._prosodics[idxA][idxB]

        except:
            if value == 'tokens':
                return self.tokens[int(number)-1]
            elif value == 'sonars':
                return self.sonars[int(number)-1]
            elif value == 'numbers':
                return self.numbers[int(number)-1]
            elif value == 'classes':
                return self.classes[int(number)-1]
            elif value == '_sonars':
                return self._sonars[int(number)-1]
            elif value == '_numbers':
                return self._numbers[int(number)-1]
            elif value == '_classes':
                return self._classes[int(number)-1]

    def _set_model(self,model):
        """
        Method defines a specific class model for the calculation.
        """
        
        # store the class-model which is applied in the respective analysis
        self.model = eval(model)
        
        self.classes = [token[:] for token in self.tokens]
        for i,tokens in enumerate(self.tokens):
            self.classes[i] = tokens2class(tokens,self.model)

        # once a class model is defined, there may be identical sequences,
        # which in IPA terms are different. In order to avoid computing
        # alignments for these identical sequences, a dictionary is created
        # which stores references to all identical sequences, thus allowing to
        # compute only one alignment for each set of identical sequences
        indices = {}
        for i,seq in enumerate(self.classes):
            try:
                indices[tuple(seq)] += [i]
            except:
                indices[tuple(seq)] = [i]

        # create additional matrices for the internal representation of the
        # class sequences
        keys = [val[0] for val in list(indices.values())]
        self.height = len(keys)
        self._classes = [self.classes[key][:] for key in keys]
        self._numbers = [[str(i+1)+'.'+str(j+1) for j in
            range(len(self._classes[i]))] for i in range(self.height)]

        # create sonars
        self._sonars = [self.tokens[key][:] for key in keys]
        for i,sonar in enumerate(self._sonars):
            self._sonars[i] = [int(x) for x in tokens2class(sonar,art)]
        
        self._prosodics = [prosodic_string(sonar) for sonar in
            self._sonars]

        # create an index which allows to quickly interchange between classes
        # and given sequences
        self.int2ext = dict(
                [(i,indices[tuple(self._classes[i])]) for i in range(len(keys))]    
                )

        # create a scoredict for the calculation of alignment analyses
        self.scoredict = {}
        for i,seqA in enumerate(self._numbers):
            for j,seqB in enumerate(self._numbers):
                if i < j:
                    for numA in seqA:
                        for numB in seqB:
                            self.scoredict[numA,numB] = self.model.scorer[
                                    self._get(numA,'_classes'),
                                    self._get(numB,'_classes')
                                    ]
                            self.scoredict[numB,numA] = self.scoredict[numA,numB]
                elif i == j:
                    for num in seqA:
                        char = self._get(num,'_classes')
                        self.scoredict[num,num] = self.model.scorer[char,char]
    
    def _set_scorer(self,score_mode='classes'):
        """
        Functions sets the scorer to the simple class model or to the library
        model.
        """

        if score_mode == 'classes':
            self.scorer = self.scoredict
        elif score_mode == 'library':
            self.scorer = self.library

    def _get_pairwise_alignments(
            self,
            mode = 'global',
            gop = -3,
            gep_scale = 0.5,
            scale = (1,1,1),
            factor = 0,
            restricted_chars = 'T'
            ):
        """
        Function calculates all pairwise alignments from the data.
        """
        
        self._alignments = [[0 for i in range(self.height)] for j in
                range(self.height)]

        weights = []
        for seq in self._prosodics:
            pros = gop * array(prosodic_weights(
                    seq,
                    scale,
                    factor
                    ),dtype="float")
            weights.append(pros.tolist())

        restrictions = []
        prosodic_strings = []
        for pros in self._prosodics:
            tmp = []
            for i,char in enumerate(pros):
                if char in restricted_chars:
                    tmp.append(-(i+1))
                else:
                    tmp.append(i+1)
            restrictions.append(tmp)
            prosodic_strings.append(pros)
        
        alignments = align_sequences_pairwise(
                self._numbers,
                weights,
                restrictions,
                prosodic_strings,
                self.scorer,
                gep_scale,
                factor,
                mode
                )
        
        k = 0
        for i in range(self.height):
            for j in range(self.height):
                if i < j:
                    almA,almB,sim = alignments[k]
                    if mode == 'local':
                        almA = [char for char in almA if char != '*']
                        almB = [char for char in almB if char != '*']
                    self._alignments[i][j] = [almA,almB,sim]
                    self._alignments[j][i] = [almB,almA,sim]
                    k += 1
                elif i == j:
                    self._alignments[i][j] = [
                            #zip(
                                self._numbers[i],
                                self._numbers[j],
                                #),
                            sum(
                                [self.scorer[char,char] for char in self._numbers[i]]
                                )
                            ]

    def _create_library(self):
        """
        Method creates an extended library for alignments using the Tcoffee
        approach.
        """
        self.library = {}
    
        for i,numA in enumerate(self._numbers):
            for j,numB in enumerate(self._numbers):
                if i < j:
                    for k in numA:
                        for l in numB:
                            self.library[k,l] = 0.0
                            self.library[l,k] = 0.0
                elif i == j:
                    for k in numA:
                        for l in numB:
                            self.library[k,l] = 0.0
                            self.library[l,k] = 0.0

    def _extend_library(self):
        """
        Extend the library by new alignments.
        """
        # add the residue-pairs of all aligned sequences first
        for i,j in [(i,j) for i in range(self.height) for j in
                range(self.height) if i <= j]:
            for m,n in zip(self._alignments[i][j][0],self._alignments[i][j][1]):
                if m != "-" and n != "-":                    
                    # add the values to the library
                    # the similarity score is determined by adding taking the
                    # average of matrix score and the similarity score of the
                    # alignment of both sequences
                    score = self.scorer[m,n]
                    sim = self._alignments[i][j][2] / float(len(self._alignments[i][j][0]))
                    self.library[m,n] += (sim + score) / 2.0
                    self.library[n,m] = self.library[m,n]
        
        # add the residue-pairs resulting from an alignment via a third
        # sequence
        
        # create the indices for the loop
        mappings = ((i,j,k) for i in range(self.height) for j in
                range(self.height) for k in range(self.height) if i <= j and 
                k != i and k != j)

        for i,j,k in mappings:
            almI,almIK,simIK = self._alignments[i][k]
            almJ,almJK,simJK = self._alignments[j][k]
            
            # determine, which of the values occur in both alignments
            # with the third sequence
            for char in self._numbers[k]:
                try:
                    valI = almI[almIK.index(char)]
                    valJ = almJ[almJK.index(char)]
                    if valI != "-" and valJ != "-":

                       score = self.scorer[valI,valJ]
                       sim = min(simIK,simJK) / ((len(almIK) + len(almJK)) / 2.0)

                       self.library[valI,valJ] += (sim + score) / 2.0
                       self.library[valJ,valI] = self.library[valI,valJ]
                except:
                    pass
       
    def _score_pairwise(
            self,
            idxA,
            idxB,
            ):
        
        scoreAB = self._alignments[idxA][idxB][2]
        scoreA = self._alignments[idxA][idxA][2]
        scoreB = self._alignments[idxB][idxB][2]

        return 1 - (2 * scoreAB / float(scoreA+scoreB))

    def _make_matrix(self):
        
        matrix = []

        for i in range(self.height):
            for j in range(self.height):
                if i < j:
                    matrix.append(
                            self._score_pairwise(i,j)
                            )
        
        self.matrix = squareform(matrix)

    def __make_guide_tree(
            self,
            tree_calc = 'median'
            ):

        self.tree_matrix = linkage(
                self.matrix,
                method = tree_calc
                )

    def _make_guide_tree(
            self,
            tree_calc = 'upgma'
            ):
        """
        Create the guide tree using either the UPGMA or the Neighbor-Joining
        algorithm.
        """
        # create the clusters
        clusters = dict(
                [(i[0],[i[1]]) for i in zip(list(range(self.height)),list(range(self.height)))]
                )
        
        # create the tree matrix
        self.tree_matrix = []
        
        # carry out the clustering
        if tree_calc == 'upgma':
            _upgma(clusters,self.matrix,self.tree_matrix)
        elif tree_calc == 'neighbor':
            _neighbor(clusters,self.matrix,self.tree_matrix)
        else:
            raise ValueError('Method <'+tree_calc+'> for tree calculation not available.')


    def _profile_score(
            self,
            colA,
            colB,
            gap_weight = 0.0
            ):

        score = 0
        counter = 0.0
        for i,charA in enumerate(colA):
            for j,charB in enumerate(colB):
                if 'X' not in (charA,charB):
                    score += self.scorer[charA,charB]
                    counter += 1.0
                else:
                    counter += gap_weight

        return score / counter

    def _swap_profile_score(
            self,
            colA,
            colB,
            gap_weight = 1.0,
            swap_penalty = -5
            ):

        score = 0
        counter = 0.0
        for i,charA in enumerate(colA):
            for j,charB in enumerate(colB):
                if 'X' not in (charA,charB) and '+' not in (charA,charB):
                    score += self.scorer[charA,charB]
                    counter += 1.0
                elif '+' in (charA,charB):
                    if 'X' in (charA,charB):
                        counter += 1.0
                        score += swap_penalty # this is the swap-cost
                    elif (charA,charB) == ('+','+'):
                        score += 0.0 # no cost for +/+-scores
                        counter += 1
                    else:
                        counter += 1.0 # all prohibited cases
                        score += -10000000
                else:
                    counter += gap_weight

        return score / counter


    def _align_profile(
            self,
            almsA,
            almsB,
            mode = 'global',
            gop = -10,
            gep_scale = 0.5,
            scale = (1.0,1.0,1.0),
            factor = 0,
            gap_weight = 0.5,
            return_similarity = False,
            iterate = False,
            restricted_chars = "T"
            ):

        profileA = array(almsA).transpose()
        profileB = array(almsB).transpose()

        # calculate profile length and profile depth for both profiles
        m,o = profileA.shape
        n,p = profileB.shape

        # create the lists which will be passed to the psa align function
        lstA = list(range(1,m+1))
        lstB = list(range(1,n+1))
                           
        # create the weights by which the gap opening penalties will be
        # modified
        sonarA = [[self._get(
                        char,
                        value = '_sonars',
                        error = ('X',0)
                        ) for char in line] for line in profileA]
        sonarB = [[self._get(
                        char,
                        value = '_sonars',
                        error = ('X',0)
                        ) for char in line] for line in profileB]

        consA = [i[i!=0].mean().round() for i in array(sonarA)]
        consB = [i[i!=0].mean().round() for i in array(sonarB)]

        prosA = prosodic_string(consA)
        prosB = prosodic_string(consB)

        weightsA = gop * array(
                prosodic_weights(prosA,scale,factor)
                )
        weightsB = gop * array(
            prosodic_weights(prosB,scale,factor)
            )
        
        # convert the tonal positions into negative indices
        resA = []
        resB = []
        for i,res in enumerate(prosA):
            if res in restricted_chars:
                resA.append(-(i+1))
            else:
                resA.append(i+1)
        for i,res in enumerate(prosB):
            if res in restricted_chars:
                resB.append(-(i+1))
            else:
                resB.append(i+1)

        # create a temporary scoring dictionary which will be passed to the
        # psa align function
        tmp = {}
        for i in lstA:        
            for j in lstB:
                score = self._profile_score(
                        profileA[i-1],
                        profileB[j-1],
                        gap_weight = gap_weight
                        )
                tmp[j,i] = score

        alignedA,alignedB,sim = align_pairwise(
                lstA,
                lstB,
                weightsA.tolist(),
                weightsB.tolist(),
                resA,
                resB,
                prosA,
                prosB,
                tmp,
                gep_scale,
                factor,
                mode
                )

        # return the similarity score, if this option is chosen
        if return_similarity == True:
            return sim

        # trace the gaps inserted in both aligned profiles and insert them
        # in the original profiles
        profileA = profileA.tolist()
        profileB = profileB.tolist()
        for i in range(len(alignedA)):
            if alignedA[i] == '-':
                profileA.insert(i,o * ['X'])
            elif alignedB[i] == '-':
                profileB.insert(i,p * ['X'])

        # invert the profiles and the weight matrices by turning columns
        # into rows and rows into columns  
        profileA = array(profileA).transpose().tolist()
        profileB = array(profileB).transpose().tolist()
        
        # return the aligned profiles and weight matrices
        if iterate == True:
            return profileA,profileB
        elif iterate == False:
            return profileA+profileB

    def _merge_alignments(
            self,
            mode = 'global',
            gop = -3,
            gep_scale = 0.5,
            scale = (1,1,1),
            factor = 0,
            gap_weight = 0.5,
            restricted_chars = 'T',
            ):

        # create the lists which will store the current stages of the
        # alignment process
        seq_ord = [[i] for i in range(self.height)]
        alm_lst = [[seq] for seq in self._numbers[:]]

        # start the iteration through the tree array: the first two lines
        # in the matrix contain the ids of the sequences in the array,
        # which are aligned along the tree
        for row in self.tree_matrix:
            m,n = int(row[0]),int(row[1])
            seq_ord.append(seq_ord[m] + seq_ord[n])
            alms = self._align_profile(
                    alm_lst[m],
                    alm_lst[n],
                    mode = mode,
                    gop = gop,
                    gep_scale = gep_scale,
                    scale = scale,
                    factor = factor,
                    gap_weight = gap_weight,
                    restricted_chars = restricted_chars
                    )
            
            alm_lst.append(alms)

        # get the last stage of each alignment process
        alm_lst = alm_lst[-1]

        # restore the original order of the strings in the alignment
        sorter = seq_ord[-1][:]
        sorter.reverse()
        alm_lst = sorted(alm_lst,key=lambda x:sorter.pop())

        # create the matrix which stores all alignments
        self._alm_matrix = array(alm_lst)

    def _update_alignments(self):

        self.alm_matrix = [0 for i in range(len(self.numbers))]

        for i,line in enumerate(self._alm_matrix):
            indices = self.int2ext[i]
            for j in indices:
                numbers = []
                for num in line:
                    try:
                        numbers.append(str(j+1)+'.'+num.split('.')[1])
                    except:
                        numbers.append('X')
                self.alm_matrix[j] = [self._get(num,'tokens') for num in numbers]

    def prog_align(
            self,
            model = 'sca',
            mode = 'global',
            gop = -3,
            gep_scale = float(0.5),
            scale = (1,1,1),
            factor = 0,
            tree_calc = 'neighbor',
            gap_weight = float(0.5),
            restricted_chars = 'T'
            ):
        """
        Carry out a progressive alignment analysis of the input sequences.

        Parameters
        ----------

        model : { 'dolgo', 'sca', 'asjp' }
            A string indicating the name of the :py:class:`Model \
            <lingpy.data.model>` object that shall be used for the analysis.
            Currently, three models are supported:
            
            * "dolgo" -- a sound-class model based on :evobib:`Dolgopolsky1986`,

            * "sca" -- an extension of the "dolgo" sound-class model based on
              :evobib:`List2012b`, and
            
            * "asjp" -- an independent sound-class model which is based on the
              sound-class model of :evobib:`Brown2008` and the empirical data
              of :evobib:`Brown2011` (see the description in
              :evobib:`List2012`.
        
        mode : { 'global', 'dialign' }
            A string indicating which kind of alignment analysis should be
            carried out during the progressive phase. Select between: 
            
            * "global" -- traditional global alignment analysis based on the
              Needleman-Wunsch algorithm :evobib:`Needleman1970`,

            * "dialign" -- global alignment analysis which seeks to maximize
              local similarities :evobib:`Morgenstern1996`.
        
        gop : int (default=-5)
            The gap opening penalty (GOP) used in the analysis.

        gep_scale : float (default=0.6)
            The factor by which the penalty for the extension of gaps (gap
            extension penalty, GEP) shall be decreased. This approach is
            essentially inspired by the exension of the basic alignment
            algorithm for affine gap penalties :evobib:`Gotoh1982`.

        scale : tuple or list (default=(0,0,0))
            The scaling factors for the modificaton of gap weights. The first
            value corresponds to sites of ascending sonority, the second value
            to sites of maximum sonority, and the third value corresponds to
            sites of decreasing sonority.

        factor : float (default=1)
            The factor by which the initial and the descending position shall
            be modified.

        tree_calc : { 'neighbor', 'upgma' }
            The cluster algorithm which shall be used for the calculation of
            the guide tree. Select between ``neighbor``, the Neighbor-Joining
            algorithm (:evobib:`Saitou1987`), and ``upgma``, the UPGMA
            algorithm (:evobib:`Sokal1958`).

        gap_weight : float (default=0)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.
        
        restricted_chars : string (default="T")
            Define which characters of the prosodic string of a sequence
            reflect its secondary structure (cf. :evobib:`List2012b`) and should therefore be aligned
            specifically. This defaults to "T", since this is the character
            that represents tones in the prosodic strings of sequences.

        """
        # create a string with the current parameters
        self.params = '_'.join(
                [
                    'prog',
                    model,
                    mode,
                    str(gop),
                    '{0:.1f}'.format(gep_scale),
                    '{0[0]:.1f}x{0[1]:.1f}x{0[2]:.1f}'.format(scale),
                    '{0:.1f}'.format(factor),
                    tree_calc,
                    '{0:.1f}'.format(gap_weight),
                    restricted_chars
                    ])

        self._set_model(model)
        self._set_scorer('classes')
        self._get_pairwise_alignments(
                gop = gop,
                gep_scale = gep_scale,
                scale = scale,
                factor = factor,
                restricted_chars=restricted_chars
                )
        self._make_matrix()
        self._make_guide_tree(tree_calc=tree_calc)
        self._merge_alignments(
                mode = mode,
                gop = gop,
                gep_scale = gep_scale,
                scale = scale,
                factor = factor,
                restricted_chars = restricted_chars,
                gap_weight = gap_weight,
                )
        self._update_alignments()

    def lib_align(
            self,
            model = 'sca',
            mode = 'global',
            modes = [
                ('global',-3,float(0.5)),
                ('local',-1,float(0.5)),
                ],
            scale = (1,1,1),
            factor = 0,
            tree_calc = 'neighbor',
            gap_weight = float(0.5),
            restricted_chars = 'T'
            ):
        """
        Carry out a library-based progressive alignment analysis of the sequences.

        In contrast to traditional progressive multiple sequence alignment
        approaches such as :evobib:`Feng1981` and :evobib:`Thompson1994`,
        library-based progressive alignment :evobib:`Notredame2000` is based on
        a pre-processing of the data where the information given in global and
        local pairwise alignments of the input sequences is used to derive a
        refined scoring function (*library*) which is later used in the
        progressive phase.


        Parameters
        ----------

        model : { 'dolgo', 'sca', 'asjp' }
            A string indicating the name of the :py:class:`Model \
            <lingpy.data.model>` object that shall be used for the analysis.
            Currently, three models are supported:
            
            * "dolgo" -- a sound-class model based on :evobib:`Dolgopolsky1986`,

            * "sca" -- an extension of the "dolgo" sound-class model based on
              :evobib:`List2012b`, and
            
            * "asjp" -- an independent sound-class model which is based on the
              sound-class model of :evobib:`Brown2008` and the empirical data
              of :evobib:`Brown2011` (see the description in
              :evobib:`List2012`.

        mode : { 'global', 'dialign' }
            A string indicating which kind of alignment analysis should be
            carried out during the progressive phase. Select between: 
            
            * "global" -- traditional global alignment analysis based on the
              Needleman-Wunsch algorithm :evobib:`Needleman1970`,

            * "dialign" -- global alignment analysis which seeks to maximize
              local similarities :evobib:`Morgenstern1996`.

        modes : list (default=[('global',-10,0.6),('local',-1,0.6)])
            Indicate the mode, the gap opening penalties (GOP), and the gap extension scale
            (GEP scale), of the pairwise alignment analyses which
            are used to create the library.
        
        gop : int (default=-5)
            The gap opening penalty (GOP) used in the analysis.

        gep_scale : float (default=0.6)
            The factor by which the penalty for the extension of gaps (gap
            extension penalty, GEP) shall be decreased. This approach is
            essentially inspired by the exension of the basic alignment
            algorithm for affine gap penalties :evobib:`Gotoh1982`.

        scale : tuple or list (default=(0,0,0))
            The scaling factors for the modificaton of gap weights. The first
            value corresponds to sites of ascending sonority, the second value
            to sites of maximum sonority, and the third value corresponds to
            sites of decreasing sonority.

        factor : float (default=1)
            The factor by which the initial and the descending position shall
            be modified.

        tree_calc : { 'neighbor', 'upgma' }
            The cluster algorithm which shall be used for the calculation of
            the guide tree. Select between ``neighbor``, the Neighbor-Joining
            algorithm (:evobib:`Saitou1987`), and ``upgma``, the UPGMA
            algorithm (:evobib:`Sokal1958`).

        gap_weight : float (default=0)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.
        
        restricted_chars : string (default="T")
            Define which characters of the prosodic string of a sequence
            reflect its secondary structure (cf. :evobib:`List2012b`) and
            should therefore be aligned specifically. This defaults to "T",
            since this is the character that represents tones in the prosodic
            strings of sequences.

        """
        # create a string with the current parameters
        params = [
                    'lib',
                    model,
                    mode,
                    '',
                    '{0[0]:.1f}x{0[1]:.1f}x{0[2]:.1f}'.format(scale),
                    '{0:.1f}'.format(factor),
                    tree_calc,
                    '{0:.1f}'.format(gap_weight),
                    restricted_chars
                    ]
        mode_params = []
        for m in modes:
            mode_params.append('{0[0]}x{0[1]}x{0[2]:.2f}'.format(m))
        mode_params = 'y'.join(mode_params)
        params[3] = mode_params
        
        self.params = '_'.join(params)
        
        # set the model
        self._set_model(model)
        
        # set the score mode to 'classes'
        self._set_scorer('classes')
        
        # start to create the library, note that scales and factors are set to
        # zero here, since scales and zeros are only useful in
        # profile-alignments. they eventually disturb pairwise alignments,
        # which is why it is important to keep their influence low when
        # creating the library from pairwise alignments
        self._create_library()
        for run in modes:
            self._get_pairwise_alignments(
                    run[0],
                    run[1],
                    run[2],
                    scale,
                    factor,
                    restricted_chars
                    )
            self._extend_library()

        # set the scorer to library mode
        self._set_scorer('library')

        # calculate pairwise alignments and the respective scores
        self._get_pairwise_alignments(
                mode,
                0,
                0.0,
                (1.0,1.0,1.0),
                0.0,
                restricted_chars
                )
        
        # create the matrix
        self._make_matrix()

        # reconstruct the tree
        self._make_guide_tree(tree_calc)
        
        # merge the alignments, not that the scale doesn't really influence any
        # of the results here, since gap scores are set to 0, gapping should be
        # the same in all positions, the factor, however, eventually influences
        # the score, since it changes character mappings as well
        self._merge_alignments(
                mode,
                0,
                0.0,
                (1.0,1.0,1.0),
                0.0,
                gap_weight,
                restricted_chars
                )
        self._update_alignments()

    def _reduce_gap_sites(
            self,
            msa,
            gap='X'
            ):
        """
        Method reduces all columns from an MSA when there are only gaps. This
        method is important for the iterative procedures.
        """

        new_msa = array(msa[:])
        no_gap_index = []
        for i in range(len(new_msa[0])):
            if list(new_msa[:,i]).count(gap) != len(new_msa):
                no_gap_index.append(i)
    
        new_msa = new_msa[:,no_gap_index].tolist()

        return new_msa

    def _split(
            self,
            idx
            ):
        """
        Split an MSA into two parts and retain their indices. 
        """
        
        # create the inverted index
        idxA = idx
        idxB = [i for i in range(self.height) if i not in idx]

        partA = self._reduce_gap_sites(self._alm_matrix[idxA])
        partB = self._reduce_gap_sites(self._alm_matrix[idxB])

        return partA,partB,idxA,idxB

    def _join(
            self,
            almA,
            almB,
            idxA,
            idxB
            ):
        """
        Join two aligned MSA by their index. 
        """
        
        m = len(almA[0])
        out_alm = [[0 for i in range(m)] for j in range(self.height)]

        for i in range(len(almA)):
            out_alm[idxA[i]] = almA[i]

        for i in range(len(almB)):
            out_alm[idxB[i]] = almB[i]
        
        out_alm = array(out_alm)

        return out_alm

    def _iter(
            self,
            idx_list,
            mode = 'global',
            gop = -3,
            gep_scale = 0.5,
            scale = (1,1,1),
            factor = 0.0,
            gap_weight = 0.5,
            check = 'final',
            restricted_chars = 'T'
            ):
        """
        Split an MSA into two parts and realign them.
        """

        sop = self.sum_of_pairs(gap_weight=gap_weight)
        alm_matrix = self._alm_matrix.copy()
        
        if len(idx_list) == 1:
            return

        for idx in idx_list:
            almA,almB,idxA,idxB = self._split(idx)
            almA,almB = self._align_profile(
                    almA,
                    almB,
                    mode = mode,
                    iterate = True,
                    gop = gop,
                    scale = scale,
                    gep_scale = gep_scale,
                    factor = factor,
                    gap_weight = gap_weight
                    )
            new_alm = self._join(
                    almA,
                    almB,
                    idxA,
                    idxB,
                    )

            self._alm_matrix = new_alm
            if check == 'immediate':
                new_sop = self.sum_of_pairs()
                if new_sop < sop:
                    self._alm_matrix = alm_matrix
                else:
                    sop = new_sop

        if check == 'final':
            new_sop = self.sum_of_pairs(gap_weight=gap_weight)
            if new_sop < sop:
                self._alm_matrix = alm_matrix

        self._update_alignments()
    
    def sum_of_pairs(
            self,
            alm_matrix = 'self',
            mat = None,
            gap_weight = 0
            ):
        """
        Calculate the sum-of-pairs score for a given alignment analysis.

        Parameters
        ----------

        alm_matrix : { 'self', 'other' }
            Indicate for which MSA the sum-of-pairs score shall be calculated.

        mat : None or :py:class:`numpy.array`
            If 'other' is chosen as an option for **alm_matrix**, define for
            which matrix the sum-of-pairs score shall be calculated.

        gap_weight : float (default=0)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.
        
        Returns
        -------
        The sum-of-pairs score of the alignment.
        """
        
        if alm_matrix == 'self':
            alm_matrix = self._alm_matrix
        else:
            alm_matrix = mat

        score = 0.0

        for i in range(alm_matrix.shape[1]):
            score += self._profile_score(
                    alm_matrix[:,i],
                    alm_matrix[:,i],
                    gap_weight = gap_weight
                    )
        return score / alm_matrix.shape[1]

    def _swap_sum_of_pairs(
            self,
            alm_matrix,
            gap_weight = 1.0,
            swap_penalty = -5
            ):
        
        score = 0.0

        for i in range(alm_matrix.shape[1]):
            score += self._swap_profile_score(
                    alm_matrix[:,i],
                    alm_matrix[:,i],
                    gap_weight = gap_weight,
                    swap_penalty = swap_penalty
                    )
        return score / alm_matrix.shape[1]
    
    def iterate_orphans(
            self,
            check = 'final',
            mode = 'global',
            gop = -3,
            gep_scale = float(0.5),
            scale = (1,1,1),
            factor = 0,
            gap_weight = 1,
            restricted_chars = 'T'
            ):
        """
        Iterate over the most divergent sequences in the sample.

        Parameters
        ----------

        check : string (default="final")
            Specify when to check for improved sum-of-pairs scores: After each
            iteration ("immediate") or after all iterations have been carried
            out ("final").
         
        mode : { 'global', 'overlap', 'dialign' }
            A string indicating which kind of alignment analysis should be
            carried out during the progressive phase. Select between: 
            
            * 'global' -- traditional global alignment analysis based on the
              Needleman-Wunsch algorithm :evobib:`Needleman1970`,

            * 'dialign' -- global alignment analysis which seeks to maximize
              local similarities :evobib:`Morgenstern1996`.

            * 'overlap' -- semi-global alignment, where gaps introduced in the
              beginning and the end of a sequence do not score.     
        
        gop : int (default=-5)
            The gap opening penalty (GOP) used in the analysis.

        gep_scale : float (default=0.6)
            The factor by which the penalty for the extension of gaps (gap
            extension penalty, GEP) shall be decreased. This approach is
            essentially inspired by the exension of the basic alignment
            algorithm for affine gap penalties [Goto81]_.

        scale : tuple or list (default=(3,1,2))
            The scaling factors for the modificaton of gap weights. The first
            value corresponds to sites of ascending sonority, the second value
            to sites of maximum sonority, and the third value corresponds to
            sites of decreasing sonority.

        factor : float (default=0.3)
            The factor by which the initial and the descending position shall
            be modified.

        gap_weight : float (default=0)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.

        Notes
        -----
        The most divergent sequences are those whose average distance to all
        other sequences is above the average distance of all sequence pairs.

        See also
        --------
        Multiple.iterate_clusters
        Multiple.iterate_similar_gap_sites
        Multiple.iterate_all_sequences

        """
        orphans = []
        means = self.matrix.mean()
        for i,line in enumerate(self.matrix):
            if line.mean() > means:
                orphans.append([i])

        self._iter(
                orphans,
                check = check,
                mode = mode,
                scale = scale,
                gop = gop,
                gep_scale = gep_scale,
                factor = factor,
                gap_weight = gap_weight,
                restricted_chars = restricted_chars
                )
           
    def iterate_clusters(
            self,
            threshold,
            check = 'final',
            mode = 'global',
            gop = -3,
            gep_scale = float(0.5),
            scale = (1,1,1),
            factor = 0,
            gap_weight = 1,
            restricted_chars = 'T'
            ):
        """
        Iterative refinement based on a flat cluster analysis of the data.
        
        This method uses the :py:func:`lingpy.algorithm.cluster.flat_upgma`
        function in order to retrieve a flat cluster of the data.

        Parameters
        ----------
        
        threshold : float
            The threshold for the flat cluster analysis.

        check : string (default="final")
            Specify when to check for improved sum-of-pairs scores: After each
            iteration ("immediate") or after all iterations have been carried
            out ("final").
         
        mode : { 'global', 'overlap', 'dialign' }
            A string indicating which kind of alignment analysis should be
            carried out during the progressive phase. Select between: 
            
            * 'global' -- traditional global alignment analysis based on the
              Needleman-Wunsch algorithm :evobib:`Needleman1970`,

            * 'dialign' -- global alignment analysis which seeks to maximize
              local similarities :evobib:`Morgenstern1996`.

            * 'overlap' -- semi-global alignment, where gaps introduced in the
              beginning and the end of a sequence do not score.     

        gop : int (default=-5)
            The gap opening penalty (GOP) used in the analysis.

        gep_scale : float (default=0.6)
            The factor by which the penalty for the extension of gaps (gap
            extension penalty, GEP) shall be decreased. This approach is
            essentially inspired by the exension of the basic alignment
            algorithm for affine gap penalties [Goto81]_.

        scale : tuple or list (default=(3,1,2))
            The scaling factors for the modificaton of gap weights. The first
            value corresponds to sites of ascending sonority, the second value
            to sites of maximum sonority, and the third value corresponds to
            sites of decreasing sonority.

        factor : float (default=0.3)
            The factor by which the initial and the descending position shall
            be modified.

        gap_weight : float (default=0)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.

        See also
        --------
        Multiple.iterate_similar_gap_sites
        Multiple.iterate_all_sequences

        """
        
        # don't calculate this if there are less than 5 sequences
        if len(self.seqs) < 3:
            return 
        
        # create the clusters
        clusters = dict(
                [(i[0],[i[1]]) for i in zip(list(range(self.height)),list(range(self.height)))]
                )

        _flat_upgma(
                clusters,
                self.matrix,
                threshold,
                )
        self._iter(
                list(clusters.values()),
                check = check,
                mode = mode,
                scale = scale,
                gop = gop,
                gep_scale = gep_scale,
                factor = factor,
                gap_weight = gap_weight,
                restricted_chars = restricted_chars
                )

    def iterate_similar_gap_sites(
            self,
            check = 'final',
            mode = 'global',
            gop = -3,
            gep_scale = float(0.5),
            scale = (1,1,1),
            factor = 0,
            gap_weight = 1,
            restricted_chars = 'T'
            ):
        """
        Iterative refinement based on the *Similar Gap Sites* heuristic.

        This heuristic is fairly simple. The idea is to try to split a given
        MSA into partitions with identical gap sites.
        
        Parameters
        ----------

        check : { 'final', 'immediate' }
            Specify when to check for improved sum-of-pairs scores: After each
            iteration ("immediate") or after all iterations have been carried
            out ("final").
         
        mode : { 'global', 'overlap', 'dialign' }
            A string indicating which kind of alignment analysis should be
            carried out during the progressive phase. Select between: 
            
            * 'global' -- traditional global alignment analysis based on the
              Needleman-Wunsch algorithm :evobib:`Needleman1970`,

            * 'dialign' -- global alignment analysis which seeks to maximize
              local similarities :evobib:`Morgenstern1996`.

            * 'overlap' -- semi-global alignment, where gaps introduced in the
              beginning and the end of a sequence do not score.       

        gop : int (default=-5)
            The gap opening penalty (GOP) used in the analysis.

        gep_scale : float (default=0.5)
            The factor by which the penalty for the extension of gaps (gap
            extension penalty, GEP) shall be decreased. This approach is
            essentially inspired by the exension of the basic alignment
            algorithm for affine gap penalties :evobib:`Gotoh1982`.

        scale : tuple or list (default=(1.2,1.0,1.1))
            The scaling factors for the modificaton of gap weights. The first
            value corresponds to sites of ascending sonority, the second value
            to sites of maximum sonority, and the third value corresponds to
            sites of decreasing sonority.

        factor : float (default=0.3)
            The factor by which the initial and the descending position shall
            be modified.

        gap_weight : float (default=1)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When, e.g., set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.

        See also
        --------
        Multiple.iterate_clusters
        Multiple.iterate_all_sequences
        Multiple.iterate_orphans

        """

        self._similar_gap_sites()
        
        if len(self.gap_dict) == 1:
            return

        self._iter(
                list(self.gap_dict.values()),
                check = check,
                mode = mode,
                scale = scale,
                gop = gop,
                gep_scale = gep_scale,
                factor = factor,
                gap_weight = gap_weight
                )

    def iterate_all_sequences(
            self,
            check = 'final',
            mode = 'global',
            gop = -3,
            gep_scale = float(0.5),
            scale = (1,1,1),
            factor = 0,
            gap_weight = 1,
            restricted_chars = 'T'
            ):
        """
        Iterative refinement based on a complete realignment of all sequences.

        This method essentially follows the iterative method of [BaSt87] with
        the exception that an MSA has already been calculated.
        
        Parameters
        ----------

        check : { 'final', 'immediate' }
            Specify when to check for improved sum-of-pairs scores: After each
            iteration ("immediate") or after all iterations have been carried
            out ("final").

        mode : { 'global', 'overlap', 'dialign' }
            A string indicating which kind of alignment analysis should be
            carried out during the progressive phase. Select between: 
            
            * 'global' -- traditional global alignment analysis based on the
              Needleman-Wunsch algorithm :evobib:`Needleman1970`,

            * 'dialign' -- global alignment analysis which seeks to maximize
              local similarities :evobib:`Morgenstern1996`.

            * 'overlap' -- semi-global alignment, where gaps introduced in the
              beginning and the end of a sequence do not score.
        
        gop : int (default=-5)
            The gap opening penalty (GOP) used in the analysis.

        gep_scale : float (default=0.5)
            The factor by which the penalty for the extension of gaps (gap
            extension penalty, GEP) shall be decreased. This approach is
            essentially inspired by the exension of the basic alignment
            algorithm for affine gap penalties [Goto81]_.

        scale : tuple or list (default=(3,1,2))
            The scaling factors for the modificaton of gap weights. The first
            value corresponds to sites of ascending sonority, the second value
            to sites of maximum sonority, and the third value corresponds to
            sites of decreasing sonority.

        factor : float (default=0.3)
            The factor by which the initial and the descending position shall
            be modified.

        gap_weight : float (default=0)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.
        
        See also
        --------
        Multiple.iterate_clusters
        Multiple.iterate_similar_gap_sites
        Multiple.iterate_orphans

        """

        indices = [[i] for i in range(self.height)]
        
        self._iter(
                indices,
                check = check,
                mode = mode,
                scale = scale,
                gop = gop,
                gep_scale = gep_scale,
                factor = factor,
                gap_weight = gap_weight,
                restricted_chars = restricted_chars
                )

    def get_peaks(
        self,
        gap_weight = 0
        ):
        """
        Calculate the profile score for each column of the alignment.

        Parameters
        ----------
        
        gap_weight : float (default=0)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.

        Returns
        -------

        peaks : list
            A list containing the profile scores for each column of the given
            alignment.
            
        Examples
        --------


        """
        
        peaks = []
        for i in range(self._alm_matrix.shape[1]):
            peaks.append(
                    self._profile_score(
                        self._alm_matrix[:,i],
                        self._alm_matrix[:,i],
                        gap_weight = gap_weight
                        )
                    )

        return peaks

    def _make_peak_idx(
            self,
            t_scale = 0.5,
            gap_weight = 0.0
            ):

        peaks = array(self.peaks(gap_weight = gap_weight))
        
        threshold = peaks.mean() + t_scale * peaks.std()

        self.peak_idx = [i for i in range(len(peaks)) if peaks[i] > threshold]

    def get_pairwise_alignments(
            self,
            new_calc = True,
            model = 'sca',
            mode = 'global',
            gop = -3,
            gep_scale = float(0.5),
            scale = (0,0,0),
            factor = 1,
            restricted_chars = 'T',
            ):
        """
        Function creates a dictionary of all pairwise alignments  scores.
        
        Parameters
        ----------
        new_calc : bool (default=True)
            Specify, whether the analysis should be repeated from the
            beginning, or whether already conducted analyses should be carried
            out.

        model : string (default="sca")
            A string indicating the name of the :py:class:`Model \
            <lingpy.data.model>` object that shall be used for the analysis.
            Currently, three models are supported:
            
            * "dolgo" -- a sound-class model based on :evobib:`Dolgopolsky1986`,

            * "sca" -- an extension of the "dolgo" sound-class model based on
              :evobib:`List2012b`, and
            
            * "asjp" -- an independent sound-class model which is based on the
              sound-class model of :evobib:`Brown2008` and the empirical data
              of :evobib:`Brown2011` (see the description in
              :evobib:`List2012`.

        mode : string (default="global")
            A string indicating which kind of alignment analysis should be
            carried out during the progressive phase. Select between: 
            
            * "global" -- traditional global alignment analysis based on the
              Needleman-Wunsch algorithm :evobib:`Needleman1970`,

            * "dialign" -- global alignment analysis which seeks to maximize
              local similarities :evobib:`Morgenstern1996`.
        
        gop : int (default=-3)
            The gap opening penalty (GOP) used in the analysis.

        gep_scale : float (default=0.6)
            The factor by which the penalty for the extension of gaps (gap
            extension penalty, GEP) shall be decreased. This approach is
            essentially inspired by the exension of the basic alignment
            algorithm for affine gap penalties :evobib:`Gotoh1982`.

        scale : tuple or list (default=(0,0,0))
            The scaling factors for the modificaton of gap weights. The first
            value corresponds to sites of ascending sonority, the second value
            to sites of maximum sonority, and the third value corresponds to
            sites of decreasing sonority.

        factor : float (default=1)
            The factor by which the initial and the descending position shall
            be modified.

        tree_calc : { 'neighbor', 'upgma' }
            The cluster algorithm which shall be used for the calculation of
            the guide tree. Select between ``neighbor``, the Neighbor-Joining
            algorithm (:evobib:`Saitou1987`), and ``upgma``, the UPGMA
            algorithm (:evobib:`Sokal1958`).

        gap_weight : float (default=0)
            The factor by which gaps in aligned columns contribute to the
            calculation of the column score. When set to 0, gaps will be
            ignored in the calculation. When set to 0.5, gaps will count half
            as much as other characters.
        
        restricted_chars : string (default="T")
            Define which characters of the prosodic string of a sequence
            reflect its secondary structure (cf. :evobib:`List2012b`) and
            should therefore be aligned specifically. This defaults to "T",
            since this is the character that represents tones in the prosodic
            strings of sequences.

        """
        
        if new_calc:
            # define the class model
            self._set_model(model)

            # reset the scorer to "classes"
            self._set_scorer('classes')

            # retrieve the alignments
            self._get_pairwise_alignments(
                    mode,
                    gop,
                    gep_scale,
                    scale,
                    factor,
                    restricted_chars
                    )

            # retrieve the scores
            self._make_matrix()

            self.alignments = {}

            for i in range(self.height):
                for j in range(self.height):
                    if i <= j:
                        # get the score of the alignment
                        score = self.matrix[i][j]
                        sim = self._alignments[i][j][2]

                        # retrieve the numeric tokens
                        tokA = self._alignments[i][j][0]
                        tokB = self._alignments[i][j][1]
                        
                        # append values to dictionary
                        for k in self.int2ext[i]:
                            for l in self.int2ext[j]:
                                almA,almB = [],[]
                                for m in tokA:
                                    try:
                                        almA.append(
                                                self._get(
                                                    str(k+1)+'.'+m.split('.')[1],
                                                    'tokens'
                                                    )
                                                )
                                    except:
                                        almA.append('-')
                                for m in tokB:
                                    try:
                                        almB.append(
                                                self._get(
                                                    str(l+1)+'.'+m.split('.')[1],
                                                    'tokens'
                                                    )
                                                )
                                    except:
                                        almB.append('-')

                                self.alignments[k,l] = [
                                        almA,
                                        almB,
                                        score
                                        ]
        else:
            # if new_calc is not chosen, the PID of an alignment will be
            # returned, beware only to calculate the pid for unique sequences
            # in order to save time and memory
            self.alignments = {}
            seqs = list(self.uniseqs.keys())

            for i,seqA in enumerate(seqs):
                for j,seqB in enumerate(seqs):
                    if i <= j:
                        # get the score of the alignment
                        almA = self.alm_matrix[self.uniseqs[seqA][0]]
                        almB = self.alm_matrix[self.uniseqs[seqB][0]]

                        # get the pid
                        score = pid(almA,almB)
                        
                        # append values to dictionary
                        for k in self.uniseqs[seqA]:
                            for l in self.uniseqs[seqB]:
                                if k != l:
                                    self.alignments[k,l] = [
                                            almA,
                                            almB,
                                            score
                                            ]

    def get_pid(
            self,
            mode = 1
            ):
        """
        Return the Percentage Identity (PID) score of the calculated MSA.
        
        Parameters
        ----------
        mode : { 1, 2, 3, 4, 5 }
            Indicate which of the four possible PID scores described in :evobib:`Raghava2006`
            should be calculated, the fifth possibility is added for linguistic
            purposes:
            
            1. identical positions / (aligned positions + internal gap positions),
            
            2. identical positions / aligned positions,
            
            3. identical positions / shortest sequence, or
            
            4. identical positions / shortest sequence (including internal gap
               pos.)

            5. identical positions / (aligned positions + 2 * number of gaps)  


        Returns
        -------
        score : float
            The PID score of the given alignment as a floating point number between
            0 and 1.

        See also
        --------
        lingpy.algorithm.misc.pid

        """

        # create a dictionary of unique sequences
        weights = {}
        for key in list(self.uniseqs.keys()):
            vals = self.uniseqs[key]
            l = len(vals)
            for val in vals:
                weights[val] = (key,1.0 / l)

        score = 0.0
        for i,seqA in enumerate(self.alm_matrix):
            for j,seqB in enumerate(self.alm_matrix):
                if i < j:
                    kA,wA = weights[i]
                    kB,wB = weights[j]
                    if kA != kB:
                        score += pid(seqA,seqB,mode) * wA * wB
        
        l = len(self.uniseqs)
        count = (l ** 2 - l) / 2
                        
        if count == 0:
            return 1.0
        else:
            return score / count

    def _similar_gap_sites(self):
        """
        Create a dictionary which lists all strings with a similar gap
        structure and their index. The gap structure is marked in the key of
        the dictionary, where '1' refers to gapped sites and '0' refers to
        ungapped sites. The values of the dictionary are a list of integers
        referring to the position of the sequences having this structure in the
        MSA.
        """
        
        self.gap_dict = {}
        """
        A dictionary storing the different gap profiles of an MSA as keys and
        the indices of the corresponding sequences as values.
        """

        for i in range(len(self._classes)):

            gaps = ''
            for seg in self._alm_matrix[i]:
                if seg == 'X':
                    gaps += '1'
                else:
                    gaps += '0'
                
            try:
                self.gap_dict[gaps] += [i]
            except KeyError:
                self.gap_dict[gaps] = [i]

    def _mk_gap_array(self):
        """
        Return an array of the gap-profiles of an alignment.
        @return: An array, representing the gap profiles as integers (0
            indicates characters and 1 indicates gaps).
        @rtype: C{scipy.array}
        """
        self._similar_gap_sites()

        gap_array = zeros(
                [len(self.gap_dict),len(self._alm_matrix[0])], 
                dtype='int'
                )

        for i in range(len(self.gap_dict)):
            
            gap_array[i] = array([int(j) for j in list(
                self.gap_dict.keys()
                )[i]])

        return gap_array

    def _swap_condition(
            self
            ):
        """
        The condition for swaps to possibly occur in the alignment. These are
        the complementary sites in the alignment, which are extracted from the
        gap array.
        
        """

        swaps = []
        gap_array = self._mk_gap_array()
        for i in range(len(gap_array[0])):

            try:
                if 0 not in gap_array[:,i] + gap_array[:,i+2]:
                    swaps.append((i))
            except:
                pass

        return swaps
        
    def _swap_check(
            self,
            ind,
            gap_weight=1.0,
            swap_penalty = -5,
            db = False
            ):
        """
        Carry out a check for swapped regions.
        """
        # [i] We define two version of the possibly swapped region, a first
        # ... one, where the original alignment is unchanged, and a second one,
        # ... where the alignment is shifted, i.e. the gaps are switched.
        matA = self._alm_matrix.copy()
        matB = self._alm_matrix.copy()

        for i in range(len(self._classes)):
            
            # [i] shift the gap of the first matrix
            if matA[i][ind] != 'X' and matA[i][ind+2] == 'X':
                matA[i][ind+2] = matA[i][ind+1]
                matA[i][ind+1] = matA[i][ind]
                matA[i][ind] = 'X'
            elif matA[i][ind] == 'X':
                matA[i][ind] = matA[i][ind+1]
                matA[i][ind+1] = matA[i][ind+2]
                matA[i][ind+2] = 'X'
            
            # [i] unswap the possibly swapped columns by shifting values
            # ... unequal to a gap and leaving a special symbol (+) which will
            # ... cope for the penalty for a swap
            if matA[i][ind] != 'X':
                pass
            elif matA[i][ind+2] != 'X' :
                matA[i][ind] = matA[i][ind+2]
                matA[i][ind+2] = '+'
            
            # [i] apply the same procedure to the unshifted matrix
            if matB[i][ind] != 'X':
                pass
            elif matB[i][ind+2] != 'X':
                matB[i][ind] = matB[i][ind+2]
                matB[i][ind+2] = '+'
        
        # [i] calculate normal and new sum-of-pairs scores, convert to integers
        # ... in order to guarantee the accuracy of the comparison of
        # ... sop-scores
        msa = int(self.sum_of_pairs(gap_weight=gap_weight) * 1000000)
        msaA = self._swap_sum_of_pairs(
                matA,
                gap_weight=gap_weight,
                swap_penalty=swap_penalty
                )
        msaB = self._swap_sum_of_pairs(
                matB,
                gap_weight=gap_weight,
                swap_penalty=swap_penalty
                )
        msaAB = int((msaA + msaB) * 0.5 * 1000000)

        
        # return True if the newly calculated sop-score is greater than the
        # previous one
        if msaAB > msa:
            return True
        else:
            return False

    def swap_check(
            self,
            swap_penalty = -1,
            score_mode = 'classes'
            ):
        """
        Check for possibly swapped sites in the alignment.

        Parameters
        ----------
        swap_penalty : int or float
            Specify the penalty for swaps in the alignment.

        score_mode : { 'classes', 'library' }
            Define the score-mode of the calculation which is either based on
            sound classes proper, or on the specific scores derived from the
            library approach.

        Returns
        -------
        result : bool
            Returns ``True``, if a swap was identified, and ``False``
            otherwise. The information regarding the position of the swap is
            stored in the attribute ``swap_index``.
        
        Notes
        -----
        The method for swap detection is described in detail in [LisB12]_.

        Examples
        --------
        Load a file containing swaps from the test data. 

        >>> from lingpy import *
        >>> mult = Multiple(get_file('test.msq'))

        Align the data, using the progressive approach.

        >>> mult.prog_align()

        Check for swaps.
        """

        self._set_scorer(score_mode)
        
        swaps = []

        for i in self._swap_condition():
            check = self._swap_check(
                    i,
                    swap_penalty = swap_penalty,
                    )
            if check == True:
                swaps.append(i)
            else:
                pass

        if len(swaps) == 0:
            return False
        else:
            # check for incompatible swaps. this is a temporary solution
            # since it might be better to check the BEST swaps and not only
            # to discard them in a linear order
            swp = []
            while swaps:
                i = swaps.pop(0)
                if i-1 not in swp and i-2 not in swp and i-3 not in swp:
                    swp.append(i)
            
            self.swap_index = [(i,i+1,i+2) for i in swp]
            
            return True
        
    def _get_params(self):
        """
        Return a string of all relevant parameters for a calculation.
        """

        out = ''
        out += repr(self.model)


                                
