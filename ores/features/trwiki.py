from revscoring.features import (
    diff, page, parent_revision, previous_user_revision, revision, user
)
from revscoring.features.modifiers import log
from . import generic

damaging = generic.damaging + [
    log(diff.added_badwords_ratio + 1),
    log(diff.badwords_added + 1),
    log(diff.badwords_removed + 1),
    log(diff.proportion_of_badwords_added + 1),
    log(diff.proportion_of_badwords_removed + 1),
    log(diff.removed_badwords_ratio + 1),
    log(parent_revision.badwords + 1),
    log(parent_revision.proportion_of_badwords + 1),
    log(revision.badwords + 1),
    log(revision.proportion_of_badwords + 1)
]

good_faith = generic.good_faith + [
    log(diff.added_badwords_ratio + 1),
    log(diff.badwords_added + 1),
    log(diff.badwords_removed + 1),
    log(diff.proportion_of_badwords_added + 1),
    log(diff.proportion_of_badwords_removed + 1),
    log(diff.removed_badwords_ratio + 1),
    log(parent_revision.badwords + 1),
    log(parent_revision.proportion_of_badwords + 1),
    log(revision.badwords + 1),
    log(revision.proportion_of_badwords + 1)
]
