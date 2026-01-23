import bcrypt

BCRYPT_ROUNDS = 12
#checks if a password string is a bcrypt hash by examing its prefix
def is_hashed(pw: str) -> bool:
    """
    Detect if a stored password looks like a bcrypt hash.
    Bcrypt hashes start with $2a$, $2b$, or $2y$.
    """
    if not isinstance(pw, str):
        return False
    return pw.startswith("$2a$") or pw.startswith("$2b$") or pw.startswith("$2y$")
#hashes a plaintext password using bcrypt with a specifies number of rounds
def hash_password(password: str) -> str:
    """
    Hash a plaintext password with bcrypt.
    """
    if password is None:
        raise ValueError("Password is None")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")
#verifies a password against a stored value, supporting both bcrypt hashes and plaintext 
def check_password(password: str, pw: str) -> bool: 
    """
    Verify a login attempt against stored value.
    - If pw is bcrypt -> bcrypt.verify
    - If pw is plaintext (pre-migration) -> fallback equality (so login still works
      before migration has been run).
    """
    if not isinstance(pw, str):
        return False
    if is_hashed(pw):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), pw.encode("utf-8"))
        except Exception:
            return False
    return password == pw
# determines if a strong password needs to be upgraded to a bcrypt hash
def need_hash(pw: str) -> bool:
    """
    Whether the stored password should be upgraded to bcrypt.
    """
    return not is_hashed(pw)