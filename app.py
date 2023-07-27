# app.py
from flask import Flask, render_template, request
import time
from rotalysis import Core

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()

    config_file = data['config_file']
    input_folder = data['input_folder']
    output_folder = data['output_folder']
    tasklist_file = data['tasklist_file']

    # You may need to modify this delay depending on your use case.
    time.sleep(2)

    # Process the files using the Core class
    core = Core(config_file, tasklist_file, input_folder, output_folder)
    core.process_task()

    return render_template('result.html')

if __name__ == "__main__":
    # app.run(host='10.29.3.28', port=80)
    app.run()
