import pytest

pytest_plugins = []


def pytest_collection_modifyitems(config, items):
    """Auto-mark all async tests with asyncio marker."""
    for item in items:
        if hasattr(item, "obj") and hasattr(item.obj, "__code__"):
            import inspect
            if inspect.iscoroutinefunction(item.obj):
                item.add_marker(pytest.mark.asyncio)
