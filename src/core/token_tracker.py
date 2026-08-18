# MIT License
# Copyright (c) 2026 Manes2008/didicrew
#
# Module: token_tracker.py
# Muc dich: Do luong va luu log token, thoi gian, chi phi cho tung AI request
#            trong quy trinh san xuat video VideoCrew.

import time
import datetime
from typing import Optional

# ─── BANG GIA USD PER 1_000 TOKENS ────────────────────────────────────────────
PRICING_TABLE = {
    # OpenAI
    "gpt-4o-mini":           {"input": 0.00015,  "output": 0.00060},
    "gpt-4o":                {"input": 0.00250,  "output": 0.01000},
    "gpt-4o-2024-11-20":     {"input": 0.00250,  "output": 0.01000},
    "gpt-4o-2024-08-06":     {"input": 0.00250,  "output": 0.01000},
    "gpt-3.5-turbo":         {"input": 0.00050,  "output": 0.00150},
    # Google Gemini
    "gemini-1.5-flash":      {"input": 0.000075, "output": 0.000300},
    "gemini-1.5-flash-8b":   {"input": 0.000038, "output": 0.000150},
    "gemini-1.5-pro":        {"input": 0.001250, "output": 0.005000},
    "gemini-2.0-flash":      {"input": 0.000100, "output": 0.000400},
    "gemini-2.0-flash-lite": {"input": 0.000075, "output": 0.000300},
    "gemini-2.5-flash":      {"input": 0.000150, "output": 0.000600},
    "gemini-2.5-pro":        {"input": 0.001250, "output": 0.010000},
}

# Chi phi DALL-E theo so luong anh (USD/image) - khong tinh theo token
DALLE_PRICING = {
    "dall-e-3-standard-1024": 0.040,   # $0.04/anh 1024x1024 standard
    "dall-e-3-hd-1024":       0.080,   # $0.08/anh 1024x1024 HD
    "dall-e-2-1024":          0.020,
}
DALLE_DEFAULT_COST_PER_IMAGE = 0.040

# ─── ESTIMATE TOKENS ──────────────────────────────────────────────────────────

def estimate_tokens(text: str, model_name: str = "gpt-4o-mini") -> int:
    """
    Uoc tinh so luong token tu van ban.
    - OpenAI models: dung tiktoken neu co, fallback len(text)//4
    - Gemini models: fallback len(text)//4 (xap xi 1 token ~ 4 chars)
    """
    if not text:
        return 0
    try:
        import tiktoken
        # tiktoken ho tro tat ca gpt models
        if "gpt" in model_name or "o1" in model_name:
            try:
                enc = tiktoken.encoding_for_model(model_name)
            except KeyError:
                enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
    except ImportError:
        pass
    # Fallback: uoc tinh don gian (1 token ~ 4 chars, phu hop ca tieng Viet)
    return max(1, len(text) // 4)


# ─── TINH CHI PHI ─────────────────────────────────────────────────────────────

def calculate_cost(input_tokens: int, output_tokens: int, model_name: str) -> float:
    """Tinh chi phi USD dua tren pricing table."""
    pricing = PRICING_TABLE.get(model_name)
    if not pricing:
        # Tim model gan nhat (prefix matching)
        for key in PRICING_TABLE:
            if model_name.startswith(key) or key.startswith(model_name.split("-")[0]):
                pricing = PRICING_TABLE[key]
                break
    if not pricing:
        # Fallback: dung gia gpt-4o-mini
        pricing = PRICING_TABLE["gpt-4o-mini"]
    cost = (input_tokens / 1000.0) * pricing["input"] + (output_tokens / 1000.0) * pricing["output"]
    return round(cost, 8)


# ─── LUU LOG VÀO DB ──────────────────────────────────────────────────────────

def _save_log(
    project_id: int,
    stage_name: str,
    sub_step_name: str,
    model_name: str,
    provider: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    elapsed_seconds: float,
):
    """Luu 1 ban ghi RequestCostLog vao DB, khong raise exception ra ngoai."""
    try:
        from src.core.models import get_db_session, RequestCostLog
        db = get_db_session()
        try:
            log = RequestCostLog(
                project_id=int(project_id),
                stage_name=stage_name,
                sub_step_name=sub_step_name,
                model_name=model_name,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost_usd=cost_usd,
                elapsed_seconds=elapsed_seconds,
            )
            db.add(log)
            db.commit()
        except Exception as ex_db:
            db.rollback()
            print(f"[WARN] TokenTracker: Khong the luu DB: {ex_db}")
        finally:
            db.close()
    except Exception as ex_import:
        print(f"[WARN] TokenTracker: Loi import: {ex_import}")


# ─── TRACK LLM.CALL() ─────────────────────────────────────────────────────────

def track_llm_call(
    llm,
    messages: list,
    sub_step_name: str,
    stage_name: str,
    project_id: Optional[int],
    model_name: str,
    provider: str = "",
) -> tuple:
    """
    Wrapper cho llm.call(messages=...) voi tracking token va thoi gian.

    Returns:
        (response_text: str, stats: dict)
        stats = {input_tokens, output_tokens, cost_usd, elapsed_seconds}
    """
    # Gom toan bo noi dung message de uoc tinh input tokens
    input_text = " ".join(m.get("content", "") for m in messages if isinstance(m, dict))
    input_tokens = estimate_tokens(input_text, model_name)

    t_start = time.monotonic()
    response_text = llm.call(messages=messages)
    elapsed = round(time.monotonic() - t_start, 3)

    output_tokens = estimate_tokens(str(response_text), model_name)
    cost = calculate_cost(input_tokens, output_tokens, model_name)

    stats = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost,
        "elapsed_seconds": elapsed,
    }

    if project_id:
        _save_log(
            project_id=project_id,
            stage_name=stage_name,
            sub_step_name=sub_step_name,
            model_name=model_name,
            provider=provider or ("openai" if "gpt" in model_name else "gemini"),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            elapsed_seconds=elapsed,
        )

    print(
        f"[TRACKER] {stage_name}/{sub_step_name} | "
        f"in={input_tokens} out={output_tokens} tokens | "
        f"cost=${cost:.6f} | time={elapsed}s"
    )
    return response_text, stats


