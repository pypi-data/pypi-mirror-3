def int_greater_than(n):
    def check(item):
        return item > n

    return check

def int_less_than(n):
    def check(item):
        return item < n

    return check

def int_greater_or_equal_to(n):
    def check(item):
        return item >= n

    return check

def int_less_or_equal_to(n):
    def check(item):
        return item <= n

    return check

def string_matching(pattern):
    def check(item):
        return item == pattern

    return check
