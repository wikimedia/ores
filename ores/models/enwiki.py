from revscoring.features import (added_badwords_ratio, added_misspellings_ratio,
                                 day_of_week_in_utc, hour_of_day_in_utc,
                                 is_content_namespace, is_custom_comment,
                                 is_section_comment,
                                 longest_repeated_char_added,
                                 longest_token_added, numeric_chars_added,
                                 prev_words, proportion_of_markup_added,
                                 proportion_of_numeric_added,
                                 proportion_of_symbolic_added,
                                 proportion_of_uppercase_added,
                                 seconds_since_last_page_edit,
                                 user_age_in_seconds, user_is_anon, user_is_bot,
                                 words_added, words_removed)
from revscoring.features.modifiers import log
from revscoring.languages import english
from revscoring.scorers import LinearSVCModel, RBFSVCModel

features = [
    log(added_badwords_ratio + 1),
    log(added_misspellings_ratio + 1),
    log(longest_repeated_char_added + 1),
    log(longest_token_added + 1),
    log(numeric_chars_added + 1),
    log(prev_words + 1),
    log(proportion_of_markup_added + 1),
    log(proportion_of_numeric_added + 1),
    log(proportion_of_symbolic_added + 1),
    log(proportion_of_uppercase_added + 1),
    log(seconds_since_last_page_edit + 1),
    log(words_added + 1),
    log(words_removed + 1),
    log(user_age_in_seconds + 1),
    user_is_anon,
    user_is_bot,
    day_of_week_in_utc,
    hour_of_day_in_utc,
    is_custom_comment,
    is_content_namespace,
    is_section_comment
]

linear_svc = LinearSVCModel(features, english)
rbf_svc = RBFSVCModel(features, english)
