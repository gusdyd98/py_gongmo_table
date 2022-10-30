#!/usr/bin/env python
# coding: utf-8

# # 38커뮤니케이션에서 공모주 정보 가져오기 (공모수량 정보 추가)

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xlwings as xw
from openpyxl import Workbook

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from matplotlib import style

style.use('ggplot')

#get_ipython().run_line_magic('matplotlib', 'inline')
font_name=font_manager.FontProperties(fname='c:/Windows/Fonts/malgun.ttf').get_name()
rc('font', family=font_name)

plt.rcParams['axes.unicode_minus']=False

#pd.describe_option() 
pd.set_option('display.max_columns', None)
pd.set_option('display.min_rows', 15)

#from IPython.core.interactiveshell import InteractiveShell
#InteractiveShell.ast_node_interactivity = "all"

#import urllib.request, urllib.parse, urllib.error, json
from pandas import json_normalize

import requests

from bs4 import BeautifulSoup
from html_table_parser import parser_functions as parser

import datetime
import time


# In[2]:


def gongmo_stock_count(url_onepage):
    tempdata=[]
    page=1

    #url=r'http://www.38.co.kr/html/fund/index.htm?o=k&page=1'

    request=requests.get(url_onepage)

    html=request.text

    soup=BeautifulSoup(html, 'html.parser')
    #soup

    #for parse in soup.find_all('table', {'summary':'신규상장종목'}):
    #    print(parse)

    gongmo_count_data=[]
    gongmolist_df=[]
    gonmolist=soup.find('table', {'summary':'공모주 청약일정'}).find_all('a')
    cnt=0;
    for num, temp in enumerate(gonmolist):
        #print(num, temp)
        gm_name=temp.get_text()
        gm_link=temp['href']
        if(gm_name==""):
            continue
        else:
            gongmolist_df.append([gm_name, gm_link])


        url_onestk_cnt=r'http://www.38.co.kr'+gongmolist_df[cnt][1]
        request=requests.get(url_onestk_cnt)

        html=request.text

        soup=BeautifulSoup(html, 'html.parser')

        temp=soup.find('table', {'summary':'공모청약일정'}).find('table')
        #temp
        temp2=parser.make2d(temp)
        #temp2
        tempdata=pd.DataFrame(temp2[2:], columns=temp2[0])
        tempdata2=tempdata[3:6].iloc[:, 1:3]
        tempdata2.columns=['배정그룹', '배정수']
        tempdata2.reset_index(inplace=True)

        tempdata2.배정수
        aaa=tempdata2.배정수
        result=[]

        for data in aaa:
            #print(data)
            ttt=data.split('주')[0]
            #print(ttt.find('~') )
            if(ttt.find('~')>-1):
                result.append(ttt.split('~')[1])
            else:
                result.append(ttt)

        tempdata2.배정수=result
        tempdata2.배정수
        tempdata2.drop('index', axis=1, inplace=True)

        #print(gongmolist_df[cnt][0])
        #print(list(tempdata2.배정수))
        #[gongmolist_df[cnt][0]]+list(tempdata2.배정수)
        tmp1=[]
        if (cnt==0):
            gongmo_count_data=[[gongmolist_df[cnt][0]]+list(tempdata2.배정수)]
        else:
            tmp1=[gongmolist_df[cnt][0]]+list(tempdata2.배정수)
            gongmo_count_data.append(tmp1)

        cnt+=1
        #print(gongmo_count_data)

    gongmo_count_data_df=pd.DataFrame(gongmo_count_data)
    gongmo_count_data_df.columns=['종목명', '우리사주', '기관투자자', '일반청약자']
    #print(gongmo_count_data_df)
    
    return pd.DataFrame(gongmo_count_data_df)


# In[3]:


