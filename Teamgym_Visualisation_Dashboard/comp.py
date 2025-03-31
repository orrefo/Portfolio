import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import scipy.stats as stats
from pandas.api.types import is_numeric_dtype

# Load the dataset
@st.cache_data

def load_data():
    data = pd.read_csv('https://raw.githubusercontent.com/orrefo/Portfolio/refs/heads/new_order/Teamgym_Visualisation_Dashboard/points.csv')
    return data

def load_csv():
    data = pd.read_csv('https://raw.githubusercontent.com/orrefo/Portfolio/refs/heads/new_order/Teamgym_Visualisation_Dashboard/points_standard.csv')
    return data

df=load_data()
dfn=load_csv()

list_values=['dfri', 'efri','cfri', 'total_score_fri','dtum', 'etum', 'ctum', 'total_score_tum', 'dtram', 'etram', 'ctram', 'total_score_tram', 'total_score', 'rank_competition']
grouper=['competition','year', 'gender', 'qualification', 'age','clean_team']
group_more=['competition','year', 'gender', 'qualification', 'age','team','clean_team','clean_team_with_number','rank_competition']
corr_list=['dfri', 'efri','cfri', 'total_score_fri','dtum', 'etum', 'ctum', 'total_score_tum', 'dtram', 'etram', 'ctram', 'total_score_tram', 'total_score', 'rank_competition','year']
list_corr_val=['num_fri','dfri', 'efri', 'cfri', 'total_score_fri', 'dtum', 'etum', 'ctum', 'total_score_tum','dtram', 'etram', 'ctram', 'total_score_tram', 'total_score', 'dfri_norm', 'efri_norm', 'cfri_norm', 'total_score_fri_norm', 'dtum_norm','etum_norm','ctum_norm','total_score_tum_norm','dtram_norm','etram_norm','ctram_norm','total_score_tram_norm','total_score_norm']
group_norm=['competition','year', 'gender', 'qualification', 'age','team','clean_team','clean_team_with_number','rank_competition','comp_str','num_fri']


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    modify = st.checkbox("Add filters", key='cat')

    if not modify:
        return df

    df = df.copy()

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", grouper)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
           
            if df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = df[column].min()
                _max = df[column].max()
                step = 1
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            else:
                user_text_input = right.selectbox(
                    f"Substring or regex in {column}",df['clean_team'].unique(),index=1
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]
    return df

def filter_dataframe_norm(df: pd.DataFrame) -> pd.DataFrame:

    modify = st.checkbox("Add filters", key='norm')

    if not modify:
        return df

    df = df.copy()

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", group_norm)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
           
            if df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = df[column].min()
                _max = df[column].max()
                step = 1
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            else:
                user_text_input = right.selectbox(
                    f"Substring or regex in {column}",df[column].unique(),index=1
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]
    return df

def filter_dataframe_num(df: pd.DataFrame) -> pd.DataFrame:

    modifys = st.checkbox("Add numeric filters",key='num')

    if not modifys:
        return df

    df = df.copy()

    modification_containers = st.container()

    with modification_containers:
        to_filter_column = st.multiselect("Filter dataframe on", list_values)
        for column in to_filter_column:
            left, right = st.columns((1, 20))
            
            _min = float(df[column].min())
            _max = float(df[column].max())
            step = (_max - _min) / 100
            user_num_input = right.slider(
                f"Values for {column}",
                min_value=_min,
                max_value=_max,
                value=(_min, _max),
                step=step)
            df = df[df[column].between(*user_num_input)]
    return df

def filters_suggest(df,value,column):
    if column =='age':
        age_f=df['age'].unique()
    else:
        age_f=df[df[column]==value]['age'].unique()
    if column =='gender':
        gender_f=df['gender'].unique()
    else:
        gender_f=df[df[column]==value]['gender'].unique()
    if column =='competition':
        competition_f=df['competition'].unique()
    else:
        competition_f=df[df[column]==value]['competition'].unique()
    if column =='qualification':
        qualification_f=df['qualification'].unique()
    else:
        qualification_f=df[df[column]==value]['qualification'].unique()
    return competition_f,age_f,gender_f,qualification_f

