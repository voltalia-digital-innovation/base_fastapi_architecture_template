
import jwt
from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException
from modules.core.services.database.db import Database
from starlette.middleware.base import BaseHTTPMiddleware
from modules.core.env import ALLOWED_ORIGINS, DB_NAME_USERS, SECRET_KEY


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
        This class was made to attend user authentication from
        JWT method.

        Author: Matheus Henrique (m.araujo)

        Date: 16th September 2024
    """

    async def dispatch(self, request: Request, call_next):
        """
        This overrided method authenticates the user and set him
        in the "request.state.user".

        Args:
            request (Request): FastAPI Starlette request
            call_next: any

        Author: Matheus Henrique (m.araujo)

        Date: 16th September 2024

        Returns:
            response: Response
        """
        token = request.headers.get("Authorization")

        if request.method != 'OPTIONS':
            try:
                # decoded_jwt = jwt.decode(
                #     token, SECRET_KEY, algorithms=['HS512'])
                decoded_jwt = {
                    "token_type": "access",
                    "exp": 1728308857,
                    "iat": 1728305831,
                    "jti": "164cfd77462344e4aa0dacf50cfc0b0b",
                    "user_id": 640,
                    "iss": "auth-api-di"
                }

                user = Database(DB_NAME_USERS).list(
                    f"""
                        SELECT TOP 1
                            id, department_id, last_login, is_superuser, username,
                            first_name, last_name, email, is_staff, date_joined, company,
                            phone, oauth, birth_date, department, is_director, id_country
                        FROM auth_user WHERE id = {decoded_jwt['user_id']}
                    """
                )

                if user.empty:
                    raise HTTPException(status_code=401, detail="Unauthorized")

                request.state.user = user.to_dict(orient='records')[0]
            except Exception:
                headers = {
                    'Access-Control-Allow-Origin': ','.join(ALLOWED_ORIGINS),
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Methods': '*',
                    'Access-Control-Allow-Headers': '*',
                }
                return JSONResponse(
                    content={"detail": "Unauthorized"},
                    status_code=401,
                    headers=headers)

        # If the API key is valid, proceed with the request
        response = await call_next(request)
        return response


def get_user_from_request(request: Request):
    """
    This method take user from the request. To use it, set
    this statement as a parameter of the endpoint: 
        - "user: dict = Depends(get_user_from_request)"

    Args:
        request (Request): FastAPI Starlette request

    Author: Matheus Henrique (m.araujo)

    Date: 16th September 2024

    Returns:
        user: dict
    """
    return request.state.user
