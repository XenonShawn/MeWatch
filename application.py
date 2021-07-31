from fastapi import FastAPI
from pydantic import BaseModel

from driver import Television

class Action(BaseModel):
    action: str
    num: int = 0
    data: str = ''

def getAPI(television: Television):
    app = FastAPI()

    @app.get('/')
    async def root():
        return {'message': 'hello world!', 'success': True}

    @app.get('/shows')
    async def get_show(name: str = None):
        if name is None:
            return {'shows': {k: v["display"] for k, v in television.allowed_shows.items()}, 'success': True}

        if name not in television.allowed_shows:
            return {'success': False, 'message': "Invalid show.", 'data': name}

        return await television.get_show(name)

    @app.post('/action')
    async def video(data: Action):
        global state
        if data.action == 'watch':
            return {'succcess': await television.watch(data.num)}
        elif data.action == 'pause':
            return {'success': await television.pause()}
        elif data.action == 'seek':
            return {'success': await television.seek(data.num)}
        elif data.action == 'volume':
            return {'success': await television.volume(data.num)}
        return {'success': False, 'data': data}
    
    return app