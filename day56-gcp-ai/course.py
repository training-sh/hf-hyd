"""Small shared runtime; agent definitions stay in the teaching notebooks."""
from pathlib import Path
import json
import os
import ssl
import uuid
from dataclasses import dataclass, field

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "config.json").read_text())
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", CONFIG["project_id"])
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", CONFIG["location"])
MODEL = os.getenv("GEMINI_MODEL", CONFIG["model"])
SKIP_SSL = os.getenv("ADK_SKIP_SSL_VALIDATION", str(CONFIG["skip_ssl_validation"])).lower() == "true"
CA_BUNDLE = os.getenv("ADK_CA_BUNDLE") or CONFIG["ca_bundle"]
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

from google.adk.agents import Agent, RunConfig
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.genai import types


def gemini(model=None):
    """ADK 2.10 uses client_kwargs, not a Gemini(http_options=...) extra field.

    Configured TLS bypass applies to both model HTTP and ADC token refresh.
    No global SSL monkey patch, environment activation or credential printing.
    """
    kwargs = dict(vertexai=True, project=PROJECT, location=LOCATION)
    if SKIP_SSL or CA_BUNDLE:
        import google.auth
        from google.auth.credentials import Credentials
        from google.auth.transport.requests import Request
        import requests

        verify = False if SKIP_SSL else CA_BUNDLE

        class AuthSession(requests.Session):
            def request(self, *args, **kw):
                kw["verify"] = verify
                return super().request(*args, **kw)

        original, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_request = Request(session=AuthSession())

        class CourseCredentials(Credentials):
            def __init__(self):
                super().__init__()
                self._quota_project_id = getattr(original, "quota_project_id", None)

            def refresh(self, request):
                original.refresh(auth_request)
                self.token, self.expiry = original.token, original.expiry

        kwargs["credentials"] = CourseCredentials()
        transport_verify = False if SKIP_SSL else ssl.create_default_context(cafile=CA_BUNDLE)
        kwargs["http_options"] = types.HttpOptions(
            client_args={"verify": transport_verify},
            async_client_args={"verify": transport_verify},
            timeout=90000,
            retry_options=types.HttpRetryOptions(attempts=2),
        )
    else:
        kwargs["http_options"] = types.HttpOptions(
            timeout=90000, retry_options=types.HttpRetryOptions(attempts=2))
    return Gemini(model=model or MODEL, client_kwargs=kwargs)


def llm(name, instruction, **kwargs):
    return Agent(name=name, model=kwargs.pop("model", None) or gemini(),
                 instruction=instruction,
                 generate_content_config=kwargs.pop("generate_content_config", None)
                 or types.GenerateContentConfig(temperature=0, max_output_tokens=CONFIG["max_output_tokens"]),
                 **kwargs)


@dataclass
class Lab:
    runner: Runner
    session: object
    user_id: str
    last_events: list = field(default_factory=list)


async def make_lab(agent=None, *, app=None, state=None, sessions=None,
                   memory=None, artifacts=None, plugins=None, user_id="customer_101"):
    service = sessions if sessions is not None else InMemorySessionService()
    name = app.name if app is not None else "ecommerce_lab"
    runner_args = {"app": app} if app is not None else {"agent": agent, "app_name": name, "plugins": plugins or []}
    runner = Runner(**runner_args, session_service=service,
                    memory_service=memory if memory is not None else InMemoryMemoryService(),
                    artifact_service=artifacts if artifacts is not None else InMemoryArtifactService())
    session = await service.create_session(app_name=name, user_id=user_id,
                                           session_id=uuid.uuid4().hex, state=state or {})
    return Lab(runner, session, user_id)


async def ask(lab, message=None, *, parts=None, run_config=None,
              invocation_id=None, state_delta=None, verbose=True):
    content = None
    if message is not None or parts is not None:
        content = types.Content(role="user", parts=parts or [types.Part(text=message)])
    events = []
    async for event in lab.runner.run_async(
        user_id=lab.user_id, session_id=lab.session.id, new_message=content,
        invocation_id=invocation_id, state_delta=state_delta,
        run_config=run_config or RunConfig(max_llm_calls=CONFIG["max_llm_calls"]),
    ):
        events.append(event)
        if event.error_code:
            raise RuntimeError(f"{event.error_code}: {event.error_message}")
        if verbose:
            for call in event.get_function_calls():
                print(f"  tool: {call.name}({call.args})")
            if event.is_final_response() and event.content:
                text = "".join(p.text or "" for p in event.content.parts or [])
                if text:
                    print(f"{event.author}: {text}")
    lab.last_events = events
    lab.session = await lab.runner.session_service.get_session(
        app_name=lab.runner.app_name, user_id=lab.user_id, session_id=lab.session.id)
    return events


def final_text(events):
    texts = ["".join(p.text or "" for p in e.content.parts or [])
             for e in events if e.is_final_response() and e.content]
    return texts[-1] if texts else ""


def token_usage(events):
    """Count completed response usage, excluding partial streaming chunks."""
    return sum((e.usage_metadata.total_token_count or 0)
               for e in events if e.usage_metadata and not e.partial)


DATA = json.loads((ROOT / "data" / "ecommerce.json").read_text())


def get_order(order_id: str) -> dict:
    """Look up a synthetic order by order ID, including items and invoice total."""
    return next((dict(o) for o in DATA["orders"] if o["order_id"] == order_id), {"error": "Order not found"})


def get_product(product_id: str) -> dict:
    """Look up a product's price and stock by its product ID."""
    return next((dict(p) for p in DATA["products"] if p["product_id"] == product_id), {"error": "Product not found"})


def get_customer(customer_id: str) -> dict:
    """Return a synthetic customer's name and membership tier."""
    return next((dict(c) for c in DATA["customers"] if c["customer_id"] == customer_id), {"error": "Customer not found"})
