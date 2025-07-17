import hmac
import hashlib
import importlib
import sys

# Save the original HMAC
original_hmac = hmac.HMAC

# Create a patched HMAC class
def patched_hmac(key, msg=None, digestmod=None):
    """
    A patched version of hmac.HMAC that handles missing digestmod parameter
    by defaulting to sha1 in Python 3.13
    """
    if digestmod is None:
        digestmod = hashlib.sha1
    return original_hmac(key=key, msg=msg, digestmod=digestmod)

# Replace the original HMAC with our patched version
hmac.HMAC = patched_hmac

# Patch the compare_digest function if needed
original_compare_digest = hmac.compare_digest

# Apply the patch
print("Applied Werkzeug security patch for Python 3.13 compatibility") 