model = """# Stochastic Simulation Algorithm input file
# --> mRNA --> 

# Reactions
R1:
    $pool > mRNA
    Ksyn*mRNA

R2:
    mRNA > $pool
    Kdeg*mRNA
 
# Fixed species
 
# Variable species
mRNA = 100
 
# Parameters
Ksyn = 4
Kdeg = 3

"""
