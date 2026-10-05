"""Entry point used by adk web, adk api_server and adk eval."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from course import llm, get_order, get_product

root_agent = llm("shop_assistant", "Use tools for order or product facts. Include the exact ID and status "
                 "when answering an order status question. Never invent records.", tools=[get_order, get_product])
