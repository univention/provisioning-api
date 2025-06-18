from pathlib import Path

import pytest


base_dir = (Path(__file__).parent / "../../../").resolve()


@pytest.fixture
def helm_default_values(request):
    default_values = [
        base_dir / "helm/udm-listener/linter_values.yaml",
    ]
    return default_values


@pytest.fixture
def chart_default_path():
    chart_path = base_dir / "helm/udm-listener"
    return chart_path
