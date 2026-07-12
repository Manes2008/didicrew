# VideoCrew

A Python project for orchestrating AI agents to generate video concepts and images using CrewAI and OpenAI.

## Project Structure

- `app.py`: Main application code.
- `app1.py`: Test script for image generation using the GPT Image API.
- `config.py`: Configuration settings.
- `core/`: Core agents and tasks definition.
- `requirements.txt`: Python package dependencies.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Run the application:
```bash
streamlit run app.py
```
Or test the image generation script:
```bash
python app1.py
```
