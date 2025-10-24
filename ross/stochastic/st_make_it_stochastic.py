"""Make it stochastic module.

This module convert an deterministic rotor to stochastic rotor.
"""

import numpy as np
import scipy as sp
import copy as cp
import numbers

from ross.rotor_assembly import Rotor
from ross.materials import Material
from ross.bearing_seal_element import BearingElement
from ross.shaft_element import ShaftElement
from ross.disk_element import DiskElement
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
        self, rotor, elements, params, distribution = 'Normal',erro = 5/100, **kwargs
    ):
        self.rotor = rotor
        self.elements = elements
        if " " in elements:
            raise ValueError("Spaces are not allowed in Element name")
        self.params = params
        self.distribution = distribution
        self.erro = erro
        
        attribute_dict = dict(
            rotor=rotor,
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
                if self.elements[z] == 'shaft_materials':
                    attr = getattr(self.rotor, 'shaft_elements')
                    values = np.zeros((len(attr),len(self.params[z])))
                    for i in range(len(attr)):
                        for j in range(len(self.params[z])):
                            attr2 = getattr(attr[i], 'material')
                            attr3 = getattr(attr2, self.params[z][j])
                            values[i][j] = attr3

                else:
                    attr = getattr(self.rotor, self.elements[z])
                    values = np.zeros((len(attr),len(self.params[z])))
                    for i in range(len(attr)):
                        for j in range(len(self.params[z])):
                            attr2 = getattr(attr[i], self.params[z][j])
                            if isinstance(attr2, list):
                                values[i][j] = attr2[0]   
                            if isinstance(attr2, numbers.Number):
                                values[i][j] = attr2

                valueslist.append(values) 

            '''
            for z in range(len(self.elements)):
                attr = getattr(self.rotor, self.elements[z])
                values = np.zeros((len(attr),len(self.params[z])))
                for i in range(len(attr)):
                    for j in range(len(self.params[z])):
                        attr2 = getattr(attr[i], self.params[z][j])
                        values[i][j] = attr2[0]   

                valueslist.append(values)   
            '''
        return valueslist   
   

    def limits(self):
        """Build the distributions.

        """

        if self.distribution == "Normal":
            distributions =[]
            values = self.pickvalues()
            for z in range(len(self.elements)):
                if self.elements[z] != 'shaft_materials':
                    listdist=[]            
                    attr = getattr(self.rotor, self.elements[z])
                    for i in range(len(attr)):
                        for j in range(len(self.params[z])):
                            std = values[z][i][j] * self.erro/2

                            listdist.append(ST_Distribution(name = self.distribution, 
                                                                info =[values[z][i][j],std],
                                                                param = self.params[z][j]))
                    distributions.append(listdist)

                else:
                    listdist=[]
                    attr = getattr(self.rotor, 'shaft_elements')
                    for i in range(len(attr)):
                        for j in range(len(self.params[z])):
                            std = values[z][i][j] * self.erro/2

                            listdist.append(ST_Distribution(name = self.distribution, 
                                                                info =[values[z][i][j],std],
                                                                param = self.params[z][j]))
                    distributions.append(listdist)
                
        elif self.distribution == "Uniform":
            distributions =[]
            values = self.pickvalues()
            for z in range(len(self.elements)):
                if self.elements[z] != 'shaft_materials':
                    listdist =[]
                    attr = getattr(self.rotor, self.elements[z])
                    for i in range(len(attr)):
                        for j in range(len(self.params[z])):
                            limsup = values[z][i][j] *(1 + self.erro)
                            liminf = values[z][i][j] *(1 - self.erro)

                            listdist.append(ST_Distribution(name = self.distribution, 
                                                                info =[liminf,limsup-liminf],
                                                                param = self.params[z][j]))
                    distributions.append(listdist)
                else:
                    listdist=[]
                    attr = getattr(self.rotor, 'shaft_elements') 
                    for i in range(len(attr)):
                        for j in range(len(self.params[z])):
                            limsup = values[z][i][j] *(1 + self.erro)
                            liminf = values[z][i][j] *(1 - self.erro)

                            listdist.append(ST_Distribution(name = self.distribution, 
                                                                info =[liminf,limsup-liminf],
                                                                param = self.params[z][j]))
                    distributions.append(listdist)
                
        else:
            raise KeyError("Wrong Name: "+self.distribution+".")

        return distributions
    
    
    def switch_rotor_values(self):
        ''' Modifing the chosen values of the rotor.
         
        '''
        
        distributions = self.limits()

        shaft = cp.deepcopy(self.rotor.shaft_elements)
        disks = cp.deepcopy(self.rotor.disk_elements)
        bearings = cp.deepcopy(self.rotor.bearing_elements)

        modified_rotor = Rotor(shaft, disks, bearings)
        
        for idk,k in enumerate(self.elements):
            if k=='bearing_elements':
                for i in range(len(modified_rotor.bearing_elements)):
                    for idj,j in enumerate(self.params[idk]):
                        try:
                            setattr(modified_rotor.bearing_elements[i], j, distributions[idk][idj].value(1))
                        except:
                            raise KeyError("Wrong Name: "+self.params[idk][j]+ " for "+ k+ ".")
        
            if k =='disk_elements' :
                for i in range(len(modified_rotor.disk_elements)):
                    for idj,j in enumerate(self.params[idk]):
                        try:
                            setattr(modified_rotor.disk_elements[i], j, distributions[idk][idj].value(1)[0])
                        except:
                            raise KeyError("Wrong Name: "+self.params[idk][j]+ " for "+ k+ ".")

            if k =='shaft_elements' :
                for i in range(len(modified_rotor.shaft_elements)):
                    for idj,j in enumerate(self.params[idk]):
                        try:
                            setattr(modified_rotor.shaft_elements[i], j, distributions[idk][idj].value(1)[0])
                        except:
                            raise KeyError("Wrong Name: "+self.params[idk][j]+ " for "+ k+ ".")

            if k =='shaft_materials' :
                for i in range(len(modified_rotor.shaft_elements)):
                    for idj,j in enumerate(self.params[idk]):
                        try:
                            attr2 = getattr(modified_rotor.shaft_elements[i], 'material')
                            setattr(attr2, j, distributions[idk][idj].value(1)[0])
                        except:
                            raise KeyError("Wrong Name: "+self.params[idk][j]+ " for "+ k+ ".")

        # declarando os mancais
        shaftlist = []

        for i in range(len(modified_rotor.shaft_elements)):
            material = Material(name = modified_rotor.shaft_elements[i].material.name,
                                rho = modified_rotor.shaft_elements[i].material.rho,
                                E = modified_rotor.shaft_elements[i].material.E,
                                G_s = modified_rotor.shaft_elements[i].material.G_s
                                )
            shaftlist.append(ShaftElement(L = modified_rotor.shaft_elements[i].L,
                                            idl = modified_rotor.shaft_elements[i].idl,
                                            odl = modified_rotor.shaft_elements[i].odl,
                                            material = material,
                                            shear_effects = modified_rotor.shaft_elements[i].shear_effects,
                                            rotary_inertia = modified_rotor.shaft_elements[i].rotary_inertia,
                                            gyroscopic = modified_rotor.shaft_elements[i].gyroscopic
                                            ))


        bearinglist = []

        for i in range(len(modified_rotor.bearing_elements)):
            bearinglist.append(BearingElement(n=modified_rotor.bearing_elements[i].n, 
                                        n_link=modified_rotor.bearing_elements[i].n_link ,
                                        kxx = modified_rotor.bearing_elements[i].kxx , 
                                        kyy = modified_rotor.bearing_elements[i].kyy , 
                                        cxx = modified_rotor.bearing_elements[i].cxx , 
                                        cyy = modified_rotor.bearing_elements[i].cyy , 
                                        mxx = modified_rotor.bearing_elements[i].mxx , 
                                        myy = modified_rotor.bearing_elements[i].myy ,
                                        frequency = modified_rotor.bearing_elements[i].frequency
                                        ))
            
        disklist = []

        for i in range(len(modified_rotor.disk_elements)):
            disklist.append(DiskElement(n = modified_rotor.disk_elements[i].n, 
                                        Id = modified_rotor.disk_elements[i].Id,
                                        Ip = modified_rotor.disk_elements[i].Ip,
                                        m = modified_rotor.disk_elements[i].m,
                                        scale_factor = modified_rotor.disk_elements[i].scale_factor,
                                        ))
            
        modified_rotor2 = Rotor(shaftlist, disklist, bearinglist)

        return modified_rotor2
    
    def getting_rotors(self):
        
        values = self.pickvalues()
        
        limsups = []
        liminfs = []
        for z in range(len(self.elements)):
            attr = getattr(self.rotor, self.elements[z])
            for i in range(len(attr)):
                for j in range(len(self.params[z])):
                    limsup = values[z][i][j] *(1 + self.erro)
                    liminf = values[z][i][j] *(1 - self.erro)
                    
                    limsups.append(limsup)
                    liminfs.append(liminf)
        
        shaft = cp.deepcopy(self.rotor.shaft_elements)
        disks = cp.deepcopy(self.rotor.disk_elements)
        bearings = cp.deepcopy(self.rotor.bearing_elements)
        
        rotor = Rotor(shaft, disks, bearings)
        
        modified_rotor = cp.deepcopy(rotor)
        
        modified_rotor2 = cp.deepcopy(rotor)
        
        rotors = []
        #rotors.append(rotor)
        
        for idk,k in enumerate(self.elements):
            if k=='bearing_elements':
                for i in range(len(modified_rotor.bearing_elements)):
                    for idj,j in enumerate(self.params[idk]):
                        try:
                            setattr(modified_rotor.bearing_elements[i], j, liminfs[idj])
                            setattr(modified_rotor2.bearing_elements[i], j, limsups[idj])
                        except:
                            raise KeyError("Wrong Name: "+self.params[idk][j]+ " for "+ k+ ".")
        
        rotors.append(modified_rotor)
        rotors.append(rotor)
        rotors.append(modified_rotor2)
        
        return rotors
        
        
    def just_to_see_Freq(self,
        inp,
        out,
        speed_range=None,
        modes=None,
        cluster_points=False,
        num_modes=12,
        num_points=10,
        rtol=0.005,
    ):
        
        rotors = self.getting_rotors()
        
        FRF_size = len(speed_range)
        freq_resp = np.empty((FRF_size, len(rotors)), dtype=complex)
        velc_resp = np.empty((FRF_size, len(rotors)), dtype=complex)
        accl_resp = np.empty((FRF_size, len(rotors)), dtype=complex)

        # Monte Carlo - results storage
        for i in range(len(rotors)):
            rotor = rotors[i]
            results = rotor.run_freq_response(
                speed_range,
                modes,
                cluster_points,
                num_modes,
                num_points,
                rtol,
            )

            freq_resp[:, i] = results.freq_resp[inp, out, :]
            velc_resp[:, i] = results.velc_resp[inp, out, :]
            accl_resp[:, i] = results.accl_resp[inp, out, :]
        
        results = st_Frequency(
            speed_range, 
            freq_resp, 
            velc_resp, 
            accl_resp
        )

        return results

                    