def common_filter(df,value1,value2,column):
    a,b,c,d=filters_suggest(df,value1,column)
    xa,xb,xc,xd=filters_suggest(df,value2,column)
    competition_f=[]
    for i in a:
        if i in xa:
            competition_f.append(i)
    age_f=[]
    for i in b:
        if i in xb:
            age_f.append(i)
    gender_f=[]
    for i in c:
        if i in xc:
            gender_f.append(i)
    qualification_f=[]
    for i in d:
        if i in xd:
            qualification_f.append(i)
    return competition_f,age_f,gender_f,qualification_f

st.sidebar.title("Dashboard Navigation")
section = st.sidebar.radio(
    "Select a Section",
    [
        "Visualize data",
        "T-test, Value VS Population",
        "T-test, Value VS Value",
        "Anova for given Variable",
        "Information about Teamgym"
    ]
)

if section == "Visualize data":
    tab1,tab2=st.tabs(['Non_standardized','With number of dancers added'])
    with tab1:
        st.title("Visualize data")
        st.write("Visualize the data and find correlations, interactions and trends. Try to filter out a specific age, team or any combination of the filters.")
        filtered_df=filter_dataframe(df.copy())
        grouper0=st.selectbox('Select grouper',grouper,index=0)
        value0=st.selectbox('Select value',list_values,index=12)       
        fig011= px.box(filtered_df,x='year',y=value0,color=grouper0,points='all',hover_data=grouper)
        fig011.update_layout(title=f'Distribution of {value0} split by {grouper0} and Year')
        st.plotly_chart(fig011, key="fig011")

        scatter1=st.selectbox('Select variable',list_values,index=0)
        scatter2=st.selectbox('Select variable',list_values,index=1)
        grouper1=st.selectbox('Select colour',grouper,index=0)
        fig012=px.scatter(filtered_df,x=scatter1,y=scatter2,color=grouper1,hover_data=grouper,trendline='ols',trendline_scope='overall')
        fig012.update_layout(title=f'Correlation of {scatter1} and {scatter2}, colored by {grouper1}')
        st.plotly_chart(fig012, key='fig012')
        df_corr = filtered_df[corr_list].corr(numeric_only=True).round(2)

        df_corr_viz = df_corr.dropna(how='all')
        fig022 = px.imshow(df_corr_viz, text_auto=True,color_continuous_scale='RdBu',color_continuous_midpoint=0)
        st.plotly_chart(fig022,key='fig022',use_container_width=True)
    with tab2:
        st.title("Visualize data")
        st.write("Visualize the data and find correlations, interactions and trends, with normalized data and labeled number of gymnast in Fristående")

        filtered_df=filter_dataframe_norm(dfn.dropna().copy())
        grouper0=st.selectbox('Select grouper',group_norm,index=0,key='norm1')
        value0=st.selectbox('Select value',list_corr_val,index=12,key='norm2')       
        fig0= px.box(filtered_df,x='year',y=value0,color=grouper0,points='all',hover_data=group_norm)
        fig0.update_layout(title=f'Distribution of {value0} split by {grouper0} and Year')
        st.plotly_chart(fig0, key="fig0")

        scatter3=st.selectbox('Select variable',list_corr_val,index=0,key='norm3')
        scatter4=st.selectbox('Select variable',list_corr_val,index=1,key='norm4')
        grouper2=st.selectbox('Select colour',group_norm,index=0,key='norm5')
        fig01=px.scatter(filtered_df,x=scatter3,y=scatter4,color=grouper2,hover_data=group_norm,trendline='ols',trendline_scope='overall')
        fig01.update_layout(title=f'Correlation of {scatter3} and {scatter4}, colored by {grouper2}')
        st.plotly_chart(fig01, key='fig01')
        df_corr = filtered_df[list_corr_val].corr(numeric_only=True).round(2)

        df_corr_viz = df_corr.dropna(how='all')
        fig02 = px.imshow(df_corr_viz, text_auto=True,color_continuous_scale='RdBu',color_continuous_midpoint=0)
        st.plotly_chart(fig02,key='fig02',use_container_width=True)


