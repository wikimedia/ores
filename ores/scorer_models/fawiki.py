from revscoring.languages import persian
from revscoring.scorers import LinearSVCModel

from ..feature_lists.fawiki import damaging

damaging_linear_svc = LinearSVCModel(damaging, language=persian)
