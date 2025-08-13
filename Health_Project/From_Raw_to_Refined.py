import pandas as pd
import numpy as np

#setting upp a bunch of dictionarys and lists later to be used in the selecting, filtering and modifying of data
list_of_columns=[
    'A001',
    'A002', 
    'A003', 
    'A004', 
    'A005',
    'A006' ,
    'A008', 
    'A009', 
    'A099', 
    'A170',
    'A173', 
    'C006', 
    'E035', 
    'E040', 
    'E124', 
    'E220', 
    'E235', 
    'E236',
    'E268', 
    'F028', 
    'F028B', 
    'F063', 
    'G006', 
    'G027A', 
    'G255', 
    'H001',
    'H006_01', 
    'H006_02', 
    'H006_03', 
    'H006_04', 
    'H006_05', 
    'S002VS',
    'S003',
    'S017', 
    'S018', 
    'S020', 
    'X001', 
    'X003', 
    'X007', 
    'X011',
    'X013', 
    'X025A_01',
    'X028',
    'X045',
    'X047_WVS',
    'X049', 
    'X050C', 
    'Y001', 
    'Y002',
    'Y003', 
    'Y010', 
    'Y011', 
    'Y011A', 
    'Y011B', 
    'Y011C', 
    'Y012', 
    'Y012A',
    'Y012B', 
    'Y012C', 
    'Y013', 
    'Y013A', 
    'Y013B', 
    'Y013C', 
    'Y014',
    'Y014A', 
    'Y014B', 
    'Y014C', 
    'Y020', 
    'Y021', 
    'Y021A', 
    'Y021B',
    'Y021C', 
    'Y022', 
    'Y022A', 
    'Y022B', 
    'Y022C', 
    'Y023', 
    'Y023A',
    'Y023B', 
    'Y023C', 
    'Y024', 
    'Y024A', 
    'Y024B', 
    'Y024C']
list_of_columns_inverting=[
    'A001',
    'A002', 
    'A003', 
    'A004', 
    'A005',
    'A006',
    'A008', 
    'A009',
    'E035', 
    'E040', 
    'E124', 
    'E220',
    'F028', 
    'F028B', 
    'G255', 
    'H001',
    'H006_01', 
    'H006_02',
    'H006_03',
    'H006_04', 
    'H006_05', 
    'S024',
    'X045_val',
    'X047_WVS']
A099_dict={
    0 :'Not a member',
    1 :'Inactive member',
    2 :'Active member'
}
X001_dict={
    1 :'Male',
    2 :'Female'
}
X007_dict={
    1 :'Married',
    2 :'Living together as married',
    3 :'Divorced',
    4 :'Separated',
    5 :'Widowed',
    6 :'Single/Never married'
}
X028_dict={
    1 :'Full time',
    2 :'Part time',
    3 :'Self employed',
    4 :'Retired',
    5 :'Housewife',
    6 :'Students',
    7 :'Unemployed',
    8 :'Other'
}
X045_dict={
    1 :'Upper class',
    2 :'Upper middle class',
    3 :'Lower middle class',
    4 :'Working class',
    5 :'Lower class'
}
X049_dict={
    1 :'under 2,000',
    2 :'2,000-5,000',
    3 :'5,000-10,000',
    4 :'10,000-20,000',
    5: '20,000-50,000',
    6: '50,000-100,000',
    7 :'100,000-500,000',
    8 :'500,000 and more'
}
remove_perc=[
    'CPI Change (%)',
    'Forested Area (%)',
    'Gross primary education enrollment (%)',
    'Gross tertiary education enrollment (%)',
    'Agricultural Land( %)',
    'Out of pocket health expenditure',
    'Out of pocket health expenditure',
    'Population: Labor force participation (%)',
    'Tax revenue (%)',
    'Total tax rate',
    'Unemployment rate'
    ]
remove_dollar=[
    'Minimum wage',
    'GDP',
    'Gasoline Price'
]
remove_comma=[
    'Urban_population',
    'Population',
    'Co2-Emissions',
    'Armed Forces size',
    'Land Area(Km2)',
    'Density\n(P/Km2)',
    'CPI'
]
remove_happiness=[
    'Happiness score',
    'GDP per capita',
    'Social support',
    'Freedom to make life choices'	,
    'Generosity',
    'Perceptions of corruption'
]

#getting the questions asked by World Values Survey, a global project that interview people all over the world about health, opions and values
question= pd.read_excel("raw_data/List_of_Variables1981_2022.xlsx")
question=question.loc[(question["Variable"].isin(list_of_columns))]
question=question[["Variable","Title","WVS7","WVS6"]]
question=question.rename(columns={
    "Variable":"question",
    "Title":"description",
    "WVS7":"wvs7",
    "WVS6":"wvs6"
    })
question.to_csv("data/question_table.csv",index=False)
print('description of world values survey question done')

#incoperating all data from World Values Suvery, and global project that interview people all over the world about health, opions and values
df=pd.read_csv("raw_data/WVS_1981-2022.csv")
df=df[list_of_columns]
df=df.clip(lower=-1)
df=df.replace(-1,np.nan)

#renaming columns that is numeric and shouldn't be
df["X045_val"]=df["X045"]
df=df.replace({
    'A099':A099_dict,
    'X001':X001_dict,
    'X007':X007_dict, 
    'X028':X028_dict,
    'X045':X045_dict, 
    'X049':X049_dict
})

#correcting values so each is right side up and 1-10
for columns in df.columns: 
    if columns in (list_of_columns_inverting):
        max=df[columns].max()
        test2=(df[columns]*-1)+max+1 #invert the values
        df[columns]=test2+(test2-1)*((10-max)/(max-1)) #normalize values to 1-10 from x 

