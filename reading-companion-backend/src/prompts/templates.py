"""Deprecated compatibility shim for prompt imports.

This module is no longer the prompt source of truth. New code should import:
- shared fragments from ``src.prompts.shared``
- capability prompts from ``src.prompts.capabilities``
- iterator_v1 prompts from ``src.iterator_reader.prompts``
- legacy unused prompt families from ``src.prompts.legacy``
"""

from src.iterator_reader.prompts import *  # noqa: F401,F403
from src.prompts.capabilities.book_analysis import *  # noqa: F401,F403
from src.prompts.legacy import *  # noqa: F401,F403
from src.prompts.shared import *  # noqa: F401,F403

