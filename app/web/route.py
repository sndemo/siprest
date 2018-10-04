import os
import random
import asyncio
import aiosip
from aiohttp import web

from web.config import config 
from web.sip.util import Registration


routes = web.RouteTableDef()

proxy_host = 'sipproxy'
proxy_port = 6100

realm = 'XXXXXX'
user = 'siprest'
pwd = 'hunter2'

local_host = 'siprest'

@routes.get('/')
async def home(request):
  return web.json_response({'status':'ok'})


@routes.get('/register/{from_user}/{from_host}/{from_port}')
async def register(request):
  print('Register request')
  from_user = request.match_info['from_user']
  from_host = request.match_info['from_host'] 
  from_port = request.match_info['from_port'] 

  sip = aiosip.Application(loop=request.loop)
 
  local_port = random.randint(6001, 6999)
  peer = await sip.connect((proxy_host, proxy_port), protocol=aiosip.TCP, local_addr=(local_host, local_port))
 
  rdialog = await peer.register(
        from_details=header(from_user,from_host, from_port), 
        to_details=header(from_user, from_host, from_port),
        contact_details=header(from_user, from_host, from_port),
        password=pwd)
  await sip.close()

  print('Registration done')
  return web.json_response({'status': rdialog.status_code , 'message': rdialog.status_message })

@routes.get('/invite/{to_user}')
async def invite(request):
  to_user = request.match_info['to_user']
  print('Invite request <to_user>', to_user)

  sip = aiosip.Application(loop=request.loop)
  
  local_port = random.randint(7001, 7999)
  peer = await sip.connect((proxy_host, proxy_port), protocol=aiosip.TCP, local_addr=(local_host, local_port))
  
  call = await peer.invite(
               from_details=header(user, local_host, local_port), 
               to_details=header(to_user, local_host, local_port),
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
