# -*- coding: cp949 -*-

print '�����ﰢ�� �׸���\n'
d = float(raw_input('���� ���� : '))

for i in range(int(d)+1):
    print('* ' * i)

area = float((d ** 2) / 2)
print('���� : %s' % area)

raw_input()
