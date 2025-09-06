import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except Exception:  # pragma: no cover
    requests = None


CANONICAL_FIELDS = [
    "bill_of_lading_number",
    "container_number",
    "consignee_name",
    "consignee_address",
    "date",
    "line_items_count",
    "average_gross_weight",
    "average_price",
]

ALIAS_MAP = {
    "bill of lading number": "bill_of_lading_number",
    "bol_number": "bill_of_lading_number",
    "bol": "bill_of_lading_number",
    "container": "container_number",
    "container no": "container_number",
    "consignee": "consignee_name",
    "consignee name": "consignee_name",
    "consignee address": "consignee_address",
    "shipment_date": "date",
    "shipping_date": "date",
    "date": "date",
    "line items count": "line_items_count",
    "items_count": "line_items_count",
    "avg gross weight": "average_gross_weight",
    "average gross weight": "average_gross_weight",
    "avg price": "average_price",
    "average price": "average_price",
}


def normalize_key(key: str) -> str:
    if not key:
        return key
    k = key.strip().lower()
    k = re.sub(r"[^a-z0-9_ ]+", "", k)
    k = k.replace(" ", "_")
    return ALIAS_MAP.get(k, k)


def try_parse_float(val: Any) -> Tuple[bool, float]:
    try:
        if isinstance(val, (int, float)):
            return True, float(val)
        s = str(val)
        s = s.replace(",", "")
        m = re.search(r"[-+]?\d*\.?\d+", s)
        if not m:
            return False, math.nan
        return True, float(m.group(0))
    except Exception:
        return False, math.nan


def try_normalize_date(val: Any) -> Tuple[bool, str]:
    from datetime import datetime
    if not val:
        return False, ""
    s = str(val).strip()
    fmts = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%B %d, %Y",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            return True, dt.strftime("%Y-%m-%d")
        except Exception:
            pass
    m = re.search(r"\b(\d{4})(\d{2})(\d{2})\b", s)
    if m:
        try:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return True, dt.strftime("%Y-%m-%d")
        except Exception:
            pass
    return False, s.lower()


def normalize_str(val: Any, keep_case: bool = False) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    s = re.sub(r"\s+", " ", s)
    if not keep_case:
        s = s.lower()
    s = re.sub(r"[\t\n\r]+", " ", s)
    s = re.sub(r"[^a-zA-Z0-9 \-/]", "", s)
    return s.strip()


def normalize_value(key: str, value: Any) -> Tuple[str, Any]:
    k = normalize_key(key)
    if k in {"line_items_count"}:
        ok, f = try_parse_float(value)
        return k, int(round(f)) if ok and not math.isnan(f) else None
    if k in {"average_gross_weight", "average_price"}:
        ok, f = try_parse_float(value)
        return k, f if ok else None
    if k == "date":
        ok, d = try_normalize_date(value)
        return k, d if ok else normalize_str(value)
    if k in {"bill_of_lading_number", "container_number"}:
        return k, normalize_str(value, keep_case=True).upper()
    return k, normalize_str(value)


def extract_canonical_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = payload.get("extracted_data", payload)
    out: Dict[str, Any] = {}
    if isinstance(data, dict):
        for raw_k, v in data.items():
            k = normalize_key(raw_k)
            if k in CANONICAL_FIELDS:
                _, nv = normalize_value(k, v)
                out[k] = nv
    if not out and isinstance(data, str):
        try:
            inner = json.loads(data)
            return extract_canonical_fields(inner)
        except Exception:
            pass
    return out


