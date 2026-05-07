"""
wiki_ingestor — MarkItDown-powered file-to-Markdown daemon for wiki-linux.
"""

from .config import IngestorConfig, write_default_config
from .converter import ConversionLedger, WikiConverter, SUPPORTED_EXTENSIONS
from .watcher import IngestorWatcher

__version__ = "1.0.0"
__all__ = [
    "IngestorConfig",
    "write_default_config",
    "ConversionLedger",
    "WikiConverter",
    "SUPPORTED_EXTENSIONS",
    "IngestorWatcher",
]
