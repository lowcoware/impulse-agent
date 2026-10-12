"""Maruchi pool provider profile.

Maruchi is a key-pool gateway: its native surface is a drop-in replacement for
``generativelanguage.googleapis.com``, and a request carries a panel key while the
gateway rotates its own upstream Gemini keys. This profile points Hermes at that
gateway using the panel key(s) the operator holds.

Two things to know about this profile, both deliberate:

- **The native wire is not declared here.** ``agent/gemini_native_adapter.py::is_native_gemini_base_url()``
  picks the native Gemini client by inspecting the base URL, and it recognises
  ``generativelanguage.googleapis.com`` (or Vertex Express) only. A Maruchi host needs
  either that check widened or a hostname containing the Google host — see PLAN.md,
  «Наш провайдер».
- **Several credentials are the normal case.** A panel key is one entry in the credential
  pool (``hermes auth add``, or the setup wizard), each entry may carry its own base URL,
  and they accumulate. ``fallback_models`` below only seeds the catalog when the live
  fetch fails; the real list comes from the gateway's own ``/v1/models``.
"""

from providers import register_provider
from providers.base import ProviderProfile

maruchi = ProviderProfile(
    name="maruchi",
    aliases=("mrch",),
    display_name="Maruchi pool",
    description="Maruchi key-pool gateway — Gemini native API, keys pooled per account",
    env_vars=("MARUCHI_PANEL_KEY", "MARUCHI_BASE_URL"),
    base_url="https://api.maruchillm.ru",
    auth_type="api_key",
    default_aux_model="gemini-flash-latest",
    fallback_models=(
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3-flash-preview",
        "gemini-3.1-flash-lite",
        "gemma-4-31b-it",
        "gemma-4-26b-a4b-it",
    ),
)

register_provider(maruchi)
