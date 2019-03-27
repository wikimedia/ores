from ores.scoring.models.rev_id_scorer import RevIdScorer


def test_statistics():
    scorer = RevIdScorer()
    stats = scorer.info['statistics']

    # Debug output if the test crashes.
    print(stats.format_str({}, threshold_ndigits=1))
    print(stats['thresholds'].format_str({}, threshold_ndigits=1))

    assert round(stats['roc_auc']['micro'], 3) == 0.996
    assert round(stats['pr_auc']['micro'], 3) == 0.992

    optimized = stats.lookup(
        '"maximum recall @ !precision >= 0.8".labels.true')
    assert optimized == 0.5
