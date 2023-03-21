from flask import Flask, request, jsonify
import subprocess


app = Flask(__name__)


@app.route("/trigger", methods = ['POST'])
def trigger():
    if request.method == 'POST':
        if 'X-GitHub-Event' in request.headers and request.headers['X-GitHub-Event'] == 'push':
            
            payload = request.get_json()

            #repo_name = payload['repository']['full_name']
            #action = payload['action']
            #commit_info = payload['commits'][0]
            pusher = payload['pusher']['name']
            email = payload['head_commit']['committer']['email']
            branch_split = payload['ref'].split('/')
            branch = branch_split[-1]

            # testing events
            # print(f"New push to {repo_name} to branch {branch} by {pusher}: {commit_info['message']}")

            if branch == "billing" or branch == "weight":
                subprocess.run(['./scripts/build.sh', branch])
            elif branch == "devops":
                subprocess.run(['./scripts/build.sh', branch])
                print("doing devops tests")
            else:
                return 400
       
        return jsonify({"action": "", "pusher": pusher, "repository.branches_url": branch})
        #return "OK", 200
    else:
        return 'Method not allowed', 405

@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