# ─── TRACK CREW.KICKOFF() ─────────────────────────────────────────────────────

def track_crew_kickoff(
    crew,
    sub_step_name: str,
    stage_name: str,
    project_id: Optional[int],
    model_name: str,
    provider: str = "",
):
    """
    Wrapper cho crew.kickoff() voi tracking token va thoi gian.
    Su dung crew_output.token_usage (CrewAI built-in).

    Returns:
        (crew_output, stats: dict)
    """
    t_start = time.monotonic()
    crew_output = crew.kickoff()
    elapsed = round(time.monotonic() - t_start, 3)

    # Doc token_usage tu CrewAI CrewOutput
    input_tokens = 0
    output_tokens = 0
    try:
        usage = crew_output.token_usage
        if usage:
            # CrewAI UsageMetrics co: prompt_tokens, completion_tokens, total_tokens
            if hasattr(usage, "prompt_tokens"):
                input_tokens = int(usage.prompt_tokens or 0)
                output_tokens = int(usage.completion_tokens or 0)
            elif isinstance(usage, dict):
                input_tokens = int(usage.get("prompt_tokens", 0))
                output_tokens = int(usage.get("completion_tokens", 0))
    except Exception:
        pass

    # Fallback: uoc tinh tu output string
    if input_tokens == 0 and output_tokens == 0:
        output_text = str(crew_output)
        output_tokens = estimate_tokens(output_text, model_name)
        input_tokens = output_tokens  # uoc tinh xap xi

    cost = calculate_cost(input_tokens, output_tokens, model_name)

    stats = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost,
        "elapsed_seconds": elapsed,
    }

    if project_id:
        _save_log(
            project_id=project_id,
            stage_name=stage_name,
            sub_step_name=sub_step_name,
            model_name=model_name,
            provider=provider or ("openai" if "gpt" in model_name else "gemini"),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            elapsed_seconds=elapsed,
        )

    print(
        f"[TRACKER] {stage_name}/{sub_step_name} | "
        f"in={input_tokens} out={output_tokens} tokens | "
        f"cost=${cost:.6f} | time={elapsed}s"
    )
    return crew_output, stats


# ─── TRACK DALL-E IMAGE GENERATION ───────────────────────────────────────────

def track_dalle_generation(
    num_images: int,
    project_id: Optional[int],
    stage_name: str = "image",
    sub_step_name: str = "dalle_generate",
    model_name: str = "dall-e-3",
    elapsed_seconds: float = 0.0,
):
    """
    Ghi log chi phi DALL-E theo so luong anh (khong tinh theo token).
    Cost: $0.04/anh standard 1024x1024.
    """
    cost = num_images * DALLE_DEFAULT_COST_PER_IMAGE

    stats = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": cost,
        "elapsed_seconds": elapsed_seconds,
        "note": f"{num_images} images x ${DALLE_DEFAULT_COST_PER_IMAGE}/image",
    }

    if project_id:
        _save_log(
            project_id=project_id,
            stage_name=stage_name,
            sub_step_name=sub_step_name,
            model_name=model_name,
            provider="openai",
            input_tokens=0,
            output_tokens=num_images,   # dung output_tokens de luu so luong anh
            cost_usd=cost,
            elapsed_seconds=elapsed_seconds,
        )

    print(f"[TRACKER] {stage_name}/{sub_step_name} | {num_images} anh DALL-E | cost=${cost:.4f} | time={elapsed_seconds}s")
    return stats


