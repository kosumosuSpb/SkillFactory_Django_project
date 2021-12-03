import re
import unittest
from django import template


register = template.Library()  # собственно, чтобы не писать каждый раз template.Library()


@register.filter(name='censor')
def censor(text):
    """
    фильтр условных запрещённых слов
    на вход получает текст, на выходе выдаёт текст, с заменёнными на звёздочки запрещёнными словами

    :param text: текст для цензуры
    :return: зацензуренный текст (в запрещённых словах остаётся только первая буква, остальные заменяются на звёздочки)
    """

    # список запрещённых слов
    forbidden_words = ['word1', 'word2', 'word3', 'text2']
    # делаем паттерн из списка запрещённых слов (регистронезависимо)
    forbidden_pattern = re.compile('|'.join(forbidden_words), re.IGNORECASE)

    # вспомогательная функция, которая будет возвращать из match-объекта зацензуренное слово,
    def replacement(match):
        return match.group()[0] + "*" * (len(match.group()) - 1)

    # возвращаем текст, с зацензуренными словами.
    # паттерн.sub(на_что_заменяем, где_делаем_замены)
    return forbidden_pattern.sub(replacement, text)


class TestCensor(unittest.TestCase):
    def test_words(self):
        self.assertEqual(censor('This is the test text. This word1 is forbidden. '
                                'And this Word2 is forbidden. As long as this word3.'),
                         'This is the test text. This w**** is forbidden. And this W**** is forbidden. '
                         'As long as this w****.')


if __name__ == '__main__':
    unittest.main()
