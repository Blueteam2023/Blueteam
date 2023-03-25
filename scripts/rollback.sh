#!/bin/sh

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./reroll.sh <tag_name>"
    exit 1
fi

TAG_NAME="$1"
source ./building.sh

cd /app
git checkout tags/"$TAG_NAME"

stop_production
exec ./scripts/deploy.sh

echo $TAG_NAME >> ./data/stable_versions.txt
send_mail "Version Rerolled: $TAG_NAME" "The application has been rerolled to version $TAG_NAME. Please review and verify the changes."
echo "Rerolled to version $TAG_NAME and sent an email to the devops team."