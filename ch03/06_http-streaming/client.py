# -*- coding: utf-8 -*-
#
# HTTP Streaming 클라이언트 구현
#
import asyncio
import requests
import logging
import mcp.types as types
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.session import RequestResponder


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger('MCP_CLIENT')

#---------------------------------------------
class LoggingCollector:
    def __init__(self):
        self.log_messages: list[types.LoggingMessageNotificationParams] = []
    
    async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
        self.log_messages.append(params)
        logger.info("MCP Log: %s - %s", params.level, params.data)

#---------------------------------------------
#-- Create a Logging Collector
logging_collector = LoggingCollector()

#---------------------------------------------
async def message_handler(
    message: RequestResponder[types.ServerRequest, types.ClientResult] 
    | types.ServerNotification 
    | Exception 
) -> None:
    logger.info("Received message: %s", message)
    if isinstance(message, Exception):
        logger.error("Exception received!")
        raise message
    elif isinstance(message, types.ServerNotification):
        logger.info("NOTIFICATION: %s", message)
    elif isinstance(message, RequestResponder):
        logger.info("REQUEST_RESPONDER: %s", message)
    else:
        logger.info("SERVER_MESSAGE: %s", message)

#---------------------------------------------
port = 8000
async def main():
    logger.info("Starting MCP Client...")
    async with streamablehttp_client(f"http://localhost:{port}/mcp") as (
        read_stream, write_stream, session_callback):
        async with ClientSession(read_stream, write_stream, 
                                 logging_callback=logging_collector,
                                 message_handler=message_handler) as session:
            id_before = session_callback()
            logger.info("Session IO before init: %s", id_before)
            await session.initialize()
            id_after = session_callback()
            logger.info("Session IO after init: %s", id_after)
            logger.info("Session initialized, ready to call tools.")
            # Call the process_file tool (MCP tool)
            tool_result = await session.call_tool("process_file", {"message": "hello from client"})
            logger.info("Tool Result: %s", tool_result)
            
            if logging_collector.log_messages:
                logger.info("Collected log messages:")
                for log in logging_collector.log_messages:
                    logger.info("Log: %s", log)

#---------------------------------------------
def stream_progress(message="hello", url="http://localhost:8000/stream"):
    params = {"message": message}
    logger.info("Connecting to %s with message: %s", url, message)
    try:
        with requests.get(url, params=params, stream=True, timeout=10) as r:
            r.raise_for_status()
            logger.info("--- Streaming Progress ---")
            for line in r.iter_lines():
                if line:
                    # Still print the streamed content to stdout for visibility
                    decoded_line = line.decode().strip()
                    print(decoded_line)
                    logger.info("Stream content: %s", decoded_line)
            logger.info("--- Stream Ended ---")
    except requests.RequestException as e:
        logger.error("Error during streaming: %s", e)

#---------------------------------------------
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        # MCP client mode
        logger.info("Running MCP client mode...")
        asyncio.run(main())
    else:
        # Classic HTTP streaming clientmode
        logger.info("Running HTTP streaming mode...")
        stream_progress()

#--실행 방법
# 1. MCP client mode
# > uv run client.py mcp
# 2. Classic HTTP streaming client mode
# > uv run client.py

