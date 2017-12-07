t = open('city_list.txt', 'r', encoding='utf8')
for i in t:
    print('\'' + i.strip() + '\',')