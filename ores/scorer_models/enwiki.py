from revscoring.languages import english
from revscoring.scorers import LinearSVCModel, RFModel

from ..feature_lists.enwiki import damaging, wp10

damaging_linear_svc = LinearSVCModel(damaging, language=english)

wp10_rf = RFModel(wp10, language=english)
