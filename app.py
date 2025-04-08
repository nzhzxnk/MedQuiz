from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://89t948.csb.app"])

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

@app.route('/api/results', methods=['POST'])
def save_results():
    data = request.get_json()  # フロントエンドから送られてきた JSON を取得
    # ここで、受け取ったデータの処理（例：データベースに保存）を実施
    # 今回はとりあえず受け取ったデータをコンソールに出力して確認する
    print("Received quiz results:", data)
    # 正常に処理できたなら 200 を返す
    return jsonify({'message': 'Results saved successfully.'}), 200

if __name__ == '__main__':
    app.run(debug=True)