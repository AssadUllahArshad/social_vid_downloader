from . import facebook, instagram, snapchat, tiktok, whatsapp, youtube

providers = {module.provider.name: module.provider for module in [youtube, instagram, facebook, tiktok, snapchat, whatsapp]}