def get_gonmo_data_fr_38communication(dataname):
    tempdata=[]
    gongmo_stock_count_df=[]
    all_data=[]
    page=1

    while(1):
        #print("page : {0}" .format(page))
        exit_flag=0
        #type => '전체종목', '수요예측일정', '수요예측결과', '공모청약일정', '신규상장종목'
        datatype={'전체종목':['전체종목','http://www.38.co.kr/html/ipo/ipo.htm?o=&key=&' ],
                  '수요예측일정':['수요예측일정','http://www.38.co.kr/html/fund/index.htm?o=r&'],
                  '수요예측결과':['수요예측결과','http://www.38.co.kr/html/fund/index.htm?o=r1&'],
                  '공모청약일정':['공모주 청약일정','http://www.38.co.kr/html/fund/index.htm?o=k&'],
                  '신규상장':['신규상장종목', 'http://www.38.co.kr/html/fund/index.htm?o=nw&'] }
       
        #url = r'http://www.38.co.kr/html/fund/index.htm?o=nw&'
        url=datatype[dataname][1]
        #print(datatype[dataname][1])
        url_page=datatype[dataname][1]+'page='+str(page)
        #print(url_page)
        request=requests.get(url, {'page': str(page)})

        html=request.text

        soup=BeautifulSoup(html, 'html.parser')
        #soup

        #for parse in soup.find_all('table', {'summary':'신규상장종목'}):
        #    print(parse)


        #print(datatype[dataname][0])
        
        if(datatype[dataname][0]=='전체종목'):
            #print(1)
            temp=soup.find_all('table',{'border':"0", 'cellpadding':"4", 'cellspacing':"0",'summary':"", 'width':'100%'})
        else:
            #print(2)
            temp=soup.find_all('table', {'summary':datatype[dataname][0]})


        temp2=parser.make2d(temp[0])
        #print(temp2)

        tempdata=pd.DataFrame(temp2[2:], columns=temp2[0])
    
        tempdata.rename(columns={'기업명':'종목명', 
                                 '희망공모가(원)':'희망공모가',
                                 '공모가(원)':'확정공모가', 
                                 '공모희망가(원)':'희망공모가',
                                 '공모금액(백만원)':'공모금액(백만)'}, inplace=True)
        tempdata

        if(len(tempdata)==0 or ( (len(tempdata)==1) and (len(tempdata['종목명'][0])==0) ) ):
            exit_flag=1
            #print('break.....')
            break

        if (page==1):
            all_data=tempdata
        else:
            all_data=pd.concat([all_data, tempdata], ignore_index=True)

        #print("no_break")        
        if(datatype[dataname][0]=='공모주 청약일정'):
            #print(1)
            if(page==1):
                gongmo_stock_count_df=gongmo_stock_count(url_page)
            else:
                gongmo_stock_count_tmp=gongmo_stock_count(url_page)
                gongmo_stock_count_df=pd.concat([gongmo_stock_count_df,gongmo_stock_count_tmp], ignore_index=True)
            
            gongmo_stock_count_df=gongmo_stock_count_df.drop_duplicates()
        else:
            #print(2)
            pass
        
        page+=1
                
        if(datatype[dataname][0]=='전체종목'):
            #print(1)
            all_data=all_data.drop('주간사', axis=1)
        else:
            pass
        
        all_data=all_data.drop_duplicates()
        
    #print('return before.....')
    #print(all_data)
    #print(gongmo_stock_count_df)
    if( (datatype[dataname][0]=='공모주 청약일정') ): # & (exit_flag==1) ):  
        #print('return before2.....')
        return     all_data, gongmo_stock_count_df
    else:
        return     all_data


# In[4]:


####get_ipython().run_cell_magic('time', '', ")
all_ipo=get_gonmo_data_fr_38communication('전체종목')
all_suyo=get_gonmo_data_fr_38communication('수요예측일정')
all_suyo_rslt=get_gonmo_data_fr_38communication('수요예측결과')
all_gongmo, all_stk_count=get_gonmo_data_fr_38communication('공모청약일정')
all_newstk=get_gonmo_data_fr_38communication('신규상장')


# In[5]:


all_1=pd.merge(all_ipo, all_suyo, how='left',on=None)
all_2=pd.merge(all_1, all_suyo_rslt, how='left', on=None)
all_3=pd.merge(all_2, all_gongmo, how='left', on=None)
all_4=pd.merge(all_3, all_stk_count, how='left', on=None)
all_5=pd.merge(all_4, all_newstk, how='left', on=None)
all_gongmo_alldata=all_5
all_gongmo_alldata.drop(['예측일','분석'], axis=1, inplace=True)

#data 타입 수정n

