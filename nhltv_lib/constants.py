# User Agents
UA_NHL = "NHL/2542 CFNetwork/758.2.8 Darwin/15.0.0"
UA_PC = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36"
    + " (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36"
)
UA_PS4 = "PS4Application libhttp/1.000 (PS4) libhttp/3.15 (PlayStation 4)"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Accept-encoding": "gzip, deflate, sdch",
    "Accept-language": "en-US,en;q=0.8",
    "User-agent": UA_PC,
    "Origin": "https://www.nhl.com",
}

auth_token = (
    "Basic d2ViX25obC12MS4wLjA6MmQxZDg0NmVhM2IxOTRhMThlZjQwYWM5ZmJjZTk3ZTM="
)

TOKEN_AUTH_HEADERS = {**HEADERS, "Authorization": auth_token}
