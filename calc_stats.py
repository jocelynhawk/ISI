import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats import multicomp
from itertools import product


data = pd.read_excel('outputclean4.xlsx')
print(data)
rows=[]
all_data_list=[]
levels = ['dis','mid','pro']
for level in ['dis','mid','pro']:
    for cat in ['con','inj']:
        data = pd.read_excel('outputclean4.xlsx',sheet_name=level +'_' + cat)
        data['category']=cat
        data['level']=level
        all_data_list.append(data.reset_index())
        data = data.set_index('p')
        for p in [30,60,90,120,150,180,210]:
            avg = data.loc[p,'perc_l'].mean()
            std = data.loc[p,'perc_l'].std()
            rows.append([level,cat,p,avg,std])
        

final_data = pd.DataFrame(rows,columns=['level','group','p','avg','std'])
final_data = final_data.set_index(['level','group'])
all_data = pd.concat(all_data_list)

def twoway_anova(data_raw):
    data_raw = data_raw.set_index('level')
    print(data_raw)
    anova_results=[]
    tukey_results=[]
    for level in levels:
        data = data_raw.loc[level]
        model = ols('perc_l ~ C(p) + C(category) + C(p):C(category)',data=data).fit()
        print(level)
        result = sm.stats.anova_lm(model,typ=2)
        mclong=multicomp.MultiComparison(data['p'],data['category'])
        print('MCLON: ',mclong.tukeyhsd())
        anova_results.append(result)
        data_p = data.set_index('p')
        data = data.reset_index()[['perc_l','p','category']].dropna()
        print(data)
        print("p ",data.p)
        print('category ',data.category)
        data['p']=data['p'].astype(str)
        data['combination'] = data.p + " / " + data.category
        tukey = multicomp.pairwise_tukeyhsd(endog=data['perc_l'], groups=data['combination'], alpha=0.05) 
        print(tukey)
        tukey_df = pd.DataFrame(data=tukey._results_table[1:],columns=tukey._results_table[0])                  
        tukey_results.append(tukey_df)


    return anova_results,tukey_results

anova_results,tukey_results = twoway_anova(all_data)
with pd.ExcelWriter('final_data4.xlsx',engine='xlsxwriter') as writer:  
    final_data.to_excel(writer,sheet_name = 'means',encoding='utf-8')
    for i in range(0,3):
        anova_results[i].to_excel(writer,sheet_name = levels[i]+'_anova',encoding='utf-8')
        tukey_results[i].to_excel(writer,sheet_name = levels[i]+'_tukey',encoding='utf-8')

