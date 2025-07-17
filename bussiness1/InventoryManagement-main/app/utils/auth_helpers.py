import hashlib
import hmac
import re
import sys
from werkzeug.security import check_password_hash, generate_password_hash

# Create a compatible version of check_password_hash
def safe_check_password_hash(pwhash, password):
    """
    A compatible version of check_password_hash that works with all Werkzeug versions.
    This is a drop-in replacement for werkzeug.security.check_password_hash.
    
    Args:
        pwhash: The hash string from the database
        password: The plaintext password to check
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        # First try the standard Werkzeug function
        return check_password_hash(pwhash, password)
    except (TypeError, ValueError) as e:
        # If we get a TypeError about digestmod or ValueError about hash type
        if 'digestmod' in str(e) or 'unsupported hash type' in str(e):
            return custom_check_password_hash(pwhash, password)
        # Re-raise if it's some other error
        raise

# Custom implementation of password checking for compatibility
def custom_check_password_hash(pwhash, password):
    """
    Custom implementation of check_password_hash for older Werkzeug versions.
    Handles the PBKDF2 and HMAC methods that Werkzeug supports.
    """
    if pwhash.count('$') < 2:
        return False
    
    method, salt, hashval = pwhash.split('$', 2)
    
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    if isinstance(salt, str):
        salt = salt.encode('utf-8')
    
    if method == 'plain':
        return password == hashval
    
    elif method.startswith('pbkdf2:'):
        # Handle PBKDF2 hashing
        args = method[7:].split(':')
        if len(args) == 1:
            hash_name = args[0]
            iterations = 150000  # Default in Werkzeug 2.0+
        else:
            hash_name = args[0]
            iterations = int(args[1])
        
        try:
            result = hashlib.pbkdf2_hmac(hash_name, password, salt, iterations).hex()
            return hmac.compare_digest(result, hashval)
        except ValueError:
            # If hash_name is unsupported, try with sha256 as fallback
            print(f"Unsupported hash type: {hash_name}, falling back to sha256")
            result = hashlib.pbkdf2_hmac('sha256', password, salt, iterations).hex()
            return hmac.compare_digest(result, hashval)
    
    else:
        # Handle standard hash methods (md5, sha1, etc.)
        if salt:
            try:
                # Try with explicit digestmod parameter for Python 3.13+
                # Convert method name to an actual hash algorithm
                try:
                    hash_algo = getattr(hashlib, method, None)
                    if hash_algo is None:
                        # If method not found as attribute, create new hashlib instance
                        digestmod = hashlib.new(method)
                    else:
                        # Use the hash algorithm constructor
                        digestmod = method
                    
                    result = hmac.new(salt, password, digestmod=digestmod).hexdigest()
                except (ValueError, AttributeError):
                    # If hash method is unsupported, try with sha1 as fallback
                    print(f"Unsupported hash type: {method}, falling back to sha1")
                    result = hmac.new(salt, password, digestmod='sha1').hexdigest()
            except (TypeError, ValueError):
                # Fallback for other cases
                try:
                    hash_obj = hashlib.new(method)
                    result = hmac.new(salt, password, hash_obj).hexdigest()
                except ValueError:
                    # If method is unsupported, try with sha1
                    print(f"Unsupported hash type: {method}, falling back to sha1")
                    hash_obj = hashlib.new('sha1')
                    result = hmac.new(salt, password, hash_obj).hexdigest()
        else:
            try:
                hash_obj = hashlib.new(method, password)
                result = hash_obj.hexdigest()
            except ValueError:
                # If method is unsupported, try with sha1
                print(f"Unsupported hash type: {method}, falling back to sha1")
                hash_obj = hashlib.new('sha1', password)
                result = hash_obj.hexdigest()
        
        return hmac.compare_digest(result, hashval)

# Create a compatible version of generate_password_hash that always
# uses a method compatible with all Werkzeug and Python versions
def safe_generate_password_hash(password, method='pbkdf2:sha256', salt_length=16):
    """
    A compatible version of generate_password_hash that works with all Werkzeug versions.
    
    Args:
        password: The plaintext password to hash
        method: The hashing method to use
        salt_length: Length of the salt
        
    Returns:
        Hashed password string
    """
    # Always use a reliable method that's supported in all versions
    reliable_method = 'pbkdf2:sha256'
    
    try:
        # Try with the requested method first
        return generate_password_hash(password, method, salt_length)
    except (TypeError, ValueError):
        # If that fails, use sha256 which is widely supported
        try:
            return generate_password_hash(password, reliable_method, salt_length)
        except (TypeError, ValueError):
            # Last resort - implement our own password hashing
            from os import urandom
            import binascii
            
            salt = urandom(salt_length)
            iterations = 150000  # Default in newer Werkzeug
            
            hash_val = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
            salt_hex = binascii.hexlify(salt).decode('ascii')
            hash_hex = binascii.hexlify(hash_val).decode('ascii')
            
            return f"pbkdf2:sha256:{iterations}${salt_hex}${hash_hex}" 