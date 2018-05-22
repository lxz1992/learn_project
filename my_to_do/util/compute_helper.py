

class ComputeHelper(object):

    @staticmethod
    def update_none_or_empty_to_zero(value):
        return 0 if not(value) else value

    @staticmethod
    def check_list_subset(check_list, valid_list):
        check_items = set(check_list)
        result = False
        try:
            result = set(valid_list).issubset(check_items)
        except Exception:
            result = False
        return result
