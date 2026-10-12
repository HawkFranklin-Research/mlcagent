from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

from mlca.config import Config, ProviderConfig, RoleConfig
from mlca.llm.catalog import DEFAULTS, cached, save_prices
from mlca.llm.credentials import forget, remember, resolve

from .model_picker import ModelPicker

KINDS = [
    ("OpenRouter", "openrouter"),
    ("OpenAI", "openai_api"),
    ("Local / OpenAI-compatible server", "openai_compatible"),
]


class OnboardingScreen(ModalScreen[dict | None]):
    CSS = """OnboardingScreen { align: center middle; }
    #settings { width: 95%; max-width: 140; height: 95%; padding: 1 2; border: round $accent; overflow-y: auto; }
    #navigator-settings, #worker-settings { height: auto; }
    Input, Select { margin-bottom: 1; } .model-row { height: 3; margin-bottom: 1; }
    .model-row Input { width: 1fr; } #settings-buttons { height: 3; }"""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.initial = {}
        self.prices = {}
        for role in ["navigator", "worker"]:
            selected = config.roles.get(role)
            name = selected.provider if selected else role + "_provider"
            provider = config.providers.get(name) or ProviderConfig(
                kind="openrouter", api_key_env="OPENROUTER_API_KEY"
            )
            self.initial[role] = (name, provider, selected)

    def compose(self) -> ComposeResult:
        with Vertical(id="settings"):
            yield Static(
                "Models and providers — keys remain in environment variables or this application session only"
            )
            yield Checkbox(
                "Use the Navigator provider and model for the Worker too",
                value=self.initial["navigator"][2] == self.initial["worker"][2],
                id="shared-model",
            )
            for role in ["navigator", "worker"]:
                _, provider, selected = self.initial[role]
                with Vertical(id=role + "-settings"):
                    yield Label(
                        "Navigator — proposes next actions"
                        if role == "navigator"
                        else "Worker — writes and repairs Python"
                    )
                    choices = KINDS + ([("Offline fake provider", "fake")] if provider.kind == "fake" else [])
                    yield Select(choices, value=provider.kind, allow_blank=False, id=role + "-kind")
                    yield Label("API key (optional paste; forgotten when this application exits)")
                    yield Input(password=True, id=role + "-key")
                    yield Static(
                        "Key available"
                        if resolve(provider.api_key_env)
                        else "No key detected; paste one or use your environment variable",
                        id=role + "-key-status",
                    )
                    yield Label(
                        "Environment variable (advanced; detected automatically for hosted providers)"
                    )
                    yield Input(provider.api_key_env or "", id=role + "-env")
                    yield Label("Endpoint — required for local/custom servers")
                    yield Input(
                        provider.base_url or DEFAULTS.get(provider.kind, ("", None))[0], id=role + "-url"
                    )
                    yield Label("Model ID — type it directly or browse provider models")
                    with Horizontal(classes="model-row"):
                        yield Input(selected.model if selected else "", id=role + "-model")
                        yield Button("Browse models", id=role + "-browse")
                    yield Label("Maximum USD per request (required if model pricing is unknown)")
                    yield Input(
                        str(provider.request_cost_bound_usd)
                        if provider.request_cost_bound_usd is not None
                        else "",
                        id=role + "-bound",
                    )
            yield Label("Budgets: maximum USD per turn / per session")
            yield Input(str(self.config.budgets.turn_max_usd), id="turn-budget")
            yield Input(str(self.config.budgets.session_max_usd), id="session-budget")
            yield Checkbox(
                "Allow weaker sandbox level B for trusted code only",
                value=self.config.sandbox.allow_level_b,
                id="allow-b",
            )
            yield Static("", id="settings-error")
            with Horizontal(id="settings-buttons"):
                yield Button("Save", id="save-settings", variant="primary")
                yield Button("Forget pasted keys", id="forget-keys")
                yield Button("Cancel", id="cancel-settings")

    def on_mount(self):
        self.shared_changed()

    def shared_changed(self):
        self.query_one("#worker-settings").display = not self.query_one("#shared-model", Checkbox).value

    def on_checkbox_changed(self, event):
        if event.checkbox.id == "shared-model":
            self.shared_changed()

    def on_select_changed(self, event):
        if event.select.id.endswith("-kind"):
            role = event.select.id.split("-")[0]
            if event.value == self.initial[role][1].kind:
                return
            url, env = DEFAULTS.get(event.value, ("", None))
            self.query_one("#" + role + "-url", Input).value = url
            self.query_one("#" + role + "-env", Input).value = env or ""
            self.query_one("#" + role + "-key", Input).value = ""
            self.query_one("#" + role + "-model", Input).value = ""
            self.query_one("#" + role + "-key-status", Static).update(
                "Key available" if resolve(env) else "No key detected"
            )

    def provider(self, role, include_key=False):
        prefix = "#" + role + "-"
        kind = self.query_one(prefix + "kind", Select).value
        current = self.initial[role][1]
        base = current if kind == current.kind else ProviderConfig(kind=kind)
        env = self.query_one(prefix + "env", Input).value.strip() or None
        key = self.query_one(prefix + "key", Input).value
        if include_key and key:
            env = remember(key)
        bound = self.query_one(prefix + "bound", Input).value.strip()
        return ProviderConfig.model_validate(
            {
                **base.model_dump(),
                "kind": kind,
                "api_key_env": env,
                "base_url": self.query_one(prefix + "url", Input).value.strip() or None,
                "request_cost_bound_usd": float(bound) if bound else None,
            }
        )

    def on_button_pressed(self, event):
        identifier = event.button.id
        if identifier == "cancel-settings":
            self.dismiss(None)
        elif identifier == "forget-keys":
            forget()
            if self.app.session:
                self.app.session.client.providers.clear()
            for role in ["navigator", "worker"]:
                self.query_one("#" + role + "-key", Input).value = ""
                self.query_one("#" + role + "-key-status", Static).update(
                    "Pasted keys forgotten (environment keys are unchanged)"
                )
        elif identifier.endswith("-browse"):
            role = identifier.split("-")[0]
            try:
                provider = self.provider(role, include_key=True)
                Config(providers={"preview": provider})

                def selected(model):
                    if model:
                        self.query_one("#" + role + "-model", Input).value = model.id
                        self.prices[role] = model

                self.app.push_screen(ModelPicker(provider), selected)
            except Exception:
                self.query_one("#settings-error", Static).update(
                    "Invalid endpoint or request bound; use HTTPS for remote endpoints"
                )
        elif identifier == "save-settings":
            try:
                providers, roles = dict(self.config.providers), dict(self.config.roles)
                shared = self.query_one("#shared-model", Checkbox).value
                selected_roles = ["navigator"] if shared else ["navigator", "worker"]
                for role in selected_roles:
                    name = self.initial[role][0]
                    if role == "worker" and name == self.initial["navigator"][0]:
                        name += "_worker"
                    provider = self.provider(role, include_key=True)
                    model = self.query_one("#" + role + "-model", Input).value.strip()
                    if not model:
                        raise ValueError("Enter a model ID for " + role)
                    if provider.kind in {"openrouter", "openai_api"} and not resolve(provider.api_key_env):
                        raise ValueError("Paste a key or set the environment variable for " + role)
                    if provider.request_cost_bound_usd is None and provider.kind != "fake":
                        from mlca.llm.pricing import estimate

                        metadata = self.prices.get(role)
                        models, _ = cached(provider)
                        metadata = (
                            metadata
                            if metadata and metadata.id == model
                            else next((m for m in models if m.id == model), None)
                        )
                        if (
                            metadata
                            and metadata.input_per_million is not None
                            and metadata.output_per_million is not None
                        ):
                            self.prices[role] = metadata
                        elif estimate(name, model, 1000, 1000) is None:
                            raise ValueError("Set a maximum USD per request; pricing is unknown for " + model)
                    providers[name] = provider
                    previous = self.initial[role][2]
                    roles[role] = RoleConfig.model_validate(
                        {**(previous.model_dump() if previous else {}), "provider": name, "model": model}
                    )
                if shared:
                    old = roles.get("worker")
                    roles["worker"] = RoleConfig.model_validate(
                        {
                            **(old.model_dump() if old else {}),
                            "provider": roles["navigator"].provider,
                            "model": roles["navigator"].model,
                        }
                    )
                data = self.config.model_dump()
                data.update(
                    providers={k: p.model_dump() for k, p in providers.items()},
                    roles={k: r.model_dump() for k, r in roles.items()},
                )
                data["budgets"].update(
                    turn_max_usd=float(self.query_one("#turn-budget", Input).value),
                    session_max_usd=float(self.query_one("#session-budget", Input).value),
                )
                data["sandbox"]["allow_level_b"] = self.query_one("#allow-b", Checkbox).value
                config = Config.model_validate(data)
                for role, model in self.prices.items():
                    if role in selected_roles and roles[role].model == model.id:
                        save_prices(roles[role].provider, [model])
                self.dismiss({"config": config.model_dump()})
            except Exception as exc:
                from mlca.config import redact

                self.query_one("#settings-error", Static).update(redact(str(exc)))
