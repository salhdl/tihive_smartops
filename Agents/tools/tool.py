from __future__ import annotations
import os
from typing import Dict, Any, List, Optional

from __future__ import annotations
from typing import Any, Dict, Iterable
from pathlib import Path
import os
import yaml

class YamlRulesTool:
    """Reads YAML rule/target files from kb/, rules/ or a direct path and returns a dict."""
    name = "YamlRulesTool"
    description = ("Reads YAML rule files (quality_rules.yaml, process_rules.yaml, "
                   "maintenance_rules.yaml, eco_targets.yaml).")

    def __init__(self, search_dirs: Iterable[Path] | None = None) -> None:
        # Priorité: RULES_DIR (env), kb/, rules/, cwd
        env_dir = os.getenv("RULES_DIR")
        default_dirs = [
            Path(env_dir) if env_dir else None,
            Path("kb"),
            Path("rules"),
            Path("."),
        ]
        self.search_dirs = [d for d in default_dirs if d is not None]
        if search_dirs:
            self.search_dirs = list(search_dirs) + self.search_dirs

    def read(self, filename: str) -> Dict[str, Any]:
        p = Path(filename)
        candidates = [p] if p.is_absolute() else [d / filename for d in self.search_dirs] + [p]

        for path in candidates:
            if path.exists() and path.is_file():
                with path.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                # Validation ultra-légère (facultatif ; adapte selon l’agent)
                if not isinstance(data, dict):
                    raise ValueError(f"YAML must be a mapping (got {type(data)}): {path}")
                return data

        # Si tu préfères le comportement silencieux, remplace par: return {}
        raise FileNotFoundError(
            f"Rules file not found. Looked in: "
            + ", ".join(str(c) for c in candidates)
        )

class DeviationTool:
    """Returns human‑readable deviation against [min,max] thresholds."""
    name = "DeviationTool"
    description = "Computes deviation label against tolerance bounds."

    def describe(self, measured: float, min_val: Optional[float], max_val: Optional[float], unit: str = "") -> str:
        if min_val is None and max_val is None:
            return f"{measured}{unit} (no reference)"
        if min_val is not None and measured < min_val:
            delta = round(min_val - measured, 4)
            return f"{measured}{unit} (−{delta}{unit} below range)"
        if max_val is not None and measured > max_val:
            delta = round(measured - max_val, 4)
            return f"{measured}{unit} (+{delta}{unit} above range)"
        return f"{measured}{unit} (within range)"

class TrendAnalysisTool:
    """Simple trend detector for a numeric column in a pandas DataFrame."""
    name = "TrendAnalysisTool"
    description = "Detects upward/downward trend on a numeric column."

    def trend_label(self, df, column: str, min_abs_slope: float = 1e-6) -> str:
        import numpy as np
        if df is None or column not in df or df.shape[0] < 2:
            return f"No trend (insufficient data for {column})"
        y = df[column].astype(float).values
        x = np.arange(len(y))
        slope = np.polyfit(x, y, 1)[0]
        if slope > min_abs_slope:
            return f"Upward trend in {column}"
        elif slope < -min_abs_slope:
            return f"Downward trend in {column}"
        return f"No significant trend in {column}"

class AnomalyTool:
    """Z‑score outlier detector for a numeric column in a pandas DataFrame."""
    name = "AnomalyTool"
    description = "Flags z‑score outliers (|z| >= threshold)."

    def outliers(self, df, column: str, z_threshold: float = 3.0) -> List[Dict[str, Any]]:
        if df is None or column not in df or df.shape[0] == 0:
            return []
        series = df[column].astype(float)
        mean = series.mean()
        std = series.std(ddof=0)
        if not std or std != std:
            return []
        zscores = (series - mean) / std
        mask = zscores.abs() >= z_threshold
        if not mask.any():
            return []
        result: List[Dict[str, Any]] = []
        for idx in series[mask].index.tolist():
            result.append({
                "index": int(idx) if isinstance(idx, int) else str(idx),
                column: float(series.loc[idx]),
                "z": float(zscores.loc[idx])
            })
        return result

