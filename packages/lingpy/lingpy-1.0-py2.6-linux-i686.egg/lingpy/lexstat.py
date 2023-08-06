# *-* coding: utf-8 *-*
"""
This is the basic module for the 
"""

from __future__ import division,print_function
import os
from numpy import array,zeros,log2 
from pickle import load,dump
from data import *
from algorithm import *
from algorithm.cluster import _flat_upgma
from align.multiple import _Multiple
from output.color import colorRange

class LexStat(object):
    """
    Basic class for handling lexicostatistical datasets.

    Parameters
    ----------
    infile : file
        A file in ``lxs``-format.  
    
    Notes
    -----
    The LexStat class serves as the base class for the handling of
    lexicostatistical datasets (see :evobib:`Swadesh1955` for a detailed description of the
    method of lexicostatistics). It provides methods for data conversion, when
    analyses on cognacy have been conducted in a qualitative way, and also
    allows to carry out cognate judgments automatically, based on the different
    methods described in :evobib:`List2012a`.

    The input data for LexStat is a simple tab-delimited text file with the
    language names in the first row, an ID in the first column, and the data in
    the columns corresponding to the language names. Additionally, the file can
    contain headwords corresponding to the IDs and cognate-IDs, specifying
    which words in the data are thought to be cognate.  This structure is
    almost the same as the one employed in the Starling database program (see
    http://starling.rinet.ru). Synonyms are also specified in the same way by
    simply adding additional rows with the same ID. The following is an example
    for the possible structure of an input file::
    
        ID  Word    German  COG   English   COG ...
        1   hand    hantʰ   1     hæːnd     1   ...
        2   fist    faustʰ  2     fist      2   ...
        ... ...     ...     ...   ...       ... ...  
    """
    def __init__(
            self,
            infile
            ):

        # store the name of the input file
        self.infile = infile.split('/')[-1].replace('.lxs','')
        
        # load the data
        try:
            txt = array(loadtxt(infile),dtype="str")
        except IOError:
            txt = array(loadtxt(infile+'.lxs'),dtype="str")

        # check whether there are cognates in the data
        if 'COG' in txt[0]:
            cog_idx = [i for i in range(txt.shape[1]) if txt[0][i] == 'COG']
            etr_idx = [i-1 for i in cog_idx]
            self.cogs = array(txt[1:,cog_idx],dtype='int')
            self.words = txt[1:,etr_idx]
        else:
            etr_idx = [i for i in range(txt.shape[1]) if txt[0][i].lower() not in
                    ['number','words']]
            self.words = txt[1:,etr_idx]
            self.cogs = zeros(self.words.shape,dtype='int')
        
        # store the numbers
        self.numbers = array(txt[1:,0],dtype='int')
        
        # check whether headwords are in the data
        if txt[0][1].lower() == 'words':
            self.items = txt[1:,1]
        else:
            self.items = array(self.numbers,dtype='str')

        # create the synonym-idx
        self.idx = {}
        for i,etr in enumerate(self.words):
            try:
                self.idx[self.numbers[i]] += [i]
            except:
                self.idx[self.numbers[i]] = [i]

        # get the language names
        self.taxa = txt[0,etr_idx]
        
        # create a specific format string in order to receive taxa of equal
        # length
        mtax = max([len(t) for t in self.taxa])
        self._txf = '{0:.<'+str(mtax)+'}'

        # get the prosodic strings and the context information
        self.tokens = self.words.copy().tolist()
        self.prostrings = self.words.copy()
        for i in range(self.words.shape[0]):
            for j in range(self.words.shape[1]):
                if self.words[i][j] != '-':
                    try:
                        tokens = ipa2tokens(self.words[i][j])
                        sonar = [int(x) for x in tokens2class(tokens,art)]
                        prostring = prosodic_string(sonar)
                        self.tokens[i][j] = tokens
                        self.prostrings[i][j] = prostring
                    except:
                        print("[i] Some error with string <"+self.words[i][j]+">")
        
        # turn self.tokens into LingpyArray
        self.tokens = LingpyArray(self.tokens)

        # create an index for all sequences
        self.idxs = self.words.copy()
        self.idxd = {}
        count = 1
        for i,line in enumerate(self.words):
            for j,entry in enumerate(line):
                if entry != '-':
                    self.idxs[i][j] = count
                    self.idxd[count] = (i,j)
                    count += 1
                else:
                    self.idxs[i][j] = 0
        self.idxs = array(self.idxs,dtype='int')
                    
        # get height and width
        self.width = len(self.taxa)
        self.height = len(self.idx)

        # create a dictionary in which data created during the calculation can
        # by stored
        self.data = {}

    def _flatten(
            self,
            idx
            ):
        """
        Return a flat representation of the data in a given semantic slot.
        """

        return [i for i in self.idxs[self.idx[idx]].flatten() if i > 0]
    
    def __getitem__(
            self,
            idx
            ):
        """
        Function returns a specified value for a general ID of the entry.
        """
        
        try:
            data = idx[1]
            idx = abs(idx[0])
        except:
            data = 'w'
            idx = abs(idx)
        
        if data == 'w':
            return self.words[self.idxd[idx]]
        elif data == 'n':
            return self._nbrs[self.idxd[idx]]
        elif data == 'N':
            return self.numbers[self.idxd[idx][0]]
        elif data == 'W':
            return self.weights[self.idxd[idx]]
        elif data == 'r':
            return self.restrictions[self.idxd[idx]]
        elif data == 'c':
            return self.classes[self.idxd[idx]]
        elif data == 'C':
            return self.cogs[self.idxd[idx]]
        elif data == 'l':
            return self.taxa[self.idxd[idx][1]]
        elif data == 'p':
            return self.prostrings[self.idxd[idx]]
        elif data == 'i':
            return self.items[self.idxd[idx][0]]
        elif data == 't':
            return self.tokens[self.idxd[idx]]

    def _get_pairs(
            self,
            idxA,
            idxB,
            data,
            repeats = False
            ):
        """
        Return a list of tuples consisting of all pairwise items of the given
        datatype.
        """

        if not repeats:
            try:
                out = self.data[str(idxA)+'/'+str(idxB)+'/'+data+'/f']
            except:
                out = [(self[a,data],self[b,data]) for (a,b) in
                        self._pairs[idxA,idxB] if a > 0]
                self.data[str(idxA)+'/'+str(idxB)+'/'+data+'/f'] = out
        else:
            try:
                out = self.data[str(idxA)+'/'+str(idxB)+'/'+data+'/t']
            except:
                out = [(self[a,data],self[b,data]) for (a,b) in 
                        self._pairs[idxA,idxB] if a != 0]
                self.data[str(idxA)+'/'+str(idxB)+'/'+data+'/t'] = out

        return out

    def __len__(self):
        """
        Return the length of the dataset in terms of the total number of words.
        """
        
        return max(self.idxd)

    def _renumber(
            self,
            loans=False
            ):
        """
        Make the numbers in the data regular.
        @todo: check whether this really works!
        """
        
        num = 1

        for key in self.idx.keys():
            flats = self._flatten(key)
            cogs = [abs(self.cogs[self.idxd[f]]) for f in flats]
            
            uniques = list(set(cogs))
            
            tmp = dict(zip(uniques,range(num,num+len(uniques)+1)))

            for f in flats:
                c = self.cogs[self.idxd[f]]
                if c > 0:
                    self.cogs[self.idxd[f]] = tmp[c]
                elif c < 0:
                    if loans:
                        self.cogs[self.idxd[f]] = -tmp[abs(c)]
                    else:
                        self.cogs[self.idxd[f]] = tmp[abs(c)]

            num += len(uniques)

    def _set_model(
            self,
            model = 'sca',
            merge_vowels = True
            ):
        """
        Define a sequence model for the current calculation and calculate
        several statistics, such as the letter frequency.
        """
        
        # store model and scoring dictionary as attributes
        self.model = eval(model)

        # define the arrays for sound classes and numbers
        self.classes = self.words.copy()
        self._nbrs = self.words.tolist()
        
        # iterate over all entries and change them according to the model
        for i,line in enumerate(self.classes):
            for j,cls in enumerate(line):
                if cls != '-':
                    classes = tokens2class(self.tokens[i][j],self.model)
                    self.classes[i][j] = classes
                    self._nbrs[i][j] = [
                            str(j) + '.' + '.'.join(k) for k in zip(
                                self.prostrings[i][j],
                                classes
                                )
                                ]

        # convert clss and nbrs into lingpy-array objects
        self._nbrs = LingpyArray(self._nbrs)

        # create the dictionary which stores the frequencies
        self.freqs = {}

        # iterate over all sequences
        for i in range(self.width):
            self.freqs[i] = {}
            for nbr in self._nbrs[:,i]:
                if nbr != '-':
                    for n in nbr:
                        try:
                            self.freqs[i][n] += 1.0
                        except KeyError:
                            self.freqs[i][n] = 1.0

        # create an empty scorer
        self.scorer = {}
        self.score_dict = {}
        
        # iterate over all chars in self._nbrs in order to get all possible
        # combinations of characters and define them as dictionary pairs
        for i in range(self.width):
            for j in range(self.width):
                if i <= j:
                    for charA in list(self.freqs[i].keys())+[str(i)+'.X.-']:
                        for charB in list(self.freqs[j].keys())+[str(j)+'.X.-']:
                            self.scorer[charA,charB] = 0.0
                            try:
                                self.score_dict[charA,charB] = \
                                        self.model.scorer[
                                                charA.split('.')[2],
                                                charB.split('.')[2]
                                                ]
                            except:
                                pass

    def _set_val(
            self,
            scale = (1.2,1.0,1.1),
            factor = 0.3,
            gop = -3,
            gep_scale = 0.6,
            restricted_chars = 'T',
            pairwise_threshold = 0.7
            ):
        """
        Determine the settings for the calculation.
        """

        self.scale = scale
        self.factor = factor
        self.gop = gop
        self.gep_scale = gep_scale
        self.restricted_chars = restricted_chars
        self.pairwise_threshold = pairwise_threshold

        # create the weights and the restrictions
        self.restrictions = self.classes.tolist()
        self.weights = self.classes.tolist()

        # iterate over all entries and change them according to the model
        for i,line in enumerate(self.prostrings):
            for j,prostring in enumerate(line):
                if prostring != '-':
                    res = []
                    for k,char in enumerate(prostring):
                        if char in self.restricted_chars:
                            res.append(-(k+1))
                        else:
                            res.append(k+1)
                    self.restrictions[i][j] = res
                    weights = self.gop * array(
                            prosodic_weights(
                                prostring,
                                scale,
                                factor
                                )
                            )
                    self.weights[i][j] = weights.tolist()
        
        self.restrictions = LingpyArray(self.restrictions)
        self.weights = LingpyArray(self.weights)

    def _make_pair(
            self,
            idxA,
            idxB
            ):
        """
        Get list of language pairs which serve as input for the align
        algorithm.

        @todo: think of a solution of excluding stuff for the distribution
        calculation and using it later anyway!
        """
        # create the list entry for the dictionary
        self._pairs[idxA,idxB] = []

        # carry out a preprocessing of the word lists in order to avoid that
        # identical words show up in the data
        clsA = self.words[:,idxA].copy()
        clsB = self.words[:,idxB].copy()

        # if the lengths of lists and sets are different, there are duplicate
        # characters which should be eliminated. This is a very rough procedure
        # which may well lead to a loss of information
        if len(clsA) != len(set(clsA)):
            tmp = []
            for i,cls in enumerate(clsA):
                if cls in tmp and cls != '-':
                    clsA[i] = '--'
                else:
                    tmp.append(cls)
        if len(clsB) != len(set(clsB)):
            tmp = []
            for i,cls in enumerate(clsB):
                if cls in tmp and cls != '-':
                    clsB[i] = '--'
                else:
                    tmp.append(cls)

        # fill the lists
        for key in self.idx.keys():
            # get all lists for the language pairs
            listA = clsA[self.idx[key]]
            listB = clsB[self.idx[key]]
            for i,lA in enumerate(listA):
                for j,lB in enumerate(listB):
                    if '-' not in (lA,lB):
                        
                        # get the pairs
                        pairA = self.idxs[self.idx[key],idxA][i]
                        pairB = self.idxs[self.idx[key],idxB][j]

                        if '--' not in (lA,lB):
                            self._pairs[idxA,idxB].append((pairA,pairB))
                        else:
                            self._pairs[idxA,idxB].append((-pairA,-pairB))
            
    def _make_all_pairs(
            self
            ):
        """
        Create pairwise lists for all languages.
        """

        self._pairs = {}
        self._alignments = {}
        self.scores = {}

        # iterate over all languages
        for i in range(self.width):
            for j in range(self.width):
                if i <= j:
                    self._make_pair(i,j)

    def _scale(
            self,
            x,
            factor = 0.01
            ):
        """
        Scaling factor for distances in dependence of sequence length.
        """
        try:
            return self.scales[x-1]
        except:
            s = 0
            self.scales = [1]
            for i in range(1,x):
                s += (x / i) * (factor ** i) * (1 - factor) ** (x-i)
                self.scales.append(1+s)
            return self.scales[x-1]

    def _self_score(
            self,
            seq,
            scorer
            ):
        """
        Return the score for an alignment with itself.
        """
        score = 0.0
        new_seq = [i for i in seq if '-' not in i]
        for a in new_seq:
            score += scorer[a,a]

        return score

    def _pair_score(
            self,
            seqA,
            seqB,
            scorer
            ):
        """
        Return the score for an alignment of two sequences.
        """
        score = 0.0
        for a,b in zip(seqA,seqB):
            if '-' not in (a,b):
                score += scorer[a,b]
            else:
                score += -1.0 

        return score

    def _distance_score(
            self,
            almA,
            almB,
            scoreAB,
            scorer
            ):
        """
        Function calculates the Downey et al. (2008) distance score for
        pairwise sequence alignments.
        """
        
        # calculate the self_scores
        scoreA = self._self_score(almA,scorer)
        scoreB = self._self_score(almB,scorer)
        
        try:
            # @check@ whether it changes the results if the scores are normalized
            # to not exceed 1.0
            score = (1.0 - (2.0 * scoreAB / (scoreA + scoreB))) 
            if score > 1.0:
                return score
            else:
                return score

        except ZeroDivisionError:   
            #print(almA,almB,scoreAB)
            #print("[!] Float division!")
            return 10.0
   
    def _align_pairwise(
            self,
            idxA,
            idxB,
            mode = 'global'
            ):
        """
        Align all words of two languages pairwise.
        """
                
        if idxA == idxB:
            numbers = self._get_pairs(idxA,idxA,'n')
            alignments = [
                    (
                        a[0],
                        a[0],
                        self._self_score(a[0],self.score_dict)
                        )
                    for a in numbers]
        else:
            numbers = self._get_pairs(idxA,idxB,'n')
            prostrings = self._get_pairs(idxA,idxB,'p')
            restrictions = self._get_pairs(idxA,idxB,'r')
            weights = self._get_pairs(idxA,idxB,'W')

            alignments = align_sequence_pairs(
                    numbers,
                    weights,
                    restrictions,
                    prostrings,
                    self.score_dict,
                    self.gep_scale,
                    self.factor,
                    mode
                    )
        
        # change alms if mode is local
        # @todo: in order to avoid loosing information, this part should
        # eventually be changed in such a way that all the rest of sequence
        # parts in local alignments is reflected as gaps, otherwise, we can
        # simply think of using dialign instead of local analyses
        if mode == 'local':
            for i,alm in enumerate(alignments):
                almA = [k for k in alm[0] if k != '*']
                almB = [k for k in alm[1] if k != '*']
                score = alm[2]
                alignments[i] = (almA,almB,score)
        
        return alignments
    
    def _get_correspondences(
            self,
            alignments,
            idxA,
            idxB
            ):
        """
        Function returns correspondence statistics. The threshold determines
        the maximum distance between two sequences which is included in the
        overall score.
        """
        reg_dist = {}

        if idxA != idxB:
            for almA,almB,scoreAB in alignments:
                
                score = self._distance_score(almA,almB,scoreAB,self.score_dict)

                if score <= self.pairwise_threshold:
                    for a,b in zip(almA,almB):
                        try:
                            reg_dist[a,b] += 1.0
                        except KeyError:
                            reg_dist[a,b] = 1.0
        elif idxA == idxB:
            for almA,almB,scoreAB in alignments:
                
                score = self._distance_score(almA,almB,scoreAB,self.score_dict)

                if score == 0:
                    for a,b in zip(almA,almB):
                        try:
                            reg_dist[a,b] += 1.0
                        except KeyError:
                            reg_dist[a,b] = 1.0

        # change gap notation
        for a,b in list(reg_dist.keys()):
            if a == '-':
                reg_dist[str(idxA)+'.X.-',b] = reg_dist[a,b]
            elif b == '-':
                reg_dist[a,str(idxB)+'.X.-'] = reg_dist[a,b]

        return reg_dist

    def _random_align_pairwise(
            self,
            idxA,
            idxB,
            mode = 'global',
            runs = 50
            ):
        """
        Align sequences pairwise, whereas all lists are shuffled in order to
        get a random distribution of the data.
        """
        numbers = self._get_pairs(idxA,idxB,'n')
        prostrings = self._get_pairs(idxA,idxB,'p')
        restrictions = self._get_pairs(idxA,idxB,'r')
        weights = self._get_pairs(idxA,idxB,'W')
       
        rand_dist = random_align_sequence_pairs(
                numbers,
                weights,
                restrictions,
                prostrings,
                self.score_dict,
                self.gep_scale,
                self.factor,
                mode,
                runs
                )
        
        # change gap symbols in order to make them comparable to pairwise
        # notation
        for a,b in list(rand_dist.keys()):
            if a == '-':
                rand_dist[str(idxA)+'.X.-',b] = rand_dist[a,b]
            elif b == '-':
                rand_dist[a,str(idxB)+'.X.-'] = rand_dist[a,b]

        return rand_dist

    def _join_dist(
            self,
            dists
            ):
        """
        Function joins two or more distributions by averaging them.
        """
        
        if len(dists) == 1:
            return dists[0]
        
        out_dist = {}
        
        keys = []
        for dist in dists:
            keys += list(dist.keys())
        
        keys = set(keys)

        for key in keys:
            vals = []
            for dist in dists:
                try:
                    vals.append(dist[key])
                except:
                    vals.append(0.0)

            out_dist[key] = sum(vals) / len(dists)

        return out_dist

    def _expand_scorer_pairwise(
            self,
            idxA,
            idxB,
            runs = 50,
            modes = ('global','local'),
            ratio = (2,1)
            ):
        """
        Add new scores to the global scoring dictionary for the dataset. Scores
        are determined by taking the logarithm of the division of the square of
        attested and expected frequencies for each character combination.
        """
        
        # get distribution for random alignments
        expected = []
        for calc in modes:
            exp = self._random_align_pairwise(
                    idxA,
                    idxB,
                    calc,
                    runs
                    )
            expected.append(exp)
        expected = self._join_dist(expected)
        
        # get distribution for real alignments
        attested = []
        for calc in modes:
            att = self._get_correspondences(
                    self._align_pairwise(
                        idxA,
                        idxB,
                        calc
                        ),
                    idxA,
                    idxB
                    )
            attested.append(att)
        attested = self._join_dist(attested)
        
        # update the scorer
        for charA in list(self.freqs[idxA].keys())+[str(idxA)+'.X.-']:
            for charB in list(self.freqs[idxB].keys())+[str(idxB)+'.X.-']:
                try:
                    exp = expected[charA,charB]
                except KeyError:
                    exp = False
                try:
                    att = attested[charA,charB]
                except KeyError:
                    att = False
                
                # if the residue pair is only attested once in the dataset,
                # this may well be a coincidence. Therefore, the score is
                # set to 0.01, in order to avoid that possible coincidences bear to
                # much weight. note that this value eventually has to be
                # modified and further investigated
                if att <= 1:
                    att = False
                
                # if there are values for both attested and expected residue
                # pairs, the algorithm follows Kessler (2000) in so far, as the
                # values are squared in order to make them more "indicative",
                # furthermore, the binary logarithm of the division of the
                # attested and the expected values is taken in order to
                # retrieve a dictionary score
                if att and exp:
                    score = log2((att ** 2) / (exp ** 2))

                # if a residue pair is only attested and not expected (which is
                # possible, if the number of shuffled iterations is too low),
                # we simply assume that the square of the expected value is
                # 0.01. this might result in a certain bias which should be
                # kept in mind when using the algorithm
                elif att and not exp:
                    score = log2((att ** 2) / 0.01)

                # if a residue pair is only expected but not attested, this
                # certainly should result in a negative values. in order to
                # avoid problematic calculations, we simply set the value to
                # -5. this may, again result in a certain bias which should be
                # kept in mind.
                elif exp and not att:
                    score = -5.0 

                # if a residue pair is neither expected nor attested, the score
                # should surely be very low, and we simply set it to -90 in
                # order to avoid the algorithm to match such residues during
                # the alignment process.
                elif not exp and not att:
                    score = -90.0
                
                # get the scores for the regular scoring dictionary. these
                # scores are combined with the correspondence-based scoring
                # scheme in order to cope for the fact that information
                # available in small word lists might be low. the combination
                # is based on a certain ratio by which both values are
                # combined. the current default is 2 : 1, i.e. the
                # correspondence-based scoring scheme counts twice as much as
                # the regular scoring scheme of the alignment algorithm being
                # applied. in case of a gap, the regular gap score as it is
                # defined in the beginning is used to represent the regular
                # scoring function.
                if '-' not in charA+charB:
                    sim = self.score_dict[charA,charB]
                else:
                    sim = self.gop
                
                # combine the scores according to the given ratio
                self.scorer[
                        charA,
                        charB
                        ] = (ratio[0] * score + ratio[1] * sim) / sum(ratio)

    def _expand_scorer(
            self,
            runs = 50,
            modes = ('global','local'),
            ratio = (2,1)
            ):
        """
        Carry out pairwise and random alignments and calculate new scores for
        the library scorer.
        """
        for i in range(self.width):
            for j in range(self.width):
                if i <= j:
                    print("[i] Calculating scores for",self.taxa[i],"and",self.taxa[j],"...")
                    self._expand_scorer_pairwise(i,j,runs,modes,ratio)

    def _get_pairwise_scores(
            self,
            idxA,
            idxB,
            mode = 'overlap',
            scale = (1.0,1.0,1.0),
            factor = 0.0,
            gep_scale = 1.0,
            score_mode = 'library',
            gop = -2
            ):
        """
        Function calculates distance scores for pairwise alignments of the
        wordlists of two languages.
        """

        if score_mode == 'library':
            scorer = self.scorer

            # calculate alignments
            # determine weights on the basis of most probable gaps
            weights = []
            numbers = self._get_pairs(idxA,idxB,'n',True)
            for a,b in numbers:
                wA,wB = [],[]
                for n in a:
                    wA.append(self.scorer[n,str(idxB)+'.X.-'])
                for n in b:
                    wB.append(self.scorer[str(idxA)+'.X.-',n])
                weights.append((wA,wB))
            restrictions = self._get_pairs(idxA,idxB,'r',True)
            prostrings = self._get_pairs(idxA,idxB,'p',True)

            # carry out alignments
            alignments = align_sequence_pairs(
                    numbers,
                    weights,
                    restrictions,
                    prostrings,
                    self.scorer,
                    gep_scale,
                    factor,
                    mode
                    )

        # simple score_mode
        elif score_mode == 'sca':
            scorer = self.score_dict
            numbers = self._get_pairs(idxA,idxB,'n',True)
            restrictions = self._get_pairs(idxA,idxB,'r',True)
            prostrings = self._get_pairs(idxA,idxB,'p',True)
            weights = [
                    (
                        list(gop * array(prosodic_weights(
                            a,
                            scale,
                            factor
                            ))),
                        list(gop * array(prosodic_weights(
                            b,
                            scale,
                            factor
                            )))
                        ) for (a,b) in prostrings]

            alignments = align_sequence_pairs(
                    numbers,
                    weights,
                    restrictions,
                    prostrings,
                    self.score_dict,
                    gep_scale,
                    factor,
                    mode
                    )

        # turchin score-mode
        elif score_mode == 'turchin':
            for i,(a,b) in enumerate(self._pairs[idxA,idxB]):
                
                a,b = abs(a),abs(b)
                tmpA = tokens2class(
                        self.tokens[self.idxd[a]],
                        dolgo
                        ).replace('V','')
                tmpB = tokens2class(
                        self.tokens[self.idxd[b]],
                        dolgo
                        ).replace('V','')
                
                if tmpA[0:2] == tmpB[0:2]:
                    dist = 0.0
                else:
                    dist = 1.0

                self.scores[a,b] = dist

        # edit distance
        elif score_mode == 'edit-dist':
            for i,(a,b) in enumerate(self._pairs[idxA,idxB]):

                a,b = abs(a),abs(b)
                tmpA = list(self[a])
                tmpB = list(self[b])

                dist = edit_dist(tmpA,tmpB)

                self.scores[a,b] = dist
        
        elif score_mode == 'edit-tokens':
            for i,(a,b) in enumerate(self._pairs[idxA,idxB]):

                a,b = abs(a),abs(b)
                tmpA = self[a,'t']
                tmpB = self[b,'t']

                dist = edit_dist(tmpA,tmpB)

                self.scores[a,b] = dist

        # change alms if mode is local
        if mode == 'local':
            for i,alm in enumerate(alignments):
                almA = [k for k in alm[0] if k != '*']
                almB = [k for k in alm[1] if k != '*']
                score = alm[2]
                alignments[i] = (almA,almB,score)

        if score_mode in ['sca','library']:
            for i,(almA,almB,scoreAB) in enumerate(alignments):
                
                # get the pairs
                pairA,pairB = self._pairs[idxA,idxB][i]
                pairA,pairB = abs(pairA),abs(pairB)
                
                # store the alignments
                self._alignments[pairA,pairB] = [almA,almB,scoreAB]
                
                # calculate the distance
                distAB = self._distance_score(almA,almB,scoreAB,scorer)

                self.scores[pairA,pairB] = distAB

    def _get_all_pairwise_scores(
            self,
            mode = 'overlap',
            scale = (1.0,1.0,1.0),
            factor = 0.0,
            gep_scale = 1.0,
            score_mode = 'library'
            ):
        """
        Calculate all pairwise scores for the current dataset.
        """

        for i in range(self.width):
            for j in range(self.width):
                if i <= j:
                    self._get_pairwise_scores(
                            i,
                            j,
                            mode,
                            scale,
                            factor,
                            gep_scale,
                            score_mode
                            )
    def _cluster(
            self,
            idx,
            threshold = 0.5
            ):
        """
        Cluster the data in order to get unified cognate judgments throughout
        the word lists.
        """
        
        # get the flats
        flats = self._flatten(idx)
        
        # create cluster dictionary
        clusters = dict([(i,[i]) for i in range(len(flats))])


        # create the matrix
        matrix = []
        
        # fill in the matrix with the calculated distance scores
        for i,idxA in enumerate(flats):
            for j,idxB in enumerate(flats):
                if i < j:
                    try:
                        matrix.append(self.scores[idxA,idxB])
                    except:
                        matrix.append(self.scores[idxB,idxA])
        
        # turn the flat matrix into a redundant matrix
        matrix = squareform(matrix)

        # cluster the data
        _flat_upgma(clusters,matrix,threshold)
        
        # get the keys for the clusters
        count = 1
        for key in clusters:
            for val in clusters[key]:
                flats[val] = (count,flats[val])
            count += 1
        
        return flats
    
    def _get_cognates(
            self,
            threshold
            ):
        """
        Calculate possible cognates from the dataset.
        """
        
        # determine the counter
        count = 0
        
        # iterate over all semantic slots and cluster the data
        for key in self.idx:
            flats = self._cluster(key,threshold)
            
            for a,b in flats:
                self.cogs[self.idxd[b]] = a + count

            count += max([k[0] for k in flats])

    def _etym_dict(
            self,
            loans = False
            ):
        
        self.etym_dict = {}
        """
        A dictionary which contains the information regarding cognacy of a
        specified dataset in 'etymological' format, i.e. every cognate is given
        a specific ID and the words and meanings corresponding to this ID are
        listed as values.
        """

        # get all ids present in the dataset
        dict_ids = list(set([abs(i) for i in self.cogs.flatten() if i != 0]))

        # iterate over the cognates and append each word corresponding to a
        # given ID to the dictionary
        for dict_id in dict_ids:
            if dict_id != 0:
                self.etym_dict[dict_id] = [
                        ['-' for i in range(len(self.taxa))],
                        ['-' for i in range(len(self.taxa))],
                        [[] for i in range(len(self.taxa))],
                        [lng for lng in self.taxa],
                        []
                        ]
        
        for i in range(len(self.cogs)):
            for j in range(len(self.cogs[i])):
                if self.cogs[i][j] != 0:
                    tmp = abs(self.cogs[i][j])
                    if self.etym_dict[tmp][0][j] != '-':
                        self.etym_dict[tmp][0][j] += \
                            [self.words[i][j]]
                        self.etym_dict[tmp][1][j] += \
                            [self.items[i]]
                        self.etym_dict[tmp][2][j] += \
                            [self.numbers[i]]
                        self.etym_dict[tmp][4].append(self.idxs[i][j])

                    else:
                        self.etym_dict[tmp][0][j] = \
                            [self.words[i][j]]
                        self.etym_dict[tmp][1][j] = \
                            [self.items[i]]
                        self.etym_dict[tmp][2][j] = \
                            [self.numbers[i]]
                        self.etym_dict[tmp][4].append(self.idxs[i][j])

    def pairwise_distances(self):
        """
        Calculate the lexicostatistical distance between all taxa.

        Returns
        ----------
        dist_matrix : `numpy.array`
            A two-dimensional array containing the scores for the pairwise
            distances between all taxa.

        Examples
        --------
        Load the benchmark file :file:`SLV.lxs` which contains manually
        conducted cognate judgments.

        >>> from lingpy import *
        >>> lex = LexStat(get_file('SLV.lxs'))
        >>> dist = lex.pairwise_distances()
        >>> formstring = '{0[0]:.2f} {0[1]:.2f} {0[2]:.2f} {0[3]:.2f}'
        >>> for line in dist: print(formstring.format(line))
        0.00 0.15 0.18 0.17
        0.15 0.00 0.20 0.10
        0.18 0.20 0.00 0.20
        0.17 0.10 0.20 0.00

        """

        dist_matrix = []

        for i in range(len(self.taxa)):
            for j in range(len(self.taxa)):
                if i < j:
                    # iterate through both lists and store, whether two entries
                    # are the same or not, ignore gapped entries
                    temp = []
                    langA = self.cogs[:,i]
                    langB = self.cogs[:,j]
                    for key in self.idx.keys():
                        ind = self.idx[key]
                        tmp = []
                        if max(langA[ind]) > 0 and max(langB[ind]) > 0:
                            for num in langA[ind]:
                                if num > 0 and num in langB[ind]:
                                    tmp.append(1)
                                else:
                                    tmp.append(0)
                        if len(tmp) != 0:
                            temp.append(max(tmp))
                    hits = sum(temp)
                    counts = len(temp)
                    calc = 1 - float(hits) / counts
                    dist_matrix.append(calc)
        dist_matrix = squareform(dist_matrix)

        return dist_matrix

    def _make_cognate_pairs(
            self,
            loans = False
            ):
        """
        Function returns a dictionary of all word-pairs (id as key) along with
        an indicator regarding cognacy.
        """

        try:
            self._pairs
        except:
            self._set_model()
            self._set_val()
            self._make_all_pairs()

        # iterate over all word-pairs and determine the cognacy
        cognates = {}
        
        for i in range(self.width):
            for j in range(self.width):
                if i <= j:
                    for pairA,pairB in self._pairs[i,j]:
                        pairA,pairB = abs(pairA),abs(pairB)

                        if pairA != pairB:
                            cogA = self[pairA,'C']
                            cogB = self[pairB,'C']

                            if cogA == cogB and cogA > 0:
                                cognates[pairA,pairB] = 1
                            elif cogA < 0 or cogB < 0:
                                if not loans:
                                    cognates[pairA,pairB] = 0
                                else:
                                    if abs(cogA) == abs(cogB):
                                        cognates[pairA,pairB] = 1
                                    else:
                                        cognates[pairA,pairB] = 0
                            else:
                                cognates[pairA,pairB] = 0
        
        return cognates

    def analyze(
            self,
            threshold,
            score_mode = 'library',
            model = 'sca',
            merge_vowels = True,
            gop = -2,
            gep_scale = float(0.6),
            scale = (float(1.2),float(1.0),float(1.1)),
            factor = float(0.3),
            restricted_chars = 'T',
            pairwise_threshold = float(0.7),
            runs = 100,
            modes = ('global','local'),
            ratio = (1,1),
            mode = 'overlap'
            ):
        """
        Conduct automatic cognate judgments following the method of :evobib:`List2012b`.

        Parameters
        ----------
        threshold : float
            The threshold which is used for the flat cluster analysis.

        score_mode : { 'library', 'sca', 'turchin', 'edit-dist', 'edit-tokens' }
            Define the `score_mode` on which the calculation of pairwise
            distances is based. Select between:

            * 'library' -- the distance scores are based on the
              language-specific scoring schemes as described in
              :evobib:`List2012b` (this is the default),

            * 'sca' -- the distance scores are based on the
              language-independent SCA distance (see :evobib:`List2012b`),

            * 'turchin' -- the distance scores are based on the approach
              described in :evobib:`Turchin2010`,

            * 'edit-dist"' -- the distance scores are based on the normalized
              edit distance (:evobib:`Levenshtein1966`), and

            * 'edit-tokens' -- the distance scores are based on the normalized
              edit distance, yet the scores are derived from the tokenized
              representation of the sequences and not from their raw,
              untokenized form.

        model : string (default="sca")
            A string indicating the name of the
            :py:class:`~lingpy.data.model.Model` object that shall be used
            for the analysis.
            Currently, three models are supported:
            
            * "dolgo" -- a sound-class model based on :evobib:`Dolgopolsky1986`,

            * "sca" -- an extension of the "dolgo" sound-class model based on
              :evobib:`List2012a`, and
            
            * "asjp" -- an independent sound-class model which is based on the
              sound-class model of :evobib:`Brown2008` and the empirical data of
              :evobib:`Brown2011`.

        merge_vowels : bool (default=True)
            Indicate, whether neighboring vowels should be merged into
            diphtongs, or whether they should be kept separated during the
            analysis.

        gop : int (default=-5)
            The gap opening penalty (gop) on which the analysis shall be based.

        gep_scale : float (default=0.6)
            The factor by which the penalty for the extension of gaps (gap
            extension penalty, GEP) shall be decreased. This approach is
            essentially inspired by the extension of the basic alignment
            algorithm for affine gap penalties by :evobib:`Gotoh1982`.

        scale : tuple or list (default=(3,1,2))
            The scaling factors for the modificaton of gap weights. The first
            value corresponds to sites of ascending sonority, the second value
            to sites of maximum sonority, and the third value corresponds to
            sites of decreasing sonority.

        factor : float (default=0.3)
            The factor by which the initial and the descending position shall
            be modified.
       
        restricted_chars : string (default="T")
            Define which characters of the prosodic string of a sequence
            reflect its secondary structure (cf. :evobib:`List2012a`) and should
            therefore be aligned specifically. This defaults to "T", since this
            is the character that represents tones in the prosodic strings of
            sequences.

        pairwise_threshold : float (default=0.7)
            Only those sequence pairs whose distance is beyond this threshold
            will be considered when determining the distribution of attested
            segment pairs.

        runs : int (default=100)
            Define how many times the perturbation method shall be carried out
            in order to retrieve the expected distribution of segment pairs.

        modes : tuple or list (default = ("global","local"))
            Define the alignment modes of the pairwise analyses which are
            carried out in order to create the language-specific scoring scheme.

        ratio : tuple (default=(1,1))
            Define the ratio by which the traditional scoring scheme and the
            correspondence-based scoring scheme contribute to the actual
            library-based scoring scheme. 

        mode : string (default = "overlap")
            Define the alignment mode which is used in order to calculate
            pairwise distance scores from the language-specific scoring
            schemes.

        """
        
        # in order to save time, the values for a given calculation are dumped
        # into a binary file and loaded, if the calculation already has been
        # carried out before
        vals = {
                'model':model,
                'merge_vowels':str(merge_vowels),
                'scale':'-'.join([str(k) for k in scale]),
                'factor':str(factor),
                'gop':str(gop),
                'restricted_chars':restricted_chars,
                'gep_scale':str(gep_scale),
                'modes':'-'.join([str(m) for m in modes]),
                'ratio':str(ratio[0])+'-'+str(ratio[1]),
                'pairwise_threshold':str(pairwise_threshold),
                'runs':str(runs)
                }
     
        val_string = self.infile + '_' + '_'.join(
                [k for k in sorted(vals.values()) if k not in "[]()'"]
                )

        self._set_model(model,merge_vowels)
        self._set_val(
                scale,
                factor,
                gop,
                gep_scale,
                restricted_chars,
                pairwise_threshold
                )
        self._make_all_pairs()
        print("[i] Loaded and calculated all essential values.")
        if score_mode == 'library':
            try:
                self.scorer = load(open(val_string+'.bin','rb'))
            except:
                self._expand_scorer(
                        runs,
                        modes,
                        ratio
                        )
                dump(self.scorer,open(val_string+'.bin','wb'))
        print("[i] Created the library.")
        self._get_all_pairwise_scores(mode,score_mode=score_mode)
        print("[i] Calculated pairwise scores.")
        self._get_cognates(threshold)
        print("[i] Calculated cognates.")
        self._etym_dict()

    def output(
            self,
            fileformat = 'lxs',
            filename = None
            ):
        """
        Write the data to file.

        Parameters
        ----------
        fileformat : { 'lxs', 'star', 'psa', 'msa', 'alm', 'dst' }
            Indicate which data should be written to a file. Select between:

            * 'lxs' -- output in ``lxs``-format,
            * 'star' -- output in ``star``-format (one separate file for each language),
            * 'psa' -- output of all pairwise alignments in ``psa``-format,
            * 'msa' -- output of all cognate sets in separate files in
              ``msa``-format, 
            * 'alm' -- output of all cognate sets in one file in ``alm``-format
              (all data with presumed cognates in aligned format), or
            * 'dst' -- the distance matrix in ``dst``-format (input format for
              distance analyses in the Phylip software package (see
              http://evolution.genetics.washington.edu/phylip/).
        
        filename : str
            Select a specific name for the outfile, otherwise, the name of
            the infile will be taken by default.
        
        """
        # check, if filename is chose as an option
        if not filename:
            filename = self.infile

        outfile = filename + '.' + fileformat

        # check whether outfile already exists
        try:
            tmp = open(outfile)
            tmp.close()
            outfile = filename + '_out.' + fileformat
        except:
            pass

        if fileformat == 'lxs':
            out = open(outfile,'w')
            try:
                self.cogs
                cognates = True
            except:
                cognates = False
            try:
                self.items
                headwords = True
            except:
                headwords = False
            
            if headwords == True:
                if cognates == True:
                    out.write('ID\tWords\t'+'\tCOG\t'.join(self.taxa)+'\tCOG\n')
                    for i in range(len(self.cogs)):
                        out.write(str(self.numbers[i])+'\t'+self.items[i])
                        for j in range(len(self.taxa)):
                            out.write('\t'+self.words[i][j])
                            out.write('\t'+str(self.cogs[i][j]))
                        out.write('\n')
                    out.close()
                elif cognates == False:
                    out.write('ID\tWords\t'+'\t'.join(self.taxa)+'\n')
                    for i in range(len(self.cogs)):
                        out.write(str(self.numbers[i])+'\t'+self.items[i])
                        for j in range(len(self.taxa)):
                            out.write('\t'+self.wordss[i][j])
                        out.write('\n')
                    out.close()
            elif headwords == False:
                if cognates == True:
                    out.write('ID\t'+'\tCOG\t'.join(self.taxa)+'\tCOG\n')
                    for i in range(len(self.cogs)):
                        out.write(str(self.numbers[i]))
                        for j in range(len(self.langs)):
                            out.write('\t'+self.words[i][j])
                            out.write('\t'+str(self.cogs[i][j]))
                        out.write('\n')
                    out.close()
                elif cognates == False:
                    out.write('ID\t'+'\t'.join(self.taxa)+'\n')
                    for i in range(len(self.cogs)):
                        out.write(str(self.numbers[i]))
                        for j in range(len(self.taxa)):
                            out.write('\t'+self.words[i][j])
                        out.write('\n')
                    out.close()

        if fileformat == 'star':
            # output the star-files, which can easily be converted into a
            # lexicostatistical list with given cognate judgments (or not)
            try:
                os.mkdir(self.infile+'_star')
                dest = self.infile+'_star/'
            except:
                pass
            for i,lang in enumerate(self.taxa):
                try:
                    out = open(dest+lang+'.star','w')
                except:
                    out = open(lang+'.star','w')
                for j,word in enumerate(self.words[:,i]):
                    try:
                        cog = str(self.cogs[j,i])
                    except:
                        cog = ''
                    wrd = self.items[j]
                    num = str(self.numbers[j])
                    if word != '-':
                        out.write('\t'.join([num,'---',word,cog])+'\n')
                out.close()

        if fileformat == 'psa':
            # output all pairwise alignments along with the explicit scores of
            # the pairs
            out = open(outfile,'w')
            out.write(self.infile+'\n')
            for i in range(self.width):
                for j in range(self.width):
                    if i < j:

                        for pairA,pairB in self._pairs[i,j]:

                            # mind that the pairs should be the absolute values
                            pairA,pairB = abs(pairA),abs(pairB)

                            # get the alignment
                            almA,almB,scoreAB = self._alignments[pairA,pairB]
                            
                            # get the tokens
                            tokenA = self.tokens[self.idxd[pairA]]
                            tokenB = self.tokens[self.idxd[pairB]]

                            # turn the alignments into ipa strings
                            outA = class2tokens(tokenA,almA)
                            outB = class2tokens(tokenB,almB)

                            # turn all gaps into gap strings in the input data
                            for k,(a,b) in enumerate(zip(almA,almB)):
                                if a == '-':
                                    almA[k] = str(i)+'.X.-'
                                if b == '-':
                                    almB[k] = str(j)+'.X.-'

                            # create a string containing all scores averaged to
                            # round(number,0)
                            scores = [
                                    str(
                                        round(self.scorer[a,b])
                                        ) for a,b in zip(
                                            almA,
                                            almB
                                            )]
                            
                            # get the item
                            item = self[pairA,'i']

                            # get the distance
                            dist = str(self.scores[pairA,pairB])
                            score = str(round(scoreAB))
                            
                            # get the taxa
                            taxA = self._txf.format(self.taxa[i])
                            taxB = self._txf.format(self.taxa[j])

                            # write the data to file
                            out.write(item+'\n')
                            out.write(taxA+'\t'+'\t'.join(outA).encode('utf-8')+'\n')
                            out.write(taxB+'\t'+'\t'.join(outB).encode('utf-8')+'\n')
                            out.write('#'+'\t'+'\t'.join(scores)+'\t'+score+'\n'+dist+'\n\n')
            out.close()

        if fileformat == 'msa':
            try:
                os.mkdir(self.infile+'_msa')
                dest = self.infile+'_msa/'
            except:
                dest = self.infile+'_msa/'

            for key,val in self.etym_dict.items():
                cog = key
                entries = [self[i] for i in val[4]]
                taxa = [self[i,'l'] for i in val[4]]
                item = self[val[4][0],'i']

                if len(taxa) > 1:
                    mult = _Multiple(entries)
                    mult.lib_align(pprint=False)
                    
                    out = open(dest+self.infile+'_'+str(cog)+'.msa','w')
                    out.write(self.infile+'\n')
                    out.write(item+'\n')
                    for i,alm in enumerate(mult.alm_matrix):
                        out.write(self._txf.format(taxa[i])+'\t')
                        out.write('\t'.join(alm).encode('utf-8')+'\n')
                    out.close()
            
        if fileformat == 'alm':

            out = open(outfile,'w')
            out.write(self.infile+'\n')

            outstring = '{0}\t{1}\t{2}\t{3}\t{4}\n'
            
            # define a previous item for item tracking
            previous_number = 0

            for key,val in sorted(self.etym_dict.items(),key=lambda x:x[0]):
                cog = key
                entries = [self[i] for i in val[4]]
                taxa = [self[i,'l'] for i in val[4]]
                item = self[val[4][0],'i']
                number = self[val[4][0],'N']

                if len(taxa) > 1:
                    mult = _Multiple(entries)
                    mult.lib_align()
                    
                    # redefine previous_number for item tracking
                    if number == previous_number:
                        pass
                    else:
                        previous_number = number
                        out.write('\n')
                    
                    for i,alm in enumerate(mult.alm_matrix):
                        out.write(
                                outstring.format(
                                    key,
                                    self._txf.format(taxa[i]),
                                    item,
                                    number,
                                    '\t'.join(alm).encode('utf-8')
                                    )
                                )
                else:
                    if number == previous_number:
                        pass
                    else:
                        previous_number = number
                        out.write('\n')
                    out.write(
                            outstring.format(
                                key,
                                self._txf.format(taxa[0]),
                                item,
                                number,
                                entries[0],
                                '--'
                                )
                            )
            out.close()
        
        if fileformat == 'dst':

            out = open(outfile,'w')

            try:
                dist_matrix = self.pairwise_distances()
            except:
                print("[!] You should conduct cognate judgments first!")
                return

            out.write(' {0}\n'.format(self.width))
            
            for i,taxA in enumerate(self.taxa):
                out.write('{0:<10}'.format(taxA))
                for j,taxB in enumerate(self.taxa):
                    out.write(' {0:.2f}'.format(dist_matrix[i][j]))
                out.write('\n')

            out.close()
