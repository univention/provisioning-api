#!/usr/bin/env bash
set -e

echo "Sending message as $AUTHOR_ALIAS to $DESTINATION"
AUTH_RESPONSE=$(curl --fail -H "Content-type:application/json" "$BASE_URL/api/v1/login" -d "{ \"username\": \"$ROCKETCHAT_USERNAME\", \"password\": \"$ROCKETCHAT_PASSWORD\" }")
AUTH_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.data.authToken')
USER_ID=$(echo "$AUTH_RESPONSE" | jq -r '.data.userId')
MESSAGE="$(envsubst < "$MESSAGE_FILE")"
REQUEST_DATA="$(\
    jq \
        --null-input \
        --arg message "$MESSAGE" \
        --arg author_alias "$AUTHOR_ALIAS" \
        --arg destination "$DESTINATION" \
        '{"channel": $destination, "text": $message, "alias": $author_alias}'
)"
curl -vvv --fail \
    -H "X-Auth-Token: $AUTH_TOKEN" \
    -H "X-User-Id: $USER_ID" \
    -H "Content-type:application/json" \
    "$BASE_URL/api/v1/chat.postMessage" \
    -d "$REQUEST_DATA"
