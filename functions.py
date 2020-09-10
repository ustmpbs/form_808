# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 15:44:51 2020

@author: Davit
"""

def name_of_bank(regn):
    # функция, которая находит название банка по регн
    i = 0
    while regn != rus_banks_cbr.loc[i, 'REGN']:
        i += 1
    return rus_banks_cbr.loc[i, 'Name'].replace('\xa0', ' ')

def regn_emit(x):
    try:
        return (rus_banks.loc[x, 'REGN'])
    except:
        return('non-bank')


def uroven_capital(x, y):
    
    if y not in ('неприменимо', 'не применимо', 'не соответствует', '-') and type(y) != float:
        if 'базов' in str(y).lower():
            return 'Базовый капитал'
        elif 'добав' in str(y).lower():
            return 'Добавочный капитал'
        elif 'допол' in str(y).lower():
            return 'Дополнительный капитал'
    else:
        if type(x) != float:
            if 'базов' in str(x).lower():
                return 'Базовый капитал'
            elif 'добав' in str(x).lower():
                return 'Добавочный капитал'
            elif 'допол' in str(x).lower():
                return 'Дополнительный капитал'
            else:
                return '-'


def summa_stoim(x):
    
    if type(x) != float:
        try:          
            summa = re.findall('\d+', x.replace(' ', ''))[0]
            if float(summa) // 10**10 != 0:
                return('Error')
            else:
                return(summa)
        except:
            return('Error')


# def summa_stoim(x):

#     # функция, которая вычленяет сумму из строки

#     tr = ['тыс', 'т.р.']
#     if type(x) != float and x != 'RUB':
#         summa = re.findall('\d+', x.replace(' ', ''))[0]        
#         try:
#             i = 0
#             while tr[i] not in x:
#                 i +=1
#             if float(summa) // 10**10 != 0:
#                 return('Error')
#             else:
#                 return(summa)
#         except:
#             if float(summa)/1000 // 10**10 != 0:
#                 return('Error')
#             else:
#                 return(str(float(summa)/1000)) 
#     else:
#         return 'Error'




def vid_stavki(x, y):

    try:
        try:
            k =0
            while vid_st.loc[k, 'vid'] not in x.lower():
                k += 1
            return(vid_st.loc[k, 'name'])
        except:
            h = 0
            while vid_st.loc[h, 'vid'] not in y.lower():
                h += 1
            return(vid_st.loc[h, 'name'])
    except:
        return('OTHER')
        
                    
def priznak_cred(n):
    
    # определяет категорию кредитора
    cols = list(priznak.columns )
    try:
        if n == 'Банк России':
            return 'CBR_borrow'
        else:                
            i = 0
            while  priznak.loc[n, cols[i]]!= 1:
                i += 1
            return cols[i]
    except:
        return 'Error'


def spread(n, v):
    pos_neg = ['уменьшенная на ', 'plus', 'plus ', 'minus', 'minus ', 'увеличенная на ']
    digit = ["\d+", "\d+\.\d+", "\d+\,\d+"]
    
    try:
        try: 
            zn = []              
            for i in pos_neg:
                for j in digit:
                    x = re.findall(i + j, n)            
                    if len(x) != 0:
                        # print(x[0])
                        zn.append(x[0])  
            return(max(zn, key = len).replace('уменьшенная на', '').replace('увеличенная на', '').replace('plus', '').replace('minus', '').replace(' ', ''))       
        except:
            znn = []
            for i in pos_neg:
                for j in digit:
                    x = re.findall(i + j, v)            
                    if len(x) != 0:
                        # print(x[0])
                        znn.append(x[0])  
            return(max(znn, key = len).replace('уменьшенная на', '').replace('увеличенная на', '').replace('plus', '').replace('minus', '').replace(' ', ''))       
    except:
        return ''  
    
def znach_normativ(n):
    niz = ["ниже ", "ниже", "ниж.", "меньше ", "< ", "<", "менее "]
    digit = ["\d+", "\d+\.\d+", "\d+\,\d+"]
    zn = []
    try:
        for i in niz:
            for j in digit:
                x = re.findall(i + j, n)            
                if len(x) != 0:
                    zn.append(x[0]+'%')              
        return(max(zn, key = len).replace('ниже', '').replace('ниж.', '').replace('менее', '').replace('<', '').replace(' ', '').replace(',', '.').replace('меньше', ''))       
    except:
        return ''


def normativ(n):
    if type(n) == float:
        return ''
    elif 'баз' in str(n).lower() or 'Н1.1' in str(n) or 'Н 1.1' in str(n) or 'H1.1' in str(n) or 'H 1.1' in str(n)  or 'Н1_1' in str(n):
        return 'Н1.1'
    elif 'основн' in str(n).lower() or 'Н1.2' in str(n) or 'Н 1.2' in str(n) or 'H1.2' in str(n) or 'H 1.2' in str(n) or 'Н1_2' in str(n):
        return 'Н1.2'
    elif 'совок' in str(n).lower() or 'Н1.0' in str(n) or 'Н 1.0' in str(n) or 'H1.0' in str(n) or 'H 1.0' in str(n) or 'Н1_0' in str(n):
        return 'Н1.0'
    else:
        return ''
    
    
    
def cur(x):
    if x in ['RUB', 'CUR', 'RUR']:
        curr_rate = 1
    elif x == 'USD':
        curr_rate = usd_cur
    elif x == 'EUR':
        curr_rate = eur_cur
    else:
        curr_rate = chf_cur
    return curr_rate


def integer(x):
    try:
        y = float(x)
        return y
    except:
        return 'text'
