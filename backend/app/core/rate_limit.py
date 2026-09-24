from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory store (per process) - fine for a single backend instance.
# Switch to storage_uri="redis://..." once Redis is provisioned, so
# limits are shared across multiple instances.
limiter = Limiter(key_func=get_remote_address)
