import re
import urllib
import urllib2

# Borrowed from jQuery
INPUT_TYPES = re.compile("^(color|date|datetime|datetime-local|email|"
                         "hidden|month|number|password|range|search|"
                         "tel|text|time|url|week)$", re.IGNORECASE)
SELECT_TEXTAREA = re.compile("^(select|textarea)$", re.IGNORECASE)


class SubmitException(Exception):
    pass

class UnknownFormInput(Exception):
    pass


# Form value getters that aren't straightforward
def get_select_val(element):
    # TODO: only returns the first selected value
    for child in element.getiterator():
        if child.tag != "option":
            continue
        if "disabled" in child.attrib:
            continue
        if "selected" in child.attrib:
            return child.attrib.get("value", "")

def get_textarea_val(element):
    return element.text or ""


class FormManager(object):
    def __init__(self, browser):
        self.browser = browser

    def fill(self, selector_value_dict):
        for selector, value in selector_value_dict.items():
            form_element = self.browser.query(selector)
            if not form_element:
                raise UnknownFormInput(selector)
            self._set_value(form_element, value)

    def _set_value(self, form_element, value):
        for element in form_element:
            # PyQuery array
            if element.tag == "input" and (element.type == "checkbox"
                                           or element.type=="radio"):
                element.checked = bool(value)
            else:
                element.value = unicode(value)

    def find_form(self, form_selector=None):
        if form_selector:
            form = self.browser.query(form_selector)
        else:
            form = self.browser.query("form")

        if not form:
            msg = "Could not find any form on this page to submit."
            if form_selector:
                msg = "Could not find form: %s" % form_selector
            raise SubmitException(msg)

        if len(form) > 1:
            raise SubmitException("Found %d forms on this page, "
                                  "please explicitly select one to submit "
                                  "by passing form_selector to submit()."
                                  % len(form))
        return form[0]

    def _is_submittable_form_element(self, element):
        attributes = element.attrib
        if "name" not in attributes:
            return False
        if "disabled" in attributes:
            return False
        if "checked" in attributes:
            return True
        if re.match(SELECT_TEXTAREA, element.tag):
            return True
        if re.match(INPUT_TYPES, attributes.get("type", "")):
            return True

        return False

    def _form_element_value(self, element):
        # PyQuery fucks this up, borrowing-ish from jQuery
        # My complements to Resig, jQuery is quite slick in how it does .val()

        if "value" in element.attrib:
            return element.attrib["value"]

        if element.tag == "select":
            return get_select_val(element)

        if element.tag == "textarea":
            return get_textarea_val(element)

        return ""


    def form_value_list(self, form_selector=None):
        form = self.find_form(form_selector)
        value_list = [] # (input_name, value)

        for descendant in form.getiterator():
            if self._is_submittable_form_element(descendant):
                val = self._form_element_value(descendant)
                value_list.append((descendant.attrib["name"], val))

        return value_list

    def get_submit_request(self, form_selector=None):
        form = self.find_form()
        method = form.attrib["method"].lower()
        action = form.attrib["action"].lower()

        form_values = self.form_value_list(form_selector)
        encoded_values = urllib.urlencode(form_values)
        if method == "get":
            url = action + "?" + encoded_values
            request = urllib2.Request(url)
        if method == "post":
            request = urllib2.Request(action, encoded_values)

        return request
