from whitenoise.storage import CompressedManifestStaticFilesStorage as BaseStorage

class ManifestStaticFilesStorage(BaseStorage):
    manifest_strict = False
