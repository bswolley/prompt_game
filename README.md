# Word Sorting Prompt Tester

A Flask-based web application for testing and evaluating word sorting prompts using the Groq API. This application allows users to test system prompts for word sorting tasks with both practice (8-word) and full test (10-word) modes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A Groq API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/bswolley/prompt_game.git
cd prompt_game
```

2. Create and activate a virtual environment:

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Groq API key:
```bash
GROQ_API_KEY=your_api_key_here
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:8080
```

## Features

- Practice Mode: Test prompts with 8-word lists
- Full Test Mode: Evaluate prompts with 10-word lists
- Detailed metrics including:
  - Combined Score
  - Overall Accuracy
  - Word Accuracy
  - Word Order Distance
- Interactive web interface
- Detailed example results with input/output comparisons

## API Endpoints

### Practice Mode
- **POST** `/api/pretest`
- Tests your prompt with 8-word lists
- Returns detailed metrics and examples

### Full Test Mode
- **POST** `/api/test_prompt`
- Tests your prompt with 10-word lists
- Configurable number of examples (5-100)

## Development

To run the application in development mode:

```bash
export FLASK_ENV=development  # On Unix/macOS
set FLASK_ENV=development    # On Windows
python app.py
```

## Testing

To run the API tests:

```bash
python test_api.py
```

## Project Structure

```
.
├── app.py              # Main application file
├── metrics.py          # Metrics calculation functions
├── dataset_utils.py    # Dataset handling utilities
├── requirements.txt    # Project dependencies
├── templates/          # HTML templates
│   └── api_test.html   # Main interface template
└── .env               # Environment variables (create this)
```

## Environment Variables

- `GROQ_API_KEY`: Your Groq API key
- `PORT`: Application port (default: 10000)

## License

[Add your license information here]
```
