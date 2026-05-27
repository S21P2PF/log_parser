import os
import shutil
import sys

# === НАСТРОЙКА: путь к папке burp_items ===
# По умолчанию предполагается, что скрипт лежит в папке scripts,
# а burp_items находится в корне проекта (рядом с scripts).
BURP_ITEMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'burp_items')

def restructure_burp_items(root_dir):
    """
    Перестраивает структуру папки root_dir (burp_items) на месте.
    Из:  root_dir / YYYY-MM-DD_HH-MM-SS_METHOD_handler / (request.txt, response.txt)
    В:   root_dir / handler / METHOD / YYYY-MM-DD_HH-MM-SS / (request.txt, response.txt)
    """
    if not os.path.isdir(root_dir):
        print(f"Ошибка: папка '{root_dir}' не существует.")
        sys.exit(1)

    # Временная папка для новой структуры (внутри root_dir)
    temp_dir = os.path.join(root_dir, '_temp_restructured')
    os.makedirs(temp_dir, exist_ok=True)

    processed = 0
    errors = 0
    empty_original_dirs = []

    for item_name in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item_name)
        # Пропускаем не-папки и временную папку
        if not os.path.isdir(item_path) or item_name.startswith('_temp'):
            continue

        # Разбираем имя: ожидается YYYY-MM-DD_HH-MM-SS_METHOD_handler
        parts = item_name.split('_', 3)
        if len(parts) < 4:
            print(f"Пропущено (неверный формат): {item_name}")
            errors += 1
            continue

        date_str, time_str, method, handler = parts
        # Простая проверка формата даты (YYYY-MM-DD)
        if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
            print(f"Пропущено (некорректная дата): {item_name}")
            errors += 1
            continue

        # Целевая папка: handler / method / YYYY-MM-DD_HH-MM-SS
        dest_relative = os.path.join(handler, method, f"{date_str}_{time_str}")
        dest_path = os.path.join(temp_dir, dest_relative)
        os.makedirs(dest_path, exist_ok=True)

        # Перемещаем файлы из исходной папки в целевую
        try:
            for fname in os.listdir(item_path):
                src_file = os.path.join(item_path, fname)
                dst_file = os.path.join(dest_path, fname)
                if os.path.isfile(src_file):
                    shutil.move(src_file, dst_file)
            processed += 1
            empty_original_dirs.append(item_path)
            print(f"OK: {item_name} -> {os.path.relpath(dest_path, temp_dir)}")
        except Exception as e:
            print(f"Ошибка при обработке {item_name}: {e}")
            errors += 1

    # Удаляем опустевшие исходные папки
    for d in empty_original_dirs:
        try:
            os.rmdir(d)
        except OSError:
            pass  # не пуста? игнорируем

    # Перемещаем всё из временной папки обратно в root_dir
    for handler_name in os.listdir(temp_dir):
        src_handler = os.path.join(temp_dir, handler_name)
        dst_handler = os.path.join(root_dir, handler_name)
        if os.path.isdir(src_handler):
            if not os.path.exists(dst_handler):
                shutil.move(src_handler, dst_handler)
            else:
                # Объединяем вложенные папки методов
                for method_name in os.listdir(src_handler):
                    src_method = os.path.join(src_handler, method_name)
                    dst_method = os.path.join(dst_handler, method_name)
                    if os.path.isdir(src_method):
                        if not os.path.exists(dst_method):
                            shutil.move(src_method, dst_method)
                        else:
                            # Объединяем папки с датами
                            for date_folder in os.listdir(src_method):
                                src_date = os.path.join(src_method, date_folder)
                                dst_date = os.path.join(dst_method, date_folder)
                                if os.path.isdir(src_date) and not os.path.exists(dst_date):
                                    shutil.move(src_date, dst_date)
                # Если после перемещения src_handler опустел, удаляем
                if not os.listdir(src_handler):
                    os.rmdir(src_handler)

    # Удаляем временную папку, если она пуста
    try:
        if not os.listdir(temp_dir):
            os.rmdir(temp_dir)
    except OSError:
        pass

    print(f"\nГотово. Успешно обработано: {processed}, ошибок/пропусков: {errors}")
    print(f"Папка '{os.path.abspath(root_dir)}' реструктурирована.")

if __name__ == '__main__':
    # Можно переопределить путь через аргумент командной строки
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = BURP_ITEMS_DIR

    restructure_burp_items(target_dir)