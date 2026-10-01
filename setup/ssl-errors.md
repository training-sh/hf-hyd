Too many things, done, not sure, what exactly fix the issue. first try  this on wsl

```
pip install pip-system-certs uv
```

```
gcloud auth application-default login
```

put this on first cell

```
import truststore

truststore.inject_into_ssl()
```

-----------


```
https://docs.cloud.google.com/sdk/docs/downloads-versioned-archives
```

UV Install

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

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
