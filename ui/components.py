"""Reusable visual building blocks. Any user-supplied text is HTML-escaped here."""

from __future__ import annotations

from html import escape

import plotly.graph_objects as go
import streamlit as st

from core import config


def html(markup: str) -> None:
    """Render a trusted HTML fragment (no scripts)."""
    st.html(markup)


def icon(name: str, size: int | None = None) -> str:
    style = f' style="font-size:{size}px"' if size else ""
    return f'<span class="material-symbols-rounded"{style}>{escape(name)}</span>'


def initials(name: str) -> str:
    parts = [p for p in (name or "").replace(".", " ").split() if p]
    return escape("".join(p[0] for p in parts[:2]).upper() or "E")


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    html(f"""
    <div class="eco-eyebrow">{escape(eyebrow)}</div>
    <div class="eco-title">{escape(title)}</div>
    {f'<div class="eco-sub">{escape(subtitle)}</div>' if subtitle else ''}
    """)


def section(title: str, hint: str = "") -> None:
    html(f'<div class="eco-section"><h3>{escape(title)}</h3><span>{escape(hint)}</span></div>')


def kpi(label: str, value: str, icon_name: str, delta: str = "", trend: str = "flat",
        tint: str | None = None) -> None:
    ic_style = f' style="background:{tint}22;color:{tint}"' if tint else ""
    delta_html = f'<div class="kpi delta {trend}">{escape(delta)}</div>' if delta else ""
    html(f"""
    <div class="eco-card"><div class="kpi">
      <div class="ic"{ic_style}>{icon(icon_name)}</div>
      <div><div class="lab">{escape(label)}</div><div class="val">{escape(value)}</div>{delta_html}</div>
    </div></div>
    """)


def category_chip(category_key: str) -> str:
    cat = config.CATEGORIES[category_key]
    return (f'<span class="chip" style="background:{cat.color}1A;color:{cat.color}">'
            f'{icon(cat.icon, 14)}{escape(cat.label)}</span>')


def hero(name: str, points: int, level: str, floor: int, nxt: int | None,
         streak: int, rank: int | None) -> None:
    if nxt:
        pct = max(0, min(100, round(100 * (points - floor) / (nxt - floor))))
        next_txt = f"{nxt - points:,} points to the next level"
    else:
        pct, next_txt = 100, "Top level reached. You're an inspiration!"
    first = escape((name or "there").split()[0])
    rank_pill = f'<span class="pill">{icon("leaderboard", 16)} Rank #{rank}</span>' if rank else ""
    html(f"""
    <div class="eco-hero"><div class="inner">
      <div style="flex:1;min-width:260px">
        <div class="hello">Welcome back, {first}</div>
        <div class="big">Small actions,<br>real change.</div>
        <span class="pill">{icon("workspace_premium", 16)} {escape(level)}</span>
        <span class="pill">{icon("local_fire_department", 16)} {streak}-day streak</span>
        {rank_pill}
      </div>
      <div class="points">
        <div class="l">TOTAL ECO POINTS</div>
        <div class="n">{points:,}</div>
        <div class="eco-bar"><div style="width:{pct}%"></div></div>
        <div class="next">{escape(next_txt)}</div>
      </div>
    </div></div>
    """)


def tip_card(label: str, icon_name: str, color: str, tip: str) -> None:
    html(f"""
    <div class="eco-card tip-card">
      <div class="cat"><div class="ic" style="background:{color}">{icon(icon_name)}</div><b>{escape(label)}</b></div>
      <p>{escape(tip)}</p>
    </div>
    """)


def fact_card(category_key: str) -> None:
    fact, source = config.FACTS[category_key]
    html(f"""
    <div class="eco-card fact">
      <div class="k">Why it matters</div>
      <p>{escape(fact)}</p>
      <small>Source: {escape(source)}</small>
    </div>
    """)


