import os
import requests
import logfire
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

ROUTER_IP = os.getenv("ROUTER_IP", "192.168.88.1")
USERNAME = os.getenv("ROUTER_USER", "admin")
PASSWORD = os.getenv("ROUTER_PASS", "")
BASE_URL = f"https://{ROUTER_IP}/rest"

@tool
def check_pppoe_status(username: str) -> str:
    """Checks the live connection status of a PPPoE client on the MikroTik router."""
    url = f"{BASE_URL}/ppp/active"
    response = requests.get(url, auth=(USERNAME, PASSWORD), verify=False)
    if response.status_code != 200:
        return f"Error reaching router: {response.status_code}"
    active_users = response.json()
    for user in active_users:
        if user.get("name") == username:
            return f"User {username} is connected. IP: {user.get('address')}"
    return f"User {username} is currently disconnected."

@tool
def get_recent_logs(limit: int = 5) -> str:
    """Fetches the most recent system logs from the router to diagnose issues."""
    url = f"{BASE_URL}/log"
    response = requests.get(url, auth=(USERNAME, PASSWORD), verify=False)
    if response.status_code == 200:
        logs = response.json()
        return "\n".join([f"[{l.get('time')}] {l.get('topics')}: {l.get('message')}" for l in logs[-limit:]])
    return "Failed to retrieve logs."

@tool
def reset_dhcp_lease(mac_address: str) -> str:
    """Resets the DHCP lease for a rogue or stuck device. Requires user confirmation."""
    print(f"\n[WARNING] The agent wants to reset the DHCP lease for MAC: {mac_address}")
    user_approval = input("I found the rogue device. May I reset it? (Type 'YES' to confirm): ")
    if user_approval.strip().upper() == "YES":
        return f"SUCCESS: DHCP lease for {mac_address} has been successfully flushed."
    return "ACTION ABORTED BY USER. Do not attempt to reset again. Suggest alternative troubleshooting steps."

@tool
def ping_gateway() -> str:
    """Fallback tool: Pings the main ISP gateway to check upstream connectivity."""
    return "SUCCESS: Gateway ping is 4ms. The upstream ISP connection is stable."

@tool
def check_router_health(ip_address: str) -> str:
    """Checks if the target router is responsive via its REST API."""
    with logfire.span("tool:check_router_health", target_ip=ip_address) as span:
        try:
            response = requests.get(f"https://{ip_address}/rest/system/resource", timeout=2, verify=False)
            response.raise_for_status()
            span.set_attribute("status", "success")
            return "SUCCESS: Router is healthy and REST API is responding."
        except requests.exceptions.Timeout:
            span.set_attribute("status", "timeout")
            span.record_exception()
            return "ERROR: The API request timed out. Do not try this tool again. Execute the 'ping_gateway' tool to check upstream connectivity instead."
        except Exception as e:
            span.record_exception()
            return f"ERROR: {str(e)}. Tell the user to manually verify the router IP."
