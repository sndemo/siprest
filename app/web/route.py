import os
import random
import asyncio
import aiosip
import contextlib
import socket

from aiohttp import web
from web.config import config 
from web.sip.util import Registration

routes = web.RouteTableDef()

proxy_host = 'sipproxy'
proxy_port = 6100
proxy_ip = socket.gethostbyname(proxy_host)

uas_host = 'sipuas'
uas_port = 6200

realm = 'XXXXXX'
user = 'siprest'
pwd = 'hunter2'

local_host = 'siprest'
local_ip = socket.gethostbyname(local_host)

@routes.get('/')
async def home(request):
  return web.json_response({'status':'ok'})


@routes.get('/register/{from_user}')
async def register(request):
  print('Register request')
  from_user = request.match_info['from_user']

  sip = aiosip.Application(loop=request.loop)

  local_port = random.randint(6001, 6999)
  peer = await sip.connect((proxy_ip, proxy_port), protocol=aiosip.TCP, local_addr=(local_ip, local_port))
  
  from_details = header(from_user,uas_host, uas_port)
  to_details=header(from_user, uas_host, uas_port)
  contact_details=header(from_user, uas_host, uas_port)
 
  rdialog = await peer.register( from_details=from_details, to_details=to_details, contact_details=contact_details, password=pwd )
  await sip.close()

  print('Registration done')
  return web.json_response({'status': rdialog.status_code , 'message': rdialog.status_message })

@routes.get('/invite/{to_user}')
async def invite(request):
  to_user = request.match_info['to_user']
  print('Invite request <to_user>', to_user)

  sip = aiosip.Application(loop=request.loop)
  
  local_port = random.randint(7001, 7999)
  peer = await sip.connect((proxy_ip, proxy_port), protocol=aiosip.TCP, local_addr=(local_ip, local_port))
  
  call = await peer.invite(
               from_details=header(user, local_host, local_port), 
               to_details=header(to_user, local_host, local_port),
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
