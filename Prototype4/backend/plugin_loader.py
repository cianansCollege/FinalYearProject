from registry import register
from plugins.dummy_model import plugin as dummy_plugin
from plugins.mfcc_logreg_v1_01 import plugin as mfcc_logreg_plugin
from plugins.wav2vec_ulster_vs_rest_rf import Wav2VecUlsterVsRestRF
from plugins.wav2vec_leinster_vs_rest_logreg import Wav2VecLeinsterVsRestLogReg
from plugins.wav2vec_ulster_leinster_rest_logreg import Wav2VecUlsterLeinsterRestLogReg
from plugins.wav2vec_province_4way_logreg import Wav2VecProvince4WayLogReg

def load_plugins() -> None:
    register(dummy_plugin)
    register(mfcc_logreg_plugin)
    register(Wav2VecUlsterVsRestRF())
    register(Wav2VecLeinsterVsRestLogReg())
    register(Wav2VecUlsterLeinsterRestLogReg())
    register(Wav2VecProvince4WayLogReg())
