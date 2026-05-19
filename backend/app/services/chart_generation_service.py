from __future__ import annotations

from typing import Any


class ChartGenerationService:
    def generate_chart_payload(
        self,
        chart_type: str,
        title: str,
        data: list[dict[str, Any]],
        x_key: str,
        y_key: str,
        description: str = "",
    ) -> dict[str, Any]:
        return {
            "type": chart_type,
            "chart_type": chart_type,
            "title": title,
            "description": description,
            "x_key": x_key,
            "y_key": y_key,
            "data": data,
        }

    def generate_table_payload(self, title: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
        columns = list(rows[0].keys()) if rows else []
        return {"title": title, "columns": columns, "rows": [[row.get(column) for column in columns] for row in rows]}

    def kpi_cards(self, kpis: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "kpi_cards",
            "title": "KPIs dinámicos",
            "data": [{"label": key, "value": value} for key, value in kpis.items()],
        }
