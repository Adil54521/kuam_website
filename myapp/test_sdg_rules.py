from unittest import TestCase

from .sdg_rules import MAX_SDG_TAGS, SDG_RULES, classify_news


class ClassifyNewsTests(TestCase):
    def assert_goal(self, expected_number, **news):
        result = classify_news(**news)
        self.assertIn(expected_number, [tag["number"] for tag in result])

    def test_rules_cover_all_17_goals(self):
        self.assertEqual(set(SDG_RULES), set(range(1, 18)))

    def test_quality_education(self):
        self.assert_goal(
            4,
            title="День знаний и новые образовательные программы",
        )

    def test_clean_energy(self):
        self.assert_goal(
            7,
            title="Солнечные панели и возобновляемая энергия",
        )

    def test_decent_work(self):
        self.assert_goal(
            8,
            title="Ярмарка вакансий и трудоустройство выпускников",
        )

    def test_responsible_consumption(self):
        self.assert_goal(
            12,
            title="Раздельный сбор и переработка отходов",
        )

    def test_climate_action(self):
        self.assert_goal(
            13,
            title="Изменение климата и сокращение выбросов",
        )

    def test_partnerships(self):
        self.assert_goal(
            17,
            title="Международное сотрудничество и меморандум",
        )

    def test_neutral_news_has_no_tags(self):
        self.assertEqual(
            classify_news(
                title="В университете состоялось мероприятие",
                content_rus="Студенты и преподаватели обсудили планы кафедры.",
            ),
            [],
        )

    def test_news_can_have_multiple_goals(self):
        result = classify_news(
            title="Чистая энергия, переработка отходов и изменение климата",
            content_rus=(
                "Солнечные панели, раздельный сбор и сокращение выбросов "
                "стали основными темами проекта."
            ),
        )
        self.assertEqual({tag["number"] for tag in result}, {7, 12, 13})

    def test_never_returns_more_than_three_tags(self):
        result = classify_news(
            content_rus=(
                "Качественное образование, чистая вода и санитария, "
                "возобновляемые источники энергии, переработка отходов, "
                "изменение климата, международное сотрудничество."
            )
        )
        self.assertLessEqual(len(result), MAX_SDG_TAGS)

    def test_handles_none_and_html(self):
        result = classify_news(
            title=None,
            content_rus="<h2>Академическая честность</h2>",
            content_kaz=None,
            content_eng=None,
        )
        self.assertIn(4, [tag["number"] for tag in result])

    def test_keyword_in_title_and_body_is_counted_only_once(self):
        result = classify_news(
            title="Качественное образование",
            content_rus="Тема проекта — качественное образование.",
        )
        goal_4 = next(tag for tag in result if tag["number"] == 4)
        self.assertEqual(goal_4["score"], 30)

