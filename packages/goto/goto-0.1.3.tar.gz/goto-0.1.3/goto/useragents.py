import random

class RNDDict(object):
    TPL = None
    DATA = {}
    
    def __getitem__(self, key):
        return random.choice(self.DATA[key])

    def __str__(self):
        return self.TPL % self


class UAOpera(RNDDict):
    # http://www.useragentstring.com/pages/Opera/
    TPL = '%(name)s (%(os)s; U; %(lang)s) Presto/%(presto)s Version/%(ver)s'
    DATA = {
        'name': ['Opera/9.80'],
        'os': ['Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1'],
        'lang': ['en', 'en-US', 'ru', 'de'],
        'presto': ['2.8.99', '2.8.131', '2.7.62'],
        'ver': ['11.10', '11.01'],
    }

class UAFirefox(RNDDict):
    TPL = '%(name)s (Windows; U; %(os)s; %(lang)s) Gecko/%(engine)s Firefox/%(ver)s'
    DATA = {
        'name': ['Mozilla/5.0'],
        'os': ['Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1'],
        'lang': ['en', 'en-US', 'ru', 'de'],
        'engine': ['20100401', '20091204', '20090402', '20091124', '20100824', '20100722'],
        'ver': ['4.0', '3.8', '3.6.9', '3.6.8', '3.6.7', '3.6.6', '3.6.5', '3.6.3', '3.6.2', '3.6.16', '3.6.15', '3.6.14', '3.6.13', '3.6.12',],
        'rv': ['1.9.2.8', '1.9.2.3', '1.9.2.9', '', '', ],
    }

class UAChrome(RNDDict):
    TPL = '%(name)s (%(os)s) AppleWebKit/%(engine)s (KHTML, like Gecko) Chrome/%(ver)s'
    DATA = {
        'name': ['Mozilla/5.0'],
        'os': ['Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1'],
        'engine': ['534.25', '534.24'],
        'ver': ['12.0.706.0 Safari/534.25', '12.0.702.0 Safari/534.24', '11.0.699.0 Safari/534.24', '11.0.697.0 Safari/534.24'],
    }

class UAIE8(RNDDict):
    TPL = '%(ua)s'
    DATA = {
        'ua': [s.strip() for s in '''
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; Media Center PC 4.0; SLCC1; .NET CLR 3.0.04320)
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 1.1.4322)
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727)
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)
            Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.0; Trident/4.0; InfoPath.1; SV1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 3.0.04506.30)
            Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.0; Trident/4.0; FBSMTWB; .NET CLR 2.0.34861; .NET CLR 3.0.3746.3218; .NET CLR 3.5.33652; msn OptimizedIE8;ENUS)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; Media Center PC 6.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.3; .NET4.0C; .NET4.0E; .NET CLR 3.5.30729; .NET CLR 3.0.30729; MS-RTC LM 8)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 3.0)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; msn OptimizedIE8;ZHCN)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8; InfoPath.3; .NET4.0C; .NET4.0E) chromeframe/8.0.552.224
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8; .NET4.0C; .NET4.0E; Zune 4.7; InfoPath.3)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8; .NET4.0C; .NET4.0E; Zune 4.7)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MS-RTC LM 8)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; Zune 4.0)
            Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; MS-RTC LM 8; Zune 4.7)
        '''.split('\n') if s.strip()],
    }

USER_AGENTS = [UAOpera, UAFirefox, UAChrome, UAIE8]

