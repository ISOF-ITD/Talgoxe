def get_swedish_alphabet():
    return [chr(i) for i in range(0x61, 0x7B)] + ['å', 'ä', 'ö']


def is_empty_string(string):
    if (string is None):
        return True
    return (len(string) < 1)


def is_not_empty_string(string):
    return not is_empty_string(string)

