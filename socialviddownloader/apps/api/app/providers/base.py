from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Capabilities:
    supportsPublicUrl: bool = False
    supportsStories: bool = False
    supportsSpotlight: bool = False
    supportsAuthentication: bool = False
    enabled: bool = False


class Provider:
    def __init__(self, name: str, enabled=False):
        self.name = name
        self.capabilities = Capabilities(supportsPublicUrl=enabled, enabled=enabled)

    def public_status(self):
        return {"platform": self.name, **asdict(self.capabilities)}

    def extract(self, url: str):
        from ..media_errors import MediaError, platform_name
        from ..runner import isolated_extract

        if not self.capabilities.enabled:
            raise MediaError("provider_disabled", f"This {platform_name(self.name)} content type is not currently supported.", 501)
        return isolated_extract(url, self.name)
