import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from scipy.optimize import curve_fit

def expFit(x, alpha, kappa):
    return alpha * np.exp(-kappa*x)

df = pd.read_csv('coupling.csv')
dplusW = df['d+w']
C = df['C']

expParam, expCov = curve_fit(expFit, dplusW, C, p0=[0.005,0.005], maxfev=10000)
print('a*e^{-kx}')
print('param [a, k] yields', expParam)
print('st. dev. [a, k] yields', np.sqrt([expCov[0][0], expCov[1][1]]))

fig, ax = plt.subplots(figsize = (6,4), dpi = 150)
plt.scatter(dplusW, C, label='estimated coupling', color='orange')
plt.plot(dplusW, expFit(dplusW, expParam[0], expParam[1]), 
         label='exponential fit', color='blue')
plt.xlabel(r'd + width (micron)', size='x-large')
plt.ylabel(r'coupling strength',  size='x-large')
plt.legend(prop={'size':'x-large'})
plt.tight_layout()
plt.show()

alpha = expParam[0]
kappa = expParam[1]
targetC = 0.0016
presetW = 0.462
dplusW_computed = -np.log(targetC/alpha)/kappa
d_computed= dplusW_computed- presetW
print('solve for d with C = '+str(targetC)+' yields d =', round(d_computed,3))


########################################
##                                    ##
##       Setting up the model         ##
##                                    ##
########################################

## Create constant

amax = 401 # number of iteration when computing eigenvalues

## Default constants
Ecm = 1.371-0.00009j
ini_C = 0.00132
XC = 1.371-0.00009j
delGamma = 0.012438968j

## Create empty dataframe for storing data
df_Eigen = pd.DataFrame(columns=['eigVal_lossDiff_applied',
                                 'eigVec_lossDiff_applied',
                                 'eigVal_lossless',
                                 'eigVec_lossless',
                                 'Coupling coeff.',
                                 'Ecm',
                                 'XC',
                                 'Ecm-XC'])

########################################
##                                    ##
##         Compute Eigenvals          ##
##                                    ##
########################################
for a in range(1,amax+1):
    C = ini_C + 0.0000015*(a-1)
    M = np.array([[ Ecm-delGamma, C  ],
                  [ C,            XC ]])
    H = np.array([[ Ecm, C  ],
                  [ C,   XC ]])
    MeigVal, MeigVec = np.linalg.eig(M)
    HeigVal, HeigVec = np.linalg.eig(H)
    # append eigenvals and eigenvectors to dataframe
    df_Eigen.loc[len(df_Eigen.index)] = [MeigVal, 
                                         MeigVec, 
                                         HeigVal, 
                                         HeigVec, 
                                         C, Ecm, 
                                         XC, Ecm-XC]

## output the dataframe
df_Eigen.to_csv('result.csv')


########################################
##                                    ##
##          Extracting data           ##
##                                    ##
########################################
## loss difference applied eigenvals
realEigVal = np.real(df_Eigen['eigVal_lossDiff_applied'].values.tolist())
compEigVal = np.imag(df_Eigen['eigVal_lossDiff_applied'].values.tolist())

realEigVal1 = [vals[0] for vals in realEigVal]
realEigVal2 = [vals[1] for vals in realEigVal]

compEigVal1 = [vals[0] for vals in compEigVal]
compEigVal2 = [vals[1] for vals in compEigVal]

realCompEigVals = [[realEigVal1, realEigVal2], [compEigVal1, compEigVal2]]

## lossless eigvals
HrealEigVal = np.real(df_Eigen['eigVal_lossless'].values.tolist())
HrealEigVal1 = [vals[0] for vals in HrealEigVal]
HrealEigVal2 = [vals[1] for vals in HrealEigVal]
HrealVals = [HrealEigVal1, HrealEigVal2]

## Extract the eigenvectors
eigVecsSet = df_Eigen['eigVec_lossDiff_applied']
eigVec1 = [[vecs[0][0], vecs[1][0]] for vecs in eigVecsSet]
eigVec2 = [[vecs[0][1], vecs[1][1]] for vecs in eigVecsSet]
HopfCoeffC = [vec[0]**2 for vec in eigVec1]
HopfCoeffE = [vec[1]**2 for vec in eigVec1]




########################################
##                                    ##
##            Generate plots          ##
##                                    ##
########################################
Cs = df_Eigen['Coupling coeff.'].values.tolist()

## plot the eigenvalues
if not os.path.exists('plots'):
    os.makedirs('plots')

names = ['Eigenval 1', 'Eigenval 2', 'Imag(', 'Re(']


fig, ax = plt.subplots(2, 1, sharex=True, figsize=(6,4), dpi=150)
for j in range(2):
    for i in range(len(realCompEigVals[j])):
        ax[j].plot(Cs, realCompEigVals[j][i], label=names[i])
        ax[j].set_ylabel(names[-j-1]+'E)', fontsize='x-large')
        if j==0:
            ax[j].plot(Cs, HrealVals[i], 
                       label='lossless modes', 
                       color='green', alpha=0.3)
plt.legend()
plt.xticks(np.linspace(Cs[0],Cs[-1],5))
plt.xlabel("coupling strength",fontsize='x-large')
plt.tight_layout()
plt.show()