def compare_fields(expected: Dict[str, Any], actual: Dict[str, Any], *,
                   rel_tol: float = 0.01, abs_tol: float = 0.01) -> Tuple[int, int, int, int]:
    correct = 0
    total_gold = 0
    fp = 0
    fn = 0
    for f in CANONICAL_FIELDS:
        if f not in expected:
            continue
        total_gold += 1
        ev = expected.get(f)
        av_present = f in actual and actual.get(f) is not None
        av = actual.get(f)

        is_num = f in {"line_items_count", "average_gross_weight", "average_price"}
        if is_num and ev is not None and av_present:
            ok_ev, evf = try_parse_float(ev)
            ok_av, avf = try_parse_float(av)
            if ok_ev and ok_av and math.isclose(evf, avf, rel_tol=rel_tol, abs_tol=abs_tol):
                correct += 1
            else:
                fp += 1 if av_present else 0
                fn += 1
            continue

        _, nev = normalize_value(f, ev)
        _, nav = normalize_value(f, av)
        if av_present and nev == nav:
            correct += 1
        else:
            fp += 1 if av_present else 0
            fn += 1

    for f in actual.keys():
        if f not in CANONICAL_FIELDS:
            continue
        if f not in expected or expected.get(f) is None:
            fp += 1

    return correct, total_gold, fp, fn


def evaluate_results(expected_data: Dict[str, Any], actual_data: Dict[str, Any], *,
                     rel_tol: float = 0.01, abs_tol: float = 0.01) -> Dict[str, Any]:
    exp = extract_canonical_fields(expected_data)
    act = extract_canonical_fields(actual_data)

    correct, total, fp, fn = compare_fields(exp, act, rel_tol=rel_tol, abs_tol=abs_tol)
    precision = correct / (correct + fp) if (correct + fp) > 0 else 0.0
    recall = correct / (correct + fn) if (correct + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = correct / total if total > 0 else 0.0

    per_field = {}
    for f in CANONICAL_FIELDS:
        if f not in exp:
            continue
        _, nev = normalize_value(f, exp.get(f))
        _, nav = normalize_value(f, act.get(f))
        if f in {"line_items_count", "average_gross_weight", "average_price"}:
            ok_ev, evf = try_parse_float(exp.get(f))
            ok_av, avf = try_parse_float(act.get(f))
            per_field[f] = bool(ok_ev and ok_av and math.isclose(evf, avf, rel_tol=rel_tol, abs_tol=abs_tol))
        else:
            per_field[f] = (nev == nav)

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "correct": int(correct),
        "total": int(total),
        "fp": int(fp),
        "fn": int(fn),
        "per_field": per_field,
        "evaluated_fields": [f for f in CANONICAL_FIELDS if f in exp],
    }


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def call_api(files_dir: Path, api_url: str) -> Dict[str, Any]:
    if requests is None:
        raise RuntimeError("The 'requests' package is required to call the API.")
    endpoint = api_url.rstrip("/") + "/process-documents"
    file_tuples = []
    for fp in sorted(files_dir.iterdir()):
        if not fp.is_file():
            continue
        # Basic content-type guess; FastAPI doesn't strictly require it
        ctype = "application/pdf" if fp.suffix.lower() == ".pdf" else "application/octet-stream"
        file_tuples.append(("files", (fp.name, fp.open("rb"), ctype)))
    if not file_tuples:
        raise FileNotFoundError(f"No files found in {files_dir}")
    resp = requests.post(endpoint, files=file_tuples, timeout=60)
    resp.raise_for_status()
    return resp.json()


@dataclass
class EvalCase:
    name: str
    path: Path
    files_dir: Path
    ground_truth_path: Path
    predictions_path: Optional[Path] = None


def discover_eval_cases(base: Path) -> List[EvalCase]:
    cases: List[EvalCase] = []
    for d in base.iterdir():
        if not d.is_dir() or not d.name.startswith("eval_"):
            continue
        files_dir = d / "files"
        gt_path = d / "ground_truth.json"
        pred_path = d / "predictions.json"
        if not gt_path.exists():
            print(f"Skipping {d.name}: missing ground_truth.json", file=sys.stderr)
            continue
        cases.append(EvalCase(
            name=d.name,
            path=d,
            files_dir=files_dir,
            ground_truth_path=gt_path,
            predictions_path=pred_path if pred_path.exists() else None,
        ))
    return sorted(cases, key=lambda c: c.name)


def aggregate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not results:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "cases": 0}
    total_correct = sum(r.get("correct", 0) for r in results)
    total = sum(r.get("total", 0) for r in results)
    total_fp = sum(r.get("fp", 0) for r in results)
    total_fn = sum(r.get("fn", 0) for r in results)
    precision = total_correct / (total_correct + total_fp) if (total_correct + total_fp) > 0 else 0.0
    recall = total_correct / (total_correct + total_fn) if (total_correct + total_fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = total_correct / total if total > 0 else 0.0
    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "cases": len(results),
    }


