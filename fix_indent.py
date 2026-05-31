with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(243, 303):
    lines[i] = '    ' + lines[i]

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
