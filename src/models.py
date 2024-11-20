from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class LeaderboardEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    prompt_length = db.Column(db.Integer)
    prompt_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dataset-specific columns
    accuracy = db.Column(db.Float)
    word_accuracy = db.Column(db.Float)
    efficiency = db.Column(db.Float)
    similarity = db.Column(db.Float)
    length_penalty_avg = db.Column(db.Float)
    prompt_efficiency = db.Column(db.Float)
    base_accuracy = db.Column(db.Float)
    
    # New columns
    system_prompt = db.Column(db.Text)  # Store the system prompt
    is_production = db.Column(db.Boolean, default=False)  # Flag for production entries
    raw_predictions = db.Column(db.JSON)  # Store raw model predictions
    inputs_used = db.Column(db.JSON)  # Store the inputs used
    
    def to_dict(self, include_private=False):
        """Convert entry to dictionary, optionally including private data"""
        data = {
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
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
        
        if include_private:
            data.update({
                'system_prompt': self.system_prompt,
                'raw_predictions': self.raw_predictions,
                'inputs_used': self.inputs_used
            })
            
        return data