"""PostgreSQL queries for EchoPulse feedback data."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")


def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def get_summary_stats(days: int = 7) -> dict:
    since = datetime.now(UTC) - timedelta(days=days)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS total FROM feedback WHERE created_at >= %s",
                (since,),
            )
            total = cur.fetchone()["total"]

            cur.execute(
                """
                SELECT category, COUNT(*) AS count
                FROM feedback
                WHERE created_at >= %s
                GROUP BY category
                ORDER BY count DESC
                """,
                (since,),
            )
            by_category = [dict(row) for row in cur.fetchall()]

            cur.execute(
                """
                SELECT severity, COUNT(*) AS count
                FROM feedback
                WHERE created_at >= %s
                GROUP BY severity
                ORDER BY CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'high'     THEN 2
                    WHEN 'medium'   THEN 3
                    WHEN 'low'      THEN 4
                END
                """,
                (since,),
            )
            by_severity = [dict(row) for row in cur.fetchall()]

            cur.execute(
                """
                SELECT sentiment, COUNT(*) AS count
                FROM feedback
                WHERE created_at >= %s
                GROUP BY sentiment
                """,
                (since,),
            )
            by_sentiment = [dict(row) for row in cur.fetchall()]

    return {
        "tool": "get_summary_stats",
        "period_days": days,
        "total": total,
        "by_category": by_category,
        "by_severity": by_severity,
        "by_sentiment": by_sentiment,
    }


def search_feedback(query: str, limit: int = 10) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, raw_text, summary, category, severity, sentiment,
                       product_area, created_at,
                       ts_rank(
                           to_tsvector('english', raw_text || ' ' || COALESCE(summary, '')),
                           plainto_tsquery('english', %s)
                       ) AS rank
                FROM feedback
                WHERE to_tsvector('english', raw_text || ' ' || COALESCE(summary, ''))
                      @@ plainto_tsquery('english', %s)
                ORDER BY rank DESC, created_at DESC
                LIMIT %s
                """,
                (query, query, limit),
            )
            results = [dict(row) for row in cur.fetchall()]

    return {
        "tool": "search_feedback",
        "query": query,
        "count": len(results),
        "results": results,
    }


def get_top_issues(category: str | None = None, days: int = 7, limit: int = 5) -> dict:
    since = datetime.now(UTC) - timedelta(days=days)

    with get_connection() as conn:
        with conn.cursor() as cur:
            if category:
                cur.execute(
                    """
                    SELECT summary, category, severity, COUNT(*) AS count
                    FROM feedback
                    WHERE created_at >= %s AND category = %s
                    GROUP BY summary, category, severity
                    ORDER BY count DESC
                    LIMIT %s
                    """,
                    (since, category, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT summary, category, severity, COUNT(*) AS count
                    FROM feedback
                    WHERE created_at >= %s
                    GROUP BY summary, category, severity
                    ORDER BY count DESC
                    LIMIT %s
                    """,
                    (since, limit),
                )
            results = [dict(row) for row in cur.fetchall()]

    return {
        "tool": "get_top_issues",
        "category_filter": category,
        "period_days": days,
        "top_issues": results,
    }


def get_trend(
    category: str | None = None,
    severity: str | None = None,
    days: int = 7,
) -> dict:
    since = datetime.now(UTC) - timedelta(days=days)

    with get_connection() as conn:
        with conn.cursor() as cur:
            filters = ["created_at >= %s"]
            params: list = [since]

            if category:
                filters.append("category = %s")
                params.append(category)
            if severity:
                filters.append("severity = %s")
                params.append(severity)

            where = " AND ".join(filters)

            cur.execute(
                f"""
                SELECT DATE(created_at) AS date, COUNT(*) AS count
                FROM feedback
                WHERE {where}
                GROUP BY DATE(created_at)
                ORDER BY date ASC
                """,
                params,
            )
            trend = [dict(row) for row in cur.fetchall()]

    return {
        "tool": "get_trend",
        "category_filter": category,
        "severity_filter": severity,
        "period_days": days,
        "trend": trend,
    }


def get_critical_items(resolved: bool = False, limit: int = 10) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, raw_text, summary, category, severity,
                       product_area, created_at, resolved
                FROM feedback
                WHERE severity IN ('high', 'critical')
                  AND resolved = %s
                ORDER BY
                    CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 END,
                    created_at DESC
                LIMIT %s
                """,
                (resolved, limit),
            )
            items = [dict(row) for row in cur.fetchall()]

    return {
        "tool": "get_critical_items",
        "showing_resolved": resolved,
        "count": len(items),
        "items": items,
    }


def mark_resolved(feedback_id: int, reason: str = "") -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE feedback
                SET resolved = true, resolved_at = now()
                WHERE id = %s
                RETURNING id, summary, category, severity, resolved_at
                """,
                (feedback_id,),
            )
            updated = cur.fetchone()
            conn.commit()

    if not updated:
        return {
            "tool": "mark_resolved",
            "success": False,
            "error": f"No item with id {feedback_id}",
        }

    return {
        "tool": "mark_resolved",
        "success": True,
        "updated": dict(updated),
        "reason": reason,
    }
