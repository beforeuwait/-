text = ''
for i in open('config_area.py', 'r', encoding='utf8'):
    text += i.replace('\t\t', '        ')

with open('config_area1.py', 'a', encoding='utf8') as f:
    f.write(text)