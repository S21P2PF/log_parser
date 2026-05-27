from lxml import etree
import os

def parse_burp_xml_to_files_direct(file_path, req_file='requests.txt', resp_file='responses.txt'):
    """
    Парсит XML и потоково записывает каждый запрос/ответ в соответствующий файл.
    Не хранит данные в памяти.
    """
    # Создаём директории для выходных файлов, если их нет
    os.makedirs(os.path.dirname(os.path.abspath(req_file)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(resp_file)), exist_ok=True)

    with open(file_path, 'rb') as f_in, \
         open(req_file, 'w', encoding='utf-8') as f_req, \
         open(resp_file, 'w', encoding='utf-8') as f_resp:
        
        context = etree.iterparse(f_in, events=('end',), tag='item')
        count = 0
        
        for event, elem in context:
            # Используем .findtext – он возвращает пустую строку, если элемент отсутствует или текст пуст
            req_text = elem.findtext('request', '')
            resp_text = elem.findtext('response', '')
            
            f_req.write(req_text + '\n')
            f_resp.write(resp_text + '\n')
            
            # Очистка памяти (важно для больших файлов)
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            
            count += 1
            if count % 1000 == 0:
                print(f"Обработано {count} элементов...")
        
        del context
        print(f"Готово. Обработано {count} элементов.")


def parse_burp_xml_to_arrays(file_path):
    """
    Парсит XML-экспорт Burp Suite, извлекая base64-содержимое
    всех запросов и ответов.
    Возвращает (requests_list, responses_list).
    """
    requests_list = []
    responses_list = []

    with open(file_path, 'rb') as f:
        context = etree.iterparse(f, events=('end',), tag='item')
        
        for event, elem in context:
            req_text = elem.findtext('request', '')
            resp_text = elem.findtext('response', '')
            
            requests_list.append(req_text)
            responses_list.append(resp_text)
            
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        
        del context

    return requests_list, responses_list


# ========== Пример использования ==========
if __name__ == '__main__':
    xml_file = '../data/HTTP_history.xml'
    # Прямая запись в файлы (без хранения списков в памяти)
    parse_burp_xml_to_files_direct(
        xml_file,
        '../data/requests.txt',
        '../data/responses.txt'
    )
    
    # Альтернативно – получить списки в память (не рекомендуется для огромных файлов)
    # reqs, resps = parse_burp_xml_to_arrays(xml_file)
    # print(f"Загружено {len(reqs)} пар")