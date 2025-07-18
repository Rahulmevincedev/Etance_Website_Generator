import os
import shutil
import smtplib
import asyncio
import json
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory, send_file
from dotenv import load_dotenv
from langgraph_agent.core import LangGraphAgent

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='NFP', static_url_path='')

# --- Agent and Asyncio Handling ---
agent = None
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

def initialize_agent():
    """Initializes the LangGraphAgent with configuration from environment variables."""
    global agent
    if agent is None:
        print("Initializing LangGraph Agent...")
        # Get agent configuration from environment variables, with defaults
        model = os.getenv("AGENT_MODEL", "gpt-3.5-turbo")
        temperature = float(os.getenv("AGENT_TEMPERATURE", 0.7))
        max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", 10))

        print(f"Agent Config: Model={model}, Temp={temperature}, Max Iterations={max_iterations}")
        
        agent = loop.run_until_complete(LangGraphAgent.ainit(
            model=model,
            temperature=temperature,
            max_iterations=max_iterations
        ))
        print("Agent Initialized.")

@app.route('/')
def index():
    """Serves the main index.html file."""
    return send_from_directory('NFP', 'index.html')

@app.route('/api/generate', methods=['POST'])
def generate_site():
    """Receives data from the frontend and uses the agent to generate the website."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON data received.'}), 400

    try:
        user_input_json = json.dumps(data, indent=2)
        print("Received data for agent:", user_input_json)
        
        result = loop.run_until_complete(
            agent.process_request(
                user_input=user_input_json,
                user_id='wizard_user',
                user_name='Wizard User',
                working_directory=os.path.abspath('Generator')
            )
        )

        if not result.get('success'):
            print("Agent failed:", result)
            return jsonify({
                'status': 'error',
                'message': result.get('response', 'Agent failed to process the request.'),
                'details': result
            }), 500

        generated_path = result.get('response')
        print(f"Agent returned path: {generated_path}")
        
        if not generated_path or not os.path.isdir(generated_path):
             return jsonify({
                'status': 'error',
                'message': f"Agent did not return a valid directory path. Agent response: {generated_path}",
             }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Website generated successfully!',
            'output_path': generated_path
        })

    except Exception as e:
        app.logger.error(f"Error in /api/generate: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_zip():
    """Zips the generated website and sends it for download."""
    data = request.get_json()
    output_path = data.get('output_path')

    if not output_path or not os.path.isdir(output_path):
        return jsonify({'status': 'error', 'message': 'Invalid or missing output_path.'}), 400

    try:
        site_name = os.path.basename(output_path.rstrip('/\\'))
        zip_path_base = os.path.join('Generator', site_name)
        shutil.make_archive(zip_path_base, 'zip', output_path)
        zip_path = f"{zip_path_base}.zip"
        return send_file(zip_path, as_attachment=True, download_name=f'{site_name}.zip')
    except Exception as e:
        app.logger.error(f"Error in /api/download: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/send-zip', methods=['POST'])
def send_zip():
    """Zips the generated files and sends them via email."""
    data = request.get_json()
    email = data.get('email')
    output_path = data.get('output_path')

    if not email or not output_path or not os.path.isdir(output_path):
        return jsonify({'status': 'error', 'message': 'Missing or invalid email/output_path.'}), 400

    try:
        site_name = os.path.basename(output_path.rstrip('/\\'))
        zip_path_base = os.path.join('Generator', site_name)
        shutil.make_archive(zip_path_base, 'zip', output_path)
        zip_path = f"{zip_path_base}.zip"

        gmail_user = os.environ.get('GMAIL_USER')
        gmail_pass = os.environ.get('GMAIL_APP_PASSWORD')

        if not gmail_user or not gmail_pass:
            return jsonify({'status': 'error', 'message': 'Email server credentials are not configured in .env file.'}), 500

        msg = EmailMessage()
        msg['Subject'] = f'Your AI-Generated Website: {site_name}'
        msg['From'] = gmail_user
        msg['To'] = email
        msg.set_content(f'Attached is your generated website "{site_name}". Thank you for using our service!')

        with open(zip_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='zip', filename=f'{site_name}.zip')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_pass)
            smtp.send_message(msg)

        os.remove(zip_path)
        return jsonify({'status': 'success', 'message': f'Website zip file sent to {email}.'})
    except Exception as e:
        app.logger.error(f"Error in /api/send-zip: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500
        
# --- Serve Generated Site Statically ---
@app.route('/Generator/<path:path>')
def serve_generated_site(path):
    """Serves files from the Generator directory for previews."""
    return send_from_directory('Generator', path)

if __name__ == '__main__':
    if not os.path.exists('Generator'):
        os.makedirs('Generator')
    initialize_agent()
    app.run(host='0.0.0.0', port=5000, debug=True)