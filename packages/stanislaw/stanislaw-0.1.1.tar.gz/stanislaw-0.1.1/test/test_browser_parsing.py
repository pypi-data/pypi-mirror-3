from unittest import TestCase
from stanislaw.browser import Browser
from stanislaw.forms import UnknownFormInput
from test.util import response_from_file

BASIC_FORM = "basic_form.html"
URL = "http://example.com/form.html"

def get_browser(url=URL, response_file=BASIC_FORM):
    b = Browser()
    b._set_response(response_from_file(url, response_file))
    return b


class FormFillTest(TestCase):
    def test_fill_all_form_values(self):
        browser = get_browser()
        browser.fill({"#first_name": "Niels",
                      "#last_name": "Bohr",
                      "#email_address": "bohr@lanl.gov"})

        self.assertEquals("Niels", browser.query("#first_name").val())
        self.assertEquals("Bohr", browser.query("#last_name").val())
        self.assertEquals("bohr@lanl.gov", browser.query("#email_address").val())

    def test_fill_some_form_values(self):
        browser = get_browser()
        browser.fill({"#first_name": "Niels",
                      "#last_name": "Bohr"})

        self.assertEquals("Niels", browser.query("#first_name").val())
        self.assertEquals("Bohr", browser.query("#last_name").val())
        self.assertEquals("teller@lanl.gov", browser.query("#email_address").val())

    def test_fill_nonexistant_element(self):
        browser = get_browser()
        self.assertRaises(UnknownFormInput, browser.fill,
                          {"#does_not_exist": "bad_value"})

        self.assertEquals("Edward", browser.query("#first_name").val())
        self.assertEquals("Teller", browser.query("#last_name").val())
        self.assertEquals("teller@lanl.gov", browser.query("#email_address").val())

class FormSerializationTest(TestCase):

    def test_form_value_list_simple(self):
        browser = get_browser()
        value_list = browser.form_manager.form_value_list()
        expected = [("first_name", "Edward"),
                    ("last_name", "Teller"),
                    ("email_address", "teller@lanl.gov")]
        self.assertEquals(expected, value_list)

    def test_value_list_after_fill(self):
        browser = get_browser()
        browser.fill({"#first_name": "Niels",
                      "#last_name": "Bohr",
                      "#email_address": "bohr@lanl.gov"})
        expected = [("first_name", "Niels"),
                    ("last_name", "Bohr"),
                    ("email_address", "bohr@lanl.gov")]
        value_list = browser.form_manager.form_value_list()
        self.assertEquals(expected, value_list)

    def test_doesnt_serialize_disabled_element(self):
        browser = get_browser(response_file="difficult_form.html")
        value_list = browser.form_manager.form_value_list()
        self.assertNotIn(("phone", "who uses phones?"), value_list)

    def test_serialize_no_defined_value(self):
        browser = get_browser(response_file="difficult_form.html")
        value_list = browser.form_manager.form_value_list()
        self.assertIn(("first_name", ""), value_list)
        self.assertIn(("last_name", ""), value_list)
        self.assertIn(("email_address", ""), value_list)
        self.assertIn(("biography", ""), value_list)

    def test_serialize_checkboxes(self):
        browser = get_browser(response_file="difficult_form.html")
        value_list = browser.form_manager.form_value_list()
        # An unchecked checkbox
        self.assertNotIn("legal_agree", [v[0] for v in value_list])

        # A checked checkbox, with value
        self.assertIn(("contact_me", "yes"), value_list)

        # A checked checkbox, no value
        self.assertIn(("checked_no_value", ""), value_list)

    def test_serialize_textareas(self):
        browser = get_browser(response_file="difficult_form.html")
        value_list = browser.form_manager.form_value_list()

        self.assertIn(("biography", ""), value_list)
        self.assertIn(("filled_textarea", "Textarea content"), value_list)
