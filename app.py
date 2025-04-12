from flask import Flask
from dotenv import load_dotenv
import os
import Backend.routes.User as user
import Backend.routes.Admin as admin

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY')

app.register_blueprint(user.user)
app.register_blueprint(admin.admin) 

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', 'localhost')
    )
