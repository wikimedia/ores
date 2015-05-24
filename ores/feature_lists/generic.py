from revscoring.features import (diff, page, parent_revision,
                                 previous_user_revision, revision, user)
from revscoring.features.modifiers import log

generic_ratio = [
    diff.added_markup_chars_ratio,
    diff.added_number_chars_ratio,
    diff.added_symbolic_chars_ratio,
    diff.added_uppercase_chars_ratio,
    diff.bytes_changed_ratio,
    log(diff.proportion_of_chars_added + 1),
    log(diff.proportion_of_chars_removed + 1),
    log(diff.proportion_of_markup_chars_added + 1),
    log(diff.proportion_of_numeric_chars_added + 1),
    log(diff.proportion_of_symbolic_chars_added + 1),
    log(diff.proportion_of_uppercase_chars_added + 1),
    parent_revision.proportion_of_markup_chars,
    parent_revision.proportion_of_numeric_chars,
    parent_revision.proportion_of_symbolic_chars,
    parent_revision.proportion_of_uppercase_chars,
    revision.proportion_of_markup_chars,
    revision.proportion_of_numeric_chars,
    revision.proportion_of_symbolic_chars,
    revision.proportion_of_templated_references,
    revision.proportion_of_uppercase_chars
]

generic_added = [
    log(diff.chars_added + 1),
    log(diff.longest_repeated_char_added + 1),
    log(diff.longest_token_added + 1),
    log(diff.markup_chars_added + 1),
    log(diff.numeric_chars_added + 1),
    log(diff.segments_added + 1),
    log(diff.symbolic_chars_added + 1),
    log(diff.uppercase_chars_added + 1),
    log(diff.words_added + 1)
]

generic_removed = [
    log(diff.chars_removed + 1),
    log(diff.markup_chars_removed + 1),
    log(diff.numeric_chars_removed + 1),
    log(diff.segments_removed + 1),
    log(diff.symbolic_chars_removed + 1),
    log(diff.uppercase_chars_removed + 1),
    log(diff.words_removed + 1)
]

generic_count = [
    parent_revision.bytes,
    log(parent_revision.chars + 1),
    log(parent_revision.markup_chars + 1),
    log(parent_revision.numeric_chars + 1),
    log(parent_revision.revision_bytes + 1),
    log(parent_revision.symbolic_chars + 1),
    log(parent_revision.uppercase_chars + 1),
    log(parent_revision.words + 1),
    log(revision.chars + 1),
    log(revision.markup_chars + 1),
    log(revision.numeric_chars + 1),
    log(revision.words + 1),
    log(revision.symbolic_chars + 1),
    log(revision.uppercase_chars + 1)
]

generic_wikimarkup = [
    page.is_mainspace,
    page.is_content_namespace,
    log(revision.cite_templates + 1),
    log(revision.has_custom_comment + 1),
    log(revision.has_section_comment + 1),
    log(revision.image_links + 1),
    log(revision.infobox_templates + 1),
    log(revision.internal_links + 1),
    log(revision.level_1_headings + 1),
    log(revision.level_2_headings + 1),
    log(revision.level_3_headings + 1),
    log(revision.level_4_headings + 1),
    log(revision.level_5_headings + 1),
    log(revision.level_6_headings + 1),
    log(revision.ref_tags + 1),
    log(revision.templates + 1)
]

generic_other = [
    diff.bytes_changed,
    log(page.age + 1),
    log(parent_revision.seconds_since + 1),
    parent_revision.was_same_user,
    log(parent_revision.words + 1),
    log(previous_user_revision.seconds_since + 1),
    log(revision.day_of_week + 1),
    log(user.age + 1),
    log(previous_user_revision.seconds_since + 1),
    user.is_anon,
    user.is_bot
]

generic_unused = [
    revision.bytes,
    log(revision.category_links + 1),
    log(revision.hour_of_day + 1),
]

generic_minimalist = [
    log(diff.added_markup_chars_ratio + 1),
    log(diff.added_number_chars_ratio + 1),
    log(diff.added_symbolic_chars_ratio + 1),
    log(diff.added_uppercase_chars_ratio + 1),
    log(diff.chars_added + 1),
    log(diff.chars_removed + 1),
    log(diff.longest_repeated_char_added + 1),
    log(diff.longest_token_added + 1),
    log(diff.markup_chars_added + 1),
    log(diff.markup_chars_removed + 1),
    log(diff.numeric_chars_added + 1),
    log(diff.numeric_chars_removed + 1),
    diff.proportion_of_chars_added,
    diff.proportion_of_chars_removed,
    diff.proportion_of_markup_chars_added,
    diff.proportion_of_numeric_chars_added,
    diff.proportion_of_symbolic_chars_added,
    diff.proportion_of_uppercase_chars_added,
    log(diff.segments_added + 1),
    log(diff.segments_removed + 1),
    log(diff.symbolic_chars_added + 1),
    log(diff.symbolic_chars_removed + 1),
    log(diff.uppercase_chars_added + 1),
    log(diff.uppercase_chars_removed + 1),
    log(diff.words_added + 1),
    log(diff.words_removed + 1),
    diff.bytes_changed,
    diff.bytes_changed_ratio,
    page.is_content_namespace,
    parent_revision.was_same_user,
    log(user.age + 1),
    user.is_anon,
    user.is_bot
]

# generic = generic_ratio + generic_added + generic_removed + generic_count + generic_wikimarkup + generic_other
generic = generic_minimalist

damaging = generic

good_faith = generic
