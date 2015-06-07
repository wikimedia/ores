revert_window = 48 # hours
revert_radius = 3  # revisions

enwiki_api = https://en.wikipedia.org/w/api.php
fawiki_api = https://fa.wikipedia.org/w/api.php
frwiki_api = https://fr.wikipedia.org/w/api.php
ptwiki_api = https://pt.wikipedia.org/w/api.php
trwiki_api = https://tr.wikipedia.org/w/api.php

########################### English Wikipedia ##################################
datasets/enwiki.rev_reverted.20k.tsv: datasets/enwiki.rev_pages.20k.tsv
	cat datasets/enwiki.rev_pages.20k.tsv | \
	./utility label_reverted \
		--api=$(enwiki_api) \
		--revert-window=$(revert_window) \
		--revert-radius=$(revert_radius) > \
	datasets/enwiki.rev_reverted.20k.tsv

datasets/enwiki.features_reverted.20k.tsv: datasets/enwiki.rev_reverted.20k.tsv
	cat datasets/enwiki.rev_reverted.20k.tsv | \
	revscoring extract_features \
		ores.feature_lists.enwiki.damaging \
		--api=$(enwiki_api) \
		--language=revscoring.languages.english > \
	datasets/enwiki.features_reverted.20k.tsv

models/enwiki.reverted.linear_svc.model: \
		datasets/enwiki.features_reverted.20k.tsv
	cat datasets/enwiki.features_reverted.20k.tsv | \
	revscoring train_test \
		revscoring.scorer_models.LinearSVCModel \
		ores.feature_lists.enwiki.damaging \
		revscoring.languages.english > \
	models/enwiki.reverted.linear_svc.model

datasets/enwiki.features_wp10.30k.tsv: datasets/enwiki.rev_wp10.30k.tsv
	cat datasets/enwiki.rev_wp10.30k.tsv | \
	revscoring extract_features \
		ores.feature_lists.enwiki.wp10 \
		--api=$(enwiki_api) \
		--language=revscoring.languages.english > \
	datasets/enwiki.features_wp10.30k.tsv

models/enwiki.wp10.rf.model: datasets/enwiki.features_wp10.30k.tsv
	cat datasets/enwiki.features_wp10.30k.tsv | \
	revscoring train_test \
		revscoring.scorer_models.RFModel \
		ores.feature_lists.enwiki.wp10 \
		revscoring.languages.english > \
	models/enwiki.wp10.rf.model


###################### Persian Wikipedia ####################################
datasets/fawiki.rev_reverted.20k.tsv: datasets/fawiki.rev_pages.20k.tsv
	cat datasets/fawiki.rev_pages.20k.tsv | \
	./utility label_reverted \
		--api=$(fawiki_api) \
		--revert-window=$(revert_window) \
		--revert-radius=$(revert_radius) > \
	datasets/fawiki.rev_reverted.20k.tsv

datasets/fawiki.features_reverted.20k.tsv: datasets/fawiki.rev_reverted.20k.tsv
	cat datasets/fawiki.rev_reverted.20k.tsv | \
	revscoring extract_features \
		ores.feature_lists.fawiki.damaging \
		--api=$(fawiki_api) \
		--language=revscoring.languages.persian > \
	datasets/fawiki.features_reverted.20k.tsv

models/fawiki.reverted.linear_svc.model: \
		datasets/fawiki.features_reverted.20k.tsv
	cat datasets/fawiki.features_reverted.20k.tsv | \
	revscoring train_test \
		revscoring.scorer_models.LinearSVCModel \
		ores.feature_lists.fawiki.damaging \
		revscoring.languages.persian > \
	models/fawiki.reverted.linear_svc.model


###################### French Wikipedia ####################################
datasets/frwiki.rev_reverted.20k.tsv: datasets/frwiki.rev_pages.20k.tsv
	cat datasets/frwiki.rev_pages.20k.tsv | \
	./utility label_reverted \
		--api=$(frwiki_api) \
		--revert-window=$(revert_window) \
		--revert-radius=$(revert_radius) > \
	datasets/frwiki.rev_reverted.20k.tsv

datasets/frwiki.features_reverted.20k.tsv: datasets/frwiki.rev_reverted.20k.tsv
	cat datasets/frwiki.rev_reverted.20k.tsv | \
	revscoring extract_features \
		ores.feature_lists.frwiki.damaging \
		--api=$(frwiki_api) \
		--language=revscoring.languages.french > \
	datasets/frwiki.features_reverted.20k.tsv

models/frwiki.reverted.linear_svc.model: \
		datasets/frwiki.features_reverted.20k.tsv
	cat datasets/frwiki.features_reverted.20k.tsv | \
	revscoring train_test \
		revscoring.scorer_models.LinearSVCModel \
		ores.feature_lists.frwiki.damaging \
		revscoring.languages.french > \
	models/frwiki.reverted.linear_svc.model

###################### Portuguese Wikipedia ####################################
datasets/ptwiki.rev_reverted.20k.tsv: datasets/ptwiki.rev_pages.20k.tsv
	cat datasets/ptwiki.rev_pages.20k.tsv | \
	./utility label_reverted \
		--api=$(ptwiki_api) \
		--revert-window=$(revert_window) \
		--revert-radius=$(revert_radius) > \
	datasets/ptwiki.rev_reverted.20k.tsv

datasets/ptwiki.features_reverted.20k.tsv: datasets/ptwiki.rev_reverted.20k.tsv
	cat datasets/ptwiki.rev_reverted.20k.tsv | \
	revscoring extract_features \
		ores.feature_lists.ptwiki.damaging \
		--api=$(ptwiki_api) \
		--language=revscoring.languages.portuguese > \
	datasets/ptwiki.features_reverted.20k.tsv

models/ptwiki.reverted.linear_svc.model: \
		datasets/ptwiki.features_reverted.20k.tsv
	cat datasets/ptwiki.features_reverted.20k.tsv | \
	revscoring train_test \
		revscoring.scorer_models.LinearSVCModel \
		ores.feature_lists.ptwiki.damaging \
		revscoring.languages.portuguese > \
	models/ptwiki.reverted.linear_svc.model


######################### Turkish Wikipedia ####################################
datasets/trwiki.rev_reverted.20k.tsv: datasets/trwiki.rev_pages.20k.tsv
	cat datasets/trwiki.rev_pages.20k.tsv | \
	./utility label_reverted \
		--api=$(trwiki_api) \
		--revert-window=$(revert_window) \
		--revert-radius=$(revert_radius) > \
	datasets/trwiki.rev_reverted.20k.tsv

datasets/trwiki.features_reverted.20k.tsv: datasets/trwiki.rev_reverted.20k.tsv
	cat datasets/trwiki.rev_reverted.20k.tsv | \
	revscoring extract_features \
		ores.feature_lists.trwiki.damaging \
		--api=$(trwiki_api) \
		--language=revscoring.languages.turkish > \
	datasets/trwiki.features_reverted.20k.tsv

models/trwiki.reverted.linear_svc.model: \
		datasets/trwiki.features_reverted.20k.tsv
	cat datasets/trwiki.features_reverted.20k.tsv | \
	revscoring train_test \
		revscoring.scorer_models.LinearSVCModel \
		ores.feature_lists.trwiki.damaging \
		revscoring.languages.turkish > \
	models/trwiki.reverted.linear_svc.model
