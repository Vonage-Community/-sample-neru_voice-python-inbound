import sys
import os
sys.path.append("vendor")
import uvicorn
import asyncio

from fastapi import Request, FastAPI
from nerualpha.neru import Neru
from nerualpha.providers.voice.voice import Voice
from nerualpha.providers.voice.contracts.vapiEventParams import VapiEventParams

app = FastAPI()
neru = Neru()

async def listenForInboundCall():
    try:
        session = neru.createSession()
        voice = Voice(session)
        await voice.onVapiAnswer('onCall').execute()
    except Exception as e:
        print(e)
        sys.exit(1)

@app.get('/_/health')
async def health():
    return 'OK'

@app.post('/onCall')
async def onCall(request: Request):
    session = neru.createSession()
    voice = Voice(session)

    body = await request.json()
    
    vapiEventParams = VapiEventParams()
    vapiEventParams.callback = 'onEvent'
    vapiEventParams.vapiUUID = body['uuid']

    await voice.onVapiEvent(vapiEventParams).execute()

    return  [
                {
                    'action': 'talk',
                    'text': 'Hi! This call was answered by NeRu.'
                }
        ]

@app.post('/onEvent')
async def onEvent(request: Request):
    body = await request.json()
    print('event status is:', body['status'])
    print('event direction is:', body['direction'])
    return 'OK'

if __name__ == "__main__":
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_until_complete(listenForInboundCall())
    port = int(os.getenv('NERU_APP_PORT'))
    uvicorn.run(app, host="0.0.0.0", port=port)
