from requests import get, delete, post

print(get('http://localhost:5000/api/v2/item/5').json())  # Получение 5 товара
print(post('http://localhost:5000/api/v2/item', json={'id': '41',
                                                      'display': 'IPS',
                                                      'title': 'Ноутбук',
                                                      'content': 'Хороший ноутбук',
                                                      'main_characteristics': '1',
                                                      'count': 1,
                                                      'price': '1Р',
                                                      'processor': 'Intel',
                                                      'videoadapter': 'Nvidia',
                                                      'ram': 'Kingston',
                                                      'battery': 'Li-on'
                                                      }))
# Добавление товара
print(get('http://localhost:5000/api/v2/item/41').json())  # Получение добавленного товара
print(delete('http://localhost:5000/api/v2/item/41'))  # Удаление 41 товара
print(get('http://localhost:5000/api/v2/item').json())  # Получение всех товаров
