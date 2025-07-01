#!/usr/bin/env python3

import asyncio
from ollama import Client, AsyncClient

async def main():
  messages = [
    {
      'role': 'user',
      'content': 'Why is the sky blue?',
    },
  ]

  client = AsyncClient()
  response = await client.chat('mistral', messages=messages)
  print(response['message']['content'])


if __name__ == '__main__':
  asyncio.run(main())
