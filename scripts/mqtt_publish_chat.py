import paho.mqtt.publish as publish
payload = '{"sender": {"base58Address": "TESTADDR123"}, "data": {"data": "Hello bot — MQTT test"}}'
publish.single('Chat', payload=payload, hostname='localhost', port=1883)
print('published Chat')
