"""
===============
Gaussian Fitter
===============

The simplest and most useful model.

Until 12/23/2011, gaussian fitting used the complicated and somewhat bloated
gaussfitter.py code.  Now, this is a great example of how to make your own
model!  Just make a function like gaussian and plug it into the SpectralModel
class.

"""
import model
import numpy 

def gaussian(x,A,dx,w, return_components=False):
    """
    Returns a 1-dimensional gaussian of form
    H+A*numpy.exp(-(x-dx)**2/(2*w**2))
    
    [height,amplitude,center,width]

    return_components does nothing but is required by all fitters
    
    """
    x = numpy.array(x) # make sure xarr is no longer a spectroscopic axis
    return A*numpy.exp(-(x-dx)**2/(2.0*w**2))

def gaussian_fitter(multisingle='multi'):
    """
    Generator for Gaussian fitter class
    """

    myclass =  model.SpectralModel(gaussian, 3,
            parnames=['amplitude','shift','width'], 
            parlimited=[(False,False),(False,False),(True,False)], 
            parlimits=[(0,0), (0,0), (0,0)],
            shortvarnames=('A',r'\Delta x',r'\sigma'),
            multisingle=multisingle,
            )
    myclass.__name__ = "gaussian"
    
    return myclass
