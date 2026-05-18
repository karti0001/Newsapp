from __future__ import annotations

import unittest
from datetime import UTC, datetime
from pathlib import Path

from wazzup.config import load_app_config, load_sources
from wazzup.feeds import parse_feed
from wazzup.models import AppConfig, ContentItem, Interest, SourceConfig
from wazzup.scoring import score_items


def content_item(item_id: str, title: str, summary: str, source_id: str = "news") -> ContentItem:
    return ContentItem(
        schema_version=1,
        id=item_id,
        source_id=source_id,
        source_name="News",
        source_tag="NEWS",
        source_type="rss",
        title=title,
        url=f"https://example.com/{item_id}",
        canonical_url=f"https://example.com/{item_id}",
        published_at="2026-05-08T10:00:00Z",
        discovered_at="2026-05-08T10:00:00Z",
        authors=[],
        tags=[],
        language="en",
        summary=summary,
        content_hash=f"hash-{item_id}",
        raw_ref=item_id,
    )


class ScoringTests(unittest.TestCase):
    def test_threat_intelligence_source_scores_high(self) -> None:
        sources = load_sources("config/sources.yml")
        app_config = load_app_config("config/interests.yml")
        items = []
        for source in sources:
            path = Path("tests/fixtures") / f"{source.id}.xml"
            if not path.exists():
                continue
            items.extend(parse_feed(source, path.read_bytes()))
        scored = score_items(items, sources, app_config, datetime(2026, 5, 6, 17, tzinfo=UTC))
        self.assertEqual("microsoft-security-threat-intelligence", scored[0].item.source_id)
        self.assertIn("security", scored[0].matched_interests)

    def test_negative_interest_weight_demotes_without_positive_interest_match(self) -> None:
        source = SourceConfig(
            id="news",
            name="News",
            source_tag="NEWS",
            type="rss",
            homepage_url="https://example.com",
            feed_url="https://example.com/feed.xml",
            language="en",
            region="global",
            weight=1.0,
        )
        app_config = AppConfig(
            summary_language="en",
            retention_days=35,
            timezone="Europe/Amsterdam",
            morning_local_time="07:00",
            evening_local_time="20:00",
            interests=[
                Interest(id="security", name="Security", weight=1.0, keywords=["security"]),
                Interest(id="celebrity-entertainment", name="Celebrity and entertainment", weight=-1.0, keywords=["glamour"]),
            ],
        )
        base_item = content_item("security-only", "Security patch released", "Security update for cloud systems.")
        demoted_item = content_item(
            "security-glamour",
            "Security patch dominates glamour event",
            "Security update discussed during a glamour event.",
        )

        scored_by_id = {
            scored.item.id: scored
            for scored in score_items([base_item, demoted_item], [source], app_config, datetime(2026, 5, 8, 11, tzinfo=UTC))
        }

        self.assertGreater(scored_by_id["security-only"].score, scored_by_id["security-glamour"].score)
        self.assertEqual(["security"], scored_by_id["security-glamour"].matched_interests)
        self.assertTrue(
            any(reason.startswith("demotes Celebrity and entertainment") for reason in scored_by_id["security-glamour"].score_reasons)
        )

    def test_football_scores_above_formula_one_for_sports_items(self) -> None:
        sources = [
            SourceConfig(
                id="football",
                name="Football",
                source_tag="FOOT",
                type="rss",
                homepage_url="https://www.voetbalzone.nl/",
                feed_url="https://www.voetbalzone.nl/rss.asp",
                language="nl",
                region="nl",
                weight=1.0,
            ),
            SourceConfig(
                id="formula-1",
                name="Formula 1",
                source_tag="F1",
                type="rss",
                homepage_url="https://www.formula1.com/",
                feed_url="https://www.formula1.com/en/latest/all.xml",
                language="en",
                region="global",
                weight=0.7,
            ),
        ]
        app_config = AppConfig(
            summary_language="en",
            retention_days=35,
            timezone="Europe/Amsterdam",
            morning_local_time="07:00",
            evening_local_time="20:00",
            interests=[
                Interest(id="football", name="Football", weight=1.0, keywords=["voetbal"]),
                Interest(id="formula-1", name="Formula 1", weight=0.7, keywords=["formula 1"]),
            ],
        )
        football_item = content_item("football", "Voetbal transfernieuws", "Nieuwe voetbaltransfer bevestigd.", "football")
        formula_one_item = content_item("formula-1", "Formula 1 paddock news", "Formula 1 update from the paddock.", "formula-1")

        scored_by_id = {
            scored.item.id: scored
            for scored in score_items(
                [formula_one_item, football_item],
                sources,
                app_config,
                datetime(2026, 5, 8, 11, tzinfo=UTC),
            )
        }

        self.assertGreater(scored_by_id["football"].score, scored_by_id["formula-1"].score)
        self.assertEqual(["football"], scored_by_id["football"].matched_interests)
        self.assertEqual(["formula-1"], scored_by_id["formula-1"].matched_interests)


if __name__ == "__main__":
    unittest.main()
