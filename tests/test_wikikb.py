import unittest
from wikiscout import wikikb


class TestPickBestLinks(unittest.TestCase):
    def test_no_match(self):
        article_links = [
            {
                "id": "harvard_university",
                "description": "Harvard University"
            },
        ]

        matching_links = [
            {"title": "Harvard (automobile)", "synonym": "Harvard", "wikiTitle": "Harvard_(automobile)"},
            {"title": "Harvard (Metra)", "synonym": "Harvard", "wikiTitle": "Harvard_(Metra)"},
        ]

        self.assertEquals("Harvard (automobile)", wikikb.pick_best_link(matching_links, article_links))

    def test_simple_match(self):
        article_links = [
            {
                "id": "one-dollar_salary",
                "description": "one-dollar salary"
            },
            {
                "id": "harvard_university",
                "description": "Harvard University"
            },
            {
                "id": "Eduardo_Saverin",
                "description": "Eduardo Saverin"
            },
        ]

        matching_links = [
            {"title": "Harvard (automobile)", "synonym": "Harvard", "wikiTitle": "Harvard_(automobile)"},
            {"title": "Harvard (Metra)", "synonym": "Harvard", "wikiTitle": "Harvard_(Metra)"},
            {"title": "Harvard University", "synonym": "Harvard", "wikiTitle": "Harvard_University"},
            {"title": "Harvard (MBTA station)", "synonym": "Harvard", "wikiTitle": "Harvard_(MBTA_station)"},
            {"title": "736 Harvard", "synonym": "Harvard", "wikiTitle": "736_Harvard"},
        ]

        self.assertEquals("Harvard University", wikikb.pick_best_link(matching_links, article_links))

    def test_single_hyperlink_match(self):
        article_links = [
            {
                "id": "Harvard_University#Colonial",
                "description": "Harvard University"
            },
        ]

        matching_links = [
            {"title": "Harvard University", "synonym": "Harvard", "wikiTitle": "Harvard_University"},
        ]

        self.assertEquals("Harvard University", wikikb.pick_best_link(matching_links, article_links))

    def test_hyperlink_match(self):
        article_links = [
            {
                "id": "Harvard_University#Colonial",
                "description": "Harvard University"
            },
        ]

        matching_links = [
            {"title": "Harvard University", "synonym": "Harvard", "wikiTitle": "Harvard_University#Students"},
        ]

        self.assertEquals("Harvard University", wikikb.pick_best_link(matching_links, article_links))
