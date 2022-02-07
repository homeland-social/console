#!/bin/sh -x

if [ ! -f "${SSH_KEY}" ]; then
    echo "Generating keys..."
    mkdir -p $(dirname ${SSH_KEY})
    dropbearkey -t ecdsa -f ${SSH_KEY} -s 384
    dropbearkey -y -f ${SSH_KEY} | grep "^ecdsa" > ${SSH_KEY}.pub
fi

# Upload ssh public key, we can't connect until this succeeds, so retry.
while true; do
    curl -d "{\"name\":\"SSH_PUB_KEY\", \"value\":\"$(cat ${SSH_KEY}.pub)\"}" \
         -H 'Content-Type: application/json' \
         -H "Authorization: Bearer ${AUTH_TOKEN}" \
         -X POST ${CONSOLE_URL}/api/settings/
    if [ $? -eq 0 ]; then
        break
    fi
    sleep 60
done

# Options:
# -T don't allocate a pty
# -i identity file
# -K keepalive (seconds?)
# -y accept host key
# -N don't run a remote command
# -R remote port forwarding

while true; do
    echo "Starting ssh client..."
    ssh -TNy -K 300 -i ${SSH_KEY} -R 0.0.0.0:0:${SSH_FORWARD_HOST}:${SSH_FORWARD_PORT} \
        ${SSH_USER}@${SSH_HOST}/${SSH_PORT}
    echo "SSH client died, restarting..."
    sleep 3
done
