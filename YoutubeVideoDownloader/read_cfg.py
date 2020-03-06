from configparser import ConfigParser

config = ConfigParser()
filename = 'spiders/config.ini'
config.read(filename, encoding='UTF-8')

#print('lang>name:', config['lang']['name'])

print('url', config['item']['url'])
print('date_latest', config['item']['date_latest'])

#config.set('table', 'order_th', '订单号,申请人,状态1')  # 对config添加值
config.set('item', 'date_latest', '20200304')
with open('config.ini', 'w', encoding='utf-8') as file:
   config.write(file)  # 值写入配置文件
