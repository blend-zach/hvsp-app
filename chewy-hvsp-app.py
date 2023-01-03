import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn import metrics
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import plotly.express as px
import json

st.set_page_config(
    page_title="Chewy HVSP Opportunities",
    page_icon="✅",
    layout="wide",
)



st.write("""
# HVSP Candidate Pages

This app helps you to choose the thresholds to select **Keywords** are more likely to create new HVSP!

By adjusting thresholds, you can choose the HVSP candidates that meet your minimal requirements. 


""")

# Read CSV data
data_path =".\data/"
filename = "hvsp_run5.csv"

# --Column names
# keyword
# Highest_Search_Volume
# Keywords
# Chewy_URL
# Total_Search_Volume
# relevance_score
# CTR
# product_count


hvsp_file = data_path + filename
df_hvsp = pd.read_csv(filename)
# df_hvsp = pd.read_csv("~/Downloads/hvsp_run_with_revision (1).csv")
df_hvsp['CTR'] = df_hvsp['CTR'].fillna(-0.01)
all_kw = df_hvsp['keyword'].unique().tolist()

keyword_list = df_hvsp.keyword.unique()
#st.write(keyword_list)


st.sidebar.header('User Input Parameters')

# Collects user input features into dataframe

def user_input_features():
    
    keyword_selected = st.sidebar.selectbox('keyword',keyword_list)    
    #st.sidebar.write(keyword_selected)
    
    ctr_threshold = st.sidebar.slider('CTR Threshold', -0.01,1.0,-0.01)
    sv_threshold = st.sidebar.slider('Total Search Volume Threshold', 0,10000,0)
    prod_ct_threshold = st.sidebar.slider('Product Count Threshold', 5,100,0)
    Relevance_threshold = st.sidebar.slider('Relevance Score Threshold', 0,10,0)
    
    
    
    data = {'ctr_threshold': ctr_threshold,
            'sv_threshold': sv_threshold,
            'prod_ct_threshold': prod_ct_threshold,
            'Relevance_threshold': Relevance_threshold,
            'keyword_selected': keyword_selected,
            
            }
    
    
    features = pd.DataFrame(data, index=[0])
    return features

input_df = user_input_features()

st.sidebar.markdown("""---""")

# st.sidebar.write("Sort results by:")    
# sort_ctr = st.sidebar.checkbox('Click Through Rate')
# sort_sv = st.sidebar.checkbox('Total Search Volume')
# sort_rs = st.sidebar.checkbox('Relevance Scores')
# sort_pc = st.sidebar.checkbox('Product Count')

st.sidebar.markdown("""---""")

keyword_selected = input_df.keyword_selected[0]
ctr_threshold = input_df.ctr_threshold[0]
sv_threshold = input_df.sv_threshold[0]
prod_ct_threshold = input_df.prod_ct_threshold[0]
Relevance_threshold = input_df.Relevance_threshold[0]


# PART 1: Print selected keyword
st.subheader('Current selected keyword:   '+ str(keyword_selected))

df_keyword = df_hvsp[(df_hvsp['keyword'] == keyword_selected)]

# st.table(df_keyword)

str1 = "- Number of products:" + "   **" + str(df_keyword['product_count'].values[0]) + "**"
str2 = "- Total Search Volume:" + "   **" +  str(df_keyword['Total_Search_Volume'].values[0]) + "**"
str3 = "- Relevance Score:" + "   **" +  str(df_keyword['relevance_score'].values[0]) + "**"
str4 = "- Click Through Rate:" + "   **" +  str(df_keyword['CTR'].values[0]) + "**"
str5 = "- Keywords in the same cluster:" + "  " + str(df_keyword['Keywords (in the same cluster)'].values[0])
str6 = "- Keyword SV:" + "   **" +  str(df_keyword['keyword sv'].values[0]) + "**"

# make any grid with a function
def make_grid(cols,rows):
    grid = [0]*cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid


mygrid = make_grid(3,2)
mygrid[0][0].write(str1)
mygrid[0][1].write(str2)
mygrid[1][0].write(str3)
mygrid[1][1].write(str4)
mygrid[2][0].write(str5)
mygrid[2][1].write(str6)

st.markdown("- URL: " + "   " +  str(df_keyword['Chewy_URL'].values[0]))



# PART 2: Add filters to the dataframe
st.subheader('Current selected thresholds:')

# st.markdown("- Click Through Rate at least:      >= " + str(ctr_threshold) + "")
# st.markdown("- Search Volume at least:       >= " + str(sv_threshold) + "")
# st.markdown("- Number of products:       >= " + str(prod_ct_threshold) + "")
# st.markdown("- Relevance score at least:       >= " + str(prod_ct_threshold) + "")


