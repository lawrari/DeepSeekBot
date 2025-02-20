import re
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from io import BytesIO


class Formattor:

    @staticmethod
    def escape_special_chars(text):
        special_chars = "*_~|`>"
        return ''.join([f"\\{char}" if char in special_chars else char for char in text])

    @staticmethod
    def remove_special_chars(text):
        special_chars = "*"
        return ''.join([char for char in text if char not in special_chars])

    @staticmethod
    def format_text(text):
        res = ""
        i = 0
        while i < len(text):
            if text[i] == "`":
                j = i + 1
                while j < len(text) and text[j] != "`":
                    j += 1
                if j < len(text):
                    res += "`" + "".join(text[i+1:j]) + "`"
                    i = j
            elif text[i] == "#" and (i == 0 or text[i-1] in "\n\r"):
                k = i + 1
                while k < len(text) and text[k] == "#":
                    k += 1
                if k < len(text) and text[k] == " ":
                    i = k
                    j = i
                    while j < len(text) and text[j] not in "\n\r":
                        j += 1
                    res += "*" + Formattor.escape_special_chars(Formattor.remove_special_chars(text[i+1:j])) + "*\n"
                    i = j
            elif text[i] == "*" and i + 1 < len(text) and text[i+1] == "*":
                j = i + 2
                while j + 1 < len(text) and not (text[j] == "*" and text[j+1] == "*"):
                    j += 1
                if j + 1 < len(text):
                    res += "*" + Formattor.escape_special_chars(text[i+2:j]) + "*"
                    i = j + 1
            elif text[i] == "~" and i + 1 < len(text) and text[i+1] == "~":
                j = i + 2
                while j + 1 < len(text) and not (text[j] == "~" and text[j+1] == "~"):
                    j += 1
                if j + 1 < len(text):
                    res += "~" + Formattor.escape_special_chars(text[i+2:j]) + "~"
                    i = j + 1
            elif text[i] == "*":
                j = i + 1
                while j < len(text) and text[j] != "*":
                    j += 1
                if j < len(text):
                    res += "_" + Formattor.escape_special_chars(text[i+1:j]) + "_"
                    i = j
            else:
                if i < len(text):
                    res += text[i]
            i += 1

        res1 = ""

        res = re.sub('\n[-][ ]', '\n• ', res, flags=re.MULTILINE)
        res = re.sub('\n[ ]*[-][ ]', '\n • ', res, flags=re.MULTILINE)

        # Check table
        lines = res.split("\n")
        i = 0

        files = []

        while i < len(lines):
            if (lines[i].startswith("|") and lines[i].endswith("|") and
                i + 2 < len(lines) and lines[i+1].startswith("|") and lines[i+1].endswith("|") and
                lines[i+2].startswith("|") and lines[i+2].endswith("|")):
                j = i + 3

                table = []

                while j < len(lines) and lines[j].startswith("|") and lines[j].endswith("|"):
                    j += 1
                
                for k in range(i, j):
                    table.append(lines[k])

                lines = lines[:i] + lines[j+1:]

                a = map(lambda x: list(map(lambda y: y.strip(), x.split("|")[1:-1])), table)

                wb = Workbook()
                ws = wb.active

                for row in list(a):
                    ws.append(row)

                for col in ws.columns:
                    max_length = 0
                    column = col[0].column
                    column_letter = get_column_letter(column)
                    
                    for cell in col:
                        try:
                            # Пытаемся получить длину значения ячейки
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = (max_length + 2)
                    ws.column_dimensions[column_letter].width = adjusted_width

                byte_data = BytesIO()

                wb.save(byte_data)

                excel_bytes = byte_data.getvalue()

                filename = f"table_{len(files)}.xlsx"
                data = excel_bytes
                
                files.append(( filename, data ))
            else:
                i += 1

        res = "\n".join(lines)

        i = 0
        while i < len(res):
            if res[i] == "`":
                j = i + 1
                while j < len(res) and res[j] != "`":
                    j += 1
                if j < len(res):
                    res1 += "`" + res[i+1:j] + "`"
                    i = j
            else:
                res1 += res[i].replace(".", "\\.") \
                            .replace("-", "\\-") \
                            .replace("+", "\\+") \
                            .replace("=", "\\=") \
                            .replace("(", "\\(") \
                            .replace(")", "\\)") \
                            .replace("!", "\\!") \
                            .replace("?", "\\!") \
                            .replace("#", "\\#") \
                            .replace("|", "\\|")
            i += 1

        return ( res1, files )

