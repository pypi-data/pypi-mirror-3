"""
The Module provides different functions for the transformation of text data into a
visually appealing format.

The main idea is to render alignments in colored tables where the colors of
the cells are chosen with respect to the sound-class of the sound value of each
given cell, such as in the following example: 

.. image:: colored_alignment.jpg
   :width: 600px
   
Here, the coloring of sounds follows the sound-class model of
:evobib:`Dolgopolsky1986`, the black margin around the cells in the second, the
third, and the fourth column indicates a swapped site.  The benefit of this way
to display alignments is that differences and similarities between the
sequences become visible at once, making it easy to check the correctness of a
given alignment analysis.

"""
import os
from ..data import *
from ..data import _color
from .color import colorRange
from ..compare import Multiple
from ..compare import Pairwise

def alm2html(
        infile,
        title = None,
        shorttitle = None
        ):
    """
    Convert files in ``alm``-format into colored ``html``-format.

    Parameters
    ----------

    title : str
        Define the title of the output file. If no title is provided, the
        default title ``LexStat - Automatic Cognate Judgments`` will be used.

    shorttitle : str
        Define the shorttitle of the ``html``-page. If no title is provided,
        the default title ``LexStat`` will be used.
    
    Notes
    -----
    The coloring of sound segments with respect to the sound class they belong
    to is based on the definitions given in the
    ``color`` :py:class:`~lingpy.data.model.Model`. It can easily be changed
    and adapted. 

    See also
    --------
    lingpy.output.plot.msa2html

    """
    # get the path to the templates
    path = os.path.split(os.path.abspath(__file__))[0] + '/templates/'
    
    # open the infile
    try:
        data = open(infile).read()[:-1]
    except:
        data = open(infile+'.alm').read()[:-1]

    # create the outfile
    outfile = infile.strip('.alm')+'.html'

    # check, whether the outfile already exists
    try:
        open(outfile).close()
        outfile = outfile.replace('.html','_out.html')
    except:
        pass
    
    # read in the templates
    html = open(path+'alm2html.html').read()
    table = open(path+'alm2html.table.html').read()

    # split the data into blocks
    blocks = data.split('\n\n')

    # retrieve the dataset
    dataset = blocks[0]

    # iterate over the rest of the blocks and store the data in a dictionary
    cogs = {}
    
    # create the outstring
    tmp_str = ''

    for block in blocks[1:]:
        lines = block.split('\n')
        
        m = []
        for l in lines:
            m.append(l.split('\t'))
        
        # create colordict for different colors
        dc = len(set([l[0] for l in m]))
        
        colors = dict([(a,b) for a,b in zip(
            sorted(set([int(l[0]) for l in m])),
            colorRange(
                dc,
                brightness = 400
                ),
            )])
        
        # get the basic item and its id
        iName = m[0][2]
        iID = m[0][3]

        # start writing the stuff to string
        tmp_str += table.format(
                NAME=iName,
                ID = iID)
        # define the basic string for the insertion
        bas = '<tr bgcolor="{0}">\n{1}\n</tr>'
        for l in m:
            # assign the cognate id
            tmp = '<td>{0}</td>\n'.format(l[0])
            tmp += '<td bgcolor=white> </td>\n'
            tmp += '<td>{0}</td>\n'.format(l[1].strip('.'))
            tmp += '<td bgcolor=white> </td>\n'
            tmp += '<td>{0}</td>\n'.format(''.join(l[4:]).replace('-',''))
            tmp += '<td bgcolor=white> </td>\n'
            tmp += '<td bgcolor=white><table bgcolor=white>\n<tr>\n{0}\n</tr>\n</table>\n'
            if len(l[4:]) > 1:
                alm = ''
                for char in l[4:]:
                    char = str(char)
                    try:
                        c = _color[char]
                    except:
                        c = _color[char[0]]
                    alm += '<td width="30px" align="center"'
                    alm += 'bgcolor="{0}"><font color="white"><b>{1}</b></font></td>'.format(c,char)
            else:
                alm = '<td bgcolor="white">{0}'.format('--')

            tmp = tmp.format(alm)
            tmp += '<tr><td></td></tr>\n'
            tmp_str += bas.format(
                    colors[int(l[0])],
                    tmp)
    if not title:
        title = "LexStat - Automatic Cognate Judgments"
    if not shorttitle:
        shorttitle = "LexStat"

    html = html.format(
            shorttitle = shorttitle,
            title = title,
            table = tmp_str,
            dataset = dataset
            )

    out = open(outfile,'w')
    out.write(html)
    out.close()

