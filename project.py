#-*- coding: utf-8 -*-
import os
import csv
import re

class PriceMachine:
    def __init__(self):
        self.data = []

    def load_prices(self, directory='.'):
        """#Сканирует указанный каталог и ищет файлы со словом 'price' в названии."""
        for filename in os.listdir(directory):
            if 'price' in filename.lower() and filename.endswith('.csv'):
                self._process_file(os.path.join(directory, filename))

    def _search_product_price_weight(self, headers):
        """Возвращает индексы столбцов для товара, цены и веса."""
        product_names = ["товар", "название", "наименование", "продукт"]
        price_names = ["цена", "розница"]
        weight_names = ["вес", "масса", "фасовка"]

        # Убираем лишние пробелы вокруг заголовков
        headers = [header.strip().lower() for header in headers]

        # Поиск индексов
        product_index = next((i for i, header in enumerate(headers) if header in product_names), None)
        price_index = next((i for i, header in enumerate(headers) if header in price_names), None)
        weight_index = next((i for i, header in enumerate(headers) if header in weight_names), None)

        return product_index, price_index, weight_index

    def _process_file(self, file_path):
        """Обрабатывает файл и загружает данные в список."""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')  # Используйте запятую как разделитель
            headers = next(reader)  # Читаем заголовки
            product_idx, price_idx, weight_idx = self._search_product_price_weight(headers)

            # Проверка на наличие всех необходимых индексов
            if product_idx is None or price_idx is None or weight_idx is None:
                print(f"Файл '{file_path}' пропущен: отсутствуют необходимые столбцы.")
                return

            for row in reader:
                if len(row) > max(product_idx, price_idx, weight_idx):
                    try:
                        product = row[product_idx].strip()
                        price = float(row[price_idx].strip())
                        weight = float(row[weight_idx].strip())
                        if weight > 0:  # Избегаем деления на ноль
                            self.data.append({
                                'product': product,
                                'price': price,
                                'weight': weight,
                                'file': os.path.basename(file_path),
                                'price_per_kg': price / weight
                            })
                    except ValueError:
                        print(f"Некорректные данные в строке: {row}")

    def find_text(self, text):
        """Находит товары по фрагменту названия и возвращает отсортированный список."""
        filtered_data = [item for item in self.data if re.search(text, item['product'], re.IGNORECASE)]
        return sorted(filtered_data, key=lambda x: x['price_per_kg'])

    def export_to_html(self, fname='output.html'):
        """Экспортирует данные в HTML файл, отсортированные по цене за килограмм."""
        # Сортируем данные по 'price_per_kg'
        sorted_data = sorted(self.data, key=lambda x: x['price_per_kg'])

        with open(fname, 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
    <html>
    <head>
     <title>Позиции продуктов</title>
     <meta charset="utf-8">  <!-- Добавлен тег meta для указания кодировки -->
    </head>
    <body>
     <table border="1">
     <tr>
     <th>№</th>
     <th>Название</th>
     <th>Цена</th>
     <th>Фасовка</th>
     <th>Файл</th>
     <th>Цена за кг.</th>
     </tr>
    ''')

            for idx, item in enumerate(sorted_data, start=1):
                f.write(f''' <tr>
     <td>{idx}</td>
     <td>{item['product']}</td>
     <td>{item['price']}</td>
     <td>{item['weight']}</td>
     <td>{item['file']}</td>
     <td>{item['price_per_kg']:.2f}</td>
     </tr>
    ''')

            f.write(''' </table>
    </body>
    </html>
    ''')

def main():
    pm = PriceMachine()
    pm.load_prices()

    print("Введите текст для поиска. Чтобы выйти, введите 'exit'.")
    while True:
        search_query = input("Поиск: ")
        if search_query.lower() == 'exit':
            print("Работа завершена. Обобщенные данные в output.html")
            break
        
        results = pm.find_text(search_query)
        if results:
            print(f"{'№':<4} {'Наименование':<30} {'Цена':<7} {'Вес':<7} {'Файл':<15} {'Цена за кг.':<15}")
            for idx, item in enumerate(results, start=1):
                print(f"{idx:<4} {item['product']:<30} {item['price']:<7} {item['weight']:<7} {item['file']:<15} {item['price_per_kg']:.2f}")
        else:
            print("Товары не найдены.")

    pm.export_to_html()  # Экспорт данных в HTML при завершении


if __name__ == "__main__":
    main()


"""
Пояснения к коду:
Класс PriceMachine: Инициализирует список для хранения загруженных данных.data
Метод load_prices: Сканирует указанный каталог, ищет файлы с "price" в названии и обрабатывает каждый файл.
Метод _process_file: Загружает данные из файла, соответствующего формату, и сохраняет их.
Метод _search_product_price_weight: Определяет индексы нужных столбцов.
Метод find_text: Позволяет искать товары по имени с использованием регулярных выражений и сортировки по цене за килограмм.
Метод export_to_html: Экспортирует данные в HTML-формате.
Функция main: Главное тело программы, которое управляет вводом пользователя и выводит результаты.
Как использовать:
Положите ваши CSV файлы с прайс-листами в заданный каталог.
Запустите программу, вводите фрагменты названий для поиска.
Для выхода и формирования агрегированного html введите "exit".
"""