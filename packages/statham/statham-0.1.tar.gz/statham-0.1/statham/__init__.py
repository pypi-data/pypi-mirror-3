# json validator


def validate(data, schema, strict=False):

    def check_object(a, b):
        if strict:
            if a.keys() != b.keys():
                return False

        for key in a.keys():
            if type(a[key]) == dict:
                if check_object(a[key], b[key]) is False:
                    return False

            if type(a[key]) == list:
                if check_list(a[key], b[key]) is False:
                    return False

            if type(a[key]) == type:
                if type(b[key]) != a[key]:
                    return False
            elif hasattr(a[key], '__call__') and a[key](b[key]) is False:
                return False

        return True

    def check_list(a, b):
        for index, item in enumerate(a):
            if type(item) == list:
                if check_list(item, b[index]) is False:
                    return False

            if type(item) == dict:
                if check_object(item, b[index]) is False:
                    return False

            if type(item) == type:
                if type(b[index]) != item:
                    return False
            elif hasattr(item, '__call__') and item(b[index]) is False:
                    return False

        return True
    
    result = True

    try:
        if type(schema) == dict:
            result = check_object(schema, data)

        if type(schema) == list:
            result = check_list(schema, data)
    except:
        result = False

    return result


crank = validate
