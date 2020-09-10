# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 11:37:36 2020

@author: Davit
"""

import os
import pandas as pd




#===============================

if month == '01':
    year_final = year -1
    month_final = '12'
else:
    year_final = year
    if int(month) <= 10:
        month_final = '0' + str(int(month)-1)
    else:
        month_final = str(int(month)-1)


path = directory + r"\101-"+str(year) +month + r'01\xlsx\a'

data = pd.read_excel(path[:-1] + month_final+str(year_final) + r"B1.xlsx")
data['NUM_SC3'] = data['NUM_SC'].apply(lambda x: x[:3])


bal = sqldf("""select a.REGN,
            sum(case when a.NUM_SC3 in ('313', '315') then a.IR else 0 end) + sum(case when a.NUM_SC in ('31702') then a.IR else 0 end) as Bank_borrow_resid_rub,
            sum(case when a.NUM_SC3 in ('313', '315') then a.IV else 0 end) + sum(case when a.NUM_SC in ('31702') then a.IV else 0 end) as Bank_borrow_resid_inv,
            sum(case when a.NUM_SC3 in ('314', '316') then a.IR else 0 end) + sum(case when a.NUM_SC in ('31703') then a.IR else 0 end) as Bank_borrow_foreign_rub,
            sum(case when a.NUM_SC3 in ('314', '316') then a.IV else 0 end) + sum(case when a.NUM_SC in ('31703') then a.IV else 0 end) as Bank_borrow_foreign_inv,
            sum(case when a.NUM_SC3 in ('312') then a.IR else 0 end) + sum(case when a.NUM_SC in ('31701', '31704', '32901') then a.IR else 0 end) as CBR_borrow_rub,
            sum(case when a.NUM_SC3 in ('312') then a.IV else 0 end) + sum(case when a.NUM_SC in ('31701', '31704', '32901') then a.IV else 0 end) as CBR_borrow_inv,
            sum(case when a.NUM_SC3 in ('410', '411', '412', '413', '427', '428', '429', '430') then a.IR else 0 end) as C_deposit_gov_rub,
            sum(case when a.NUM_SC3 in ('410', '411', '412', '413', '427', '428', '429', '430') then a.IV else 0 end) as C_deposit_gov_inv,
            sum(case when a.NUM_SC3 in ('414', '415', '416', '417', '418', '419', '420', '421', '422', '431', '432', '433', '434', 435, '436', '437', '438', '439') then a.IR else 0 end) as C_deposit_resid_rub,
            sum(case when a.NUM_SC3 in ('414', '415', '416', '417', '418', '419', '420', '421', '422', '431', '432', '433', '434', 435, '436', '437', '438', '439') then a.IV else 0 end) as C_deposit_resid_inv,
            sum(case when a.NUM_SC3 in ('426', '440') then a.IR else 0 end) as C_deposit_foreign_rub,
            sum(case when a.NUM_SC3 in ('426', '440') then a.IV else 0 end) as C_deposit_foreign_inv,
            sum(case when a.NUM_SC3 in ('520', '523') then a.IR else 0 end) + sum(case when a.NUM_SC in ('52401', '52406') then a.IR else 0 end) as Sec_issued_rub,
            sum(case when a.NUM_SC3 in ('520', '523') then a.IV else 0 end) + sum(case when a.NUM_SC in ('52401', '52406') then a.IV else 0 end) as Sec_issued_inv
            from data a group by a.REGN""")



bal_long = pd.melt(bal, id_vars = 'REGN', value_vars=['Bank_borrow_resid_rub', 'Bank_borrow_resid_inv', 'Bank_borrow_foreign_rub', 'Bank_borrow_foreign_inv',  'CBR_borrow_rub', 'CBR_borrow_inv', 'C_deposit_gov_rub', 'C_deposit_gov_inv', 'C_deposit_resid_rub', 'C_deposit_resid_inv', 'C_deposit_foreign_rub', 'C_deposit_foreign_inv', 'Sec_issued_rub', 'Sec_issued_inv'])
bal_long['valuta'] = bal_long['variable'].apply(lambda x: 'RUB' if x.endswith('_rub') else 'INV')
bal_long['variable'] = bal_long['variable'].apply(lambda x: x[: -4])






out['prov'] =1

for i in range(len(out)):    
    if out.loc[i, 'Название'] == 'Error' or out.loc[i, 'Признак кредитора']== "Error" or out.loc[i, 'STOIM_INS'] == np.nan or out.loc[i, 'Номинальная стоимость, тыс. ед. валюты'] == 'Error':
            out.loc[i, 'prov'] = 0
      
        
        
prom = out[out['prov']==1]    #.loc[:, 'REGN':'Условие: уровень']

sum_deal = sqldf(""" select a.REGN, a.'Валюта', sum(a.'Номинальная стоимость, тыс. ед. валюты') as nom_stoim_sum,
                      a.'Признак кредитора'
                      from prom a
                      group by a.REGN, a.'Валюта', a.'Признак кредитора'
                  """)
                                    
sum_deal['Курс'] = sum_deal['Валюта'].apply(lambda x: cur(x))
sum_deal['check_rub'] = sum_deal['Валюта'].apply(lambda x: 'RUB' if x in ['RUB', 'CUR'] else 'INV')

sum_deal['Стоим_руб'] = sum_deal['Курс'] * sum_deal['nom_stoim_sum']

sum_deal_meta = sqldf("""select 
                          a.REGN, a.check_rub, a.'Признак кредитора', sum(a.'Стоим_руб') as 'Стоим_руб_мета'
                          from sum_deal a
                          group by a.REGN, a.check_rub, a.'Признак кредитора'
                      """)

prov_bal = sqldf("""select a.*, b.value,
                     (case when a.'Стоим_руб_мета' <= b.value or abs((a.'Стоим_руб_мета' - b.value)/a.'Стоим_руб_мета') <= 0.05 or a.'Признак кредитора' = 'Capital' then '1' else 'Error' end) as 'stat_bal'
                     from sum_deal_meta a 
                     left join bal_long b on a.'REGN' = b.'REGN' and a.'Признак кредитора' = b.'variable' and a.check_rub = b.valuta
                     order by a.REGN, a.'Признак кредитора'
                 """)



final = sqldf("""select a.*, b.'Стоим_руб_мета', b.value as value_101, b.stat_bal
                    from out a 
                    left join prov_bal b on a.'REGN' = b.'REGN' and a.check_rub = b.check_rub and a.'Признак кредитора' = b.'Признак кредитора'                   
                 """)
 




        



