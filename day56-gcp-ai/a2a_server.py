"""Optional local A2A service, launched and cleaned up by notebook 28."""
import sys
import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from course import llm, get_order

if __name__ == "__main__":
    port = int(sys.argv[1])
    agent = llm("orders_service", "Use get_order to answer questions about demo orders.", tools=[get_order])
    app = to_a2a(agent, host="127.0.0.1", port=port)
    uvicorn.run(app, host="127.0.0.1", port=port)
