import matplotlib
from matplotlib import image
from matplotlib.widgets import Button
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import os
import csv
import statistics as stats
import math 


class specimen:
    def __init__(self,folder_name):
        self.folder_name = folder_name
        self.datasheets = os.listdir(master_folder_name + '/' + folder_name)
        self.trials=[]
        self.get_data()

        #Call strain function and create data frame of strain data
        self.perc_elongs = pd.DataFrame()
        baselines=[]
        pressures=[]
        for trial in self.trials:
            if trial.p == 10:
                baselines.append(trial)
            else:
                pressures.append(trial)
        
        for pressure in pressures:
            for baseline in baselines:
                try:
                    df = calc_strain(baseline.dist,pressure.dist,folder_name)
                    df['specimen'] = folder_name 
                except:
                    df = pd.DataFrame([])
                self.perc_elongs = pd.concat([self.perc_elongs,df])
        
    #Load data and create trial_data objects
    def get_data(self):
        data=np.empty([18,360])
        for sheet in self.datasheets:
            self.trials.append(trial_data(master_folder_name + '/' + self.folder_name + '/', sheet))
        


class trial_data:
    def __init__(self,folder,sheet):
        self.folder=folder[-5:-1]
        self.path = folder+sheet
        self.p = int(sheet[0:2])
        if self.p>10 and self.p%10>0:
            self.p = self.p*10
        self.load_data()
        self.clean_data()
        self.calc_dist()


    #load csv file and extract data
    def load_data(self):
        print(self.path)

        #Find first row of data
        with open(self.path) as csvfile:
            spamreader = csv.reader(csvfile)
            i = 0
            for row in spamreader:
                if len(row)>2:
                    if row[2] == 'X':
                        break
                i+=1


        #create dataframe of raw data
        #make header names by combining existing headers (mid,pro,dis) with first row(X,Y,Z)
        self.data = pd.read_csv(self.path,skiprows=i-1,usecols=range(2,18*3+2))
        markers=[]
        for i in range(0,18*3-1,3):
            header = list(self.data)[i]
            new_header = header[-4:]
            markers.append(new_header)
            self.data = pd.DataFrame.rename(self.data,columns={header:new_header})
            for j in range(0,3):
                header = list(self.data)[i+j]
                self.data = pd.DataFrame.rename(self.data,columns={header:new_header+str(self.data[header][0])})
        
        
    #remove outliers and combine XYZ columns for each marker
    def clean_data(self):
        #delete first two rows
        data = self.data.drop(labels=[0,1],axis=0)

        #calculate mean and standard deviation for each column
        avgs,stds=[],[]
        for marker in data:
            data[marker] = pd.to_numeric(data[marker])
            avgs.append(data[marker].mean())
            stds.append(data[marker].std())

            
        #add average and standard deviation values to the bottom of each column in dataframe
        avg = pd.DataFrame([avgs],columns=list(data),index=['avg'])
        std = pd.DataFrame([stds],columns=list(data),index=['std'])
        data = pd.concat([data,avg,std])
        
        #remove outliers and combine xyz columns for each marker
        self.marker_xyz = pd.DataFrame()
        for i in range(0,18*3,3):
            xyz = data.iloc[:,i:i+3].dropna().to_numpy()
            avg_pt = data.loc['avg'][i:i+3]
            std_pt = data.loc['std'][i:i+3]
            x,y,z=[],[],[]

            #Iterate through each xyz point, if fewer than 2 stds from mean, save x,y, and z values in lists 
            for row in xyz[:-2,:]:
                if np.linalg.norm(row-avg_pt)<np.linalg.norm(std_pt)*2:
                    x.append(row[0])
                    y.append(row[1])
                    z.append(row[2])

            #If no points found, set marker_xyz dataframe to nan and continue to next marker
            if len(x)==0:
                self.marker_xyz[list(data)[i][0:4]] = [np.array([float("nan")]*3)]
                continue

            #Add xyz mean for each marker to new data frame. each column is a different marker and each value is a numpy array of [x,y,z]
            self.marker_xyz[list(data)[i][0:4]] = [np.array([stats.mean(x),stats.mean(y),stats.mean(z)])]

    #Calculate distance between adjacent markers in each row
    def calc_dist(self):
        dists=[]
        for level in ['pro','mid','dis']:
            for i in range(1,6):
                category = 'control'
                marker0 = self.marker_xyz[level + str(i)][0]
                marker1 = self.marker_xyz[level + str(i+1)][0]
                d = np.linalg.norm(marker0-marker1)
                if i==3:
                    category = 'injection'
                dists.append([level,d,str(i)+str(i+1),category,self.p])
        
        #add calculated distances to dataframe and set indices to level and markers
        dist = pd.DataFrame(dists,columns=['level','d','markers','category','p'])
        dist=dist.set_index(['level','markers']).sort_index()
        self.dist=dist


def calc_strain(baseline,data1,folder):
    elongs=[]

    #iterate through levels, then through each pair of adjacent markers
    for level in levels:
        for i in range(1,6):
            markers=str(i)+str(i+1)
            #get distance between pair of markers at baseline pressure and current pressure
            d0=baseline.loc[(level,markers),'d']
            d1=data1.loc[(level,markers),'d']
            #calculate percent elongation
            elong=(d1-d0)/d0
            #set category and pressure
            category=baseline.loc[(level,markers),'category']
            p=data1.loc[(level,markers),'p']
            if math.isnan(elong)==True:
                continue
            elongs.append([level,elong,markers,category,p,folder])

    #add calculated distances to dataframe and set indices to level, category, and pressure
    perc_elong = pd.DataFrame(elongs,columns=['level','perc_l','markers','category','p','specimen'])
    #perc_elong = perc_elong.set_index(['specimen','level','category','p',]).sort_index() 
    return perc_elong
                      


#name of folder where each specimen folder is stored
master_folder_name="20221209 Data"
#list of specimen folders
folders=os.listdir(master_folder_name)
specimens=[]
levels=['pro','mid','dis']
#iterate through each specimen folder
for folder in folders:
    specimens.append(specimen(folder).perc_elongs)
total_data = pd.concat(specimens)
all_data = total_data.set_index(['specimen','level','markers','p',]).sort_index()
print(all_data)

#Write data into excel file, separating by level and category
with pd.ExcelWriter('Results.xlsx',engine='xlsxwriter') as writer:  
    for level in levels:
        for cat in ['control','injection']:
            all_data.loc[('ok',level,cat)].to_excel(writer, sheet_name=level + '_' + cat[0:3],encoding='utf-8')


            