elif section == "T-test, Value VS Population": 
    st.title("T-test, Value VS Population")
    st.write("Do a T-test using any ordinal variable and compare a Value and see if it's significantly better then the comparable population.")

    column=st.selectbox("Test on ordinal variable", group_more,index=7)    
    team1=st.selectbox('Select Value',df[column].unique(),index=2)
    competition_def, age_def, gender_def, qualification_def=filters_suggest(df,team1,column)
    competition_choice=st.multiselect('competition',df['competition'].unique(),competition_def)
    age_choice=st.multiselect('Age',df['age'].unique(),age_def)
    gender_choice=st.multiselect('Gender',df['gender'].unique(),gender_def)
    qualification_choice=st.multiselect('qualification',df['qualification'].unique(),qualification_def)
    df_choice=df[(df['competition'].isin(competition_choice))&(df['age'].isin(age_choice))&(df['gender'].isin(gender_choice))&(df['qualification'].isin(qualification_choice))]
    df_choice=filter_dataframe_num(df_choice)
    df_min_choice=df_choice[df_choice[column]==team1]
    df_cho=df_choice[~(df_choice[column]==team1)]
    x=41
    for i in list_values:
      st.write(team1,i)
      fig=px.box(df_choice,y=i,color=(df_choice[column]==team1),points='all',hover_data=grouper)
      fig.update_layout(title=f'Difference in {i} Between {team1} and comparable population')
    
      st.plotly_chart(fig, key=f"fig{x}")
      test=stats.ttest_ind(df_min_choice[i].dropna(),df_cho[i].dropna())
      n=len(df_min_choice.index)+len(df_cho.index)
      st.write(f"Average for {team1}: {round(df_min_choice[i].mean(),2)} and for the Competition it's:{round(df_cho[i].mean(),2)}")
      st.write(f"P-value is:{test.pvalue} T-score is:{ round(test.statistic,4)}, with n of {n}")
      st.markdown("""---""")
      x+=1

    

elif section == "T-test, Value VS Value":
    st.title("T-test, Value VS Value")
    st.write(' Do a T-test using any ordinal variable and compare two Values and see who is best')

    column=st.selectbox("Test on ordinal variable", group_more,index=7)
    left,right=st.columns((1,1))    
    team1=left.selectbox('Select Value 1',df[column].unique(),index=1)
    team2=right.selectbox('Select Value 2',df[column].unique(),index=0)
    competition_def, age_def, gender_def, qualification_def=common_filter(df,team1,team2,column)
    competition_choice=st.multiselect('competition',df['competition'].unique(),competition_def)
    age_choice=st.multiselect('Age',df['age'].unique(),age_def)
    gender_choice=st.multiselect('Gender',df['gender'].unique(),gender_def)
    qualification_choice=st.multiselect('Qualification',df['qualification'].unique(),qualification_def)
    df_choice=df[(df['competition'].isin(competition_choice))&(df['age'].isin(age_choice))&(df['gender'].isin(gender_choice))&(df['qualification'].isin(qualification_choice))]
    df_choice=filter_dataframe_num(df_choice)
    df_min_choice=df_choice[df_choice[column]==team1]
    df_cho=df_choice[df_choice[column]==team2]
    df_two_values=pd.concat([df_min_choice,df_cho])

    fig5=px.box(df_two_values,x='year',y='total_score',color=column,points='all',hover_data=grouper)
    st.plotly_chart(fig5, key="fig5")
    x=51
    for i in list_values:
      st.write(team1,i)
      fig=px.box(df_two_values,y=i,color=column,points='all',hover_data=grouper)
      fig.update_layout(title=f'Distribution of {i} for {team1} VS {team2}')
    
      st.plotly_chart(fig, key=f"fig{x}")
      test=stats.ttest_ind(df_min_choice[i].dropna(),df_cho[i].dropna())
      n=len(df_min_choice.index)+len(df_cho.index)
      st.write(f"Average for {team1}: {round(df_min_choice[i].mean(),2)}, for {team2} is:{round(df_cho[i].mean(),2)}")
      st.write(f"P-value is:{test.pvalue} T-score is:{ round(test.statistic,4)}, with n of {n}")
      st.markdown("""---""")
      x+=1

