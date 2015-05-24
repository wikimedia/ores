from revscoring.languages import french
from revscoring.scorers import LinearSVCModel

from ..feature_lists.frwiki import damaging

damaging_linear_svc = LinearSVCModel(damaging, language=french)
