# these imports register the functions with the
# registered_tokenizers function registry.
from .termite import termite
from .pyldavis import lda_vis

from ._registry import registered_visualizers, visualize