elif section=="Anova for given Variable":
    st.title("ANOVA for given Variable")
    only_num_fri=st.checkbox('with only labeld number in fri')
    if only_num_fri==True:
        column=st.selectbox("Do ANOVA on", group_norm,index=10)
        df_choice=filter_dataframe_norm(dfn.dropna().copy())
        choice_stand=['efri_norm','dfri_norm','total_score_fri_norm','total_score_fri','total_score_norm','total_score']
    else:
        column=st.selectbox("Do ANOVA on", grouper,index=0)
        df_choice=filter_dataframe(dfn.copy())
        choice_stand=['total_score','total_score_fri','total_score_tum','total_score_tram']
    x=61
    test_values=st.multiselect('What to test',list_corr_val,choice_stand)
    for i in test_values:
        left, right=st.columns((2.8,1))
        fig=px.box(df_choice,y=i,color=column,points='all',hover_data=grouper)
        fig.update_layout(title=f'Distribution of {i} split by {column}')
        x,y=stats.f_oneway(*[df_choice[df_choice[column] == variant][i].dropna() for variant in df_choice[column].unique()])
        
        left.plotly_chart(fig, key=f"fig{x}")
        anova_info=pd.DataFrame()
        for ix in df_choice[column].unique():
            temp=round(df_choice[df_choice[column]==ix][i].mean(),2)
            count=df_choice[df_choice[column]==ix][i].count()
            anova_info=pd.concat([anova_info,pd.DataFrame({ 'Group':[ix],'Mean':[temp],'Count':[count]})], ignore_index=True)
        right.dataframe(anova_info,hide_index=True)
        right.write(f'F-value: {round(x,1)}')
        right.write(f'P-value: {y}')
        right.write(f'N= {anova_info['Count'].sum()}')    
        st.markdown("""---""")

        x+=1
else:
    st.title('Info about the different types of data')
    st.subheader('different scores')
    left_i,right_i=st.columns((2,10))
    left_i.write('e...')
    right_i.write("this is the execution, it's a score between 0-10 based of how good a teamed performed(the style)")
    st.markdown("""---""")
    left_i1,right_i1=st.columns((2,10))
    left_i1.write('d...')
    right_i1.write("this is the difficulty, the combined difficulty of a performance, its from 0-upwards, no limit but usually below 12 and very age dependant( the hardness/difficulty)")
    st.markdown("""---""")
    left_i2,right_i2=st.columns((2,10))
    left_i2.write("c...")
    right_i2.write("this is the composition, does the performance include all must haves. it range from 0-2 ")
    st.markdown("""---""")
    left_i12,right_i12=st.columns((2,10))
    left_i12.write("total_score")
    right_i12.write("the combined value, (e+d+c) given for each discipline")
    st.markdown("""---""")
    st.subheader('disciplines:')
    left_i3,right_i3=st.columns((1,10))
    left_i3.write('...fri')
    right_i3.write("its  fristående, a discipline like a dance performed by the whole team(8-12) people")
    st.markdown("""---""")
    left_i4,right_i4=st.columns((1,10))
    left_i4.write('...tum')
    right_i4.write("its tumbling, a discipline performed by doing flickis and saltos on a long floor)")
    st.markdown("""---""")
    left_i5,right_i5=st.columns((1,10))
    left_i5.write("...tram")
    right_i5.write("its trampett, a discipline where you jump a small trampoline and do lots of flips in the air.")
    st.markdown("""---""")
    st.subheader('Competitions:')
    st.write("USM=      youth swedish championship(SM=svenska mästerskapen),youth's biggest competition")
    st.write("SC=       Swedish cup, a pre competition to JSM/SM")
    st.write("JSM/SM=   Juniors/Seniors biggest competition in sweden")
    st.write("JNM/NM=   Nordic Champion, biggest competition for teams in Junior/Seniors")
    st.write("JEM/EM=   European Championship, National teams and biggest competition in the world for Juniors/Seniors")  





