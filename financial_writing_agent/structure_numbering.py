"""One Financial-owned source of truth for publication H1 numbering.

The editorial blueprint, structure review and DOCX renderer must agree for
every positive section index. No arbitrary ten/fifteen-section limit.
"""
from __future__ import annotations


def chinese_section_number(index: int) -> str:
    if type(index) is not int or index < 1:
        raise ValueError("section index must be a positive integer")
    digits = "零一二三四五六七八九"
    if index < 10:
        return digits[index]
    if index < 20:
        return "十" + (digits[index - 10] if index > 10 else "")
    if index < 100:
        tens, ones = divmod(index, 10)
        return digits[tens] + "十" + (digits[ones] if ones else "")
    if index < 1000:
        hundreds, remainder = divmod(index, 100)
        result = digits[hundreds] + "百"
        if remainder == 0:
            return result
        if remainder < 10:
            return result + "零" + digits[remainder]
        if remainder < 20:
            return result + "一" + chinese_section_number(remainder)
        return result + chinese_section_number(remainder)
    raise ValueError("publication section index over 999 is unsupported")


def chinese_section_prefix(index: int) -> str:
    return chinese_section_number(index) + "、"
