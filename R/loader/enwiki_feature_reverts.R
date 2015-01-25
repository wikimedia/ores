source("env.R")
source("util.R")

load_enwiki_feature_reverts = tsv_loader(
    paste(DATA_DIR, "enwiki.v2.features_reverted.5k.tsv", sep="/"),
    "ENWIKI_FEATURE_REVERTS",
    function(dt){
        names(dt) = c(
            "added_badwords_ratio",
            "added_misspellings_ratio",
            "day_of_week_in_utc",
            "hour_of_day_in_utc",
            "is_custom_comment",
            "is_mainspace",
            "is_section_comment",
            "longest_repeated_char_added",
            "longest_token_added",
            "numeric_chars_added",
            "prev_words",
            "proportion_of_markup_added",
            "proportion_of_numeric_added",
            "proportion_of_symbolic_added",
            "proportion_of_uppercase_added",
            "seconds_since_last_page_edit",
            "segments_added",
            "segments_removed",
            "user_age_in_seconds",
            "user_is_anon",
            "user_is_bot",
            "reverted"
        )
        dt
    }
)