def impact_list(items: list[dict], limit: int = 6) -> None:
    if not items:
        html('<div class="eco-card"><p style="margin:0;color:var(--eco-muted)">'
             'Your impact summary appears after your first logged action.</p></div>')
        return
    rows = []
    for it in items[:limit]:
        cat = config.CATEGORIES[it["category"]]
        rows.append(f"""
        <div class="impact">
          <div class="ic" style="background:{cat.color}">{icon(cat.icon)}</div>
          <div><div class="q">{it['quantity']:,} <span class="u">{escape(it['unit'])}</span></div>
          <div class="u">{escape(it['label'])}</div></div>
        </div>""")
    html(f'<div class="eco-card">{"".join(rows)}</div>')


def growth_tree(points: int) -> None:
    stages = [(0, "Seedling"), (100, "Sprout"), (300, "Sapling"), (700, "Young tree"), (1500, "Forest guardian")]
    layers, stage = 1, stages[0][1]
    for i, (threshold, name) in enumerate(stages):
        if points >= threshold:
            layers, stage = i + 1, name
    colors = ["#A7D9B5", "#6FBF8A", "#3FA36B", "#1F7A4D", "#14532D"]
    leaves = "".join(
        f'<ellipse cx="100" cy="{58 + i * 17}" rx="{24 + i * 10}" ry="22" fill="{colors[i]}" opacity=".95"/>'
        for i in range(layers)
    )
    html(f"""
    <div class="eco-card" style="text-align:center">
      <div class="eco-eyebrow">Your eco tree</div>
      <svg viewBox="0 0 200 180" width="100%" height="190" role="img" aria-label="Eco tree, stage {escape(stage)}">
        <ellipse cx="100" cy="166" rx="62" ry="8" fill="#E2EAE0"/>
        <path d="M93 164 Q99 120 96 92 L104 92 Q101 128 109 164 Z" fill="#8B6242"/>
        {leaves}
      </svg>
      <div style="font-weight:800;font-size:1.15rem">{escape(stage)}</div>
      <div style="color:var(--eco-muted);font-size:.85rem">Grows as you earn points</div>
    </div>
    """)


def style_fig(fig: go.Figure, height: int = 300) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, Segoe UI, sans-serif", color="#5D6F64", size=12),
        margin=dict(l=8, r=8, t=36, b=8),
        title_font=dict(size=15, color="#13261D"),
        hoverlabel=dict(bgcolor="#0F3D2E", bordercolor="#0F3D2E", font=dict(color="#fff")),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#E2EAE0", tickfont=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor="#EEF3EC", zeroline=False, tickfont=dict(size=11))
    return fig


def area_chart(x, y, title: str, height: int = 300) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="lines+markers", line=dict(color="#1F7A4D", width=3, shape="spline"),
        marker=dict(size=6, color="#1F7A4D"), fill="tozeroy", fillcolor="rgba(63,163,107,.15)",
        hovertemplate="%{x|%d %b}: <b>%{y} pts</b><extra></extra>",
    ))
    fig.update_layout(title=title)
    return style_fig(fig, height)


def bar_chart(x, y, title: str, height: int = 300) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=x, y=y, marker=dict(color="#3FA36B", cornerradius=8),
        hovertemplate="Week of %{x}: <b>%{y} pts</b><extra></extra>",
    ))
    fig.update_layout(title=title, bargap=.35)
    return style_fig(fig, height)


def donut(labels, values, colors, title: str, height: int = 300) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=.68, marker=dict(colors=colors, line=dict(color="#fff", width=3)),
        textinfo="none", hovertemplate="%{label}: <b>%{value} pts</b> (%{percent})<extra></extra>", sort=False,
    ))
    total = int(sum(values))
    fig.update_layout(title=title, annotations=[dict(text=f"<b>{total:,}</b><br>points", showarrow=False,
                                                     font=dict(size=15, color="#13261D"))])
    fig = style_fig(fig, height)
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.05, font=dict(size=11)))
    return fig


def footer() -> None:
    html('<div class="eco-footer">EcoBin · Mission LiFE citizen engagement · HackCult \'26<br>'
         'Facts are general information from cited public sources, not measurements of your personal impact.</div>')
