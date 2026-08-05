# backup_restore.py
import base64
import io
import json
import os
import zipfile
from datetime import datetime, date
from pathlib import Path

BACKUP_VERSION = "1.0"

TABLE_ORDER = [
    "users", "allowed_ips", "channels", "channel_stage_configs",
    "projects", "video_duration_configs", "project_stages", "media_files",
    "prompt_optimization_logs", "video_analysis_logs", "system_configs",
]
LOCAL_DIRS = ["generated_images", "generated_audios", "generated_voices", "generated_videos", "exports"]


def _serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return {"__type__": "bytes", "data": base64.b64encode(obj).decode("ascii")}
    if isinstance(obj, (int, float, bool, str)) or obj is None:
        return obj
    return str(obj)


def _row_to_dict(row):
    result = {}
    for col in row.__table__.columns:
        val = getattr(row, col.name)
        result[col.name] = _serialize(val) if val is not None else None
    return result


def _get_model_map():
    from src.core.models import (
        User, AllowedIP, Channel, ChannelStageConfig,
        Project, VideoDurationConfig, ProjectStage, MediaFile,
        PromptOptimizationLog, VideoAnalysisLog, SystemConfig
    )
    return {
        "users": User, "allowed_ips": AllowedIP, "channels": Channel,
        "channel_stage_configs": ChannelStageConfig, "projects": Project,
        "video_duration_configs": VideoDurationConfig, "project_stages": ProjectStage,
        "media_files": MediaFile, "prompt_optimization_logs": PromptOptimizationLog,
        "video_analysis_logs": VideoAnalysisLog, "system_configs": SystemConfig,
    }


def _get_pks(model):
    return [col.name for col in model.__table__.primary_key]


def create_backup(db, include_local_files=True):
    model_map = _get_model_map()
    stats = {}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for tname in TABLE_ORDER:
            model = model_map.get(tname)
            if not model:
                continue
            try:
                rows = db.query(model).all()
                data = [_row_to_dict(r) for r in rows]
                stats[tname] = len(data)
                zf.writestr(f"db/{tname}.json", json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
            except Exception as ex:
                stats[tname] = f"ERROR: {ex}"
        file_stats = {}
        if include_local_files:
            base_path = Path(os.getcwd())
            for dname in LOCAL_DIRS:
                dpath = base_path / dname
                if not dpath.exists():
                    continue
                cnt = 0
                for fp in dpath.rglob("*"):
                    if fp.is_file():
                        zf.write(str(fp), f"files/{fp.relative_to(base_path).as_posix()}")
                        cnt += 1
                file_stats[dname] = cnt
        stats["local_files"] = file_stats
        meta = {
            "backup_version": BACKUP_VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "table_order": TABLE_ORDER,
            "stats": stats,
        }
        zf.writestr("metadata.json", json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8"))
    return buf.getvalue(), stats


def restore_backup(db, zip_bytes, overwrite=False):
    model_map = _get_model_map()
    results = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes), mode="r") as zf:
        try:
            meta = json.loads(zf.read("metadata.json").decode("utf-8"))
            table_order = meta.get("table_order", TABLE_ORDER)
        except Exception:
            table_order = TABLE_ORDER
        for tname in table_order:
            jpath = f"db/{tname}.json"
            if jpath not in zf.namelist():
                continue
            model = model_map.get(tname)
            if not model:
                continue
            pk_cols = _get_pks(model)
            try:
                rows_data = json.loads(zf.read(jpath).decode("utf-8"))
            except Exception as ex:
                results[tname] = {"error": str(ex)}
                continue
            inserted = skipped = errors = 0
            for row_dict in rows_data:
                try:
                    clean = {}
                    for k, v in row_dict.items():
                        if isinstance(v, dict) and v.get("__type__") == "bytes":
                            clean[k] = base64.b64decode(v["data"])
                        elif isinstance(v, str) and "T" in v and len(v) >= 19:
                            try:
                                clean[k] = datetime.fromisoformat(v)
                            except Exception:
                                clean[k] = v
                        else:
                            clean[k] = v
                    pk_filter = {c: clean.get(c) for c in pk_cols if clean.get(c) is not None}
                    existing = db.query(model).filter_by(**pk_filter).first() if pk_filter else None
                    if existing:
                        if overwrite:
                            for k, v in clean.items():
                                if k not in pk_cols:
                                    setattr(existing, k, v)
                            inserted += 1
                        else:
                            skipped += 1
                    else:
                        db.add(model(**clean))
                        inserted += 1
                except Exception as ex:
                    errors += 1
                    print(f"[RESTORE WARN] {tname}: {ex}")
            try:
                db.commit()
            except Exception as ex:
                db.rollback()
                results[tname] = {"error": f"Commit failed: {ex}"}
                continue
            results[tname] = {"inserted": inserted, "skipped": skipped, "errors": errors}
        base_path = Path(os.getcwd())
        file_restored = 0
        for name in zf.namelist():
            if name.startswith("files/") and not name.endswith("/"):
                target = base_path / name[len("files/"):]
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or overwrite:
                    target.write_bytes(zf.read(name))
                    file_restored += 1
        results["local_files_restored"] = file_restored
    return results


def get_backup_preview(zip_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), mode="r") as zf:
            return json.loads(zf.read("metadata.json").decode("utf-8"))
    except Exception as ex:
        return {"error": str(ex)}