#-- 출력 결과
#---------------------------------------------
# 1. MCP client mode
# > uv run client.py mcp
# 2025-06-21 01:15:49 - MCP_CLIENT - INFO - Running MCP client mode...
# 2025-06-21 01:15:49 - MCP_CLIENT - INFO - Starting MCP Client...
# 2025-06-21 01:15:49 - MCP_CLIENT - INFO - Session IO before init: None
# 2025-06-21 01:15:49 - httpx - INFO - HTTP Request: POST http://localhost:8000/mcp "HTTP/1.1 307 Temporary Redirect"
# 2025-06-21 01:15:49 - httpx - INFO - HTTP Request: POST http://localhost:8000/mcp/ "HTTP/1.1 200 OK"
# 2025-06-21 01:15:49 - mcp.client.streamable_http - INFO - Received session ID: 80fd615f5bfc4024880765556ff33839
# 2025-06-21 01:15:49 - MCP_CLIENT - INFO - Session IO after init: 80fd615f5bfc4024880765556ff33839
# 2025-06-21 01:15:49 - MCP_CLIENT - INFO - Session initialized, ready to call tools.
# 2025-06-21 01:15:49 - httpx - INFO - HTTP Request: GET http://localhost:8000/mcp "HTTP/1.1 307 Temporary Redirect"
# 2025-06-21 01:15:49 - httpx - INFO - HTTP Request: POST http://localhost:8000/mcp "HTTP/1.1 307 Temporary Redirect"
# 2025-06-21 01:15:49 - httpx - INFO - HTTP Request: GET http://localhost:8000/mcp/ "HTTP/1.1 200 OK"
# 2025-06-21 01:15:49 - httpx - INFO - HTTP Request: POST http://localhost:8000/mcp/ "HTTP/1.1 202 Accepted"
# 2025-06-21 01:15:49 - httpx - INFO - HTTP Request: POST http://localhost:8000/mcp "HTTP/1.1 307 Temporary Redirect"
# 2025-06-21 01:15:49 - httpx - INFO - HTTP Request: POST http://localhost:8000/mcp/ "HTTP/1.1 200 OK"
# 2025-06-21 01:15:49 - MCP_CLIENT - INFO - MCP Log: info - Processing file_1.txt (0/3)...
# 2025-06-21 01:15:49 - MCP_CLIENT - INFO - Received message: root=LoggingMessageNotification(method='notifications/message', params=LoggingMessageNotificationParams(meta=None, level='info', logger=None, data='Processing file_1.txt (0/3)...'), jsonrpc='2.0')
# 2025-06-21 01:15:49 - MCP_CLIENT - INFO - NOTIFICATION: root=LoggingMessageNotification(method='notifications/message', params=LoggingMessageNotificationParams(meta=None, level='info', logger=None, data='Processing file_1.txt (0/3)...'), jsonrpc='2.0')
# 2025-06-21 01:15:50 - MCP_CLIENT - INFO - MCP Log: info - Processing file_2.txt (1/3)...
# 2025-06-21 01:15:50 - MCP_CLIENT - INFO - Received message: root=LoggingMessageNotification(method='notifications/message', params=LoggingMessageNotificationParams(meta=None, level='info', logger=None, data='Processing file_2.txt (1/3)...'), jsonrpc='2.0')
# 2025-06-21 01:15:50 - MCP_CLIENT - INFO - NOTIFICATION: root=LoggingMessageNotification(method='notifications/message', params=LoggingMessageNotificationParams(meta=None, level='info', logger=None, data='Processing file_2.txt (1/3)...'), jsonrpc='2.0')
# 2025-06-21 01:15:51 - MCP_CLIENT - INFO - MCP Log: info - Processing file_3.txt (2/3)...
# 2025-06-21 01:15:51 - MCP_CLIENT - INFO - Received message: root=LoggingMessageNotification(method='notifications/message', params=LoggingMessageNotificationParams(meta=None, level='info', logger=None, data='Processing file_3.txt (2/3)...'), jsonrpc='2.0')
# 2025-06-21 01:15:51 - MCP_CLIENT - INFO - NOTIFICATION: root=LoggingMessageNotification(method='notifications/message', params=LoggingMessageNotificationParams(meta=None, level='info', logger=None, data='Processing file_3.txt (2/3)...'), jsonrpc='2.0')
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - MCP Log: info - All files processed
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - Received message: root=LoggingMessageNotification(method='notifications/message', params=LoggingMessageNotificationParams(meta=None, level='info', logger=None, data='All files processed'), jsonrpc='2.0')
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - NOTIFICATION: root=LoggingMessageNotification(method='notifications/message', params=LoggingMessageNotificationParams(meta=None, level='info', logger=None, data='All files processed'), jsonrpc='2.0')
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - Tool Result: meta=None content=[TextContent(type='text', text='Processed files: file_1.txt, file_2.txt, file_3.txt | Messages: hello from client', annotations=None)] isError=False
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - Collected log messages:
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - Log: meta=None level='info' logger=None data='Processing file_1.txt (0/3)...'
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - Log: meta=None level='info' logger=None data='Processing file_2.txt (1/3)...'
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - Log: meta=None level='info' logger=None data='Processing file_3.txt (2/3)...'
# 2025-06-21 01:15:52 - MCP_CLIENT - INFO - Log: meta=None level='info' logger=None data='All files processed'
# 2025-06-21 01:15:52 - httpx - INFO - HTTP Request: DELETE http://localhost:8000/mcp "HTTP/1.1 307 Temporary Redirect"
# 2025-06-21 01:15:52 - httpx - INFO - HTTP Request: DELETE http://localhost:8000/mcp/ "HTTP/1.1 200 OK"

#---------------------------------------------
# 2. Classic HTTP streaming client mode
# > uv run client.py
# 2025-06-21 00:59:57 - mcp_client - INFO - Running HTTP streaming mode...
# 2025-06-21 00:59:57 - mcp_client - INFO - Connecting to http://localhost:8000/stream with message: hello
# 2025-06-21 00:59:57 - mcp_client - INFO - --- Streaming Progress ---
# Processing file 1/3...
# 2025-06-21 00:59:57 - mcp_client - INFO - Stream content: Processing file 1/3...
# Processing file 2/3...
# 2025-06-21 00:59:58 - mcp_client - INFO - Stream content: Processing file 2/3...
# Processing file 3/3...
# 2025-06-21 00:59:59 - mcp_client - INFO - Stream content: Processing file 3/3...
# Here's the file content: hello
# 2025-06-21 01:00:00 - mcp_client - INFO - Stream content: Here's the file content: hello
# 2025-06-21 01:00:00 - mcp_client - INFO - --- Stream Ended ---