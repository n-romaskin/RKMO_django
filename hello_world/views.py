import openpyxl
import os
from django.http import JsonResponse
from django.shortcuts import render

def hello_world(request):
    LIMIT_ROWS = 20000
    THIS_PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FILENAME = 'Реестр заявлений ПОО на 2020-06-29.xlsx'
    START_ROW = 2
    TAB_NAME = 'Реестр заявлений ПОО на 2020-06'
    NOT_FOUND = 'Нет подходящих результатов по текущему запросу...'
    fullDataObj = {}
    selectedSpec = 0
    selectedSpecName = ''
    selectedPayment = 0
    selectedPaymentName = ''
    specsList = {
        0: '40.02.01 Право и организация социального обеспечения',
        1: '09.02.06 Сетевое и системное администрирование',
        2: '20.02.04 Пожарная безопасность',
        3: '15.02.15 Технология металлообрабатывающего производства',
        4: '15.02.14 Оснащение средствами автоматизации технологических процессов и производств (по отраслям)',
        5: '23.01.17 Мастер по ремонту и обслуживанию автомобилей',
        6: '15.02.13 Техническое обслуживание и ремонт систем вентиляции и кондиционирования',
        7: '43.01.09 Повар, кондитер',
        8: '09.01.03 Мастер по обработке цифровой информации',
        9: '11.02.16 Монтаж, техническое обслуживание и ремонт электронных приборов и устройств',
        10: '43.02.15 Поварское и кондитерское дело',
        11: '20.02.02 Защита в чрезвычайных ситуациях',
        12: '15.01.05 Сварщик (ручной и частично механизированной сварки (наплавки)',
        13: '23.02.07 Техническое обслуживание и ремонт-двигателей, систем и агрегатов автомобилей',
        14: '38.02.01 Экономика и бухгалтерский учет (по отраслям)',
        15: '19.01.04 Пекарь',
        16: '15.02.10 Мехатроника и мобильная робототехника (по отраслям)',
        17: '43.02.01 Организация обслуживания в общественном питании',
        18: '46.02.01 Документационное обеспечение управления и архивоведение'
    }
    specsListReversed = {}
    specsListLen = 19
    paymentList = {
        0: 'Бюджет',
        1: 'Контракт',
        2: 'Целевое обучение'
    }
    paymentListReversed = {}
    paymentListLen = 3

    json = False
    if(request.GET.get('json')=='1'):
        json = True
    if(request.GET.get('selectedSpec')):
        if (int(request.GET.get('selectedSpec')) < specsListLen):
            selectedSpec = int(request.GET.get('selectedSpec'))
            selectedSpecName = specsList[selectedSpec]
    if(request.GET.get('selectedPayment')):
        selectedPayment = 0
        if(int(request.GET.get('selectedPayment'))<paymentListLen):
            selectedPayment = int(request.GET.get('selectedPayment'))
        selectedPaymentName = paymentList[selectedPayment]

    wb = openpyxl.load_workbook(filename = THIS_PROJ_DIR+'/xlsx/'+FILENAME)
    sheet = wb[TAB_NAME]

    for key, value in specsList.items():
        specsListReversed[value] = key
    for key, value in paymentList.items():
        paymentListReversed[value] = key

    for key, value in specsList.items():
        # key - id специальности из массива specsList в начале программы
        # value - название специальности из того же массива specsList
        fullDataObj[key] = {
            'specName': value,
            'users': {
                0: [],          # Бюджет
                1: [],          # Контракт
                2: []           # Целевое
            }
        }

    row = START_ROW
    while (sheet['B'+str(row)].value and row < LIMIT_ROWS):
        score = sheet['L'+str(row)].value.capitalize()
        status = sheet['P'+str(row)].value.capitalize()
        if (score and status == 'Принято к рассмотрению'):
            score = float(score)
            name = sheet['B'+str(row)].value.capitalize()
            surname = sheet['C'+str(row)].value.capitalize()
            patronymic =  sheet['D'+str(row)].value.capitalize()
            spec = sheet['K'+str(row)].value
            specKey = specsListReversed[spec]
            payment = sheet['M'+str(row)].value.capitalize()
            paymentKey = paymentListReversed[payment]
            fullDataObj[specKey].get('users')[paymentKey].append({
#                'place': 0,
                'name': name,
                'surname': surname,
                'patronymic': patronymic,
                'spec': spec,
                'score': score,
                'payment': payment
            })
        row = row + 1

    def keyFunc(item):
       return item.get('score')

    specKey = 0
    for specValue in specsList:
        paymentKey = 0
        for paymentValue in paymentList:
            fullDataObj[specKey].get('users')[paymentKey].sort(key = keyFunc, reverse = True)
            place = 0
            for obj in fullDataObj[specKey].get('users')[paymentKey]:
                place = place + 1
                obj.update({'place': place})
            paymentKey = paymentKey + 1
        specKey = specKey + 1
    params = {
        'selectedSpec': selectedSpec,
        'selectedSpecName': selectedSpecName,
        'selectedPayment': selectedPayment,
        'selectedPaymentName': selectedPaymentName,
        'paymentList': paymentList,
        'paymentListReversed': paymentListReversed,
        'specsList': specsList,
        'fullDataObj': fullDataObj,
        'NOT_FOUND': NOT_FOUND,
    }
    if (json):
        return JsonResponse(params)
#        return JsonResponse(fullDataObj)
    else:
        return render(request, 'result.html', params)
