from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods = ["GET", "POST"])
def messages():
    if request.method == "GET":
        messages_list = []
        messages = Message.query.order_by(Message.created_at.desc()).all()
        for message in messages:
            message_dict = {
                "id": message.id,
                "body": message.body,
                "username": message.username,
                "created_at": message.created_at,
                "updated_at": message.updated_at,
            }
            messages_list.append(message_dict)

        response = make_response(
            jsonify(messages_list),
            200,
            {"Content_Type": "application/json"}
        )
        return response
    
    elif request.method == "POST":
        new = request.get_json()
        message = Message(
            body=new['body'],
            username=new['username']
        )

        db.session.add(message)
        db.session.commit()
        
        response = make_response(
            jsonify(message.to_dict()),
            201,
        )

        return response


@app.route('/messages/<int:id>', methods = ["PATCH", "DELETE"])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if request.method == "PATCH":
        messages = request.get_json()
        for attr in messages:
            setattr(message, attr, messages[attr])

        db.session.add(message)
        db.session.commit()

        response = make_response(
            jsonify(message.to_dict()),
            200
        )

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response = make_response(
            jsonify({'deleted': True}),
            200,
        )

    return response

if __name__ == '__main__':
    app.run(port=5555)
