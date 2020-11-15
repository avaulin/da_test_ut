#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

#установим значения ссылок которые буду использоваться.
#notelection.online - копия vybory.izbirkom.ru, но без капчи 
ik_link = 'http://notelections.online/region/krasnodar?action=ik'
votes_main_link = 'http://notelections.online/region/region/krasnodar?action=show&root=1&tvd=4234220141772&vrn=4234220141768&region=23&global=null&sub_region=23&prver=2&pronetvd=1&vibid=4234220141772&type=381'
main_link = 'http://notelections.online'
kprf_name = 'КОММУНИСТИЧЕСКАЯ ПАРТИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ'

#получим страницу со сводными результатами голосования 
r = requests.get(votes_main_link)
html = r.text
soup = BeautifulSoup(html, 'lxml')

#получим ссылки на результаты голосований по всем ОИО
tags = soup.body('table')[9]('a')
links = [tag['href'] for tag in tags]

#по ссылкам ОИО найдем результаты голования на всех участках и запишем в список result
result = []
for link in links:
    cur_soup = BeautifulSoup(requests.get(main_link+link).text, 'lxml')
    KPRF_persents = [re.findall('\w+.\d+%',tag.text)[0] for tag in cur_soup.body('table')[9]('tr')[18]('td')]
    OIO_numbers = [re.findall('\d+',tag.string)[0] for tag in cur_soup.body('table')[9]('a')]
    result.extend(list(zip(OIO_numbers, KPRF_persents)))

#удалим участки ИК по которым нет сведений о составе комиссии 
ik_to_drop = ['2299','2094','2096','2099','6099','6097','6098','2393','2394','2397','2398','2399','2395','2396']
i = 0
while i < len(result):
    if result[i][0] in ik_to_drop:
        del result[i]
    else:
        i+=1
        
#по всем ИК посчитаем количество членов партии КПРФ
#с помощью post запроса будем открывать страницу каждой ИК
kprf_members_counts = []
for ik in result:
    r = requests.post(ik_link, data = {'numik':ik[0]})
    ik_soup = BeautifulSoup(r.text, 'lxml')
    kprf_members_count = re.findall(kprf_name, ik_soup.body('table')[2].text)
    kprf_members_counts.append(len(kprf_members_count))

#создадим DataFrame, процент голов приведем к числовому типу
df = pd.DataFrame(data=result, columns=['IK', 'pers'])
df['kprf'] = kprf_members_counts
df['pers'] = df['pers'].str.replace('%','').astype('float')

#вывод ответа на 1й вопрос
ik_list = df[df['kprf']==0]['IK'].to_list()
print(ik_list)

#вывод ответа на 2й вопрос
kprf = df[df['kprf']>0]['pers'].mean()
no_kprf = df[df['kprf']<1]['pers'].mean()
dif = kprf - no_kprf
print(kprf, no_kprf, dif)


# In[ ]:




