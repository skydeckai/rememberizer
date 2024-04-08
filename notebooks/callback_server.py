from flask import Flask, request

app = Flask(__name__)

@app.route('/callback')
def callback():
    global auth_code
    auth_code = request.args.get('code')
    if auth_code:
        # Respond to the browser that the code was received
        return f"Authorization code received: <code>{auth_code}</code>. Copy this code to your notebook."
    else:
        return "Authorization code not found in the request"

def run_app():
    app.run(port=5000)
run_app()