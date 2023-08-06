from foundry import settings as foundry_settings

from skeleton.settings_live_base import *


FOUNDRY['layers'] = ('web', 'basic',)

foundry_settings.compute_settings(sys.modules[__name__])
