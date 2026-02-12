import asyncio
import json
import sys
from pipeline import run_agent

async def main():
    query = sys.argv[1]
    result = await run_agent(query)
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(main())
