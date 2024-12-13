import re
import sys
import argparse
import xml.etree.ElementTree as ET


class ConfigError(Exception):
    """Класс для ошибок парсинга конфигурации."""
    pass


def parse_config(config_text):
    """Парсит текст учебного конфигурационного языка в промежуточное представление."""
    lines = config_text.splitlines()
    constants = {}
    parsed_data = []

    comment_block = False
    for line in lines:
        line = line.strip()
        
        # Игнорирование многострочных комментариев
        if line.startswith("{{!--"):
            comment_block = True
        if comment_block:
            if line.endswith("--}}"):
                comment_block = False
            continue
        
        if not line or line.startswith("//"):
            continue

        # Объявление константы
        match_var = re.match(r"var\s+([a-zA-Z][_a-zA-Z0-9]*)\s*:=\s*(.+)", line)
        if match_var:
            name, value = match_var.groups()
            value_parsed = parse_value(value, constants)
            constants[name] = value_parsed
            parsed_data.append({"type": "constant", "name": name, "value": value_parsed})
            continue

        # Вычисление константы
        match_eval = re.match(r"!\[([a-zA-Z][_a-zA-Z0-9]*)\]", line)
        if match_eval:
            name = match_eval.group(1)
            if name not in constants:
                raise ConfigError(f"Undefined constant: {name}")
            parsed_data.append({"type": "evaluation", "name": name, "value": constants[name]})
            continue

        raise ConfigError(f"Syntax error: {line}")

    return parsed_data


def parse_value(value, constants):
    """Парсит значение: число или массив."""
    value = value.strip()

    # Числа
    if re.match(r"^-?\d+(\.\d+)?$", value):
        return float(value) if "." in value else int(value)

    # Массивы
    if value.startswith("<<") and value.endswith(">>"):
        items = value[2:-2].split(",")
        return [parse_value(item.strip(), constants) for item in items]

    # Неизвестное значение
    raise ConfigError(f"Invalid value: {value}")


def generate_xml(parsed_data):
    """Генерирует XML из промежуточного представления."""
    root = ET.Element("config")

    for item in parsed_data:
        if item["type"] == "constant":
            constant_elem = ET.SubElement(root, "constant", name=item["name"])
            append_value(constant_elem, item["value"])
        elif item["type"] == "evaluation":
            eval_elem = ET.SubElement(root, "evaluation", name=item["name"])
            append_value(eval_elem, item["value"])

    return ET.tostring(root, encoding="unicode", method="xml")


def append_value(parent, value):
    """Добавляет значение (число или массив) в XML."""
    if isinstance(value, list):
        array_elem = ET.SubElement(parent, "array")
        for item in value:
            append_value(array_elem, item)
    else:
        value_elem = ET.SubElement(parent, "value")
        value_elem.text = str(value)


def main():
    parser = argparse.ArgumentParser(description="Учебный конфигурационный язык -> XML")
    parser.add_argument("--input", required=True, help="Путь к входному файлу конфигурации")
    parser.add_argument("--output", required=True, help="Путь к выходному XML файлу")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as infile:
            config_text = infile.read()

        parsed_data = parse_config(config_text)
        xml_output = generate_xml(parsed_data)

        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(xml_output)

        print("Конвертация завершена успешно.")
    except ConfigError as e:
        print(f"Ошибка конфигурации: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    main()
