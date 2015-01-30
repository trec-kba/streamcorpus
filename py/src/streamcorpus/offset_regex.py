'''
This module defines a regular expression named ``RE_TOKENS`` that is
meant to be used with the ``REGEX`` offset type. Generally speaking,
it is useful as a tokenizer that can be consistently applied across
various programming environments (specifically, Javascript and Python).
'''
import re

RANGES_CHINESE = u'\u2E80-\u2EFF\u3000-\u303F\u3200-\u32FF' \
                  '\u3400-\u4DBF\u4E00-\u9FFF'
TOKENS = ur'[{RANGES_CHINESE}]|([^\s{RANGES_CHINESE}]+)'.format(
    RANGES_CHINESE=RANGES_CHINESE)
RE_TOKENS = re.compile(TOKENS)

