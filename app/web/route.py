import os
import random
import asyncio
import aiosip
from aiohttp import web

from web.config import config 
from web.sip.util import Registration


routes = web.RouteTableDef()

srv_host = 'sipregistrar'
srv_port = 6000
realm = 'XXXXXX'
user = None
pwd = 'hunter2'
local_host = 'siprest'
local_port = random.randint(6001, 6100)

@routes.get('/')
async def home(request):
  return web.json_response({'status':'ok'})


@routes.get('/register/{user}')
async def register(request):
  print('Register request')
  user = request.match_info['user']
  
  sip = aiosip.Application(loop=request.loop)
  peer = await sip.connect((srv_host, srv_port), protocol=aiosip.TCP, local_addr=(local_host, local_port))
  await peer.register(
        from_details=header(user, local_host, local_port), 
        to_details=header(user, srv_host, srv_port),
        contact_details=header(user, local_host, local_port),
        password=pwd)
  await sip.close()

  print('Registration done')
  return web.json_response({'status': 'ok'})

@routes.get('/invite/{to_host}/{to_port}/{to_user}')
async def register(request):
  to_host = request.match_info['to_host']
  to_port = request.match_info['to_port']
  to_user = request.match_info['to_user']
  print('Invite request <to_host, to_port, to_user>', to_host, to_port, to_user)

  sip = aiosip.Application(loop=request.loop)
  peer = await sip.connect((to_host, to_port), protocol=aiosip.TCP, local_addr=(local_host, local_port))
  
  call = await peer.invite(
               from_details=header(user, local_host, local_port), 
               to_details=header(to_user, to_host, to_port),
               contact_details=header(user, local_host, local_port),
               password=pwd)

  async with call:
      async def reader():
          async for msg in call.wait_for_terminate():
              print("CALL STATUS:", msg.status_code)

          print("CALL ESTABLISHED")
          await asyncio.sleep(5)
          print("GOING AWAY...")

      with contextlib.suppress(asyncio.TimeoutError):
          await asyncio.wait_for(reader(), timeout=10)

  print("CALL TERMINATED")
  await sip.close()
  return web.json_response({'status': 'ok'})

def header(user, host, port) :
   return aiosip.Contact.from_header('sip:{}@{}:{}'.format( user, host,  port))
