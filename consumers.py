import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.upload_id = self.scope["url_route"]["kwargs"]["upload_id"]
        self.group_name = f"progress_{self.upload_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def progress_message(self, event):
        # event = {"type":"progress_message","data":{...}}
        await self.send(text_data=json.dumps(event["data"]))
