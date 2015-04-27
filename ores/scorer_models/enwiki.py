from revscoring.languages import english
from revscoring.scorers import LinearSVCModel

from ..feature_lists.enwiki import damaging

damaging_linear_svc = LinearSVCModel(damaging, language=english)
