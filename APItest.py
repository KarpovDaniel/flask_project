from requests import get, delete, post

print(get('http://127.0.0.1:5000/api/v2/item/5').json())  # Получение 5 товара
print(post('http://localhost:5000/api/v2/item', json={'id': '41',
                                                      'title': 'Ноутбук',
                                                      'content': '',
                                                      'price': 1,
                                                      'main_characteristics': '1',
                                                      'count': 1
                                                      }))
# Добавление товара
print(get('http://127.0.0.1:5000/api/v2/item/41').json())  # Получение добавленного товара
print(delete('http://localhost:5000/api/v2/item/41'))  # Удаление 41 товара
print(get('http://127.0.0.1:5000/api/v2/item').json())  # Получение всех товаров
