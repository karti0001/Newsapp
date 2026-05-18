from __future__ import annotations

import unittest

from wazzup.config import load_app_config, load_sources

MIN_EXPECTED_SOURCES = 15


class ConfigTests(unittest.TestCase):
    def test_load_sources(self) -> None:
        sources = load_sources("config/sources.yml")
        self.assertGreaterEqual(len(sources), MIN_EXPECTED_SOURCES)
        self.assertEqual("microsoft-security-threat-intelligence", sources[1].id)
        self.assertEqual("MS TI", sources[1].source_tag)
        self.assertIn("economist", {source.id for source in sources})
        self.assertIn("financial-times", {source.id for source in sources})
        self.assertIn("fd-nl", {source.id for source in sources})
        self.assertIn("the-hacker-news", {source.id for source in sources})
        self.assertNotIn("zandvoortsecourant", {source.id for source in sources})
        self.assertIn("formula1-official-news", {source.id for source in sources})
        self.assertIn("autosport-f1", {source.id for source in sources})
        self.assertIn("motorsport-f1", {source.id for source in sources})
        self.assertIn("racefans", {source.id for source in sources})
        self.assertIn("vi-net-binnen", {source.id for source in sources})
        self.assertIn("voetbalzone", {source.id for source in sources})
        self.assertNotIn("nba-official-news", {source.id for source in sources})
        self.assertNotIn("espn-nba", {source.id for source in sources})
        self.assertIn("github-blog", {source.id for source in sources})
        self.assertIn("openai-news", {source.id for source in sources})
        self.assertIn("anthropic-news", {source.id for source in sources})
        self.assertIn("hugging-face-blog", {source.id for source in sources})
        self.assertIn("azure-updates", {source.id for source in sources})
        self.assertIn("tech", {category for source in sources for category in source.categories})
        self.assertIn("ai", {category for source in sources for category in source.categories})
        self.assertIn("formula-1", {category for source in sources for category in source.categories})
        self.assertIn("football", {category for source in sources for category in source.categories})
        self.assertNotIn("nba", {category for source in sources for category in source.categories})
        timeout_by_id = {source.id: source.timeout_seconds for source in sources}
        weight_by_id = {source.id: source.weight for source in sources}
        feed_url_by_id = {source.id: source.feed_url for source in sources}
        source_by_id = {source.id: source for source in sources}
        self.assertEqual(30, timeout_by_id["microsoft-security-blog"])
        self.assertEqual("https://fd.nl/?rss", feed_url_by_id["fd-nl"])
        self.assertEqual("https://www.vi.nl/rss/nieuws", feed_url_by_id["vi-net-binnen"])
        self.assertEqual("https://www.voetbalzone.nl/rss.asp", feed_url_by_id["voetbalzone"])
        self.assertEqual("https://www.vi.nl/nieuws/net-binnen", source_by_id["vi-net-binnen"].homepage_url)
        self.assertEqual("https://www.voetbalzone.nl/", source_by_id["voetbalzone"].homepage_url)
        self.assertEqual(0.7, weight_by_id["formula1-official-news"])
        self.assertEqual(0.7, weight_by_id["autosport-f1"])
        self.assertEqual(0.7, weight_by_id["motorsport-f1"])
        self.assertEqual(0.7, weight_by_id["racefans"])
        self.assertEqual(1.0, weight_by_id["vi-net-binnen"])
        self.assertEqual(1.0, weight_by_id["voetbalzone"])
        self.assertIn("Accept", sources[0].headers)

    def test_load_app_config(self) -> None:
        config = load_app_config("config/interests.yml")
        self.assertEqual("en", config.summary_language)
        self.assertEqual(35, config.retention_days)
        self.assertGreaterEqual(len(config.interests), 3)
        negative_interests = {interest.id: interest for interest in config.interests if interest.weight < 0}
        self.assertIn("uk-politics", negative_interests)
        self.assertIn("celebrity-entertainment", negative_interests)
        self.assertIn("glamour", negative_interests["celebrity-entertainment"].keywords)
        interests = {interest.id: interest for interest in config.interests}
        self.assertIn("formula-1", interests)
        self.assertIn("football", interests)
        self.assertNotIn("nba", interests)
        self.assertIn("finance-investing", interests)
        self.assertIn("grand prix", interests["formula-1"].keywords)
        self.assertEqual(0.7, interests["formula-1"].weight)
        self.assertIn("investing", interests["finance-investing"].keywords)
        self.assertGreater(interests["football"].weight, interests["formula-1"].weight)
        self.assertEqual(1.0, interests["football"].weight)
        self.assertIn("voetbal", interests["football"].keywords)


if __name__ == "__main__":
    unittest.main()
