from flask import Flask, render_template, request, redirect, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script', methods=['POST'])
def run_script():
    script_name = request.form['script']
    command = request.form.get('command', '')  # command 인자를 받아옵니다.
    servername_start = request.form.get('servername_start', '')  # servername_start 인자를 받아옵니다.
    output = ""

    if script_name == 'detect_notrun':
        output = subprocess.check_output(['python', 'detect_notrun.py'], universal_newlines=True)
    elif script_name == 'instance_all_reboot':
        output = subprocess.check_output(['python', 'instance_all_reboot.py'], universal_newlines=True)    
    elif script_name == 'status_multi':
        # command 인자를 환경 변수로 설정합니다.
        os.environ['COMMAND_INPUT1'] = servername_start
        os.environ['COMMAND_INPUT2'] = command
        output = subprocess.check_output(['python', 'status_multi.py'], universal_newlines=True)
    elif script_name == 'command_auto_multi':
        # command 인자를 환경 변수로 설정합니다.
        os.environ['COMMAND_INPUT1'] = servername_start
        os.environ['COMMAND_INPUT2'] = command
        output = subprocess.check_output(['python', 'command_auto_multi.py'], universal_newlines=True)   
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
