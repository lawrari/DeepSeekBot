from collections import OrderedDict
from datetime import datetime, timedelta


class Dialog:
    def __init__(self):
        self.messages = []
        self.created_at = datetime.now()

    def __iter__(self):
        return iter(self.messages)
    
    def __getitem__(self, index):
        return list(self.messages)[index]
    
    def __len__(self):
        return len(self.messages)
    
    async def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})
    
    async def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})
    
    async def is_older_than_24h(self):
        return datetime.now() - self.created_at > timedelta(hours=24)
    
    async def clear(self):
        self.messages = []
    

class Dialogs:
    def __init__(self, limit=1000):
        self.dialogs = OrderedDict()
        self.limit = limit

    def __iter__(self):
        return iter(self.dialogs.items())
    
    def __getitem__(self, index):
        return list(self.dialogs.items())[index]
    
    def __len__(self):
        return len(self.dialogs)
    
    def __contains__(self, dialog_id):
        return dialog_id in self.dialogs
    
    async def create_dialog(self, dialog_id):
        if len(self.dialogs) >= self.limit:
            self.dialogs.popitem(last=False)
        self.dialogs[dialog_id] = Dialog()
    
    async def clear_dialog(self, dialog_id):
        if dialog_id in self.dialogs:
            self.dialogs[dialog_id] = Dialog()
    
    async def delete_dialog(self, dialog_id):
        self.dialogs.pop(dialog_id, None)
    
    async def remove_old_dialogs(self):
        to_delete = [dialog_id for dialog_id, dialog in self.dialogs.items() if await dialog.is_older_than_24h()]
        for dialog_id in to_delete:
            del self.dialogs[dialog_id]