def msa2html(
        infile,
        shorttitle = None,
        filename = None
        ):
    """
    Convert files in ``msa``-format into colored ``html``-format.

    Parameters
    ----------

    shorttitle : str
        Define the shorttitle of the ``html``-page. If no title is provided,
        the default title ``LexStat`` will be used.

    filename : str
        Define the name of the output file. If no name is defined, the name of
        the input file will be taken as a default.

    Examples
    --------
    Load the libary.

    >>> from lingpy import *
    
    Load an ``msq``-file from the test-sets.

    >>> msa = Multiple(get_file('test.msq'))

    Align the data progressively and carry out a check for swapped sites.

    >>> msa.prog_align()
    >>> msa.swap_check()
    >>> print(msa)
    w    o    l    -    d    e    m    o    r    t
    w    a    l    -    d    e    m    a    r    -
    v    -    l    a    d    i    m    i    r    -

    Save the data to the file ``test.msa``.

    >>> msa.output('msa')

    Convert the ``msa``-file to ``html``.

    >>> msa2html('test.msa')
    
    Notes
    -----
    The coloring of sound segments with respect to the sound class they belong
    to is based on the definitions given in the
    ``color`` :py:class:`~lingpy.data.model.Model`. It can easily be changed
    and adapted. 

    See also
    --------
    lingpy.output.plot.alm2html
    """
    
    # while alm-format can be read from the text-file without problems,
    # msa-format should be loaded first (once this is already provided), the
    # loss in speed won't matter much, since output of data is not a daily task
    
    # get the path to the templates
    path = os.path.split(os.path.abspath(__file__))[0] + '/templates/'

    # load msa
    msa = Multiple(infile)

    # load templates
    html = open(path+'msa2html.html').read()

    # load dataset, etc.
    dataset = msa.dataset
    pid_score = int(100 * msa.get_pid() + 0.5)
    infile = msa.infile
    seq_id = msa.seq_id

    # define the titles etc.
    if not shorttitle:
        shorttitle = 'SCA'
    
    # determine the length of the longest taxon
    taxl = max([len(t) for t in msa.taxa])

    out = ''
    tr = '<tr class="msa">\n{0}\n</tr>'
    td_taxon = '<td class="taxon" width="'+str(15 * taxl)+'">{0}</td>\n'
    perc = int(80 / len(msa.alm_matrix[0]) + 0.5)
    td_residue = '<td class="residue" width="50" align="center" bgcolor="{1}">{0}</td>\n'
    td_swap = '<td class="residue swap" style="border:solid 3px black" width="50" align="center" bgcolor="{1}">{0}</td>\n'
    
    # check for swaps in the alignment
    if hasattr(msa,'swap_index'):
        swaps = []
        for s in msa.swap_index:
            swaps.extend(s)
    else:
        swaps = []

    # start iteration
    for i,taxon in enumerate(msa.taxa):
        tmp = ''
        tmp += td_taxon.format(taxon)
        for j,char in enumerate(msa.alm_matrix[i]):
            try:
                c = _color[char]
            except:
                try:
                    c = _color[char[0]]
                except:
                    print(char)
                    input()            
            if j in swaps:
                tmp += td_swap.format(char,c)
            else:
                tmp += td_residue.format(char,c)
        out += tr.format(tmp)
    html = html.format(
            table = out,
            dataset = dataset,
            pid = pid_score,
            file = infile,
            sequence = seq_id,
            shorttitle = shorttitle,
            width=len(msa.alm_matrix[0]),
            table_width='{0}'.format(len(msa.alm_matrix[0])* 50 + 15 * taxl),
            taxa = len(msa.alm_matrix),
            uniseqs=len(msa.uniseqs)
            )
    
    
    if not filename:
        outfile = msa.infile + '.html'
    else:
        outfile = filename + '.html'

    # check, whether the outfile already exists
    try:
        open(outfile).close()
        outfile = outfile.replace('.html','_out.html')
    except:
        pass

    out = open(outfile,'w')
    out.write(html)
    out.close()

