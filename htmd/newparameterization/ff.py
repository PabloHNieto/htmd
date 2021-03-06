# (c) 2015-2016 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#

import math
import re
from copy import deepcopy

class BondPrm:
  def __init__( self, types, r0=0., k0=0. ):
    self.types = types
    self.r0 = r0
    self.k0 = k0

class AnglePrm:
  def __init__( self, types, theta0=0., k0=0., rUB=0., kUB=0. ):
    self.types  = types
    self.theta0 = theta0
    self.k0     = k0
    self.rUB     = rUB
    self.kUB     = kUB

class TorsPrm:
  def __init__( self, types, n=0., k0=0., phi0=0. ):
    self.types  = types
    self.n    = n
    self.k0   = k0
    self.phi0 = phi0

class NBPrm:
  def __init__( self, types, epsilon=0., rmin2=0., epsilon_14=None, rmin2_14=None ):
    self.types  = types
    self.epsilon = epsilon
    self.rmin2    = rmin2
    self.epsilon_14  = epsilon_14
    self.rmin2_14    = rmin2_14


class PRM:
  def __init__(self, filename):
   f = open(filename, "r" )
   lines = f.readlines()
   f.close()

   self.bonds    =[]
   self.angles   =[]
   self.dihedrals=[]
   self.impropers=[]
   self.nonbonded=[]
   mode=None
   skip=0
   for l in lines:
     l = l.strip()
     l = re.sub( "/!.*$//", "", l ) # Remove any comment
     
     if   l ==  "BONDS"    : 
       mode="BONDS"
       skip=1
     elif l == "ANGLES"   : 
       mode="ANGLES"
       skip=1
     elif l == "DIHEDRALS": 
       mode="DIHEDRALS"
       skip=1
     elif l == "IMPROPER" : 
       mode="IMPROPER"
       skip=1
     elif l.startswith( "NONBONDED "): 
        mode="NONBONDED"
        skip=2 
     elif l is "": 
        mode = None
     if skip>0: skip=skip-1
     elif mode:
       ll=l.split()
       if mode.startswith( "BONDS" ):
         self.bonds.append( BondPrm([ ll[0], ll[1] ], r0=float(ll[3]), k0=float(ll[2]) ) )
       elif mode.startswith( "ANGLES" ):
         if(len(ll)<=5):
           self.angles.append( AnglePrm([ ll[0], ll[1], ll[2] ], theta0=float(ll[4]), k0=float(ll[3]) ) )
         else:
           self.angles.append( AnglePrm([ ll[0], ll[1], ll[2] ], theta0=float(ll[4]), k0=float(ll[3]), rB=float(ll[6]), kB=float(ll[5]) ) )

       elif mode.startswith( "DIHEDRALS" ):
         self.dihedrals.append( TorsPrm( [ ll[0], ll[1], ll[2], ll[3] ] , n=int(ll[5]), k0=float(ll[4]),  phi0=float(ll[6]) ) ) 
       elif mode.startswith( "IMPROPER" ):
         self.impropers.append( TorsPrm( [ ll[0], ll[1], ll[2], ll[3] ], n=int(ll[5]), k0=float(ll[4]), phi0=float(ll[6]) ) )
       elif mode.startswith( "NONBONDED" ):
         if len(ll) < 5:
           self.nonbonded.append( NBPrm( [ ll[0] ], epsilon=float(ll[2]), rmin2=float(ll[3]) ) )
         else:
           self.nonbonded.append( NBPrm( [ ll[0] ], epsilon=float(ll[2]), rmin2=float(ll[3]), epsilon_14 = float(ll[5]), rmin2_14 = float(ll[6]) ) )
  
       
  def write(self, filename ):
    f = open(filename, "w" )
    print("* prm file build by parameterize", file=f )
    print("*\n", file=f )
    print("BONDS", file=f)
    for a in self.bonds:
      print("%-6s %-6s %8.2f %8.4f" %( a.types[0], a.types[1], a.k0, a.r0 ), file=f )
    print("\nANGLES", file=f)
    for a in self.angles:
      if a.kUB>0.:
        print("%-6s %-6s %-6s %8.2f %8.2f %8.2f %8.2f" %( a.types[0], a.types[1], a.types[2], a.k0, a.theta0, a.kUB, a.rUB  ), file=f )
      else:
        print("%-6s %-6s %-6s %8.2f %8.2f" %( a.types[0], a.types[1], a.types[2], a.k0, a.theta0 ), file=f )
    print("\nDIHEDRALS", file=f)
    for a in self.dihedrals:
      print("%-6s %-6s %-6s %-6s %12.8f %d %12.8f" %( a.types[0], a.types[1], a.types[2], a.types[3], a.k0, a.n, a.phi0 ), file=f )
    print("\nIMPROPER", file=f)
    for a in self.impropers:
      print("%-6s %-6s %-6s %-6s %12.8f %d %12.8f" %( a.types[0], a.types[1], a.types[2], a.types[3], a.k0, a.n, a.phi0 ), file=f )
    print("\nNONBONDED nbxmod  5 atom cdiel shift vatom vdistance vswitch -", file=f )
    print("cutnb 14.0 ctofnb 12.0 ctonnb 10.0 eps 1.0 e14fac 1.0 wmin 1.5", file=f )
    for a in self.nonbonded:
      if( a.epsilon_14 != None ):
        print("%-6s 0.0000 %8.4f %8.4f 0.0000 %8.4f %8.4f" % ( a.types[0], a.epsilon, a.rmin2, a.epsilon_14, a.rmin2_14 ), file=f )
      else:
        print("%-6s 0.0000 %8.4f %8.4f" % ( a.types[0], a.epsilon, a.rmin2 ), file=f )
    f.close()

  def vdwParam( self, n1, n2, s14 ):
    p1 = None
    p2 = None
    for b in self.nonbonded:
      if b.types[0] == n1: p1 = b 
      if b.types[0] == n2: p2 = b 

    # not found, maybe it's a duplicate that needs new params
    if( not p1 ) and ( "_" in n1 ): 
       xn1 = re.sub("_[0123456789]$", "", n1 )
       for b in self.nonbonded:
          if b.types[0] == xn1:
            p1 = b
            b = deepcopy(b)
            b.types[0] = n1
            self.nonbonded.append( b )
       if n1==n2:
            p2 = b

    if( not p2 ) and ( "_" in n2 ): 
       xn2 = re.sub("_[0123456789]$", "", n2 )
       for b in self.nonbonded:
          if b.types[0] == xn2:
            p2 = b
            b = deepcopy(b)
            b.types[0] = n2
            self.nonbonded.append( b )




    if (not p1) or (not p2):
      raise ValueError( "Could not find nb parameters for %s" %( n1 ) )

    epsilon_1 = p1.epsilon
    epsilon_2 = p2.epsilon
    rmin2_1   = p1.rmin2
    rmin2_2   = p2.rmin2
    
    if s14 and (p1.epsilon_14 != None):
      epsilon_1 = p1.epsilon_14
      rmin2_1   = p1.rmin2_14

    if s14 and (p2.epsilon_14 != None):
      epsilon_2 = p2.epsilon_14
      rmin2_2   = p2.rmin2_14

    neg_emin = math.sqrt( epsilon_1 * epsilon_2 ) 
    rmin     = ( rmin2_1 + rmin2_2 ) 
    A = neg_emin * math.pow( rmin, 12 )
    B = 2.0 * neg_emin * math.pow( rmin, 6 )

    return(A, B)

    

  def bondParam( self, n1, n2 ):
    for b in self.bonds:
       if b.types[0] == n1 and b.types[1] == n2: return b
       if b.types[1] == n1 and b.types[0] == n2: return b

    # not found, maybe it's a duplicate that needs new params
    if( "_" in n1 ) or ( "_" in n2 ):
       xn1 = re.sub("_[0123456789]$", "", n1 )
       xn2 = re.sub("_[0123456789]$", "", n2 )
       b = self.bondParam( xn1, xn2 )
       c = BondPrm( [n1, n2], r0=b.r0, k0=b.k0 )
       self.bonds.append(c)
       return b

    raise ValueError( "Could not find bond parameters for %s-%s" %( n1, n2 ) )

  def angleParam( self, n1, n2, n3 ):
    for b in self.angles:
       if b.types[0] == n1 and b.types[1] == n2 and b.types[2] == n3: return b;
       if b.types[2] == n1 and b.types[1] == n2 and b.types[0] == n3: return b;

    # not found, maybe it's a duplicate that needs new params
    if( "_" in n1 ) or ( "_" in n2 ) or ( "_" in n3 ):
       xn1 = re.sub("_[0123456789]$", "", n1 )
       xn2 = re.sub("_[0123456789]$", "", n2 )
       xn3 = re.sub("_[0123456789]$", "", n3 )
       b = self.angleParam( xn1, xn2, xn3 )
       c = AnglePrm( [ n1, n2, n3 ], theta0=b.theta0, k0=b.k0, rUB=b.rUB, kUB=b.kUB )
       self.angles.append(c)
       return b


    raise ValueError( "Could not find angle parameters for %s-%s-%s" %( n1, n2, n3 ) )

  def dihedralParam( self, n1, n2, n3, n4 ):
    ret   = []
    found = False
    for i in  range(6):
     ret.append( TorsPrm( [ n1, n2, n3, n4] , phi0=0., n=i+1, k0=0.  ) )

    for b in self.dihedrals:
       if b.types[0] == n1 and b.types[1] == n2 and b.types[2] == n3 and b.types[3] == n4: 
          ret[b.n-1] = b
          found     = True 
       elif b.types[3] == n1 and b.types[2] == n2 and b.types[1] == n3 and b.types[0] == n4: 
         # print(b)
          ret[b.n-1]= b
          found    = True

    # not found, maybe it's a duplicate that needs new params
    if not found:
      if( "_" in n1 ) or ( "_" in n2 ) or ( "_" in n3 ) or ( "_" in n4 ):
       xn1 = re.sub("_[0123456789]$", "", n1 )
       xn2 = re.sub("_[0123456789]$", "", n2 )
       xn3 = re.sub("_[0123456789]$", "", n3 )
       xn4 = re.sub("_[0123456789]$", "", n4 )
       b = self.dihedralParam( xn1, xn2, xn3, xn4 )
       r=[]
      # print(b)
       for c in b:
      #   print(c)
         c = deepcopy(c)
         c.types[0] = n1
         c.types[1] = n2
         c.types[2] = n3
         c.types[3] = n4
         self.dihedrals.append(c)
         r.append(c)
       return r


    if not found: 
      raise ValueError( "Could not find dihedral parameters for %s-%s-%s-%s" %( n1, n2, n3, n4 ) )
    return ret


  def improperParam( self, n1, n2, n3, n4 ):
    ret=[]
    for b in self.impropers:
       if b.types[0] == n1 and b.types[1] == n2 and b.types[2] == n3 and b.types[3] == n4: ret.append( b )
       elif b.types[3] == n1 and b.types[2] == n2 and b.types[1] == n3 and b.types[0] == n4: ret.append( b )

    # not found, maybe it's a duplicate that needs new params
    if len(ret) == 0:
      if( "_" in n1 ) or ( "_" in n2 ) or ( "_" in n3 ) or ( "_" in n4 ):
       xn1 = re.sub("_[0123456789]$", "", n1 )
       xn2 = re.sub("_[0123456789]$", "", n2 )
       xn3 = re.sub("_[0123456789]$", "", n3 )
       xn4 = re.sub("_[0123456789]$", "", n4 )
       b = self.improperParam( xn1, xn2, xn3, xn4 )
       r = []
       for c in b:
         c = deepcopy(c)
         c.types[0] = n1
         c.types[1] = n2
         c.types[2] = n3
         c.types[3] = n4
         self.impropers.append(c)
         r.append(c)
       return r


    if len(ret) == 0:
      raise ValueError( "Could not find improper parameters for %s-%s-%s-%s" %( n1, n2, n3, n4 ) )
    return ret

  def updateDihedral( self, phi ):
   pp = deepcopy(phi)
   for p in self.dihedrals:
     if( phi[0].types[0] != p.types[0] or phi[0].types[1] != p.types[1] or phi[0].types[2] != p.types[2] or phi[0].types[3] != p.types[3] ):
       pp.append(p) 
   self.dihedrals = pp







