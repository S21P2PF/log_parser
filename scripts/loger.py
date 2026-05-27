import os
import re
from datetime import datetime
from lxml import etree

def safe_filename(s, max_len=50):
    """Очищает строку от символов, недопустимых в именах папок"""
    return re.sub(r'[\\/*?:"<>|]', '_', s)[:max_len]

def parse_burp_time_to_str(time_str):
    """Преобразует время из Burp XML в формат YYYY-MM-DD_HH-MM-SS"""
    if not time_str:
        return "unknown_time"
    parts = time_str.split()
    if len(parts) < 6:
        return "unknown_time"
    month = parts[1]
    day = parts[2]
    time_part = parts[3]
    year = parts[5]
    month_num = {
        'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
        'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12
    }.get(month, 1)
    hour, minute, second = map(int, time_part.split(':'))
    dt = datetime(int(year), month_num, int(day), hour, minute, second)
    return dt.strftime("%Y-%m-%d_%H-%M-%S")

def create_folders(xml_path, req_decoded_path, resp_decoded_path, output_dir="items"):
    os.makedirs(output_dir, exist_ok=True)

    with open(xml_path, 'rb') as f_xml, \
         open(req_decoded_path, 'r', encoding='utf-8') as f_req, \
         open(resp_decoded_path, 'r', encoding='utf-8') as f_resp:

        context = etree.iterparse(f_xml, events=('end',), tag='item')
        count = 0

        for event, elem in context:
            count += 1

            # Читаем соответствующую строку из каждого decoded-файла
            req_line = f_req.readline()
            resp_line = f_resp.readline()
            if not req_line or not resp_line:
                print(f"Предупреждение: в файлах недостаточно строк для элемента {count}, останов.")
                break

            req_line = req_line.rstrip('\n')
            resp_line = resp_line.rstrip('\n')

            # Восстанавливаем переводы строк (предполагаем, что в файле \n заменены на \\n)
            req_decoded = req_line.replace('\\n', '\n')
            resp_decoded = resp_line.replace('\\n', '\n')

            # --- Берём метаданные из XML ---
            time_raw = elem.findtext('time', '')
            time_str = parse_burp_time_to_str(time_raw)
            method = elem.findtext('method', 'UNKNOWN')
            url = elem.findtext('url', '')
            url_clean = safe_filename(url.replace('https://', '').replace('http://', ''))

            # --- Формируем имя папки ---
            folder_name = f"{time_str}_{method}_{url_clean}"
            # Укорачиваем, если слишком длинное
            if len(folder_name) > 180:
                folder_name = folder_name[:180]
            folder_path = os.path.join(output_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # --- Сохраняем запрос и ответ ---
            with open(os.path.join(folder_path, 'request.txt'), 'w', encoding='utf-8') as f_out_req:
                f_out_req.write(req_decoded)
            with open(os.path.join(folder_path, 'response.txt'), 'w', encoding='utf-8') as f_out_resp:
                f_out_resp.write(resp_decoded)

            # Очистка памяти
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

            if count % 100 == 0:
                print(f"Обработано {count} пар...")

        # Проверка, не осталось ли лишних строк
        if f_req.readline() or f_resp.readline():
            print("Внимание: количество строк в decoded-файлах больше, чем элементов в XML.")

    print(f"Готово. Создано {count} папок в '{output_dir}'.")


if __name__ == '__main__':
    create_folders(
        xml_path='../data/HTTP_history.xml',       # исходный XML Burp
        req_decoded_path='../data/requests_decoded.txt', # файл с декодированными запросами (построчно)
        resp_decoded_path='../data/responses_decoded.txt', # файл с декодированными ответами
        output_dir='../burp_items'
    )