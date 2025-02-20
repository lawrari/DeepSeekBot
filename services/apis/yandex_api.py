from services.apis.base import BaseClient
import aiohttp
import base64


class YandexOCR(BaseClient):
    def __init__(self, oauth_token: str, iam_token: str = "", folder_id: str = "", **kwargs):
        self.iam_token = iam_token
        self.oauth_token = oauth_token
        self.folder_id = folder_id
        self.base_url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"
        super().__init__(base_url=self.base_url)

    async def _post(self, data: dict, headers: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.base_url, json=data, headers=headers) as response:
                return await response.json()

    def _extract_full_text(self, api_response):
        full_text = []
        
        try:
            blocks = api_response["result"]["text_annotation"]["blocks"]
            for block in blocks:
                for line in block["lines"]:
                    for alternative in line["alternatives"]:
                        full_text.append(alternative["text"])
        except KeyError:
            return ""
        
        print(full_text)
        
        return " ".join(full_text)
    
    async def _get_IAM_token(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://iam.api.cloud.yandex.net/iam/v1/tokens",
                json={"yandexPassportOauthToken": self.oauth_token}
            ) as response:
                response_json = await response.json()
                return response_json["iamToken"]
    
    async def _get_cloud_id(self):
        self.iam_token = await self._get_IAM_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(url="https://resource-manager.api.cloud.yandex.net/resource-manager/v1/clouds", headers={"Authorization": "Bearer {:s}".format(self.iam_token)}) as response:
                response_json = await response.json()
                return response_json["clouds"][0]["id"]
    
    async def _get_folder_id(self):
        self.iam_token = await self._get_IAM_token()
        cloud_id = await self._get_cloud_id()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"https://resource-manager.api.cloud.yandex.net/resource-manager/v1/folders?cloudId={cloud_id}",
                headers={"Authorization": f"Bearer {self.iam_token}"}
            ) as response:
                response_json = await response.json()
                return response_json["folders"][0]["id"]
            
    @staticmethod
    def encode_file(file_input):
        if isinstance(file_input, str):  # If it's a file path
            with open(file_input, "rb") as fid:
                file_content = fid.read()
        elif isinstance(file_input, bytes):  # If it's already bytes
            file_content = file_input
        else:
            raise TypeError("file_input must be a file path (str) or bytes")

        return base64.b64encode(file_content).decode("utf-8")

    async def recognize(self, image: str, *args, **kwargs):
        self.iam_token = await self._get_IAM_token()

        data = {
            "mimeType": "JPEG",
            "languageCodes": ["*"],
            "model": "page",
            "content": image,
        }

        if not self.folder_id:
            self.folder_id = await self._get_folder_id()

        headers= {
            "Content-Type": "application/json",
            "Authorization": "Bearer {:s}".format(self.iam_token),
            "x-folder-id": self.folder_id,
            "x-data-logging-enabled": "true"
            }
        
        response = await self._post(data=data, headers=headers)

        return response["result"]["textAnnotation"]["fullText"]

