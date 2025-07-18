import os
import shutil
import smtplib
import asyncio
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory
from langgraph_agent.core import LangGraphAgent

app = Flask(__name__, static_folder='NFP', static_url_path='')

# Initialize the agent (reuse for all requests)
agent = None

async def get_agent():
    """Initializes the LangGraphAgent asynchronously if not already done."""
    global agent
    if agent is None:
        agent = await LangGraphAgent.ainit()
    return agent

@app.route('/')
def index():
    """Serves the main index.html file of the frontend wizard."""
    return send_from_directory('NFP', 'index.html')

@app.route('/api/generate', methods=['POST'])
async def generate_site():
    """
    Receives website data from the frontend, processes it with the LangGraph agent,
    and generates the website files.
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON data received.'}), 400

    try:
        agent_instance = await get_agent()
        result = await agent_instance.process_request(
            user_input=str(data),
            user_id='wizard_user',
            user_name='Wizard User',
            working_directory=os.path.abspath('Generator')
        )

        return jsonify({
            'status': 'success' if result.get('success') else 'error',
            'message': result.get('response'),
            'output_path': result.get('context', {}).get('working_directory', ''),
            'details': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/send-zip', methods=['POST'])
def send_zip():
    """
    Zips the generated website files and sends them to the user's email address
    as an attachment.
    """
    data = request.get_json()
    email = data.get('email')
    output_path = data.get('output_path')

    if not email or not output_path:
        return jsonify({'status': 'error', 'message': 'Missing email or output_path.'}), 400

    try:
        zip_base = os.path.abspath(output_path)
        zip_name = os.path.basename(zip_base.rstrip('/\\'))
        shutil.make_archive(zip_base, 'zip', zip_base)

        gmail_user = os.environ.get('GMAIL_USER')
        gmail_pass = os.environ.get('GMAIL_APP_PASSWORD')

        if not gmail_user or not gmail_pass:
            return jsonify({'status': 'error', 'message': 'Gmail credentials not set in environment.'}), 500

        msg = EmailMessage()
        msg['Subject'] = 'Your AI-Generated Restaurant Website'
        msg['From'] = gmail_user
        msg['To'] = email
        msg.set_content('Attached is your generated restaurant website as a zip file. Thank you for using our service!')

        with open(f'{zip_base}.zip', 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='zip', filename=f'{zip_name}.zip')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_pass)
            smtp.send_message(msg)

        os.remove(f'{zip_base}.zip')

        return jsonify({'status': 'success', 'message': f'Zip file sent to {email}.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Ensure the 'Generator' directory exists
    if not os.path.exists('Generator'):
        os.makedirs('Generator')
    app.run(host='0.0.0.0', port=5000, debug=True)