from app import create_app
import os
from flask import jsonify

app = create_app()

@app.errorhandler(ValueError)
def handle_value_error(e):
    if e.args and isinstance(e.args[0], dict):
        return jsonify(e.args[0]), 409

    return jsonify({
        "status": "error",
        "message": str(e)
    }), 400


if __name__ == "__main__":
    
    #print(app.config)
    app.run(debug=True,host="0.0.0.0", port=int(os.getenv("PORT")))
