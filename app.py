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
    # ユーザーごとに識別する。ここでは表示名や uid などを利用できます。
    user_id = db.Column(db.String(64), nullable=False)
    # 問題ID
    question_id = db.Column(db.String(64), nullable=False)
    # 回答結果: Trueなら正解、Falseなら不正解
    is_correct = db.Column(db.Boolean, nullable=False)
    # 最新の回答日時。自動で設定されるデフォルト値も利用可能
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def serialize(self):
        return {
            "question_id": self.question_id,
            "is_correct": self.is_correct,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }

# （必要なら最初にテーブルを作成）
with app.app_context():
    db.create_all()

# 結果を保存するエンドポイント（POST）
@app.route('/api/results', methods=['POST'])
def save_results():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user_id = data.get('user_id')
    results = data.get('results')  # results は各問題の結果を含むリストを想定

    if not user_id or not results:
        return jsonify({'error': 'Invalid data'}), 400

    # 各問題の結果を処理します
    for result in results:
        question_id = result.get('question_id')
        is_correct = result.get('is_correct')
        timestamp_str = result.get('timestamp')
        # timestamp を文字列から datetime に変換
        new_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        
        # すでにこのユーザー、問題に対する記録があるか検索
        existing = QuizResult.query.filter_by(user_id=user_id, question_id=question_id).first()
        if existing:
            # 新しいタイムスタンプの方が後なら更新
            if new_timestamp > existing.timestamp:
                existing.is_correct = is_correct
                existing.timestamp = new_timestamp
        else:
            new_result = QuizResult(
                user_id=user_id,
                question_id=question_id,
                is_correct=is_correct,
                timestamp=new_timestamp
            )
            db.session.add(new_result)
    db.session.commit()
    return jsonify({'message': 'Results saved successfully.'}), 200

# 履歴取得用のエンドポイント（GET）
@app.route('/api/history/<user_id>', methods=['GET'])
def get_history(user_id):
    results = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.timestamp.desc()).all()
    # serialize() メソッドを使って各レコードを辞書に変換
    history = [r.serialize() for r in results]
    return jsonify(history), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)