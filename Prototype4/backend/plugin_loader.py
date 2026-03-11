from registry import register
from plugins.dummy_model import plugin as dummy_plugin
from plugins.mfcc_logreg_v1_01 import plugin as mfcc_logreg_plugin


def load_plugins() -> None:
    register(dummy_plugin)
    register(mfcc_logreg_plugin)