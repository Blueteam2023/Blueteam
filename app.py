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
            if action == 'closed' and payload['pull_request']['merged_at'] is not None: #if pull request approved
                if branch == "billing" or branch=="weight":
                    print("Starting testing process")
                    subprocess.run(['./scripts/building.sh', branch, pusher, url])
                    return jsonify({"action": action, "pusher": pusher, "repository.branches_url": branch})
                elif branch == "reverted_main":
                    print("Deleting reverted branch")
                    #deleting reverted branch and pulling reverted main
                    subprocess.run(['git', 'branch', '-D', 'reverted_main', '&&',
                                    'git', 'push', 'origin', '--delete', 'reverted_main', '&&',
                                    'git', 'checkout', 'main', '&&', 'git', 'pull'])
                    return "Revert succeeded", 200
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    # Running production in first init
    subprocess.run(['./scripts/deploy.sh'])

