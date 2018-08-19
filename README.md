# light_reporter
Send Hue light status to influxdb

### Get user id
`POST to http://<Hue hub ip>/api` with this body `{ "devicetype": "API Client" }`
### Run
`docker run --name light_reporter --restart=unless-stopped -e USER=<user id> -dt ashearer/light_reporter:latest`