all_gongmo_alldata['청구일']=pd.to_datetime(all_gongmo_alldata['청구일'])
all_gongmo_alldata['신규상장일']=pd.to_datetime(all_gongmo_alldata['신규상장일'])
all_gongmo_alldata['확정공모가']=pd.to_numeric(all_gongmo_alldata['확정공모가'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['시초가(원)']=pd.to_numeric(all_gongmo_alldata['시초가(원)'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['시초/공모(%)']=pd.to_numeric(all_gongmo_alldata['시초/공모(%)'].replace('(^%)|(nan)|(%)', '', regex=True), errors='coerce')
all_gongmo_alldata['첫날종가(원)']=pd.to_numeric(all_gongmo_alldata['첫날종가(원)'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['공모금액(백만)']=pd.to_numeric(all_gongmo_alldata['공모금액(백만)'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['자본금(백만)']=pd.to_numeric(all_gongmo_alldata['자본금(백만)'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['매출액(백만)']=pd.to_numeric(all_gongmo_alldata['매출액(백만)'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['당기순이익(백만)']=pd.to_numeric(all_gongmo_alldata['당기순이익(백만)'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['현재가(원)']=pd.to_numeric(all_gongmo_alldata['현재가(원)'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['전일비(%)']=pd.to_numeric(all_gongmo_alldata['전일비(%)'].replace('(^%)|(nan)|(%)', '', regex=True), errors='coerce')
all_gongmo_alldata['공모가대비등락률(%)']=pd.to_numeric(all_gongmo_alldata['공모가대비등락률(%)'].replace('(^%)|(nan)|(%)', '', regex=True), errors='coerce')
all_gongmo_alldata['의무보유확약']=pd.to_numeric(all_gongmo_alldata['의무보유확약'].replace('(^%)|(nan)|(%)', '', regex=True), errors='coerce')
all_gongmo_alldata['우리사주']=pd.to_numeric(all_gongmo_alldata['우리사주'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['기관투자자']=pd.to_numeric(all_gongmo_alldata['기관투자자'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['일반청약자']=pd.to_numeric(all_gongmo_alldata['일반청약자'].apply(lambda x: str(x).replace(',', '')), errors='coerce')
all_gongmo_alldata['기관경쟁률']=pd.to_numeric(all_gongmo_alldata['기관경쟁률'].apply(lambda x: str(x).replace(':1', '')), errors='coerce')
all_gongmo_alldata['청약경쟁률']=pd.to_numeric(all_gongmo_alldata['청약경쟁률'].apply(lambda x: str(x).replace(':1', '')), errors='coerce')
print(all_gongmo_alldata.columns)
colname=['청구일','수요예측일','공모주일정','신규상장일', '종목명','주업종', '주간사','희망공모가','확정공모가','기관경쟁률', '의무보유확약',
         '청약경쟁률', '시초가(원)','시초/공모(%)',  '첫날종가(원)', '상태',
         '우리사주', '기관투자자', '일반청약자','공모금액(백만)','당기순이익(백만)', '자본금(백만)', 
         '매출액(백만)','현재가(원)', '전일비(%)', '공모가대비등락률(%)', '']
         
#data오류 수정n#

all_gongmo_alldata_cp=all_gongmo_alldata.copy()
all_gongmo_alldata[all_gongmo_alldata['종목명']=='지아이텍'].index
all_gongmo_alldata.loc[all_gongmo_alldata[all_gongmo_alldata['종목명']=='지아이텍'].index,'기관투자자']=16200000
all_gongmo_alldata[all_gongmo_alldata['종목명']=='지아이텍']['기관투자자']
writer = pd.ExcelWriter("C:/Users/gusdyd98gray/OneDrive/현용문서/00.공모주/gongmo_data.xlsx", mode='w',engine='xlsxwriter')
sheetname=str('rawdata_'+datetime.date.today().strftime('%Y_%m_%d'))
all_gongmo_alldata[colname].sort_values(['공모주일정'], axis=0, ascending=False).to_excel(writer, sheet_name = sheetname, encoding='utf-8', index=False)
writer.save()
writer.close()
writer.handles = None


# ----

# ## PROGRAM END

# ----

# ## PROGRAM END

# In[ ]:




