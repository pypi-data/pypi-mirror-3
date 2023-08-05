from selenium.webdriver.support.ui import Select

def catch_assert(func):
    def wrap_func(self, *args, **kw):
        try:
            func(self, *args, **kw)
        except AssertionError as e:
            self.verificationErrors.append(str(e))
    return wrap_func


class WebdriverCommands(object):
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.verificationErrors = []

    def _tag_and_value(self, tvalue):
        # target can be e.g. "css=td.f_transfectionprotocol"
        s = tvalue.split('=')
        tag, value = s if len(s) == 2 else (None, None)

        if not tag in ['css', 'id', 'name', 'link', 'label']:
            # Older sel files do not specify a 'css' or 'id' prefix. Lets distinguish by inspecting 'target'
            # NOTE: This check is probably not complete here!!! Watch out for problems!!!
            value = tvalue
            if tvalue.startswith('//'):
                tag = 'xpath'
            else:
                tag = 'id'
        return tag, value

    def _find_target(self, target):
        ttype, ttarget = self._tag_and_value(target)
        if ttype == 'css':
            return self.driver.find_element_by_css_selector(ttarget)
        if ttype == 'xpath':
            return self.driver.find_element_by_xpath(ttarget)
        elif ttype == 'id':
            return self.driver.find_element_by_id(ttarget)
        elif ttype == 'name':
            return self.driver.find_element_by_name(ttarget)
        elif ttype == 'link':
            return self.driver.find_element_by_link_text(ttarget)
        else:
            raise RuntimeError('no way to find target "%s"' % target)

    ########################################################################################################

    def wd_open(self, target, value):
        self.driver.get(self.base_url + target)

    @catch_assert
    def wd_verifyTextPresent(self, target, value):
        assert target in self.driver.page_source

    @catch_assert
    def wd_verifyText(self, target, value):
        assert self._find_target(target) == value

    def wd_clickAndWait(self, target, value):
        self._find_target(target).click()

    def wd_select(self, target, value):
        target_elem = self._find_target(target)
        tag, tvalue = self._tag_and_value(value)
        if tag == 'label':
            Select(target_elem).select_by_visible_text(tvalue)
        else:
            raise NotImplementedError()

    def wd_type(self, target, value):
        target_elem = self._find_target(target)
        target_elem.clear()
        target_elem.send_keys(value)

    def wd_verifyElementPresent(self, target, value):
        # The following command raises an NoSuchElementException which we let through!
        self._find_target(target)
