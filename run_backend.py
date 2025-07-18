import os
from flask import Flask, request, jsonify, send_file
import asyncio
from langgraph_agent.core import LangGraphAgent
import shutil
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# Initialize the agent (reuse for all requests)
agent = None

async def get_agent():
    global agent
    if agent is None:
        agent = await LangGraphAgent.ainit()
    return agent

@app.route('/api/generate', methods=['POST'])
def generate_site():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON data received.'}), 400
    try:
        # Run the agent asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agent_instance = loop.run_until_complete(get_agent())
        result = loop.run_until_complete(
            agent_instance.process_request(
                user_input=str(data),
                user_id='wizard_user',
                user_name='Wizard User',
                working_directory=os.path.abspath('Generator')
            )
        )
        loop.close()
        # Return the agent's response
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
    data = request.get_json()
    email = data.get('email')
    output_path = data.get('output_path')
    if not email or not output_path:
        return jsonify({'status': 'error', 'message': 'Missing email or output_path.'}), 400
    try:
        # Zip the output_path folder
        zip_base = os.path.abspath(output_path)
        zip_name = os.path.basename(zip_base.rstrip('/\\'))
        zip_path = os.path.join('Generator', f'{zip_name}.zip')
        shutil.make_archive(zip_base, 'zip', zip_base)
        # Send email with zip attachment
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
        # Optionally, remove the zip after sending
        os.remove(f'{zip_base}.zip')
        return jsonify({'status': 'success', 'message': f'Zip file sent to {email}.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 