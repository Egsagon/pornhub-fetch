import re

raw = open('test').read()


r = re.compile(r'\/\*.*?\*\/')

res = r.sub('', raw)

with open('test-nocoment', 'w') as file:
    file.write(res)