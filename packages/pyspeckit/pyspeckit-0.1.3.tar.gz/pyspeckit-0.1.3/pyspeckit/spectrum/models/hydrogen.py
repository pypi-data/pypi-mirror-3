"""
Hydrogen Models
---------------

Hydrogen in HII regions is typically assumed to follow Case B recombination
theory.

The values for the Case B recombination coefficients are given by [Hummer & Storey 1987].  
They are also computed in [Hummer 1994] and tabulated at [a wiki]

.. [Hummer & Storey 1987] `Recombination-line intensities for hydrogenic ions.
    I - Case B calculations for H I and He II
    <http://adsabs.harvard.edu/cgi-bin/nph-bib_query?bibcode=1987MNRAS.224..801H&db_key=AST>`_

.. [Hummer 1994] `<http://adsabs.harvard.edu/abs/1994MNRAS.268..109H>`_

.. [a wiki] `<http://wiki.hmet.net/index.php/HII_Case_B_Recombination_Coefficients>`_

"""

# log(temperature), alphaBalphaB = [[1.0,9.283],
alphaB=[[1.2,8.823],
    [1.4,8.361],
    [1.6,7.898],
    [1.8,7.435],
    [2.0,6.973],
    [2.2,6.512],
    [2.4,6.054],
    [2.6,5.599],
    [2.8,5.147],
    [3.0,4.700],
    [3.2,4.258],
    [3.4,3.823],
    [3.6,3.397],
    [3.8,2.983],
    [4.0,2.584],
    [4.2,2.204],
    [4.4,1.847],
    [4.6,1.520],
    [4.8,1.226],
    [5.0,0.9696],
    [5.2,0.7514],
    [5.4,0.5710],
    [5.6,0.4257],
    [5.8,0.3117],
    [6.0,0.2244],
    [6.2,0.1590],
    [6.4,0.1110],
    [6.6,0.07642],
    [6.8,0.05199],
    [7.0,0.03498]]

# beta is 946 / H 03b2 / oct 1662


# the command to make this:
# %s/\v.*\n?([0-9]\.[0-9]+).*jH(.+\n?|[^β]\n?[0-9]\.[0-9]+) ?([0-9]\.[0-9]+) ([0-9]\.[0-9]+) ([0-9]\.[0-9]+)/[\1, \3, \4, \5]\r/ 
# from this:
# http://www.scribd.com/doc/70881169/Physics-of-the-Interstellar-and-Intergalactic-Medium
# with some by-hand editing too

# Table 14.2 in Draine 2001

#Balmer-line intensities relative to Hβ 0.48627 µm
balmer = [["a" ,0.65646, 3.03, 2.86, 2.74],
          ["b" ,0.48627, 1., 1., 1.,],
          ["g" ,0.43418, 0.459, 0.469, 0.475],
          ["d" ,0.41030, 0.252, 0.259, 0.264],
          ["e" ,0.39713, 0.154, 0.159, 0.163],
          ["8" ,0.102, 0.105, 0.106],
          ["9" ,0.102, 0.0711, 0.0732, 0.0746],
          ["10",0.37990, 0.0517, 0.0531, 0.0540]]

#Paschen (n→3) line intensities relative to corresponding Balmer lines
paschen = [["a", 1.8756, 0.405, 0.336, 0.283],
           ["b", 1.2821, 0.399, 0.347, 0.305],
           ["g", 1.0941, 0.391, 0.348, 0.311],
           ["d", 1.0052, 0.386, 0.348, 0.314],
           ["e", 0.95487, 0.382, 0.348, 0.316],
           ["9", 0.92317, 0.380, 0.347, 0.317],
           ["10",0.90175, 0.380, 0.347, 0.317]]


#Brackett (n→4) line intensities relative to corresponding Balmer lines
brackett = [["a", 4.0523, 0.223, 0.169, 0.131],
            ["b", 2.6259, 0.219, 0.174, 0.141],
            ["g", 2.1661, 0.212, 0.174, 0.144],
            ["d", 1.9451, 0.208, 0.173, 0.145],
            ["e", 1.8179, 0.204, 0.173, 0.146],
            ["10",1.7367, 0.202, 0.172, 0.146]]

#Pfundt (n→5) line intensities relative to corresponding Balmer lines
pfundt = [["6", 7.4599, 0.134, 0.0969, 0.0719],
          ["7", 4.6538, 0.134, 0.101, 0.0774] ,
          ["8", 3.7406, 0.130, 0.101, 0.0790] ,
          ["9", 3.2970, 0.127, 0.100, 0.0797] ,
          ["10",3.0392, 0.125, 0.0997, 0.0801]]

#Humphreys (n→6) line intensities relative to corresponding Balmer lines
humphreys = [["7", 2.372, 0.0855, 0.0601, 0.0435],
             ["8", 7.5026, 0.0867, 0.0632, 0.0471],
             ["9", 5.9083, 0.0850, 0.0634, 0.0481],
             ["10",5.1287, 0.0833, 0.0632, 0.0486]]


def rrl(n,dn=1,amu=1.007825):   
    """compute Radio Recomb Line feqs in GHz
     from Brown, Lockman & Knapp ARAA 1978 16 445"""
    nu = 3.289842e6*(1-5.48593e-4/amu)*(1/float(n)**2 - 1/float(n+dn)**2)
    return nu

