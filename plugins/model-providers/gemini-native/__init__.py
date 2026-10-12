"""Native Gemini provider profile for a custom endpoint.

Talks Gemini's native REST wire and is meant for an operator-supplied endpoint: the default
is Google's own API, and any drop-in replacement that speaks the same wire works by pointing
``GEMINI_NATIVE_BASE_URL`` (or a credential's own base URL) at it. Bring your own key — or
several; the pool accumulates them.

Two things to know about this profile, both deliberate:

- **The native wire is chosen by name.** ``agent/auxiliary_client.py::_GEMINI_NATIVE_PROVIDER_NAMES``
  lists provider names that always take the native client, and ``gemini-native`` is one of them.
  That is deliberate: a replacement gateway's hostname does not look like Google's, and
  ``agent/gemini_native_adapter.py::is_native_gemini_base_url()`` only recognises
  ``generativelanguage.googleapis.com`` and Vertex Express by URL shape.
- **Several credentials are the normal case.** A key is one entry in the credential pool
  (``hermes auth add``, or the setup wizard), each entry may carry its own base URL, and they
  accumulate. ``fallback_models`` below only seeds the catalog when the live fetch fails; the
  real list comes from the endpoint's own model listing.
"""

from providers import register_provider
from providers.base import ProviderProfile

gemini_native = ProviderProfile(
    name="gemini-native",
    aliases=("gnative",),
    display_name="Gemini native API (custom endpoint)",
    description="Native Gemini API — your own keys against Google or a drop-in endpoint",
    env_vars=("GEMINI_NATIVE_API_KEY", "GEMINI_NATIVE_BASE_URL"),
    base_url="https://generativelanguage.googleapis.com",
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

register_provider(gemini_native)
