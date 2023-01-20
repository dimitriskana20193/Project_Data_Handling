import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 


# Read the tabular data, tab seperated 
Batch_info = pd.read_csv('/home/dimitriskana/workspace/pantelis_project/metadata/batch_info.csv'
,sep='\t')

Batch_info['StartDate'] = pd.to_datetime(Batch_info['StartDate'])
Batch_info['EndDate'] = pd.to_datetime(Batch_info['EndDate'])
# change str to datetime
Batches = pd.read_csv('/home/dimitriskana/workspace/pantelis_project/metadata/batch_phase.csv',
sep='\t')
Batches['StartDate'] = pd.to_datetime(Batches['StartDate'])
Batches['EndDate'] = pd.to_datetime(Batches['EndDate'])
#did the same for the other metadata file
#change the type also for the sensors 
Temp_S1 = pd.read_csv('/home/dimitriskana/workspace/pantelis_project/400E_Temp1.csv', sep = '\t')
Temp_S1['timestamp'] = pd.to_datetime(Temp_S1['timestamp'])
Temp_S2 = pd.read_csv('/home/dimitriskana/workspace/pantelis_project/400E_Temp2.csv', sep = '\t')
Temp_S2['timestamp'] = pd.to_datetime(Temp_S2['timestamp'])
PH_S1 = pd.read_csv('/home/dimitriskana/workspace/pantelis_project/400E_PH1.csv', sep = '\t')
PH_S1['timestamp'] = pd.to_datetime(PH_S1['timestamp'])
PH_S2 = pd.read_csv('/home/dimitriskana/workspace/pantelis_project/400E_PH2.csv', sep='\t')
PH_S2['timestamp'] = pd.to_datetime(PH_S2['timestamp'])
# create array with nans in order to fill the the batch ID after analysis  

"""what we do here is that we select the indices that correspond with the cultivation phase. 
 Then turn them into an array and deduct 1. That is to ensure to get the correct ID. 
We get the Id that way because the StartDate of cultivation happen before the test or after it
 So we want the previous ID as we can see it in the Batch_info dataframe 
Afterwards we match the labels while droping the index in order to get 1-1 replacement.""" 
# create array with nans in order to fill the the batch ID after analysis  
Batches['BatchID'] = np.nan 

Batches = Batches[Batches['BatchPhase']=='cultivation'].reset_index()
Batches['BatchDuration'] = Batches['EndDate']-Batches['StartDate']
Batches['BatchID'] =Batch_info.loc[(np.array(Batches['index'].to_list())-1).tolist(),'BatchID'].reset_index().drop('index', axis = 1)
Batches.drop('index', axis = 1, inplace =True)

Times = Batches.copy().drop(['BatchPhase'],axis = 1)
Batches.drop(['StartDate', 'EndDate','BatchPhase'], axis = 1, inplace = True)
Agg = pd.DataFrame(index = Temp_S1.index, columns = ['Temp_1','Temp_2','Ph_1','Ph_2'])
Agg['Temp_1'] = Temp_S1['value']
Agg['Temp_2'] = Temp_S2['value']
Agg['Ph_1'] = PH_S1['value']
Agg['Ph_2'] = PH_S2['value']

# the aggregated values are mean, std, max, min and the vertical orientation is Temprature on top and Phase bellow
Batches['Sensor1'] = np.array([Agg['Temp_1'].mean(), Agg['Temp_1'].std(), Agg['Temp_1'].max(), Agg['Temp_1'].min(),
Agg['Ph_1'].mean(),Agg['Ph_1'].std(),Agg['Ph_1'].max(),Agg['Ph_1'].min(), np.nan])
Batches['Sensor2'] = np.array([Agg['Temp_2'].mean(), Agg['Temp_2'].std(), Agg['Temp_2'].max(), Agg['Temp_2'].min(),
Agg['Ph_2'].mean(), Agg['Ph_2'].std(), Agg['Ph_2'].max(), Agg['Ph_2'].min(), np.nan])



fig,ax = plt.subplots(nrows = 3, ncols = 3, figsize = (10,5) )
#flatten axes
ax = ax.ravel()
Agg_BatchT = []
Agg_BatchPH = []
# for the phase sensors as well 
fig2,ax2 = plt.subplots(nrows = 3, ncols = 3, figsize = (10,5) )
#flatten axes
ax2= ax2.ravel()

for j,rows in Times.iterrows():
    # find the window of values we want and calculate the difference
    sd = Times.iloc[j]['StartDate']
    ed = Times.iloc[j]['EndDate']
    tempd = Temp_S2.loc[(Temp_S2['timestamp']>=sd) &
    (Temp_S2['timestamp']<=ed)
    ].reset_index().drop('index', axis = 1) - Temp_S1.loc[(Temp_S1['timestamp']>=sd) &
    (Temp_S1['timestamp']<=ed)].reset_index().drop('index', axis = 1)
   
    Agg_BatchT.append({'BatchID':Times.iloc[j]['BatchID'],
    'BatchDuration':Times.iloc[j]['BatchDuration'],
    'TempDiffMean': tempd['value'].mean(),
    'TempDiffStd': tempd['value'].std(),
    'TempDiffMax': tempd['value'].max(),
    'TempDiffMin': tempd['value'].min()})
    ax[j].scatter(tempd.index.to_list(),tempd['value'], 
    c =tempd['value'], cmap = 'nipy_spectral' )
    ax[j].set_xlabel('Data Points')
    ax[j].set_ylabel('Temperature Sensor Difference')
    ax[j].set_title(Times.iloc[j]['BatchID'])
    #same for the phase sensors
    PH_D = PH_S2.loc[(PH_S2['timestamp']>=sd) &
    (PH_S2['timestamp']<=ed)
    ].reset_index().drop('index', axis = 1) - PH_S1.loc[(PH_S1['timestamp']>=sd) &
    (PH_S1['timestamp']<=ed)].reset_index().drop('index', axis = 1)
    
    Agg_BatchPH.append({'BatchID':Times.iloc[j]['BatchID'],
    'BatchDuration':Times.iloc[j]['BatchDuration'],
    'PhaseDiffMean': PH_D['value'].mean(),
    'PhaseDiffStd': PH_D['value'].std(),
    'PhaseDiffMax': PH_D['value'].max(),
    'PhaseDiffMin': PH_D['value'].min()})
    ax2[j].scatter(PH_D.index.to_list(),PH_D['value'], 
    c =tempd['value'], cmap = 'nipy_spectral' )
    ax2[j].set_xlabel('Data Points')
    ax2[j].set_ylabel('Phase Sensor Difference')
    ax2[j].set_title(Times.iloc[j]['BatchID'])

plt.show()
    
DF_T = pd.DataFrame(Agg_BatchT)
DF_PH = pd.DataFrame(Agg_BatchPH)

DF_T.to_csv()
DF_PH.to_csv()
Times.to_csv()