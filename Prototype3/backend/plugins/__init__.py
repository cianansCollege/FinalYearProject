# Registers available model plugins during backend startup import.

from registry import register
from plugins.dummy_model import plugin as dummy_plugin

register(dummy_plugin)
