"""UI helpers and shared styles for NYEREKA Streamlit pages."""
from __future__ import annotations

import html
import streamlit as st


def apply_theme(page_title: str | None = None, subtitle: str | None = None) -> None:
    st.markdown(
        """
        <style>
            :root {
                --ny-bg: var(--background-color);
                --ny-card: var(--secondary-background-color);
                --ny-text: var(--text-color);
                --ny-muted: color-mix(in srgb, var(--text-color) 66%, transparent);
                --ny-border: color-mix(in srgb, var(--primary-color) 35%, var(--secondary-background-color));
                --ny-shadow: 0 8px 18px rgba(0, 0, 0, 0.10);
            }
            [data-testid="stAppViewContainer"] {
                background: var(--ny-bg);
                color: var(--ny-text);
            }
            .ny-header {
                background: linear-gradient(
                    135deg,
                    color-mix(in srgb, var(--primary-color) 20%, var(--secondary-background-color)) 0%,
                    var(--secondary-background-color) 100%
                );
                color: var(--ny-text);
                border: 1px solid var(--ny-border);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                margin-bottom: 0.9rem;
                box-shadow: var(--ny-shadow);
            }
            .ny-header h1 {
                margin: 0;
                font-size: 1.35rem;
                font-weight: 760;
                letter-spacing: 0.2px;
                color: var(--ny-text);
            }
            .ny-header p {
                margin: 0.35rem 0 0;
                color: var(--ny-muted);
                font-size: 0.92rem;
                line-height: 1.45;
            }
            .kpi-card {
                background: var(--ny-card);
                border: 1px solid var(--ny-border);
                border-left: 4px solid var(--primary-color);
                border-radius: 14px;
                padding: 0.84rem 0.9rem;
                min-height: 104px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
            .kpi-label {
                font-size: 0.76rem;
                color: var(--ny-muted);
                text-transform: uppercase;
                letter-spacing: 0.28px;
            }
            .kpi-value {
                font-size: 1.35rem;
                font-weight: 780;
                color: var(--ny-text);
                margin-top: 0.2rem;
                line-height: 1.2;
                word-break: break-word;
            }
            .kpi-sub {
                margin-top: 0.15rem;
                font-size: 0.8rem;
                color: var(--ny-muted);
                line-height: 1.35;
            }
            .note-box {
                background: color-mix(in srgb, var(--primary-color) 10%, var(--ny-card));
                border: 1px solid var(--ny-border);
                border-radius: 12px;
                padding: 0.78rem 0.9rem;
                color: var(--ny-text);
                font-size: 0.9rem;
            }
            .ny-link-card {
                background: var(--ny-card);
                border: 1px solid var(--ny-border);
                border-radius: 12px;
                padding: 0.68rem 0.8rem;
                margin-bottom: 0.45rem;
            }
            .ny-link-card a {
                color: var(--primary-color);
                font-weight: 700;
                text-decoration: none;
            }
            .ny-link-card a:hover { text-decoration: underline; }
            .ny-link-meta {
                margin-top: 0.1rem;
                color: var(--ny-muted);
                font-size: 0.82rem;
            }
            @media (max-width: 768px) {
                .ny-header h1 { font-size: 1.1rem; }
                .kpi-value { font-size: 1.15rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if page_title:
        subtitle_html = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
        st.markdown(f'<div class="ny-header"><h1>{html.escape(page_title)}</h1>{subtitle_html}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{html.escape(label)}</div>
            <div class="kpi-value">{html.escape(value)}</div>
            <div class="kpi-sub">{html.escape(sub)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_source_links(df, *, name_col: str = "dataset_name", url_col: str = "source_url", meta_cols: list[str] | None = None) -> None:
    if df is None or len(df) == 0:
        st.info("No source links available.")
        return

    meta_cols = meta_cols or []
    for _, row in df.iterrows():
        name = html.escape(str(row.get(name_col, "Source")))
        url = html.escape(str(row.get(url_col, "#")))
        meta_parts = []
        for col in meta_cols:
            val = row.get(col)
            if val is not None and str(val) != "nan":
                meta_parts.append(f"{col.replace('_', ' ').title()}: {val}")
        meta = " | ".join(meta_parts)
        meta_html = f'<div class="ny-link-meta">{html.escape(meta)}</div>' if meta else ""
        st.markdown(
            f'<div class="ny-link-card"><a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>{meta_html}</div>',
            unsafe_allow_html=True,
        )
