class LedgerEntryFactory:
    _creators = {}

    @classmethod
    def register(cls, entry_type: str):
        def decorator(creator_fn):
            cls._creators[entry_type] = creator_fn
            return creator_fn
        return decorator

    @classmethod
    def create(cls, dto):
        entry_type = dto.type

        if entry_type not in cls._creators:
            raise ValueError(f"Unknown LedgerEntry type: {entry_type}")

        return cls._creators[entry_type](dto)