#countries table for mearging between different datasets with proper country names, taken from wikipedia
countries=pd.read_csv("raw_data/ISO_3166-1_2.csv")
countries=countries[["English short name \n (using title case)","Alpha-2 code","Numeric code"]]
countries=countries.rename(columns={
    "English short name \n (using title case)":"country_name",
    "Alpha-2 code":"alpha2_code",
    "Numeric code":"country_code"
    })

df=pd.merge(df,countries,how="left",left_on="S003",right_on="country_code")
df.to_csv("data/data_individual_lvl.csv",index=False)
print('data on individual level done')

#manual addition of columns not to weight, like year and what country
list_not_to_weigh=[
    'S017',
    'S002VS',
    'S018',
    'S020',
    'country_code'
]
#looks for things which arn't integer and floaters and remove from weighting
for columns in df.columns:
    type=df[columns].dtype
    if type not in ['float64','int64']:
        list_not_to_weigh.append(columns)

df_w=df
# returns original table as weighted table
for columns in df_w.columns:
    if columns not in list_not_to_weigh:
        df_w[columns]=df_w[columns]*df_w["S017"]
#grouping by country to make a country table and which vawe of study it was on
df_country=df_w.groupby(['country_name','S002VS']).mean(numeric_only=True)
#get a list with the highest wave of reasarchg a country have been in.
list_most_recent_by_country=df_w.groupby('country_name')['S002VS'].max('S002VS')
list_most_recent_by_country=list_most_recent_by_country.reset_index()

# geting the location of rows to filter down later. 
list_of_recent=[]
x=0
while x<=len(list_most_recent_by_country)-1:
    num=df_country.index.get_loc(tuple(list_most_recent_by_country.loc[x].tolist()))
    list_of_recent.append(num)
    x=x+1

#selecting only most recent, data
df_country=df_country.iloc[list_of_recent]
df_country=df_country.reset_index()

#adding on non nuimeric information again.
countries=countries[["country_code","alpha2_code"]]
df_country=pd.merge(df_country,countries,how="left",left_on="country_code",right_on="country_code")

#geting suicide information from WHO - World Health organization, 
suicide=pd.read_csv("raw_data/crudeSuicideRates.csv")
# selecting one row per country and looking att both sexes. picking 2015 since it's the most recent data that is accurate
suicide=suicide.loc[suicide["Dim1"]=="Both sexes"]
suicide=suicide.loc[suicide["Period"]==2015]
suicide=suicide[["Location","First Tooltip"]]
suicide=suicide.rename(columns={
    "First Tooltip":"crude_suicide_per_100,000"
    })
data_suc=df_country.merge(suicide,left_on="country_name",right_on="Location",how="left")

#data taken from following citation, it's a merge of a lot of different datasets about countries education, population, etc... "Nidula Elgiriyewithana. (2023). Global Country Information Dataset 2023 [Data set]. Kaggle. https://doi.org/10.34740/KAGGLE/DSV/6101670"
info=pd.read_csv("raw_data/world-data-2023.csv")
df_country_added_info=data_suc.merge(info,left_on="alpha2_code",right_on="Abbreviation",how="left")

#removing comas and other non number symbols and converting to float
for columns in df_country_added_info.columns:
    if columns in (remove_perc):
        df_country_added_info[columns]=df_country_added_info[columns].str.replace('%','').str.replace(',','').astype('float')
    if columns in (remove_dollar):
        df_country_added_info[columns]=df_country_added_info[columns].str.replace('$','').str.replace(',','').astype('float')
    if columns in (remove_comma):
        df_country_added_info[columns]=df_country_added_info[columns].str.replace(',','').astype('float')


df_country_added_info["gdp_capita"]=df_country_added_info["GDP"]/df_country_added_info["Population"]

#this is the world happines report and is given out by a partnership of Gallup, the Oxford Wellbeing Research Centre and the UN Sustainable Development Solutions Network. this is the main i will compare against the WVS
happines_report=pd.read_csv("raw_data/world_happiness_combined.csv",delimiter=";")

#taken the most recent data from tyhe report
listy=happines_report.groupby('Country')['Year'].max('Year')
listy=listy.reset_index()
df_temp=pd.DataFrame()
list_of_recent_2=[]
x=0
while x<=len(listy)-1:
    country_temp=listy.iloc[x,0]
    year_temp=listy.iloc[x,1]
    df_temp=pd.concat([df_temp,happines_report.loc[(happines_report["Country"]==country_temp)&(happines_report["Year"]==year_temp)]],ignore_index=True)
    x=x+1

# removing commas to dots
for columns in df_temp.columns:
    if columns in remove_happiness:
        df_temp[columns]=df_temp[columns].str.replace(',','.').astype('float')

#adding on the information to the data table
df_country_added_info=df_country_added_info.merge(df_temp,left_on='country_name',right_on='Country',how='left')
df_country_added_info["world_happiness_report_rank"]=df_country_added_info["Happiness score"].rank(ascending=False)

#this is the prevalence of deppresive disorder in each country, from IHME, Global Burden of Disease (2024)
deppresion=pd.read_excel("raw_data/deppresive_prelavece_country.xlsx")
deppresion=deppresion.rename(columns={'prevalence':'deppresion_percent'})
df_country_added_info=df_country_added_info.merge(deppresion, left_on="country_name",right_on="Country/area",how="left")

#this is the amount of DALY rates from non-communicable diseases (NCDs), also from IHME, Global Burden of Disease (2024)
daily=pd.read_excel("raw_data/dailys_world.xlsx")
df_country_added_info=df_country_added_info.merge(daily, left_on="country_name",right_on="Country",how="left")

df_country_added_info.to_csv('data/data_country_lvl.csv',index=False)
print('adding additional information done')
