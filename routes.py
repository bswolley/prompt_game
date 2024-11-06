# prompt_testing/routes.py
from flask import Blueprint, request, jsonify, render_template
from .metrics import calculate_metrics  # import your metrics functions

api = Blueprint('api', __name__)

@api.route('/')
def home():
    return render_template('api_test.html')

@api.route('/api/pretest', methods=['POST'])
def pretest():
    # Your pretest logic
    pass

@api.route('/api/test_prompt', methods=['POST'])
def test_prompt():
    # Your test_prompt logic
    pass