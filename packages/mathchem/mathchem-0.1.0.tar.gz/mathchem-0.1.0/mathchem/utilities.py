from mathchem import *

        
    
def batch_process(infile, outfile, function) :
    """ Reads file line-by-line and apply a <function> to each line
        
    Designed to read files of graph6 format
    """
    
    f_out = open(outfile, 'w')
    f_in = open(infile, 'r')
    
    lines = f_in.readlines()    
    f_in.close()
        
    for line in lines:
        f_out.writelines(function(line))

    f_out.close()
