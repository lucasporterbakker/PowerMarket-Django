from decimal import Decimal


# def humanize_decimal(decimal_val, decimal_digits=None):
#     if decimal_val:
#         val = str(decimal_val)
#         comps = val.split('.')
#         i = comps[0]
#         if len(comps) == 2:
#             d = comps[1]
#         else:
#             d = None
#         if len(i) > 6:
#             val = i[:-6] + ',' + i[-6:-3] + ',' + i[-3:]
#         elif len(i) > 3:
#             val = i[:-3] + ',' + i[-3:]
#         if d:
#             if decimal_digits:
#                 val += ".{}".format(d[:decimal_digits])
#             else:
#                 val += ".{}".format(d)
#         return val


def dehumanize_decimal(string_val):
    if string_val:
        val = string_val.replace(',', '')
        return val
