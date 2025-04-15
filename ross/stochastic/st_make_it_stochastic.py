"""Distributions module.

This module defines the Distributions class and defines
the distribution of each random parameter.
"""

import numpy as np
import scipy as sp

from st_bearing_seal_element import ST_BearingElement2
from st_distributions import ST_Distribution

from ross.units import check_units

class ST_Make_it_Stochastic():
    """Convert an deterministic object to stochastic.

    Class used to turn an deterministic object of the rotor into stochastic.

    Parameters
    ----------
    name : str, list
        Distribution type.
    info : float, list
        The information needed to built the Distribution.
    param : str, list, pint.Quantity
        The random parameter or a list of random parameters.
    

    Examples
    --------
    >>> # Steel with random Young's modulus.
    >>> from st_distributions import ST_Distribution 
    >>> import numpy as np
    >>> E = np.random.uniform(208e9, 211e9, 5)
    >>> dist_E = ST_Distribution(name="Normal", info=[208e9, 211e9], param="E")
    >>> dist_E.value(1)
    array([6.32013755e+10])
    """

    @check_units
    def __init__(
        self, rotor, element, params, distribution = Normal ,erro = 5/100, **kwargs
    ):
        self.rotor = rotor
        self.element = element
        if " " in element:
            raise ValueError("Spaces are not allowed in Element name")
        self.params = params
        self.distribution = str(distribution)
        self.erro = erro
        
        attribute_dict = dict(
            rotor=rotor
            element=element,
            params=params,
            distribution = distribution,
            erro=erro,
        )
        self.attribute_dict = attribute_dict
              
    def values(self):

        valueslist =[]
        if len(element) == 1: 
            values = np.zeros((len(self.rotor.element),len(params)))
            for i in range(len(self.rotor.element)):
                for j in range(len(params)):
                    values[i][j] = self.rotor.element.params[j][0]

            valueslist.append(values)

        else:
            for z in range(len(element)):
                values = np.zeros((len(self.rotor.element[z]),len(params[z])))
                for i in range(len(self.rotor.element[z])):
                    for j in range(len(params[z])):
                        values[i][j] = self.rotor.element[z].params[z][j][0]   

                valueslist.append(values)   

        return valueslist   

    def limits(self):
        """Evaluate an array with random values of the PDF.

        Parameters
        ----------
        size : int
            The size of the array with random values.
        """

        if self.distribution == "Normal":
            std = 

                
        elif self.distribution == "Uniform":
            Dist = sp.stats.uniform(loc = self.info[0], scale=self.info[1]-self.info[0])
            val = Dist.rvs(size)[0:size]

                
        else:
            raise KeyError("Wrong Name: "+self.distribution+".")

        return val