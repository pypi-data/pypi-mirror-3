# coding: utf-8

parts = u' ▁▂▃▄▅▆▇▉'

def sparks(nums):
    fraction = max(nums) / float(len(parts) - 1)
    return ''.join(parts[0 if x ==0 else int(round(x/fraction))] for x in nums)


