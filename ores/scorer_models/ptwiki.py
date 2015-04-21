from revscoring.languages import portuguese
from revscoring.scorers import LinearSVCModel

from ..feature_lists.ptwiki import damaging

damaging_linear_svc = LinearSVCModel(damaging, language=portuguese)