kpi1, kpi2, kpi3, kpi4 = st.columns(4)

# fill in those three columns with respective metrics or KPIs
kpi1.metric(
    label="Relevance score ⏳",
    value=Relevance_threshold,
)

kpi2.metric(
    label="Total Search Volume 💍",
    value=sv_threshold,
)

kpi3.metric(
    label="Number of products #",
    value=prod_ct_threshold,
)

kpi4.metric(
    label="Click Through Rate #",
    value=ctr_threshold,
)

# Apply filters
st.subheader('All keywords satisfy the selected thresholds:')

data = df_hvsp[(df_hvsp['CTR']>=ctr_threshold) & (df_hvsp['Total_Search_Volume']>=sv_threshold) & (df_hvsp['product_count']>=prod_ct_threshold) & (df_hvsp['relevance_score']>=Relevance_threshold)] 

# # Sort by selected columns
# if sort_ctr:
#     #st.write("Sort by CTR")
#     data.sort_values(by = ['CTR'], ascending = [False])
    
# if sort_sv:
#     #st.write("Sort by Total_Search_Volume")
#     data.sort_values(by = ['Total_Search_Volume'], ascending = [False])  
    
# if sort_rs:
#     #st.write("Sort by Relevance Scores")
#     data.sort_values(by = ['relevance_score'], ascending = [False]) 
    
# if sort_pc:
#     #st.write("Sort by Product Count")
#     data.sort_values(by = ['product_count'], ascending = [False]) 

#st.table(data)    

# PART 3: Show the dataframe
gb = GridOptionsBuilder.from_dataframe(data)
gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
gb.configure_side_bar() #Add a sidebar
gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
# gb.configure_column("keyword_", header_name="revised_keyword", editable=False)
gb.configure_column("keyword", editable=True)
gridOptions = gb.build()


grid_response = AgGrid(
    data,
    gridOptions=gridOptions,
    data_return_mode='AS_INPUT', 
    update_mode='MODEL_CHANGED', 
    fit_columns_on_grid_load=False,
    # theme='', #Add theme color to the table
    enable_enterprise_modules=True,
    height=350, 
    width='100%',
    # reload_data=True
)

data = grid_response['data']
selected = grid_response['selected_rows'] 
 
df = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df


# PART 4: Some charts and stats
st.subheader('Statistics after applying filters')


# 4 boxplots
fig_col1, fig_col2= st.columns(2)

with fig_col1:
    st.markdown("#### Boxplot of CTR")
    fig = px.box(data, y="CTR")
    st.write(fig)

with fig_col2:
    st.markdown("#### Boxplot of Relevance")
    fig2 = px.box(data, y="relevance_score")
    st.write(fig2)
    
    
fig_col1, fig_col2= st.columns(2)

with fig_col1:
    st.markdown("#### Boxplot of Product Counts")
    fig = px.box(data, y="product_count")
    st.write(fig)

with fig_col2:
    st.markdown("#### Boxplot of Highest Search Volume")
    fig2 = px.box(data, y="keyword sv")
    st.write(fig2)    
    


# Scatter Plots

fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    st.markdown("#### CTR vs. Relevance")
    fig1 = px.scatter(
        data_frame=data, y="relevance_score", x="CTR"
    )
    st.write(fig1)
    
with fig_col2:
    st.markdown("#### CTR vs. Total Search Volume")
    fig2 = px.scatter(
        data_frame=data, y="Total_Search_Volume", x="CTR"
    )
    st.write(fig2)

    
# histogramS

fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    st.markdown("#### Number of Pages by Product Counts")
    fig1 = px.histogram(data_frame=data, x="product_count")
    st.write(fig1)
   
with fig_col2:
    st.markdown("#### Number of Pages by Relevance")
    fig2 = px.histogram(data_frame=data, x="relevance_score")
    st.write(fig2)    
    


# df = data.describe(include='all').fillna("").astype("str")
# st.write(df)


# PART 5: Write the new results to jason file for production. ------------- to do
if df.shape[0] > 0:
    output_candidate = df['keyword'].unique().tolist()
    output_file = {k:'true' for k in output_candidate}
    json_string = json.dumps(output_file)
    st.download_button('Download JSON output', json_string, 'data.json')
else:
    x = {}
    json_string = json.dumps(x)
    st.download_button('Download JSON output', json_string, 'data.json')

if st.sidebar.button('Save Results'):
    data.to_json("hvsp_json")
    st.sidebar.write('Json file is saved successfully!')

st.sidebar.markdown("""---""")






