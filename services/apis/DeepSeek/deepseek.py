from openai import AsyncOpenAI
from services.apis.deepseek.dialogs import Dialog


class DeepSeek:
    def __init__(self, api_key, model="deepseek-reasoner"):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com"
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    
    async def stream_response(self, dialog: Dialog):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=dialog.messages,
            stream=True,
            stream_options={"include_usage": True}
        )

        async for chunk in response:
            if chunk.choices[0].delta.content and chunk.choices[0].delta.content != " ":
                yield chunk.choices[0].delta.content, chunk.usage