def run_case(case: EvalCase, *, api_url: Optional[str], rel_tol: float, abs_tol: float,
             save_predictions: bool) -> Dict[str, Any]:
    gt = load_json(case.ground_truth_path)

    # Prefer API if provided and files exist; otherwise use predictions.json if present
    predictions_payload: Optional[Dict[str, Any]] = None
    used_source = None

    if api_url and case.files_dir.exists():
        predictions_payload = call_api(case.files_dir, api_url)
        used_source = f"api:{api_url}"
        if save_predictions:
            out_path = case.path / "predictions.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(predictions_payload, f, indent=2, ensure_ascii=False)
    elif case.predictions_path and case.predictions_path.exists():
        predictions_payload = load_json(case.predictions_path)
        used_source = case.predictions_path.name
    else:
        raise FileNotFoundError(
            f"No predictions available for {case.name}. Provide --api and add files/ or create predictions.json."
        )

    metrics = evaluate_results(gt, predictions_payload, rel_tol=rel_tol, abs_tol=abs_tol)
    metrics.update({"case": case.name, "source": used_source})
    return metrics


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run evaluations against ground truth using files->API or predictions.json")
    sub = parser.add_subparsers(dest="cmd", required=False)

    run_p = sub.add_parser("run", help="Run a specific eval case (eval_<name>)")
    run_p.add_argument("name", help="Eval directory name or suffix; e.g., 'sample_basic' or 'eval_sample_basic'")
    run_p.add_argument("--api", default='http://0.0.0.0:8000', help="Base API URL (e.g., http://localhost:8000)")
    run_p.add_argument("--rel-tol", type=float, default=0.01)
    run_p.add_argument("--abs-tol", type=float, default=0.01)
    run_p.add_argument("--no-save-predictions", action="store_true", help="Do not persist predictions.json")
    run_p.add_argument("--out", type=Path, default=None, help="Optional summary output path for this run")

    all_p = sub.add_parser("run-all", help="Discover and run all eval_* cases under eval/")
    all_p.add_argument("--api", default='http://0.0.0.0:8000', help="Base API URL (e.g., http://localhost:8000)")
    all_p.add_argument("--rel-tol", type=float, default=0.01)
    all_p.add_argument("--abs-tol", type=float, default=0.01)
    all_p.add_argument("--no-save-predictions", action="store_true")
    all_p.add_argument("--out", type=Path, default=None, help="Optional summary output path for the aggregate run")

    args = parser.parse_args(argv)

    base = Path(__file__).parent

    if args.cmd == "run":
        # Resolve a case name
        target_name = args.name if args.name.startswith("eval_") else f"eval_{args.name}"
        case_dir = base / target_name
        if not case_dir.exists():
            print(f"Eval case not found: {target_name}", file=sys.stderr)
            sys.exit(2)
        cases = [EvalCase(
            name=target_name,
            path=case_dir,
            files_dir=case_dir / "files",
            ground_truth_path=case_dir / "ground_truth.json",
            predictions_path=(case_dir / "predictions.json" if (case_dir / "predictions.json").exists() else None),
        )]
    else:
        cases = discover_eval_cases(base)

    if not cases:
        print("No eval cases found.", file=sys.stderr)
        sys.exit(1)

    results: List[Dict[str, Any]] = []
    for case in cases:
        try:
            r = run_case(case, api_url=getattr(args, "api", None), rel_tol=args.rel_tol, abs_tol=args.abs_tol,
                         save_predictions=not getattr(args, "no_save_predictions", False))
            results.append(r)
        except Exception as e:
            print(f"Error running {case.name}: {e}", file=sys.stderr)

    summary = aggregate_metrics(results)
    report = {"summary": summary, "cases": results}
    print(json.dumps(report, indent=2, ensure_ascii=False))

    out_path: Optional[Path] = getattr(args, "out", None)
    if out_path:
        # Ensure relative paths are written under eval/ directory
        if not out_path.is_absolute():
            out_path = base / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
