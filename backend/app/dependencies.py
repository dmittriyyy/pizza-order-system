from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database import get_db
from .models.users import User, UserRole
from .schemas.token import TokenData
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


async def get_current_user(token=Depends(oauth2_scheme), db=Depends(get_db)):
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


async def get_current_user_optional(token=Depends(oauth2_scheme), db=Depends(get_db)):
    return await get_current_user(token, db)


async def get_current_admin_user(token=Depends(oauth2_scheme), db=Depends(get_db)):
    user = await get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован"
        )
    
    user_role_str = user.role.value if hasattr(user.role, 'value') else user.role
    if user_role_str != UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль администратора"
        )
    return user


def require_role(*allowed_roles):
    async def role_checker(current_user=Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не авторизован"
            )
        
        user_role_str = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
        user_role = UserRole(user_role_str)
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется одна из ролей: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


require_admin = require_role(UserRole.admin)
require_cook = require_role(UserRole.cook, UserRole.admin)
require_courier = require_role(UserRole.courier, UserRole.admin)
require_user = require_role(UserRole.client, UserRole.cook, UserRole.courier, UserRole.admin)
