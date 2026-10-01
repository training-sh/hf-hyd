```
uv pip install --system-certs truststore
```

```
import truststore

truststore.inject_into_ssl()
```

```
import truststore
truststore.inject_into_ssl()

from google.adk.agents import Agent
from google.adk.models import Gemini

model = Gemini(
    model="gemini-2.5-flash-lite",
    client_kwargs={
        "vertexai": True,
        "project": PROJECT_ID,
        "location": "global",
    },
)
```
