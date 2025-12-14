from fastapi import Depends, HTTPException
from app.utils.verify import verify_token

def require_roles(*allowed_roles):
    def _checker(user=Depends(verify_token)):
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return _checker

# helper for multiple allowed roles
def require_any(*allowed_roles):
    return require_roles(*allowed_roles)
