from pressure_skill.i18n import infer_locale, merge_locale


def test_infer_locale_english():
    s = "My manager keeps asking for a full report by EOD without clear scope."
    assert infer_locale(s) == "en"


def test_infer_locale_chinese():
    s = "老板说明天必须交，但什么叫详细他不说清楚。"
    assert infer_locale(s) == "zh"


def test_merge_locale_prefers_english_when_dominant():
    assert merge_locale(" ".join(["deadline"] * 20), "x") == "en"