class RTF:
  def __init__(self, filename):
   f = open(filename, "r" )
   lines = f.readlines()
   f.close()

   self.types=[]
   self.mass_by_type=dict()
   self.element_by_type=dict()
   self.type_by_name=dict()
   self.type_by_index=[]
   self.index_by_name=dict()
   self.names=[]
   self.charge_by_name=dict()
   self.bonds=[]
   self.impropers=[]
   self.typeindex_by_type=dict()
   self.netcharge= 0.

   aidx=0

   for l in lines:
     if l.startswith("MASS "):
       k=l.split()
       at = k[2]
       self.mass_by_type[ at ]    = float(k[3])
       self.element_by_type[ at ] = k[4]
       self.typeindex_by_type[ at ] = int(k[1])
       self.types.append(at)
     elif l.startswith("RESI "):
       k=l.split()
       self.netcharge=float(k[2])
     elif l.startswith("ATOM "):
       k=l.split()
       self.names.append( k[1] )
       self.index_by_name[ k[1] ] = aidx
       self.type_by_index.append( k[2] )
       self.type_by_name[ k[1] ] =  k[2] 
       self.charge_by_name[ k[1] ] = float( k[3] )
       aidx=aidx+1
     elif l.startswith("BOND "):
       k=l.split()
       self.bonds.append( [self.index_by_name[k[1]], self.index_by_name[k[2]]] )

     elif l.startswith("IMPR "):
       k=l.split()
       self.impropers.append( [self.index_by_name[k[1]], self.index_by_name[k[2] ], self.index_by_name[k[3]], self.index_by_name[k[4] ] ] )
     
     self.natoms = aidx

  def write( self, filename ):
   f=open( filename, "w" )
   print( "* Charmm RTF built by parameterize", file=f )
   print( "* ", file=f )
   print( "  22     0", file=f )
   for a in self.types:
     print("MASS %5d %s %8.5f %s" % ( self.typeindex_by_type[a], a, self.mass_by_type[a], self.element_by_type[a] ), file=f )
   print( "\nAUTO ANGLES DIHE\n", file=f )
   print( "RESI  MOL %8.5f" % ( self.netcharge ), file=f )
   print( "GROUP",file=f )
   for a in self.names:
     print( "ATOM %4s %6s %8.6f" %( a, self.type_by_name[a], self.charge_by_name[a] ), file=f )
   for a in self.bonds:
     print( "BOND %4s %4s" %( self.names[ a[0] ], self.names[ a[1] ] ), file=f )
   for a in self.impropers:
     print( "IMPR %4s %4s %4s %4s" %( self.names[ a[0] ], self.names[ a[1] ], self.names[a[2]], self.names[a[3]] ), file=f )
   print( "PATCH FIRST NONE LAST NONE", file=f )
   print("\nEND", file=f )
   f.close()

  def updateCharges( self, charges ):
    if(charges.shape[0] != self.natoms ): 
      raise ValueError( "charge array not natoms in length" )
    for i in range(self.natoms):
       name = self.names[i]
       self.charge_by_name[ name ] = charges[i]
   
#if __name__ == "__main__":
#
#  prm=PRM("ethanol.prm")
#  prm.write("ethanol_out.prm")
#  rtf=RTF("ethanol.rtf")
#  rtf.write("ethanol_out.rtf")