# ─── TRACK VIDEO RENDER (local, no LLM cost) ─────────────────────────────────

def track_video_render(
    project_id: Optional[int],
    engine_name: str,
    elapsed_seconds: float,
    stage_name: str = "video",
    sub_step_name: str = "video_render",
):
    """Ghi log thoi gian render video local (khong co LLM cost)."""
    stats = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "elapsed_seconds": elapsed_seconds,
    }
    if project_id:
        _save_log(
            project_id=project_id,
            stage_name=stage_name,
            sub_step_name=f"{sub_step_name}_{engine_name}",
            model_name=engine_name,
            provider="local",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            elapsed_seconds=elapsed_seconds,
        )
    print(f"[TRACKER] video/render | engine={engine_name} | time={elapsed_seconds}s")
    return stats


# ─── QUERY SUMMARY ────────────────────────────────────────────────────────────

def get_stage_summary(project_id: int, stage_name: str) -> list:
    """
    Tra ve danh sach cac request da ghi cho (project_id, stage_name),
    sap xep theo thu tu thoi gian.
    Returns: list of dict
    """
    try:
        from src.core.models import get_db_session, RequestCostLog
        db = get_db_session()
        try:
            rows = (
                db.query(RequestCostLog)
                .filter_by(project_id=int(project_id), stage_name=stage_name)
                .order_by(RequestCostLog.created_at.asc())
                .all()
            )
            return [
                {
                    "sub_step_name": r.sub_step_name,
                    "model_name": r.model_name,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "total_tokens": r.total_tokens,
                    "cost_usd": r.cost_usd,
                    "elapsed_seconds": r.elapsed_seconds,
                    "created_at": r.created_at,
                }
                for r in rows
            ]
        finally:
            db.close()
    except Exception as ex:
        print(f"[WARN] TokenTracker.get_stage_summary: {ex}")
        return []


def get_project_summary(project_id: int) -> dict:
    """
    Tra ve dict tong hop chi phi va token toan du an theo tung stage.
    Returns: {
        "stages": {stage_name: {total_tokens, cost_usd, elapsed_seconds, requests_count}},
        "grand_total": {total_tokens, cost_usd, elapsed_seconds}
    }
    """
    try:
        from src.core.models import get_db_session, RequestCostLog
        from sqlalchemy import func as sa_func
        db = get_db_session()
        try:
            rows = db.query(RequestCostLog).filter_by(project_id=int(project_id)).all()
            stages = {}
            for r in rows:
                sn = r.stage_name
                if sn not in stages:
                    stages[sn] = {"total_tokens": 0, "cost_usd": 0.0, "elapsed_seconds": 0.0, "requests_count": 0}
                stages[sn]["total_tokens"] += (r.total_tokens or 0)
                stages[sn]["cost_usd"] += (r.cost_usd or 0.0)
                stages[sn]["elapsed_seconds"] += (r.elapsed_seconds or 0.0)
                stages[sn]["requests_count"] += 1
            grand = {
                "total_tokens": sum(s["total_tokens"] for s in stages.values()),
                "cost_usd": sum(s["cost_usd"] for s in stages.values()),
                "elapsed_seconds": sum(s["elapsed_seconds"] for s in stages.values()),
            }
            return {"stages": stages, "grand_total": grand}
        finally:
            db.close()
    except Exception as ex:
        print(f"[WARN] TokenTracker.get_project_summary: {ex}")
        return {"stages": {}, "grand_total": {"total_tokens": 0, "cost_usd": 0.0, "elapsed_seconds": 0.0}}


def get_all_projects_summary(limit: int = 50) -> list:
    """
    Tra ve tong hop chi phi cua tat ca cac du an (dung cho trang Cau hinh AI).
    Returns: list of dict {project_id, total_tokens, cost_usd, elapsed_seconds, requests_count}
    """
    try:
        from src.core.models import get_db_session, RequestCostLog
        db = get_db_session()
        try:
            rows = db.query(RequestCostLog).order_by(RequestCostLog.project_id).all()
            projects = {}
            for r in rows:
                pid = r.project_id
                if pid not in projects:
                    projects[pid] = {
                        "project_id": pid,
                        "total_tokens": 0,
                        "cost_usd": 0.0,
                        "elapsed_seconds": 0.0,
                        "requests_count": 0,
                    }
                projects[pid]["total_tokens"] += (r.total_tokens or 0)
                projects[pid]["cost_usd"] += (r.cost_usd or 0.0)
                projects[pid]["elapsed_seconds"] += (r.elapsed_seconds or 0.0)
                projects[pid]["requests_count"] += 1
            return sorted(projects.values(), key=lambda x: x["project_id"], reverse=True)[:limit]
        finally:
            db.close()
    except Exception as ex:
        print(f"[WARN] TokenTracker.get_all_projects_summary: {ex}")
        return []
