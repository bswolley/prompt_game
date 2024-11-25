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
    
    # Translation-specific columns
    semantic_similarity = db.Column(db.Float)
    language_quality = db.Column(db.Float)
    target_language = db.Column(db.String(10))
    
    # General columns
    system_prompt = db.Column(db.Text)
    is_production = db.Column(db.Boolean, default=False)
    raw_predictions = db.Column(db.JSON)
    inputs_used = db.Column(db.JSON)
    
    def to_dict(self, include_private=False):
        """Convert entry to dictionary, optionally including private data"""
        base_data = {
            'name': self.name,
            'score': self.score,
            'prompt_length': self.prompt_length,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
        
        # Add dataset-specific metrics
        if self.dataset_type == 'word_sorting':
            base_data.update({
                'accuracy': self.accuracy,
                'word_accuracy': self.word_accuracy,
                'efficiency': self.efficiency
            })
        elif self.dataset_type == 'text_summarization':
            base_data.update({
                'similarity': self.similarity,
                'length_penalty_avg': self.length_penalty_avg,
                'prompt_efficiency': self.prompt_efficiency
            })
        elif self.dataset_type == 'causal_judgement':
            base_data.update({
                'accuracy': self.accuracy,
                'base_accuracy': self.base_accuracy,
                'efficiency': self.efficiency
            })
        elif self.dataset_type == 'translation_task':
            base_data.update({
                'semantic_similarity': self.semantic_similarity,
                'language_quality': self.language_quality,
                'efficiency': self.efficiency,
                'target_language': self.target_language
            })
        
        if include_private:
            base_data.update({
                'system_prompt': self.system_prompt,
                'raw_predictions': self.raw_predictions,
                'inputs_used': self.inputs_used
            })
            
        return base_data