#!/usr/bin/python
# -*- coding: utf-8 -*-

'''

http://stackoverflow.com/questions/280712/javascript-unicode-regexes

 http://en.wikipedia.org/wiki/CJK_Unified_Ideographs


'''

import regex as re

token_re = re.compile(ur'[\u2E80-\u2EFF\u3000-\u303F\u3200-\u32FF\u3400-\u4DBF\u4E00-\u9FFF]' + \
                      ur'|[^\s\n\r\u2E80-\u2EFF\u3000-\u303F\u3200-\u32FF\u3400-\u4DBF\u4E00-\u9FFF]+')
                      #ur'|(P<spans>\<span\>)')

text = u'''
This is some text



in Chinese




that we can all see as separate tokens:






Isabella quarter obverse.jpg伊莎贝拉25美分硬币又名哥伦布博览会25美分硬
币，是1893年铸造的一种美国纪念币，由联邦国会应芝加哥哥伦布纪念博览会女
士经理人董事会的请求授权发行。这种25美分硬币上刻有西班牙女王伊莎贝拉的
形象，当年正是因为有她的资助，克里斯托弗·哥伦布才得以远航前往新大陆。硬
币由美国铸币局首席雕刻师查尔斯·爱德华·巴伯设计，是美国发行的所有25美分
纪念币中唯一没有进入市场流通的一种。以芝加哥社交名媛伯莎·帕尔默为首的女
士经理人董事会希望由女性来设计这种硬币，她们为此请来雕塑家卡罗琳·佩德尔，
但佩德尔因同铸币局官员存在分歧而退出项目，设计工作于是落到巴伯的肩上。
硬币背面描绘的是位正在纺纱的女性，左手持有拉线棒，右手拿着锭子，代表女
性的工作行业，图案是基于助理雕刻师乔治·T·摩根的草图设计。钱币学媒体对硬
币设计评价不佳，硬币本身当年在博览会上也不畅销，由于定价和哥伦布半美元




一样都是1美元，所以25美分面值看起来不像半美元那么划算。最终有近一半已经
铸造的硬币送回铸币局熔毁，近万枚由各女士经理人以面值买下，再在20世纪初
进入钱币市场。如今，这些硬币深受收藏家追捧，根据理查德·约曼2014年版的
《美国钱币指南手册》，这些硬币的价值约在450到6000美元之间。

'''


def print_regex_offsets():
    for m in token_re.finditer(text):
        start, end = m.span()
        print start, end, text[start:end].encode('utf8')


def test_regex_offsets():
    without_collapse = [text[m.span()[0] : m.span()[1]].encode('utf8')
                        for m in token_re.finditer(text)]
    collapsed_text = re.sub(r'\s+', ' ', text, re.MULTILINE)
    #collapsed_text = collapsed_text[:30] + '<span>' + collapsed_text[30:]
    assert len(collapsed_text) < len(text)
    with_collapse = [collapsed_text[m.span()[0] : m.span()[1]].encode('utf8')
                     for m in token_re.finditer(collapsed_text)]

    assert with_collapse == without_collapse, set(with_collapse) - set(without_collapse)

        
if __name__ == '__main__':
    test_regex_offsets()
