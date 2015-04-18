from revscoring.features import (
    diff, page, parent_revision, previous_user_revision, revision, user
)
from revscoring.features.modifiers import log
from . import generic

damaging = generic.damaging + [
    log(max(diff.added_badwords_ratio + 1,1)),
    log(max(diff.added_misspellings_ratio + 1,1)),
    log(max(diff.badwords_added + 1,1)),
    log(max(diff.badwords_removed + 1,1)),
    log(max(diff.misspellings_added + 1,1)),
    log(max(diff.misspellings_removed + 1,1)),
    log(max(diff.proportion_of_badwords_added + 1,1)),
    log(max(diff.proportion_of_badwords_removed + 1,1)),
    log(max(diff.proportion_of_misspellings_added + 1,1)),
    log(max(diff.proportion_of_misspellings_removed + 1,1)),
    log(max(diff.removed_badwords_ratio + 1,1)),
    log(max(diff.removed_misspellings_ratio + 1,1)),
    log(max(parent_revision.badwords + 1,1)),
    log(max(parent_revision.misspellings + 1,1)),
    log(max(parent_revision.proportion_of_badwords + 1,1)),
    log(max(parent_revision.proportion_of_misspellings + 1,1)),
    log(max(revision.badwords + 1,1)),
    log(max(revision.misspellings + 1,1)),
    log(max(revision.proportion_of_badwords + 1,1)),
    log(max(revision.proportion_of_misspellings + 1,1)),
    log(revision.infonoise + 1)
]

good_faith = generic.good_faith + [
    log(max(diff.added_badwords_ratio + 1,1)),
    log(max(diff.added_misspellings_ratio + 1,1)),
    log(max(diff.badwords_added + 1,1)),
    log(max(diff.badwords_removed + 1,1)),
    log(max(diff.misspellings_added + 1,1)),
    log(max(diff.misspellings_removed + 1,1)),
    log(max(diff.proportion_of_badwords_added + 1,1)),
    log(max(diff.proportion_of_badwords_removed + 1,1)),
    log(max(diff.proportion_of_misspellings_added + 1,1)),
    log(max(diff.proportion_of_misspellings_removed + 1,1)),
    log(max(diff.removed_badwords_ratio + 1,1)),
    log(max(diff.removed_misspellings_ratio + 1,1)),
    log(max(parent_revision.badwords + 1,1)),
    log(max(parent_revision.misspellings + 1,1)),
    log(max(parent_revision.proportion_of_badwords + 1,1)),
    log(max(parent_revision.proportion_of_misspellings + 1,1)),
    log(max(revision.badwords + 1,1)),
    log(max(revision.misspellings + 1,1)),
    log(max(revision.proportion_of_badwords + 1,1)),
    log(max(revision.proportion_of_misspellings + 1,1)),
    log(revision.infonoise + 1)
]
