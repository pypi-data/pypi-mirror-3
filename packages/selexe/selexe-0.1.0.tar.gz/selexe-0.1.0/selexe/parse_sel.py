import BeautifulSoup


def parse_sel(fp):
    soup = BeautifulSoup.BeautifulSoup(fp.read())
    body = soup.find('tbody')
    for tr in body.findAll('tr'):
        # return tuple (command, target, value) -> this corresponds to column names in Selenium IDE
        t = tuple([td.string for td in tr.findAll('td')])
        yield t



if __name__ == '__main__':
    fp = open('testdata/simple.sel')
    print list(parse_sel(fp))
