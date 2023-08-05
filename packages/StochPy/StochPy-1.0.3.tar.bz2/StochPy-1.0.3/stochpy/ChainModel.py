# ---> S2 <--> S3 ... <---> Sn-1 --> Sn

class BuildModel():
  def __init__(self,N):
    self.N = N
    self.num = 0
    self.BuildAll()

  def Print(self):
    print self.reaction_num,'\n',self.reaction,'\n',self.rate  

  def Build1(self,atom_num): # -->
    self.num+=1
    self.reaction_num = 'R'+ str(self.num)+':'
    self.reaction = '    '+'S'+str(atom_num)+' > '+ 'S'+str(atom_num+1) 
    self.rate = '    k1*S'+str(atom_num)
    self.Print()

  def Build2(self,atom_num): # <--
    self.num+=1 
    self.reaction_num = 'R'+ str(self.num)+':'
    self.reaction = '    '+'S'+str(atom_num+1)+' > '+ 'S'+str(atom_num) 
    self.rate = '    k1*S'+str(atom_num+1)
    self.Print()    

  def BuildAll(self):  
    self.Build1(1)
    self.Build2(1)
    for atom in range(2,self.N-1):             
       self.Build1(atom)
       self.Build2(atom)
    self.Build1(self.N-1)
    self.Build2(self.N-1)


#if __main__ == 'main' :
number = 5
BuildModel(number)

ratio = 1
print ''
print '# InitPar'
print 'k1 =',ratio, '# noise'
print ''
print '# InitVar' 


print 'S1 = 1'
for i in range(2,number+1):
  stuff =  'S'+str(i)+' = '+ str(0)
  print stuff
