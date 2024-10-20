#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


import subprocess
import sys
from pathlib import Path
from typing import List


def main():
    changed_files = sys.argv[1:]
    charts = get_changed_charts(changed_files)

    if not charts:
        print("No chart changes detected.")
        sys.exit(0)

    results = [lint_chart(chart) for chart in charts]
    if not all(results):
        sys.exit(1)


def lint_chart(chart: Path) -> bool:
    print(f"\nRunning kyverno test in {chart}")
    template_result = subprocess.run(
        [
            "helm",
            "template",
            chart.as_posix(),
            "--values",
            (chart / "linter_values.yaml").as_posix(),
            "--values",
            (chart / ".kyverno/values-kyverno.yaml").as_posix(),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if template_result.returncode != 0:
        print("Failed to render helm template for chart: {chart}")
        print(template_result.stderr)
        return False
    with (chart / ".kyverno/manifest.yaml").open("w") as manifest_file:
        manifest_file.write(template_result.stdout)
        # manifest_file.write(template_result.stdout.decode("utf-8").replace('\r', ''))

    kyverno_result = subprocess.run(
        ["kyverno", "test", "--detailed-results", (chart / ".kyverno/").as_posix()],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if kyverno_result.returncode != 0:
        print(f"Kyverno test failed in {chart}")
        print(kyverno_result.stdout.decode("utf-8").split("Test Summary: ")[1])
        return False
    return True


def get_changed_charts(changed_files: List[str]):
    charts = set()
    for file in changed_files:
        file_path = Path(file)
        if len(file_path.parts) < 2:
            continue

        chart_dir = Path(file_path.parts[0]) / file_path.parts[1]
        if chart_dir.is_dir():
            charts.add(chart_dir)
    return charts


if __name__ == "__main__":
    main()
