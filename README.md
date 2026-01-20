# TinhSuper Obfuscator API

API lưu trữ & phân phối Lua script cho Roblox executor (Delta X safe).

## Endpoints

### GET /
Check API status

### GET /ping
Keep-alive

### POST /add
Upload script

```json
{
  "script": "-- lua code here"
}
