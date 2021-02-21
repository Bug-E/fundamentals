import scrapy
from scrapy.selector import Selector
import re

class ScreenerSpider(scrapy.Spider):
    name = 'screener'
    allowed_domains = ['screener.in']
    start_urls = ['https://www.screener.in/screens/']
    # start_urls = ['https://www.screener.in/company/EQUITAS']

    def parse(self, response):
        print('Parse: ', response.url)
        url = response.url
        if re.search('login', url) or re.search('register', url) or re.search(
                'actions\/', url) or re.search('limit\=', url):
            return
        if re.search('screener\.in\/company\/[\da-zA-Z]+\/', response.url):
            name = response.selector.xpath('//h1/text()').get()
            ratios = response.selector.xpath(
                '//ul[@id="top-ratios"]//span[@class="number"]')
            data_company_id = response.selector.xpath(
                '//div[@id="company-info"]/@data-company-id').get()
            if len(ratios) != 10:
                raise Exception("Expected 10 ratio numbers")
            # capture yearly metrics
            vals = response.selector.xpath(
                '//section[@id="profit-loss"]/div/table/tbody/tr/td')
            cols = response.selector.xpath(
                '//section[@id="profit-loss"]/div/table/thead/tr/th')
            dataCols = len(cols) - 1

            heads = ['sales', 'expenses', 'operating profit', 'opm', 'other income', 'interest',
                     'depreciation', 'profit before tax', 'tax', 'net profit', 'eps', 'dividend %']
            try:
                for i in range(dataCols):
                    d = {'name': parseVal(name),
                         'date': parseVal(Selector(text=cols[i + 1].get()).xpath('//text()').get()),
                         'type': 'YEARLY',
                         'data-company-id': data_company_id,
                         'cap': parseVal(getText(ratios, 0)),
                         'pe': parseVal(getText(ratios, 4)),
                         'current price': parseVal(getText(ratios, 1))}
                    for j in range(len(heads)):
                        d[heads[j]] = parseVal(Selector(text=vals[(j*(dataCols+1))+i+1].get()).xpath('//text()').get())
                    yield d
            except:
                pass

            # capture quarterly matrics
            vals = response.selector.xpath(
                '//section[@id="quarters"]/div/table/tbody/tr/td')
            cols = response.selector.xpath(
                '//section[@id="quarters"]/div/table/thead/tr/th')
            dataCols = len(cols) - 1

            heads = ['sales', 'expenses', 'operating profit', 'opm', 'other income', 'interest',
                     'depreciation', 'profit before tax', 'tax', 'net profit', 'eps', 'dividend %']

            try:
                for i in range(dataCols):
                    d = {'name': parseVal(name),
                         'date': parseVal(Selector(text=cols[i + 1].get()).xpath('//text()').get()),
                         'type': 'QARTERLY',
                         'data-company-id': data_company_id,
                         'cap': parseVal(getText(ratios, 0)),
                         'pe': parseVal(getText(ratios, 4)),
                         'current price': parseVal(getText(ratios, 1))}
                    for j in range(len(heads)):
                        d[heads[j]] = parseVal(Selector(text=vals[(j*(dataCols+1))+i+1].get()).xpath('//text()').get())
                    yield d
            except:
                pass
        else:
            nextPageUrls = getNextPageUrls(response)
            for url in nextPageUrls:
                yield scrapy.Request(response.urljoin(url))

def getText(sel, i):

    return Selector(text=sel[i].get()).xpath('//text()').get()

def parseVal(val):

    if val is None:
        return None
    val = val.strip()
    try:
        return int(val)
    except:
        pass
    try:
        return float(val)
    except:
        pass
    try:
        if val == 'True' or val == 'true' or val == 'False' or val == 'false':
            return bool(val)
    except:
        pass
    try:
        if type(val) == str and val.endswith('%'):
            return parseVal(val[:-1])
    except:
        pass
    return val

def getNextPageUrls(response):
    links = response.selector.xpath('//a/@href').extract()
    companyPages = []
    other = []
    for l in links:
        if re.search('login', l) or re.search('register', l) or re.search(
                'actions\/', l) or re.search('limit\=', l):
            continue
        if re.search('\/company\/[\da-zA-Z]+\/', l):
            match = re.search('\/company\/[\da-zA-Z]+\/', l)
            span = match.span()
            l = l[span[0]:span[1]]
            companyPages += [l]
        elif re.search('screens', l) or re.search('page', l):
            other += [l]
    return companyPages + other



