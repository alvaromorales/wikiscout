import unittest
from scout.tools import infobox

class TestNormalizeTemplate(unittest.TestCase):
    def test_caps(self):
        assert infobox.normalize_template('INFOBOX_template') == 'infobox_template'

    def test_underscores(self):
        assert infobox.normalize_template('infobox__officeholder') == 'infobox_officeholder'

    def test_spaces(self):
        assert infobox.normalize_template(' INFOBOX__PERSON ') == 'infobox_person'

class TestNormalizeAttribute(unittest.TestCase):
    def test_valid(self):
        assert infobox.normalize_attribute('birth_date') == 'birth_date'

    def test_numbers(self):
        assert infobox.normalize_attribute('PREdecessor1') == 'predecessor'

    def test_spaces(self):
        assert infobox.normalize_attribute(' SUCCESSOR__17   ') == 'successor'

class TestValidationRules(unittest.TestCase):
    def test_valid_attribute(self):
        assert infobox.validate_attribute('predecessor3') == True

    def test_invalid_attribute(self):
        assert infobox.validate_attribute('1') == False

    def test_valid_template(self):
        assert infobox.validate_template('infobox_officeholder') == True

    def test_invalid_template(self):
        assert infobox.validate_template('infobox_person/template') == False
