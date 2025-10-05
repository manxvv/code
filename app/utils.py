# from functools import wraps
# from datetime import datetime
# import jwt
# from flask import request, jsonify, current_app, g, make_response

# from datetime import timedelta
# # def token_required(f):
# #     @wraps(f)
# #     def decorated(*args, **kwargs):
# #         token = None

# #         if "Authorization" in request.headers:
# #             auth_header = request.headers["Authorization"]
# #             if auth_header.startswith("Bearer "):
# #                 token = auth_header.split(" ")[1]

# #         if not token:
# #             return jsonify({"error": "Token is missing"}), 401

# #         try:
# #             decoded = jwt.decode(
# #                 token,
# #                 current_app.config["JWT_SECRET"],
# #                 algorithms=[current_app.config["JWT_ALGORITHM"]]
# #             )
# #             request.user = decoded   
# #         except jwt.ExpiredSignatureError:
# #             return jsonify({"error": "Token expired"}), 401
# #         except jwt.InvalidTokenError:
# #             return jsonify({"error": "Invalid token"}), 401

# #         return f(*args, **kwargs)

# #     return decorated




# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get("Authorization", "")
#         token = None
#         if auth_header.startswith("Bearer "):
#             token = auth_header.split(" ")[1]

#         if not token:
#             return jsonify({"message": "Token is missing"}), 401

#         try:
#             decoded = jwt.decode(
#                 token,
#                 current_app.config["JWT_SECRET"],
#                 algorithms=[current_app.config["JWT_ALGORITHM"]]
#             )
#             g.user = decoded  # store user info in g


#             print(decoded,"decodeddecodeddecodeddecodeddecoded")
#             token = jwt.encode(
#                 {
#                     "sub": str(decoded["sub"]),
#                     "role": str(decoded["role"]),  
#                     "exp": datetime.utcnow() + timedelta(hours=1)
#                 },
#                 current_app.config["JWT_SECRET"],
#                 algorithm=current_app.config["JWT_ALGORITHM"]
#             )
            
            
#             request.user = decoded 

#         except jwt.ExpiredSignatureError:
#             return jsonify({"message": "Token expired"}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({"message": "Invalid token"}), 401

#         # Call the actual view function
#         response = f(*args, **kwargs)

#         # Attach the new token in response header
#         # If the view returns a dict/tuple, turn it into a Response first
#         if not hasattr(response, 'headers'):
#             response = make_response(response)

#         response.headers["Authorization"] = f"Bearer {token}"
#         return response

#     return decorated

# ==========================sfdfdsfd==================================================
from functools import wraps
from datetime import datetime, timedelta
import jwt
from flask import request, jsonify, current_app, g, make_response

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        incoming_token = None
        if auth_header.startswith("Bearer "):
            incoming_token = auth_header.split(" ")[1]

        if not incoming_token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            decoded = jwt.decode(
                incoming_token,
                current_app.config["JWT_SECRET"],
                algorithms=[current_app.config["JWT_ALGORITHM"]]
            )
            g.user = decoded  # store user info here

            # Issue a fresh token with a new expiry
            new_token = jwt.encode(
                {
                    "sub": str(decoded.get("sub")),
                    "role": str(decoded.get("role")),
                    "exp": datetime.utcnow() + timedelta(hours=6)
                },
                current_app.config["JWT_SECRET"],
                algorithm=current_app.config["JWT_ALGORITHM"]
            )


            request.user = decoded 
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        # Call the view function
        response = f(*args, **kwargs)

        # Attach the new token to response header
        if not hasattr(response, "headers"):
            response = make_response(response)

        response.headers["Authorization"] = f"Bearer {new_token}"
        return response

    return decorated


# from functools import wraps
# from datetime import datetime, timedelta
# import jwt
# from flask import request, jsonify, current_app, make_response

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get("Authorization", "")
#         incoming_token = None
#         if auth_header.startswith("Bearer "):
#             incoming_token = auth_header.split(" ")[1]

#         if not incoming_token:
#             return jsonify({"message": "Token is missing"}), 401

#         try:
#             decoded = jwt.decode(
#                 incoming_token,
#                 current_app.config["JWT_SECRET"],
#                 algorithms=[current_app.config["JWT_ALGORITHM"]]
#             )

#             # Create a fresh token
#             new_token = jwt.encode(
#                 {
#                     "sub": str(decoded.get("sub")),
#                     "role": str(decoded.get("role")),
#                     "exp": datetime.utcnow() + timedelta(hours=6)
#                 },
#                 current_app.config["JWT_SECRET"],
#                 algorithm=current_app.config["JWT_ALGORITHM"]
#             )

#         except jwt.ExpiredSignatureError:
#             return jsonify({"message": "Token expired"}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({"message": "Invalid token"}), 401

#         # Pass the decoded token to the route
#         response = f(decoded_token=decoded, *args, **kwargs)

#         # Attach the new token to response header
#         if not hasattr(response, "headers"):
#             response = make_response(response)
#         response.headers["Authorization"] = f"Bearer {new_token}"
#         return response

#     return decorated
