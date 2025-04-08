from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ここで CORS を有効にする

# SQLAlchemy の初期化とモデルの定義を先に行う
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'  # 例としてSQLiteを利用
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False)
    quiz_id = db.Column(db.String(64), nullable=False)
    question_id = db.Column(db.String(64), nullable=False)
    question = db.Column(db.Text)
    user_answer = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 必要なら、データベースのテーブルを作成
with app.app_context():
    db.create_all()

# エンドポイントの定義
@app.route('/api/history/<user_id>', methods=['GET'])
def get_history(user_id):
    results = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.timestamp.desc()).all()
    history = []
    for r in results:
        history.append({
            'quiz_id': r.quiz_id,
            'question_id': r.question_id,
            'question': r.question,
            'user_answer': r.user_answer,
            'correct_answer': r.correct_answer,
            'is_correct': r.is_correct,
            'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(history), 200

@app.route('/api/data', methods=['POST'])
def process_data():
    data = request.get_json()  # クライアントから送られてきた JSON を取得
    # ここで受け取ったデータに対する処理を実施（必要に応じてDBへの保存など）
    processed = data  # この例では単にそのまま返すだけ
    return jsonify({'received': processed}), 200

if __name__ == '__main__':
    app.run(debug=True)