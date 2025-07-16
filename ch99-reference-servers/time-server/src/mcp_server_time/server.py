from datetime import datetime, timedelta
from enum  import Enum
import json
from typing import Sequence

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from tzlocal import get_localzone_name  # -- return returns "Europe/Paris", etc.

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError
from pydantic import BaseModel


class TimeTools(str, Enum):
    GET_CURRENT_TIME = "get_current_time"
    CONVERT_TIME = "convert_time"

class TimeResult(BaseModel):
    timezone: str
    datetime: str
    is_dst: bool
    
class TimeConversionResult(BaseModel):
    source: TimeResult
    target: TimeResult
    time_difference: str
    
class TimeConversionInput(BaseModel):
    source_tz: str
    time: str
    target_tx_list: list[str]
    

def get_local_tz(local_tz_override: str | None = None):
    if local_tz_override:
        try:
            return get_zoneinfo(local_tz_override)
        except:
            pass
    
    # Get local timezone from datetime.now()
    try:
        local_tzname = get_localzone_name()
        if local_tzname is not None:
            return get_zoneinfo(local_tzname)
    except:
        pass
    
    # Fallback to UTC if everything fails
    from datetime import timezone
    return timezone.utc

def get_zoneinfo(timezone_name: str):
    try:
        # tzdata가 없는 경우 대체 방법 사용
        import os
        if hasattr(ZoneInfo, '_get_tzdata_path'):
            # Python 3.9+ with tzdata
            return ZoneInfo(timezone_name)
        else:
            # fallback to system timezone data
            return ZoneInfo(timezone_name)
    except Exception as e:
        # 일반적인 timezone들에 대한 fallback
        common_timezones = {
            'Asia/Seoul': 9,
            'America/New_York': -5,
            'America/Los_Angeles': -8,
            'Europe/London': 0,
            'Europe/Paris': 1,
            'Asia/Tokyo': 9,
            'Australia/Sydney': 10
        }
        
        if timezone_name in common_timezones:
            # UTC 오프셋을 사용한 간단한 timezone 생성
            from datetime import timezone, timedelta
            offset_hours = common_timezones[timezone_name]
            return timezone(timedelta(hours=offset_hours))
        
        raise ValueError(f"Invalid timezone: {timezone_name}. Available: {list(common_timezones.keys())}")


class TimeServer:
    def get_current_time(self, timezone_name: str) -> TimeResult:
        """Get current time in specified timezone"""
        timezone = get_zoneinfo(timezone_name)
        current_time = datetime.now(timezone)
        
        return TimeResult(
            timezone=timezone_name,
            datetime=current_time.isoformat(timespec="seconds"),
            is_dst=bool(current_time.dst())
        )

    def convert_time(self, source_tz: str, time_str: str, target_tz: str) -> TimeConversionResult:
        """Convert time from source timezone to target timezones"""
        source_timezone = get_zoneinfo(source_tz)
        target_timezone = get_zoneinfo(target_tz)
    
        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            raise ValueError(f"Invalid time format. Expected HH:MM, [24-hour format]")
        
        now = datetime.now(source_timezone)
        source_time = datetime(
            now.year,
            now.month,
            now.day,
            parsed_time.hour,
            parsed_time.minute,
            tzinfo=source_timezone,
        )
        
        target_time = source_time.astimezone(target_timezone)
        source_offset = source_time.utcoffset() or timedelta()
        target_offset = target_time.utcoffset() or timedelta()
        
        hours_differrence = (target_offset - source_offset).total_seconds() / 3600
        
        if hours_differrence.is_integer():
            time_diff_str = f"{hours_differrence:+.1f}h"
        else:
            # For fractional hours like Nepal's \UTC+5:45
            time_diff_str = f"{hours_differrence:+.2f}".rstrip("0").rstrip(".") + "h"
        
        return TimeConversionResult(
            source=TimeResult(
                timezone=source_tz,
                datetime=source_time.isoformat(timespec="seconds"),
                is_dst=bool(source_time.dst())
            ),
            target=TimeResult(
                timezone=target_tz,
                datetime=target_time.isoformat(timespec="seconds"),
                is_dst=bool(target_time.dst())
            ),
            time_difference=time_diff_str
        )

#=============================================================    
async def serve(local_timezone: str | None = None) -> None:
    server = Server("mcp-time-server")
    time_server = TimeServer()
    local_tz = str(get_local_tz(local_timezone))
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available time tools"""
        return [
            Tool(
                name=TimeTools.GET_CURRENT_TIME.value,
                description="Get current time in specified timezone",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": f"IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use '{local_tz}' as local timezone if no timezone provided by the user.",
                        }
                    },
                    "required": ["timezone"],
                },
            ),
            Tool(
                name=TimeTools.CONVERT_TIME.value,
                description="Convert time between timezones",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_timezone": {
                            "type": "string",
                            "description": f"Source IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use '{local_tz}' as local timezone if no source timezone provided by the user.",
                        },
                        "target_timezone": {
                            "type": "string",
                            "description": f"Target IANA timezone name (e.g., 'Asia/Tokyo', 'America/San_Francisco'). Use '{local_tz}' as local timezone if no target timezone provided by the user.",
                        },
                        "time": {
                            "type": "string",
                            "description": "Time in HH:MM format (24-hour format, e.g., '14:30')",
                        },
                    },
                    "required": ["source_timezone", "time","target_timezone"],
                },
            ),
        ]
        
    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """handle tool calls for time queries"""
        try:
            result = None
            if name == TimeTools.GET_CURRENT_TIME.value:
                timezone = arguments.get("timezone").strip()
                if not timezone:
                    raise ValueError("Missing required argument: timezone")
                
                result = time_server.get_current_time(timezone)
            
            elif name == TimeTools.CONVERT_TIME.value:
                if not all(k in arguments for k in ["source_timezone", "time", "target_timezone"]):
                    raise ValueError("Missing required arguments")
                
                result = time_server.convert_time(
                    arguments["source_timezone"].strip(),
                    arguments["time"].strip(),
                    arguments["target_timezone"].strip(),
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            if result is None:
                raise ValueError(f"No result returned for tool: {name}")
                
            return [
                TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))
            ]
        except Exception as e:
            return [
                TextContent(type="text", text=f"Error: {str(e)}")
            ]

    #----------------------------------------------------    
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
#=============================================================    

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(serve())    

#-- 실행
# cd ./ch99-reference-servers/time-server
# > npx @modelcontextprotocol/inspector uv run python -m mcp_server_time
#-- go to inspector