# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 14:39:18 2022

@author: Rahul Reddy EE20B105
"""
from sys import argv, exit
import numpy as np
import math as m

CIRCUIT_START = '.circuit'
CIRCUIT_END = '.end'

class cktelement:

    def __init__(self, cmptname,node1,node2,value,node3,node4,voltageSource,phase):
        self.cmpntname=cmptname
        self.node1=node1
        self.node2=node2
        self.value=value
        self.node3=node3
        self.node4=node4
        self.voltageSource=voltageSource
        self.phase=phase
element=[]
vsrc_crnt=0
vscrc_cntr=0
c=1j
current_dict={"i":-4}

if len(argv) != 2:
    print("Wrong number of arguments")
    exit()  

try:
    with open(argv[1]) as f:
        lines = f.readlines()
        start = -1; end = -2
        for line in lines:              # extracting circuit definition start and end lines
            if CIRCUIT_START == line[:len(CIRCUIT_START)]:
                start = lines.index(line)
            elif CIRCUIT_END == line[:len(CIRCUIT_END)]:
                end = lines.index(line)
                break
        if start >= end:                # validating circuit block
            print('Invalid circuit definition')
            exit(0)
        for line in lines[start+1:end]:
            info=line.split('#')[0].split()
            for i in range(1,3):
                if info[i]== 'GND' : 
                    info[i]=0
            if len(info)==6:
                if info[3]=='ac':
                    element.append(cktelement(info[0],info[1],info[2],float(info[4])/2,-2,-2,'Vx',info[5]))
                    for lin2 in lines[end+1:end+2]:
                        info2=lin2.split('#')[0].split()
                        freq=float(info2[2])
                else:
                    element.append(cktelement(info[0],info[1],info[2],info[5],info[3],info[4],'Vx',0))
            elif len(info)==5:
                element.append(cktelement(info[0],info[1],info[2],info[4],-2,-2,info[3],0))
                
            else:         
                element.append(cktelement(info[0],info[1],info[2],info[3],-2,-2,'Vx',0))
            
            f.close()
        node_list=[]
        ele_name=[]
        for i in range(len(element)):
            node_list.append(element[i].node1)
            node_list.append(element[i].node2)
            ele_name.append(element[i].cmpntname[0])
            
            if (element[i].cmpntname[0]=='V' or element[i].cmpntname[0]=='E' or element[i].cmpntname[0]=='H'):
                vsrc_crnt+=1
        node_set=set(node_list)
        elenm_set=set(ele_name)
        #checking if circuit has only voltage or current sources
        if (len(elenm_set)==1 and(ele_name[1]=='V' or ele_name[1]=='I')): 
            print("Invalid circuit")
            exit()
        rows=len(node_set)+vsrc_crnt-1
        M=np.zeros((rows,rows),dtype = 'complex_')
        b=np.zeros((rows,1),dtype = 'complex_')
        for i in range(len(element)):
            if element[i].cmpntname[0]=='L':
                element[i].value=freq*2*m.pi*c*float(element[i].value)
            elif element[i].cmpntname[0]=='C':
                element[i].value=1/(freq*2*m.pi*c*float(element[i].value))
            if element[i].cmpntname[0]=='R' or element[i].cmpntname[0]=='L' or element[i].cmpntname[0]=='C':
                if element[i].node1==0:
                    M[int(element[i].node2)-1][int(element[i].node2)-1]+=(1/complex(element[i].value))
                elif element[i].node2==0:
                    M[int(element[i].node1)-1][int(element[i].node1)-1]+=(1/complex(element[i].value))
                else:
                    M[int(element[i].node1)-1][int(element[i].node1)-1]+=(1/complex(element[i].value))
                    M[int(element[i].node1)-1][int(element[i].node2)-1]+=(-1/complex(element[i].value))
                    M[int(element[i].node2)-1][int(element[i].node1)-1]+=(-1/complex(element[i].value))
                    M[int(element[i].node2)-1][int(element[i].node2)-1]+=(1/complex(element[i].value))
            
            #filling the matrix for each element
            if element[i].cmpntname[0]=='V':
                if element[i].node1==0:
                    M[int(element[i].node2)-1][vscrc_cntr+len(node_set)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node2)-1]+=-1
                elif element[i].node2==0:
                    M[int(element[i].node1)-1][vscrc_cntr+len(node_set)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node1)-1]+=1
                else:
                    M[int(element[i].node1)-1][vscrc_cntr+len(node_set)-1]+=1
                    M[int(element[i].node2)-1][vscrc_cntr+len(node_set)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node1)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node2)-1]+=-1
                    
                b[vscrc_cntr+len(node_set)-1][0]=float(element[i].value)
                current_dict[str(element[i].cmpntname)]=[vscrc_cntr+len(node_set),element[i].node1,element[i].node2]
                vscrc_cntr+=1
            
            
            if element[i].cmpntname[0]=='I':
                if element[i].node1==0:
                    b[int(element[i].node2)-1][0]=-float(element[i].value)
                elif element[i].node2==0:
                    b[int(element[i].node1)-1][0]=float(element[i].value)
                else:
                    b[int(element[i].node1)-1][0]=float(element[i].value)
                    b[int(element[i].node2)-1][0]=-float(element[i].value)
            
            
            if element[i].cmpntname[0]=='G':
                if element[i].node1==0:
                    M[int(element[i].node2)-1][int(element[i].node3)-1]+=(1/complex(element[i].value))
                    M[int(element[i].node2)-1][int(element[i].node4)-1]+=(1/complex(element[i].value))
                elif element[i].node2==0:
                    M[int(element[i].node1)-1][int(element[i].node3)-1]+=(1/complex(element[i].value))
                    M[int(element[i].node1)-1][int(element[i].node4)-1]+=(1/complex(element[i].value))
                elif element[i].node3==0:
                    M[int(element[i].node1)-1][int(element[i].node4)-1]+=(1/complex(element[i].value))
                    M[int(element[i].node2)-1][int(element[i].node4)-1]+=(1/complex(element[i].value))
                elif element[i].node4==0:
                    M[int(element[i].node1)-1][int(element[i].node3)-1]+=(1/complex(element[i].value))
                    M[int(element[i].node2)-1][int(element[i].node3)-1]+=(1/complex(element[i].value))
                else:
                    M[int(element[i].node1)-1][int(element[i].node3)-1]+=(1/complex(element[i].value))
                    M[int(element[i].node1)-1][int(element[i].node4)-1]+=(-1/complex(element[i].value))
                    M[int(element[i].node2)-1][int(element[i].node3)-1]+=(-1/complex(element[i].value))
                    M[int(element[i].node2)-1][int(element[i].node4)-1]+=(1/complex(element[i].value))
            
            
            if element[i].cmpntname[0]=='E':
                if element[i].node1==0:
                    M[int(element[i].node2)-1][vscrc_cntr+len(node_set)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node2)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node3)-1]+=-complex(element[i].value)
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node4)-1]+=complex(element[i].value)
                elif element[i].node2==0:
                    M[int(element[i].node1)-1][vscrc_cntr+len(node_set)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node1)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node3)-1]+=-complex(element[i].value)
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node4)-1]+=complex(element[i].value)
                elif element[i].node3==0:
                    M[int(element[i].node1)-1][vscrc_cntr+len(node_set)-1]+=1
                    M[int(element[i].node2)-1][vscrc_cntr+len(node_set)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node1)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node2)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node4)-1]+=complex(element[i].value)
                elif element[i].node4==0:
                    M[int(element[i].node1)-1][vscrc_cntr+len(node_set)-1]+=1
                    M[int(element[i].node2)-1][vscrc_cntr+len(node_set)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node1)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node2)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node3)-1]+=-float(element[i].value)
                else:
                    M[int(element[i].node1)-1][vscrc_cntr+len(node_set)-1]+=1
                    M[int(element[i].node2)-1][vscrc_cntr+len(node_set)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node1)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node2)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node3)-1]+=-complex(element[i].value)
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node4)-1]+=complex(element[i].value)
            
            
            if element[i].cmpntname[0]=='H':
                if element[i].node1==0:
                    M[int(element[i].node2)-1][vscrc_cntr+len(node_set)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node2)-1]+=-1
                elif element[i].node2==0:
                    M[int(element[i].node1)-1][vscrc_cntr+len(node_set)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node1)-1]+=1
                else:    
                    M[int(element[i].node1)-1][vscrc_cntr+len(node_set)-1]+=1
                    M[int(element[i].node2)-1][vscrc_cntr+len(node_set)-1]+=-1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node1)-1]+=1
                    M[vscrc_cntr+len(node_set)-1][int(element[i].node2)-1]+=-1
                M[vscrc_cntr+len(node_set)-1][int(current_dict[element[i].voltageSource][0])-1]+=complex(element[i].value)
                if current_dict[element[i].voltageSource][1]==0:
                    M[int(current_dict[element[i].voltageSource][0])-1][int(current_dict[element[i].voltageSource][2])-1]+=-1
                    M[int(current_dict[element[i].voltageSource][2])-1][int(current_dict[element[i].voltageSource][0])-1]+=-1
                elif current_dict[element[i].voltageSource][2]==0:
                    M[int(current_dict[element[i].voltageSource][0])-1][int(current_dict[element[i].voltageSource][1])-1]+=1
                    M[int(current_dict[element[i].voltageSource][1])-1][int(current_dict[element[i].voltageSource][0])-1]+=1
                else:    
                    M[int(current_dict[element[i].voltageSource][1])-1][int(current_dict[element[i].voltageSource][0])-1]+=1
                    M[int(current_dict[element[i].voltageSource][2])-1][int(current_dict[element[i].voltageSource][0])-1]+=-1
                    M[int(current_dict[element[i].voltageSource][0])-1][int(current_dict[element[i].voltageSource][1])-1]+=1
                    M[int(current_dict[element[i].voltageSource][0])-1][int(current_dict[element[i].voltageSource][2])-1]+=-1
                vscrc_cntr+=1
                
                
            if element[i].cmpntname[0]=='F':
                if element[i].node1==0:
                    M[int(element[i].node2)-1][int(current_dict[element[i].voltageSource][0])-1]+=-complex(element[i].value)
                elif element[i].node2==0:
                    M[int(element[i].node1)-1][int(current_dict[element[i].voltageSource][0])-1]+=complex(element[i].value)
                else:
                    M[int(element[i].node1)-1][int(current_dict[element[i].voltageSource][0])-1]+=complex(element[i].value)
                    M[int(element[i].node2)-1][int(current_dict[element[i].voltageSource][0])-1]+=-complex(element[i].value)
                if current_dict[element[i].voltageSource][1]==0:
                    M[int(current_dict[element[i].voltageSource][0])-1][int(current_dict[element[i].voltageSource][2])-1]+=-1
                    M[int(current_dict[element[i].voltageSource][2])-1][int(current_dict[element[i].voltageSource][0])-1]+=-1
                elif current_dict[element[i].voltageSource][2]==0:
                    M[int(current_dict[element[i].voltageSource][0])-1][int(current_dict[element[i].voltageSource][1])-1]+=1
                    M[int(current_dict[element[i].voltageSource][1])-1][int(current_dict[element[i].voltageSource][0])-1]+=1
                else:    
                    M[int(current_dict[element[i].voltageSource][1])-1][int(current_dict[element[i].voltageSource][0])-1]+=1
                    M[int(current_dict[element[i].voltageSource][2])-1][int(current_dict[element[i].voltageSource][0])-1]+=-1
                    M[int(current_dict[element[i].voltageSource][0])-1][int(current_dict[element[i].voltageSource][1])-1]+=1
                    M[int(current_dict[element[i].voltageSource][0])-1][int(current_dict[element[i].voltageSource][2])-1]+=-1
        x = np.linalg.solve(M, b)
        print("Node voltages and current through voltage sources in order is given in the following matrix")
        print(x)
            
except IOError:
    print('Invalid file')
    

    exit()
