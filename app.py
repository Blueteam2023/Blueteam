from flask import Flask, request, jsonify, render_template, redirect, url_for
import re
import subprocess
import requests
import threading
import os



app = Flask(__name__)


def run_script(branch, pusher, url, number):
    subprocess.run(['./scripts/building.sh', branch, pusher, url, number])


@app.route("/trigger", methods=['POST'])
def trigger():
    if request.method == 'POST':
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.get_json()
        if event_type == 'pull_request':
            action = payload['action']
            branch = payload['pull_request']['head']['ref']
            pusher = payload['pull_request']['user']['login']
            number = str(payload['number'])
            url = payload['pull_request']['url']
            print(f"New event: from {branch}, user: {pusher}, action: {action}, Request {number}")
            if action == 'closed' and payload['pull_request']['merged_at'] is not None: #if pull request approved
                if branch == "billing" or branch=="weight":
                    print("Starting testing process")
                    t = threading.Thread(target=run_script, args=(branch, pusher, url, number))
                    t.start()
                    return jsonify({"action": action, "pusher": pusher, "repository.branches_url": branch}), 200
                elif "revert" in branch:
                    return "Reverted branch, doing nothing", 200
                else:
                    return "Invalid branch", 400
            else:
                print(f"Unkown action: {action}") #optional send mail notification
                return "Invalid request" ,400
        else:
            return 'Unknown event', 400  

    else:
        return 'Method not allowed', 405
         



@app.route("/health")
def health_check():
    return "OK", 200


@app.route('/monitor')
def monitor():
    with open('./data/stable_versions.txt', 'r') as f:
        lines = f.readlines()
        current_version = lines[-1].strip()
        previous_version = lines[-2].strip()

    
    services = {
        'production': {
            'billing': 'http://billing-app:80/health',
            'weight': 'http://weight-app:8000/health'
        },
        'testing': {
            'billing': 'http://test-billing-app:80/health',
            'weight': 'http://test-weight-app:8000/health'
        }
    }

    statuses = {}

    for env, env_services in services.items():
        statuses[env] = {}
        for service, url in env_services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    statuses[env][service] = "OK"
                else:
                    statuses[env][service] = f"Error: {response.status_code}"
            except requests.exceptions.RequestException:
                statuses[env][service] = "Down - Service Unreachable"

    return render_template('monitor.html', statuses=statuses, last_version=current_version, prev_version=previous_version)


@app.route('/rollback', methods=['POST'])
def rollback():
    tag = request.form['tag']
    subprocess.run(["./scripts/rollback.sh", tag])
    return redirect(url_for('monitor'))

if __name__ == "__main__":
    app.run()


