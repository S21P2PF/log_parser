import base64
import sys
from pathlib import Path

def decode_base64_to_single_lines(input_file, output_file, encoding='utf-8', newline_replacement='\\n'):
    """
    Декодирует каждую строку входного файла из base64,
    и заменяет все переводы строк в декодированном тексте на указанную строку.
    Выходной файл содержит одну строку на каждый входной base64.
    """
    with open(input_file, 'r', encoding=encoding) as f_in, \
         open(output_file, 'w', encoding=encoding) as f_out:
        
        line_num = 0
        for line in f_in:
            line_num += 1
            line = line.rstrip('\n')
            if not line:
                # Пустую строку можно пропустить или записать пустую строку
                f_out.write('\n')
                continue
            
            try:
                decoded_bytes = base64.b64decode(line)
                decoded_text = decoded_bytes.decode(encoding, errors='replace')
                # Заменяем все переводы строк на маркер
                single_line = decoded_text.replace('\r\n', newline_replacement).replace('\n', newline_replacement).replace('\r', newline_replacement)
                f_out.write(single_line + '\n')
            except Exception as e:
                print(f"Ошибка декодирования строки {line_num}: {e}")
                f_out.write(f"[DECODE ERROR line {line_num}: {e}]\n")

if __name__ == '__main__':

    input_file_reqests = "../data/requests.txt"
    output_file_reqests = "../data/requests_decoded.txt"
    
    input_file_responses = "../data/responses.txt"
    output_file_responses = "../data/responses_decoded.txt"
    
    if not Path(input_file_reqests).exists():
        print(f"Файл {input_file_reqests} не найден.")
        sys.exit(1)
    
    decode_base64_to_single_lines(input_file_reqests, output_file_reqests)
    print(f"Requests готово. Результат в {output_file_reqests}")

    if not Path(input_file_responses).exists():
        print(f"Файл {input_file_responses} не найден.")
        sys.exit(1)
    
    decode_base64_to_single_lines(input_file_responses, output_file_responses)
    print(f"Responses готово. Результат в {output_file_responses}")