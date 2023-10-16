#!/bin/bash

# recreate RabbitMQ 'Trac' virtual host
# credentials for RabbitMQ instance {'vhost':'Trac', 'user':'lshift', 'pw':'lshift'}
VHOST_NAME="Trac"
AMQP_USERNAME="lshift"
AMQP_PASSWORD="lshift"

# recreate "Trac" vhost
sudo rabbitmqctl delete_vhost "$VHOST_NAME" >/dev/null 2>&1 || true
sudo rabbitmqctl add_vhost "$VHOST_NAME"

# recreate admin user "lshift:lshift"
sudo rabbitmqctl delete_user "$AMQP_USERNAME" >/dev/null 2>&1 || true
sudo rabbitmqctl add_user "$AMQP_USERNAME" "$AMQP_PASSWORD"

# reset permissions for lshift in "Trac"
sudo rabbitmqctl clear_permissions -p "Trac" "lshift"
sudo rabbitmqctl set_permissions -p "Trac" "lshift" ".*" ".*" ".*"
