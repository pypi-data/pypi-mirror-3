
class Mol ():
    r"""
    Molecule.
    """
    # Adjacency matrix
    __A = []
    # Laplacian matrix
    __L = []
    # Normalized laplacian matrix
    __NL = []
    # Signless laplacian matrix
    __Q = []
    # Distance matrix
    __D = []
    # Resistance Distance matrix
    __RD = []

    __Order = 0
    __Edges = []
    
    __Sage_graph = None
    __NX_graph = None
    
    __Degrees = []
    
    
    __Spectrum = []
    __Laplacian_spectrum = []
    __Distance_spectrum = []
    __Norm_laplacian_spectrum = []
    __Signless_laplacian_spectrum = []
    __RD_spectrum = []
    
    __Is_connected = None
    
    def _reset_(self):
        """ Reset all attributes """
        # Adjacency matrix
        self.__A = []
        # Laplacian matrix
        self.__L = []
        # Normalized laplacian matrix
        self.__NL = []
        # Signless laplacian matrix
        self.__Q = []
        # Distance matrix
        self.__D = []
        # Resistance Distance matrix
        self.__RD = []
    
        self.__Order = 0
        self.__Edges = []
        
        self.__Sage_graph = None
        self.__NX_graph = None
        
        self.__Degrees = []
        
        
        self.__Spectrum = []
        self.__Laplacian_spectrum = []
        self.__Distance_spectrum = []
        self.__Norm_laplacian_spectrum = []
        self.__Signless_laplacian_spectrum = []
        self.__RD_spectrum = []
        
        self.__Is_connected = None
    
    def __init__(self, g6str=None):
        """ Molecular graph class """
        if g6str != None:
            self.read_g6(g6str)
        
          
    def __repr__(self):
        if self.__A != None: return  'Molecular graph on '+ str(self.__Order)+' vertices'
        return 'Empty Molecular graph'
        
    def __len__(self):
        if self.__A != None: return len(self.__A)
        else: return 0
            
      
    def order(self):
        """ Return number of vertices """
        return self.__Order
    
    def edges(self):
        """ Return list of Edges """    
        return self.__Edges
    
    def vertices(self):
        """ Return list of vertices """
        return range(self.__Order)
           
    def sage_graph(self):
        """ Return Sage Graph object """
        #if not self._is_sage_graph(): self._init_sage_graph_()
        if self.__Sage_graph is None: self._init_sage_graph_()
        return self.__Sage_graph
         
            
    def NX_graph(self):
        """ Return NetworkX graph object """
        if self.__NX_graph is None:
            import networkx as nx
            self.__NX_graph = nx.Graph(self.__Edges)
        return self.__NX_graph
        
        
    def _init_sage_graph_(self):
        """ Initialize SAGE graph from Adjacency matrix"""
        from sage.graphs.graph import Graph
        self.__Sage_graph = Graph(self.__Edges)
            
            
    def read_g6(self, s):
        """ Initialize graph from graph6 string """
        def graph_bit(pos,off):
            return ( (ord(s[off + 1+ pos/6]) - 63) & (2**(5-pos%6)) ) != 0
        
        # reset all the attributes before changing the structure    
        self._reset_()
        
        n = ord(s[0]) - 63
        off = 0
        if n==63:
            if not ord(s[1]) - 63 == 63:
                n = sum(map(lambda i: (ord(s[i]) - 63) << (6*(3-i)),range(1,3)))
                off = 3
            else:
                n = sum(map(lambda i: (ord(s[i]) - 63) << (6*(7-i)),range(2,7)))
                off = 7
        self.__Order = n     
    
        self.__A = [[0 for col in range(n)] for row in range(n)]
    
        i=0; j=1
        
        self.__Edges = [];
        for x in range(n*(n-1)/2):
            if graph_bit(x, off):
                self.__A[i][j] = 1
                self.__A[j][i] = 1
                self.__Edges.append((i,j))
            if j-i == 1:
                i=0
                j+=1
            else:
                i+=1
    
    def read_sdf_file(self, filename, hydrogens=False):
        r"""
        read SDF file and build molecular graph
        """
        def _read_molfile_value( file, length, strip=1, conversion=None):
            """reads specified number of characters, if strip strips whitespace,
            if conversion (a fuction taking one string argument) applies it;
            if empty string is obtained after stripping 0 is returned"""
            str = file.read( length)
            if strip:
                str = str.strip()
            if str == "":
                return 0
            if conversion:
                str = conversion( str)
            return str
        # reset all the attributes before changing the structure    
        self._reset_()
        # TODO: insert try ... here
        file = open(filename, 'r')
        # read header. We don't use this data
        for i in range( 3):
          file.readline()
        #self._read_file(file, hydrogens) 
        # numbers of atoms
        atoms = _read_molfile_value( file, 3, conversion=int)
        self.__Order = atoms;
        # numbers of bonds
        bonds = _read_molfile_value( file, 3, conversion=int)
        file.readline()
        #in v we will keep vertices (Atoms) 
        v = [];
        for i in range( atoms ):
            # here we read atom positions but not using them yet
            x = _read_molfile_value( file, 10, conversion=float)
            y = _read_molfile_value( file, 10, conversion=float)
            z = _read_molfile_value( file, 10, conversion=float)
            _read_molfile_value( file, 1) # empty space
            symbol = _read_molfile_value( file, 3)
            file.readline() # next line
            
            if hydrogens == False and (symbol == 'H' or symbol == 'h'):
                self.__Order = self.__Order - 1
            else:
                v.append(i+1);
         
        
        # reset Adjacency matrix fill 0
        self.__A = [[0 for col in range(self.__Order)] for row in range(self.__Order)]

        for i in range( bonds ):
            a1 = _read_molfile_value( file, 3, conversion=int)
            a2 = _read_molfile_value( file, 3, conversion=int)
            bond_type = _read_molfile_value( file, 3, conversion=int)            
            file.readline() # next line
            if a1 in v and a2 in v:
                # add edge here!
                i = v.index(a1)
                j = v.index(a2)
                self.__A[i][j] = 1
                self.__A[j][i] = 1
                self.__Edges.append((i,j))
       
        file.close()



    def write_dot_file(self, filename):
        
        f_out = open(filename, 'w')
        f_out.writelines('graph Mol {\n')
        for (i,j) in self.edges():
            f_out.writelines( '    ' + str(i) + ' -- ' + str(j) +';\n')
        f_out.writelines('}')    
        f_out.close()
                    
    #
    #
    # matrices
    #
    #
    
    def adjacency_matrix(self):
        """ Return Adjacency matrix
        
        Alias : A
        """    
        return self.__A
        
    A = adjacency_matrix


    def laplacian_matrix(self):
        """ Return Laplacian matrix
        
        L = D-A
        where  D - matrix whose diagonal elements are the degrees of the corresponding vertices
               A - adjacency matrix
                
        Alias : L
        """
        if self.__L == []:
            import numpy as np;
            self.__L = np.diag(self.degrees()) - np.matrix(self.__A);
        return self.__L
        
    L = laplacian_matrix
    
    
    def signless_laplacian_matrix(self):
        """ Return Signless Laplacian matrix
        
        Q = D+A
        Alias : Q
        """
        if self.__Q == []:
            import numpy as np;
            self.__Q = np.diag(self.degrees()) + np.matrix(self.__A);
        return self.__Q
        
    Q = signless_laplacian_matrix
    
    
    def normalized_laplacian_matrix(self):
        """ Return Normalized Laplacian matrix
        
        NL = deg^(-1/2) * L * deg(1/2)
        Alias : NL
        """
        ## TODO: check if we have zeros in degrees()
        if self.__NL  == []:
            import numpy as np;
            d1 = np.diag( np.power( self.degrees(), -.5 ))
            d2 = np.diag( np.power( self.degrees(),  .5 ))
            self.__NL = d1 * self.laplacian_matrix() * d2
        return self.__NL
        
    NL = normalized_laplacian_matrix


    def distance_matrix(self):
        """ Return Distance matrix
        
        Alias : D
        """    
        if self.__Order == 0: return []
        
        if self.__D == [] :
            import numpy as np;
            # use here float only for using np.inf - infinity
            A = np.matrix(self.__A, dtype=float)
            n,m = A.shape
            I=np.identity(n)
            A[A==0]=np.inf # set zero entries to inf
            A[I==1]=0 # except diagonal which should be zero
            for i in range(n):
                r = A[i,:]
                A = np.minimum(A, r + r.T)
            self.__D = np.matrix(A,dtype=int)
            
        return self.__D  
        
    D = distance_matrix
    
    def reciprocal_distance_matrix(self):
        """ Return Reciprocal Distance matrix """

        import numpy as np;

        rd = np.matrix(self.distance_matrix(),dtype=float)
        # probably there exists more python way to apply a function to each element of matrix
        for i in range(self.__Order):
            for j in range(self.__Order):
                if not rd[i,j] == 0: rd[i,j] = 1 / rd[i,j]
        
        return rd

    
    def resistance_distance_matrix(self):
        """ Return Resistance Distance matrix """
        
        if not self.is_connected() or self.__Order == 0:
            return False
            
        if self.__RD == []:
            import numpy as np
            #from numpy import linalg as la
            n = self.__Order
            s = n*self.laplacian_matrix() + 1
            sn = n* np.linalg.inv(s)
            RD = np.ndarray((n,n))
            for i in range(n):
                for j in range(n):
                    RD[i,j] = sn[i,i] + sn[j,j] - 2*sn[i,j]
            self.__RD = RD
            
        return self.__RD
    #
    #
    # Graph invariants
    #
    #
    
    def diameter(self):
        """ Return diameter of the graph
        
        Diameter is the maximum value of distance matrix
        """
        return self.distance_matrix().max()
        
    
        
    def degrees(self):
        """ Return degree of the vertex
        
        Alias : deg
        """
        if self.__Degrees == []:
            self.__Degrees = map(lambda r: sum(r) , self.__A)
        ## calcuate degrees for all vertices
        return self.__Degrees
        
    deg = degrees
                
                
    def eccentricity(self):
        """ Eccentricity of the graph for all its vertices"""
        if self.__Order == 0: return None
        
        return self.distance_matrix().max(axis=0).tolist()[0]
        
        
        
    def distances_from_vertex(self, v):
        """ Return list of all distances from a given vertex to all others"""
        # used to test graph where it is connected or not
        seen={}  
        level=0  
        nextlevel=[v]
        while nextlevel:
            thislevel=nextlevel 
            nextlevel=[] 
            for v in thislevel:
                if v not in seen: 
                    seen[v]=level 
                    nb = [i for (i,j) in zip(range(len(self.__A[v])), self.__A[v]) if j!=0]
                    nextlevel.extend(nb)
            #if (cutoff is not None and cutoff <= level):  break
            level=level+1
        return seen
        
        
        
    def is_connected(self):
        """ Return True/False depends on the graph is connected or not """ 
        if self.__Order == 0: return False
         
        if self.__Is_connected is None:
            # we take vertex 0 and check whether we can reach all other vertices 
            self.__Is_connected = len(self.distances_from_vertex(0)) == self.order()
        return self.__Is_connected
        
        
            
    #
    #
    # Graph spectra
    #
    #
    
    def spectrum(self, matrix="adjacency"):
        r""" Calculates spectrum of the graph
    
        args:
            matrix (str)
                'adjacency'             or 'A' : default
                'laplacian'             or 'L'
                'distance'              or 'D'
                'signless_laplacian'    or 'Q'
                'normalized_laplacian'  or 'NL'
                'resistance_distance'   or 'RD'
                'reciprocal_distance'
                
        """
        if self.__Order == 0: return []
        
        if matrix == "adjacency" or matrix == "A":
            if self.__Spectrum == []:
                from numpy import linalg as la
                s = la.eigvalsh(self.__A).tolist()
                s.sort(reverse=True)
                self.__Spectrum = s
            return self.__Spectrum
                
        elif matrix == "laplacian" or matrix == "L":
            if self.__Laplacian_spectrum == []:
                from numpy import linalg as la
                s = la.eigvalsh(self.laplacian_matrix()).tolist()
                s.sort(reverse=True)
                self.__Laplacian_spectrum = s
            return self.__Laplacian_spectrum
            
        elif matrix == "distance" or matrix == "D":
            if self.__Distance_spectrum == []:
                from numpy import linalg as la
                s = la.eigvalsh(self.distance_matrix()).tolist()
                s.sort(reverse=True)
                self.__Distance_spectrum = s
            return self.__Distance_spectrum  
        
        elif matrix == "signless_laplacian" or matrix == "Q":
            if self.__Signless_laplacian_spectrum == []:
                ## TODO: check if we have zeros in degrees()
                from numpy import linalg as la
                s = la.eigvalsh(self.signless_laplacian_matrix()).tolist()
                s.sort(reverse=True)
                self.__Signless_laplacian_spectrum = s
            return self.__Signless_laplacian_spectrum  

        elif matrix == "normalized_laplacian" or matrix == "NL":
            if self.__Norm_laplacian_spectrum == []:
                ## TODO: check if we have zeros in degrees()
                from numpy import linalg as la
                s = la.eigvalsh(self.normalized_laplacian_matrix()).tolist()
                s.sort(reverse=True)
                self.__Norm_laplacian_spectrum = s
            return self.__Norm_laplacian_spectrum  

        elif matrix == "resistance_distance" or matrix == "RD":
            if self.__RD_spectrum == []:
                from numpy import linalg as la
                s = la.eigvalsh(self.resistance_distance_matrix()).tolist()
                s.sort(reverse=True)
                self.__RD_spectrum = s
            return self.__RD_spectrum
        # NO CACHE
        elif matrix == "reciprocal_distance" :
            s = la.eigvalsh(self.reciprocal_distance_matrix()).tolist()
            s.sort(reverse=True)
            return s
       
        else:
            return False        
    
    
    def spectral_moment(self, k, matrix="adjacency"):
        """ Return k-th spectral moment
        
        parameters: matrix - see spectrum help
        """
        from numpy import power
        return power(self.spectrum(matrix),k).tolist()
    
        
    def energy(self, matrix="adjacency"):
        """ Return energy of the graph 
        
        parameters: matrix - see spectrum help
        """
        return sum( map( lambda x: abs(x) ,self.spectrum(matrix)))
        
    

    #
    #
    # Chemical indices
    #
    #
    
    def zagreb_m1_index(self):
        """ Calculates Zagreb M1 Index """    
        return sum(map(lambda d: d**2, self.degrees()))
        
    
    def zagreb_m2_index(self):
        """ Calculates Zagreb M2 Index 
        
        The molecular graph must contain at least one edge, otherwise the function Return False
        Zagreb M2 Index is a special case of Connectivity Index with power = 1"""
        return sum( map(lambda (e1, e2): self.degrees()[e1]*self.degrees()[e2] , self.edges()) )    

    
    def connectivity_index(self, power):
        """ Calculates Connectivity index (R)"""
        E = self.edges() # E - all edges
        if len(E) == 0: return 0
        return sum( map(lambda (e1 ,e2): ( self.degrees()[e1]*self.degrees()[e2] ) ** power , E) )

    
    def eccentric_connectivity_index(self):
        """ Calculates Eccentric Connectivity Index 
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        max_dist = map(lambda row: row.max() , self.distance_matrix())
        return sum( map( lambda a,b: a*b, self.degrees(), max_dist ) )
        
    
    def randic_index(self):
        """ Calculates Randic Index 
        
        The molecular graph must contain at least one edge, otherwise the function Return False
        Randic Index is a special case of Connectivity Index with power = -1/2"""
        return self.connectivity_index(-0.5)
                        
    
    def atom_bond_connectivity_index(self):
        """ Calculates Atom-Bond Connectivity Index (ABC) """
        s = 0.0 # summator
        for (u,v) in self.edges():
            d1 = self.degrees()[u]
            d2 = self.degrees()[v]
            s += ( 1.0* (d1 + d2 - 2 ) / (d1 * d2)) ** .5
        return s   
    
    
    def estrada_index(self, matrix = "adjacency"):
        """ Calculates Estrada Index (EE)  
        
        args:
            matrix -- see spectrum for help, default value is 'adjacency'
            
        There is an alias 'distance_estrada_index' for distance matrix
        """
        from numpy import exp        
        return sum( map( lambda x: exp( x.real ) , self.spectrum(matrix) ) ) 
        
        
    def distance_estrada_index(self):
        """ Calculates Distance Estrada Index (DEE) 
        
        Special case of Estrada index with distance matrix
        """
        return self.estrada_index('distance')
    
    
    
    def degree_distance(self):
        """ Calculates Distance Degree (DD)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False      
        from numpy import matrix
        dd = matrix(self.degrees()) * self.distance_matrix().sum(axis=1)
        return dd[0,0]
        
    def reverse_degree_distance(self):
        """ Calculates Reverse Distance Degree (rDD)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        return 2*( self.order()-1 ) * len(self.edges()) * self.diameter() - self.degree_distance()
    
    
    def molecular_topological_index(self):
        """ Calculates (Schultz) Molecular Topological Index (MTI)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        # (A+D)*d
        from numpy import matrix
        A = matrix(self.__A)
        d = matrix(self.degrees())
        return ( (A + self.distance_matrix()) * d.T ).sum()
    
        
    def eccentric_distance_sum(self):
        """ Calculates Distance Sum
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        return (self.eccentricity() * self.distance_matrix().sum(axis=1))[0,0]
    
    
    # strange - it is slow ((
    def balaban_j_index(self):
        """ Calculates Balaban J index 
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        from numpy import sqrt
        ds = self.distance_matrix().sum(axis=1)
        m = len(self.edges())
        k = (m / ( m - self.__Order +2.0 ))
        return k * sum( map(lambda (u ,v): 1 / sqrt((ds[u][0,0]*ds[v][0,0])), self.edges() ))
        
    def kirchhoff_index(self):
        """ Calculates Kirchhoff Index (Kf)
        
        Kf = 1/2 * sum_i sum_j RD[i,j]
        Based on resistance distance matrix RD
        
        Alias: resistance
        
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        return self.resistance_distance_matrix().sum() / 2
        
    resistance = kirchhoff_index
    
    def wiener_index(self):
        """ Calculates Wiener Index (W)
        
        W = 1/2 * sum_i sum_j D[i,j]
        where D is distance matrix
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        return self.distance_matrix().sum() / 2
        

    def reverse_wiener_index(self):
        """ Calculates Reverse Wiener Index (RW)
        
        RW = 1/2 * sum_i!=j ( d - D[i,j] )
        where D is distance matrix and d is diameter
        
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        # here we use formula: RW = 1/2 * n * (n-1) * d - W
        return  self.diameter() * (self.__Order * (self.__Order - 1)) / 2 - self.wiener_index()
        
    def hyper_wiener_index(self):
        """ Calculates Hyper-Wiener Index (WW)
        
        WW = 1/2 * ( sum_ij d(i,j)^2 + sum_i_j d(i,j) )
        where D is distance matrix

        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False         
        from numpy import power
        return ( power(self.distance_matrix(),2).sum() + self.distance_matrix().sum() ) / 4 # since we have symmetric matrix
        
        
    def harary_index(self):
        """ Calculates Harary Index (H)
        
        H = sum_i sum_j Rd[i,j]
        where Rd is reciprocal distance matrix 
        Rd[i,j] = 1 / D[i,j] for D[i,j] != 0
        Rd[i,j] = 0 otherwise

        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False         
        return self.reciprocal_distance_matrix().sum()
            
        
        
        
        