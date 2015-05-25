from revscoring.languages import turkish
from revscoring.scorers import LinearSVCModel

from ..feature_lists.trwiki import damaging

damaging_linear_svc = LinearSVCModel(damaging, language=turkish)
