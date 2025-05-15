"""Make it stochastic module.

This module convert an deterministic rotor to stochastic rotor.
"""

import numpy as np
import scipy as sp

from st_bearing_seal_element import ST_BearingElement2
from st_distributions import ST_Distribution
from st_rotor_assembly import ST_Rotor2

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
    
    """

    @check_units
    def __init__(
        self, rotor, elements, params, distribution = 'Normal' ,erro = 5/100, **kwargs
    ):
        self.rotor = rotor
        self.elements = elements
        if " " in elements:
            raise ValueError("Spaces are not allowed in Element name")
        self.params = params
        self.distribution = distribution
        self.erro = erro
        
        attribute_dict = dict(
            rotor=rotor
            elements=elements,
            params=params,
            distribution = distribution,
            erro=erro,
        )
        self.attribute_dict = attribute_dict


    def pickvalues(self):
        """Evaluate an array with values of parameters.

        """

        valueslist =[]
        if len(self.elements) == 1:
            attr = getattr(self.rotor, self.elements[0])
            values = np.zeros((len(attr),len(self.params[0])))
            for i in range(len(attr)):
                for j in range(len(self.params[0])):
                    attr2 = getattr(attr[i], self.params[0][j])
                    values[i][j] = attr2[0]

            valueslist.append(values)

        else:
            for z in range(len(self.elements)):
                attr = getattr(self.rotor, self.elements[z])
                values = np.zeros((len(attr),len(self.params[z])))
                for i in range(len(attr)):
                    for j in range(len(self.params[z])):
                        attr2 = getattr(attr[i], self.params[z][j])
                        values[i][j] = attr2[0]   

                valueslist.append(values)   

        return valueslist   
   

    def limits(self):
        """Build the distributions.

        """

        if self.distribution == "Normal":
            distributions =[]
            values = self.pickvalues()
            for z in range(len(self.elements)):
                attr = getattr(rotor1, self.elements[z])
                for i in range(len(attr)):
                    for j in range(len(self.params[z])):
                        std = values[z][i][j] * self.erro/2

                        distributions.append(ST_Distribution(name = self.distribution, 
                                                             info =[values[z][i][j],std],
                                                             param = self.params[z][j]))

                
        elif self.distribution == "Uniform":
            distributions =[]
            values = self.pickvalues()
            for z in range(len(self.elements)):
                attr = getattr(rotor1, self.elements[z])
                for i in range(len(attr)):
                    for j in range(len(self.params[z])):
                        limsup = values[z][i][j] *(1 + self.erro)
                        liminf = values[z][i][j] *(1 - self.erro)

                        distributions.append(ST_Distribution(name = self.distribution, 
                                                             info =[liminf,limsup-liminf],
                                                             param = self.params[z][j]))

                
        else:
            raise KeyError("Wrong Name: "+self.distribution+".")

        return distributions