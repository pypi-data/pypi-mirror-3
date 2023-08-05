# TODO: Write Monte Carlo tests

# Use Django translations if available
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    _ = lambda x: x
