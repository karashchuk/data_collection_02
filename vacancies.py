from pprint import pprint
from bs4 import BeautifulSoup as bs
import requests
import numpy as np 
import pandas as pd
import re 

# Общие параметры
search = input('Введите название вакансии: ')
#search = 'Python'
#search = 'Python Django javascript'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
vacancies =[]

# Сбор вакансий на https://hh.ru
main_link = 'https://hh.ru'
page = 0

print ('Сбор вакансий на сайте:'+ main_link )
#params = '/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text=' + search
while page >= 0:
    params = {'L_is_autosearch': 'false','clusters': 'true','enable_snippets': 'true','text': search ,'page': page}
    response = requests.get(f'{main_link}/search/vacancy?', headers=headers, params=params).text
    #response = requests.get(f'{main_link}{params}', headers=headers).text
    soup = bs(response,'lxml')
    vac_list = soup.find_all(attrs= {'data-qa':['vacancy-serp__vacancy','vacancy-serp__vacancy vacancy-serp__vacancy_premium']})
    print (f'Лист {page+1} - {len(vac_list)} записей')
    for vacancy in vac_list:
        vac_data ={}
        name = vacancy.find('a',{'data-qa':'vacancy-serp__vacancy-title'}).getText()
        href = vacancy.find('a',{'data-qa':'vacancy-serp__vacancy-title'})['href']
        # Предложение по зарплате в разбивке
        if vacancy.find('span',{'data-qa':'vacancy-serp__vacancy-compensation'}):
            comp = vacancy.find('span',{'data-qa':'vacancy-serp__vacancy-compensation'}).getText().replace('\xa0','').split(' ')
            if len(comp) == 3:
                if comp[0] == 'от':
                    comp_max = None
                    comp_min = int(comp[1])
                elif comp[0] == 'до':
                    comp_min = None
                    comp_max = int(comp[1])
                else:
                    comp_max = None
                    comp_min = None
            else:
                comp_min = int(comp[0].split('-')[0])
                comp_max = int(comp[0].split('-')[1])
            comp_car = re.findall(r'[a-zA-Zа-яА-Я]+',comp[-1])[0]
        else:
            comp = None
            comp_max = None
            comp_min = None
            comp_car = None
        # Работодатель может быть не указан    
        empl = vacancy.find('a',{'data-qa':'vacancy-serp__vacancy-employer'})
        if empl:
            employer = empl.getText()
        else:
            employer = None 
        address = vacancy.find('span',{'data-qa':'vacancy-serp__vacancy-address'}).getText()

        vac_data['name'] = name
        vac_data['href'] = href
        vac_data['comp_min'] = comp_min
        vac_data['comp_max'] = comp_max
        vac_data['comp_car'] = comp_car
        vac_data['employer'] = employer
        vac_data['address'] = address
        vac_data['site'] = main_link
        vacancies.append(vac_data)

    # Переход на следующую страницу
    if soup.find('a',{'data-qa':'pager-next'}):
        nextpage = soup.find('a',{'data-qa':'pager-next'})
        page = int(nextpage['data-page'])
        #params = nextpage['href']
    else:
        page = -1 # выход из цикла
#pprint((vacancies))


# Сбор вакансий на https://superjob.ru
main_link = 'https://www.superjob.ru'
page = 0
params = '/vacancy/search/?keywords='+ search+'&geo%5Bc%5D%5B0%5D=1'
print ('Сбор вакансий на сайте:'+ main_link )
while page >= 0:
    response = requests.get(f'{main_link}{params}', headers=headers).text
    soup = bs(response,'lxml')
    vac_list = soup.find_all('div',{'class':'QiY08 LvoDO'})
    print (f'Лист {page+1} - {len(vac_list)} записей')
    for vacancy in vac_list:
        vac_data = {}
        name = vacancy.find('a',{'class':'icMQ_'}).getText()
        href = main_link + vacancy.find('a',{'class':'icMQ_'})['href']
        # Предложение по зарплате в разбивке
        comp = vacancy.find('span',{'class':'_3mfro _2Wp8I _31tpt f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}).getText().replace('\xa0','')
        if len(re.findall(r'\d+',comp)) == 2:
            comp_min = int(re.findall(r'\d+',comp)[0])
            comp_max = int(re.findall(r'\d+',comp)[1])
            comp_car = re.findall(r'[a-zA-Zа-яА-Я]+',(re.findall(r'\d+[a-zA-Zа-яА-Я]+',comp)[0]))[0]
        elif len(re.findall(r'\d+',comp)) == 1:
            if comp[:2] == 'от':
                comp_min = int(re.findall(r'\d+',comp)[0])
                comp_max = None
            else:
                comp_min = None
                comp_max = int(re.findall(r'\d+',comp)[0])
            comp_car = re.findall(r'[a-zA-Zа-яА-Я]+',(re.findall(r'\d+[a-zA-Zа-яА-Я]+',comp)[0]))[0]
        else:
            comp_min = None
            comp_max = None
            comp_car = None

        empl = vacancy.find('span',{'class':'_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI'})
        if empl:
            employer = empl.getText()
        else:
            employer = None        
        #employer = vacancy.find('span',{'class':'_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI'}).getText()
        address = vacancy.find('span',{'class':'_3mfro f-test-text-company-item-location _9fXTd _2JVkc _2VHxz'}).findChildren()[2].getText()

        vac_data['name'] = name
        vac_data['href'] = href
        vac_data['comp_min'] = comp_min
        vac_data['comp_max'] = comp_max
        vac_data['comp_car'] = comp_car
        vac_data['employer'] = employer
        vac_data['address'] = address
        vac_data['site'] = main_link
        vacancies.append(vac_data)
    # Переход на следующую страницу
    np = soup.find('a',{'class':'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe'})
    if np:
        nextpage = np['href']
        params = nextpage + '&geo%5Bc%5D%5B0%5D=1'
        page += 1
        #print (params)
    else:
        page = -1
        #print ('finish')   
    #print (page)
print(f'\nВсего собрано {len(vacancies)} вакансий')

df = pd.DataFrame(vacancies)
df.to_csv("test.csv", sep=";", index = False)
#print(df)
df1 = df[['name','comp_min','comp_max']]
pprint (df1)
