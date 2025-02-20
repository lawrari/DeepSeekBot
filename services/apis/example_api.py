from services.apis.base import BaseClient


class ExampleApi(BaseClient):
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.base_url = "https://example.com/api/v1"
        super().__init__(base_url=self.base_url)

    async def get_data(self, *args, **kwargs):
        #  await self._make_request(...)
        return
