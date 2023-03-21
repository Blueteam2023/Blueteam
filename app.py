from flask import Flask, request, jsonify
import subprocess


app = Flask(__name__)


app.route("/trigger", methods=['POST'])
def trigger():
  if request.method == 'POST':
        event_type = request.headers.get('X-GitHub-Event')
        print(request.headers)
        payload = request.get_json()
        print(payload)
        if event_type == 'push':
            # handle push event
            branch = payload['ref'].split('/')[-1]
            pusher = payload['pusher']['name']
            email = payload['head_commit']['committer']['email']
            if branch == "billing" or branch=="weight":
                subprocess.run(['./scripts/build.sh', branch])
            elif branch =="devops":
                subprocess.run(['./scripts/build.sh', branch])

            return jsonify({"action": "", "pusher": pusher, "repository.branches_url": branch})
          
        elif event_type == 'pull_request':
            action = payload['action']
            if action == 'closed' and payload['pull_request']['merged'] and payload['pull_request']['base']['ref'] == 'main':
                source_branch = payload['pull_request']['head']['ref']
                print(source_branch)
            #    subprocess.run(['./scripts/production.sh', source_branch])
                print("Bulding production")
            
        else:
            # handle other event types

            return 'OK', 200
  else:
    return 'Method not allowed', 405
         



@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

