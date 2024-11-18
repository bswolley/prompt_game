# src/models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class LeaderboardEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    prompt_length = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dataset-specific columns
    accuracy = db.Column(db.Float)
    word_accuracy = db.Column(db.Float)
    efficiency = db.Column(db.Float)
    similarity = db.Column(db.Float)
    length_penalty_avg = db.Column(db.Float)
    prompt_efficiency = db.Column(db.Float)
    base_accuracy = db.Column(db.Float)

    def to_dict(self):
        return {
            'name': self.name,
            'score': self.score,
            'prompt_length': self.prompt_length,
            'accuracy': self.accuracy,
            'word_accuracy': self.word_accuracy,
            'efficiency': self.efficiency,
            'similarity': self.similarity,
            'length_penalty_avg': self.length_penalty_avg,
            'prompt_efficiency': self.prompt_efficiency,
            'base_accuracy': self.base_accuracy,
            'timestamp': self.timestamp.isoformat()
        }