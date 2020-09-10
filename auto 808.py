# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 11:37:36 2020

@author: Davit
"""

import os
import urllib as ur
import remoteunrar 
import pandas as pd
import numpy as np
import re
from pandasql import sqldf
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import HTML

directory = r'D:\Bank of Russia\form 808'
os.chdir(directory )

year = int(input('введите год:'))
month = input('введите месяц:')

data_analysis = str(year) + '-'+ month + '-01'


print('Производится расчет на '+ data_analysis +' ...')

# запуск функций
runcell(0, directory + '/functions.py')
#===============================

out = pd.read_excel('form_808_01042020.xlsx')
# header = out.iloc[0]
# out = out[1:]
# out.columns = header

# out = out.reset_index().drop('index', axis =1)

rus_banks_cbr = pd.read_excel('creditors_priznak.xlsx', sheet_name = 'rus_banks_cbr')
rus_banks = pd.read_excel('creditors_priznak.xlsx', sheet_name = 'rus_banks')
rus_banks = rus_banks.set_index('Name')
rus_banks['REGN'] = rus_banks['REGN'].apply(lambda x: x if type(x) == float else int(x))

priznak = pd.read_excel('creditors_priznak.xlsx', sheet_name = 'initial_data')
priznak = priznak.set_index('Name')

vid_st = pd.read_excel('stavka.xlsx', sheet_name = 'vid_stavki')
bal_names = pd.read_excel('stavka.xlsx', sheet_name = 'bal_names')
bal_names  = bal_names.set_index('priznak')

currency = pd.read_excel('stavka.xlsx', sheet_name = 'currency')
currency = currency.set_index('date')

usd_cur = currency.loc[data_analysis, 'usd']
eur_cur = currency.loc[data_analysis, 'eur']
chf_cur = currency.loc[data_analysis, 'chf']

out['NOM_STOIM'] = out['NOM_STOIM'].apply(lambda x: x.replace('(643', '(rub') if type(x) != float else x)



# Цикл для названия банков. Заполняет столб "Название"
for i in range(len(out)):
    try:
        out.loc[i, 'Название'] = name_of_bank(out.loc[i,'REGN'])
    except Exception:
        out.loc[i, 'Название'] = 'Error'
    
    # уровень капитала
    out.loc[i, 'Уровень капитала'] = uroven_capital(out.loc[i, 'UROV_DO'], out.loc[i, 'UROV_POSLE'])
    
    # заполняет столбец TIP_STAVKI
    a = out.loc[i, 'TIP_STAVKI']
    b = out.loc[i, 'STAVKA']
    
    
    if type(a) != float and type(b) != float:
        if 'неприм' in a.lower().replace(' ', '') or 'неустан' in a.lower().replace(' ', '') or 'нет' in a.lower().replace(' ', '') or 'неприм' in b.lower().replace(' ', '') or 'неустан' in b.lower().replace(' ', '') or 'нет' in b.lower().replace(' ', ''):
            out.loc[i, 'Фактическая ставка'] = 'NA'   
        elif 'фиксир' in str(a).lower() and 'от' not in str(a).lower():
            digit = ["\d", "\d+\.\d+", "\d+\,\d+"]
            zn = []
            try:
                for j  in digit:
                    x = re.findall(j, b)
                    if len(x)!= 0:
                        zn.append(x[0])
                out.loc[i, 'Фактическая ставка'] = max(zn, key = len).replace(',', '.')
            except:
                out.loc[i, 'Фактическая ставка'] = 'FLOATING'
        elif 'от фикс' in str(a).lower() or 'от плав' in str(a).lower():
            out.loc[i, 'Фактическая ставка'] = 'OTHER'
        else:
            out.loc[i, 'Фактическая ставка'] = 'FLOATING'
    else:
        out.loc[i, 'Фактическая ставка'] = ''
        
    # заполняет столбец "Базовая ставка"
    if 'плав' in str(a).lower() and 'от' not in str(a).lower():
        out.loc[i, 'Базовая ставка'] = vid_stavki(b, a)
    elif 'фикс' in str(a).lower() and 'от' not in str(a).lower():
        out.loc[i, 'Базовая ставка'] = '-'
    else:
        out.loc[i, 'Базовая ставка'] = 'OTHER' 


# Заполняет столбец "ID"   
for i, trial in out.iterrows():
    out.loc[i, 'ID'] = "Займ {}".format(trial["NOM_GR"]-2)   

# заполняет сумму
out['Стоимость, включаемая в расчет капитала, тыс. ед. валюты'] = out['STOIM_INS'].apply(lambda x: summa_stoim(x))
out['Номинальная стоимость, тыс. ед. валюты'] = out['NOM_STOIM'].apply(lambda x: summa_stoim(x))    


# заполняет валюту
out['Валюта'] = out['NOM_STOIM'].apply(lambda x: 'RUB' if 'руб' in str(x).lower() or 'rub' in str(x).lower() or 'rur' in str(x).lower() or 'т.р.' in str(x).lower() else 'EUR' if 'eur' in str(x).lower() or 'евр' in str(x).lower() else 'USD' if 'usd' in str(x).lower() or 'дол' in str(x).lower() else 'CHF' if 'фран' in str(x).lower() else 'CUR' )

# заполнят поле "Условие: норматив"
out['Условие: норматив'] = out['USL_SPIS'].apply(lambda x: normativ(x))

# Заполняет поле "Условие: уровень"
out['Условие: уровень'] = out['USL_SPIS'].apply(lambda x: ''  if type(x) == float else znach_normativ(x))
            
# Заполняет столбец "Признак кредитора"
out['REGN_EMIT'] = out['NAME_EMIT'].apply(lambda x: regn_emit(x))
# out['Признак кредитора'] = out['NAME_EMIT'].apply(lambda x: priznak_cred(x))  
for i in range(len(out)):
    if out.loc[i, 'REGN'] == out.loc[i, "REGN_EMIT"]:
        out.loc[i, 'Признак кредитора'] = 'Capital'
    else:
        out.loc[i, 'Признак кредитора'] = priznak_cred(out.loc[i, 'NAME_EMIT'])
    
    
    if 'облиг' in str(out.loc[i,'TIP_INS']).lower() and type(out.loc[i,'TIP_INS']) != float:
        out.loc[i, 'Признак кредитора'] = 'Sec_issued'

# подготовка для расчета спреда
out['STAVKA'] = out['STAVKA'].apply(lambda x: '' if type(x) == float else x.replace("+", " plus").replace("-", " minus"))
out['TIP_STAVKI'] = out['TIP_STAVKI'].apply(lambda x: '' if type(x) == float else x.replace("+", " plus").replace("-", " minus"))

# расчет спреда
# out["Спрэд"] = out['STAVKA'].apply(lambda x: '' if type(x) == float else spread(x))   
 

out['Курс'] = out['Валюта'].apply(lambda x: cur(x))
out['check_rub'] = out['Валюта'].apply(lambda x: 'RUB' if x in ['RUB', 'CUR'] else 'INV')


# подгтовка данных по 101 форме и дальнейшие расчеты для столбца "Статья баланса"
runcell(0, directory + '/prep_101_form.py')

final['STAVKA'] = final['STAVKA'].apply(lambda x: x.replace('%', '').replace(',', '.'))
final['fix_stav'] = final['STAVKA'].apply(lambda x: integer(x))


for i in range(len(final)):
        
    # расчет спреда
    final.loc[i, 'Спрэд'] = spread(final.loc[i, 'TIP_STAVKI'], final.loc[i, 'STAVKA'])

    # заполняет столбец "Статья баланса"
    if final.loc[i, 'stat_bal'] == '1':
        final.loc[i, 'Статья баланса'] = bal_names.loc[final.loc[i, 'Признак кредитора'], 'name']
    else:
        final.loc[i, 'Статья баланса'] = 'Error'
    
    # заполняет срочность базовой ставки    
    if 'фикс' in str(final.loc[i, 'TIP_STAVKI']).lower() and 'от' not in str(final.loc[i, 'TIP_STAVKI']).lower() and type(final.loc[i, 'fix_stav']) == float:
        final.loc[i, 'Срочность базовой ставки'] = '-'
    elif 'фикс' in str(final.loc[i, 'TIP_STAVKI']).lower() and 'от' not in str(final.loc[i, 'TIP_STAVKI']).lower() and type(final.loc[i, 'fix_stav']) == str:
        final.loc[i, 'Срочность базовой ставки'] = 'OTHER'
    elif 'плав' in str(final.loc[i, 'TIP_STAVKI']).lower() and 'от' not in str(final.loc[i, 'TIP_STAVKI']).lower():
        final.loc[i, 'Срочность базовой ставки'] = '1 день'
    
    
# удаляет ненужные компоненты
del i, a, b, j, x, zn, trial



final = final[['REGN', 'Название', 'Уровень капитала',
       'Фактическая ставка', 'Базовая ставка', 'ID',
       'Стоимость, включаемая в расчет капитала, тыс. ед. валюты',
       'Номинальная стоимость, тыс. ед. валюты', 'Валюта', 'Условие: норматив',
       'Условие: уровень', 'Признак кредитора', 'Курс', 'check_rub', 'prov',
       'Стоим_руб_мета', 'value_101', 'stat_bal', 'fix_stav', 'Спрэд',
       'Статья баланса', 'Срочность базовой ставки',  'NOM_GR', 'NAME_EMIT', 'REGN_EMIT', 'KOD_BUM', 'OKSM', 'NAME_COUN',
       'UROV_DO', 'UROV_POSLE', 'UROV_KONS', 'TIP_INS', 'STOIM_INS',
       'NOM_STOIM', 'KLASS_BU', 'DATE_VYP', 'BEZSR', 'DATE_POG', 'PRAVO_VYK',
       'SUMMA_VYK', 'DATE_REAL2', 'TIP_STAVKI', 'STAVKA', 'USL_PREKR',
       'OBIAZ_VYP', 'USL_UVEL', 'HAR_VYP', 'KONVERT', 'USL_KONV', 'POLN_KONV',
       'STAVK_KONV', 'OBIAZ_KONV', 'UR_KONV', 'NAME_KONV', 'SPISANIE',
       'POLN_SPIS', 'VREM_SPIS', 'MEH', 'TYPE_SBRD', 'SUBORD', 'SOOTV',
       'NESOOTV', 'USL_SPIS']]


final.to_excel('final_808.xlsx')
bal.to_excel('bal.xlsx')
sum_deal_meta.to_excel('sum_deal_meta.xlsx')
sum_deal.to_excel('sum_deal.xlsx')
bal_long.to_excel('bal_long.xlsx')
prom.to_excel('prom.xlsx')


print("""   
Расчет окончен
""")
      
      
     