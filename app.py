from flask import Flask, request, jsonify
import re
import subprocess


app = Flask(__name__)


@app.route("/trigger", methods=['POST'])
def trigger():
    if request.method == 'POST':
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.get_json()
        print(event_type)
        if event_type == 'pull_request':
            action = payload['action']
            branch = payload['pull_request']['head']['ref']
            pusher = payload['pull_request']['user']['login']
            url = payload['pull_request']['url']
            if action == 'opened':
                #email = payload['head_commit']['committer']['email']
                if branch == "billing" or branch=="weight" or branch=="devops": # remove devops
                    print("Starting testing process")
                    subprocess.run(['./scripts/testing.sh', branch, pusher, url])
                    return jsonify({"action": action, "pusher": pusher, "repository.branches_url": branch})
                else:
                    return "Invalid branch", 400
                #subprocess.run(['./scripts/production.sh', source_branch.group(1)])
            elif action == 'closed' and payload['pull_request']['merged_at'] is not None:
                print(f"Deploing to production from {branch}")
                subprocess.run(['./scripts/production.sh', branch, pusher])
                return jsonify({"action": action, "pusher": pusher, "repository.branches_url": branch})
            else:
                print(f"Unkown action: {action}")
                return "Invalid request" ,400
        else:
            return 'Unknown event', 400  

    else:
        return 'Method not allowed', 405
         



@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

