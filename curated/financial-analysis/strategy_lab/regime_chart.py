"""Interactive HTML chart — regime bands + backtest trades + equity curve.

Generates a self-contained HTML file using Plotly that shows:
- Price chart with colored regime bands (bull/bear/choppy/consolidation)
- Buy/sell trade markers from backtested strategies
- Equity curve per strategy
- Volume bars
- All interactive: zoom, hover tooltips, toggle strategies via legend

Usage:
    from regime_chart import generate_chart
    path = generate_chart(df, regimes, trades_by_strategy, ticker="NVDA")
    # Opens in browser: open path

    # Regime-only (no trades):
    path = generate_chart(df, regimes, ticker="NVDA")
"""
import pandas as pd
import numpy as np
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Regime visual config
REGIME_FILL = {
    'bull': 'rgba(0, 200, 83, 0.12)',
    'bear': 'rgba(255, 23, 68, 0.12)',
    'choppy': 'rgba(255, 193, 7, 0.08)',
    'consolidation': 'rgba(158, 158, 158, 0.08)',
}
REGIME_BORDER = {
    'bull': 'rgba(0, 200, 83, 0.5)',
    'bear': 'rgba(255, 23, 68, 0.5)',
    'choppy': 'rgba(255, 193, 7, 0.35)',
    'consolidation': 'rgba(158, 158, 158, 0.35)',
}
REGIME_TEXT = {
    'bull': '#00c853',
    'bear': '#ff1744',
    'choppy': '#ffc107',
    'consolidation': '#9e9e9e',
}

# Strategy trade colors (for up to 6 strategies)
STRATEGY_COLORS = [
    '#00e5ff', '#ff6d00', '#aa00ff', '#76ff03', '#ff4081', '#40c4ff',
]


def generate_chart(df, regimes, trades_by_strategy=None, equity_by_strategy=None,
                   walk_forward_results=None, ticker="", output_path=None):
    """Generate interactive HTML chart with regime bands and trade markers.

    Args:
        df: OHLCV DataFrame with DatetimeIndex
        regimes: List of dicts from detect_regimes()
        trades_by_strategy: Dict of {name: trades_df}
            trades_df columns: EntryTime, ExitTime, EntryPrice, ExitPrice, PnL, ReturnPct
        equity_by_strategy: Dict of {name: equity_series (pd.Series)}
        walk_forward_results: Dict of {name: {windows_passed, n_windows, status, ...}}
        ticker: Ticker symbol
        output_path: Output HTML path (default: {ticker}_chart.html in project dir)

    Returns:
        Absolute path to the generated HTML file.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    if output_path is None:
        name = ticker.lower() if ticker else "regime"
        output_path = os.path.join(PROJECT_DIR, f"{name}_chart.html")

    has_trades = trades_by_strategy and len(trades_by_strategy) > 0
    has_equity = equity_by_strategy and len(equity_by_strategy) > 0

    # Subplot layout
    n_rows = 2 + (1 if has_equity else 0)
    heights = [0.55] + ([0.25] if has_equity else []) + [0.20]
    titles = [f"{ticker} — Price + Auto-Detected Regimes"]
    if has_equity:
        titles.append("Strategy Equity Curves")
    titles.append("Volume")

    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=heights,
        subplot_titles=titles,
    )

    # ── Row 1: Price + Regime Bands ──────────────────────────────────────

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Price',
        increasing=dict(line=dict(color='#26a69a'), fillcolor='#26a69a'),
        decreasing=dict(line=dict(color='#ef5350'), fillcolor='#ef5350'),
        showlegend=False,
    ), row=1, col=1)

    # Regime bands
    for regime in regimes:
        label = regime['label']
        ret = regime.get('total_return', 0)
        vol = regime.get('annualized_vol', 0)
        bars = regime.get('bars', 0)
        sign = '+' if ret >= 0 else ''

        fill = REGIME_FILL.get(label, REGIME_FILL['choppy'])
        border = REGIME_BORDER.get(label, REGIME_BORDER['choppy'])
        text_color = REGIME_TEXT.get(label, '#888')

        fig.add_vrect(
            x0=regime['start'], x1=regime['end'],
            fillcolor=fill,
            line=dict(width=1, color=border, dash='dot'),
            row=1, col=1,
        )

        # Regime label annotation at top
        mid_date = regime['start'] + (regime['end'] - regime['start']) / 2
        fig.add_annotation(
            x=mid_date,
            y=1.02,
            yref='paper',
            text=f"<b>{label.upper()}</b><br>{sign}{ret:.0f}% | {bars}d | vol {vol:.0f}%",
            showarrow=False,
            font=dict(size=10, color=text_color),
            xanchor='center',
        )

    # Trade markers
    if has_trades:
        for i, (name, trades) in enumerate(trades_by_strategy.items()):
            if trades is None or len(trades) == 0:
                continue

            color = STRATEGY_COLORS[i % len(STRATEGY_COLORS)]
            wf_tag = ""
            if walk_forward_results and name in walk_forward_results:
                wf = walk_forward_results[name]
                wf_tag = f" [{wf['windows_passed']}/{wf['n_windows']} {wf['status']}]"

            # Entry markers
            fig.add_trace(go.Scatter(
                x=trades['EntryTime'],
                y=trades['EntryPrice'],
                mode='markers',
                name=f'{name} BUY{wf_tag}',
                marker=dict(
                    symbol='triangle-up', size=11, color=color,
                    line=dict(width=1, color='white'),
                ),
                text=[f"BUY ${p:.2f}<br>{d}" for p, d in
                      zip(trades['EntryPrice'], trades['EntryTime'])],
                hovertemplate='%{text}<extra></extra>',
                legendgroup=name,
            ), row=1, col=1)

            # Exit markers (closed trades only)
            if 'ExitTime' in trades.columns:
                closed = trades.dropna(subset=['ExitTime'])
                if len(closed) > 0:
                    exit_colors = [color if pnl > 0 else '#ff1744' for pnl in closed['PnL']]
                    fig.add_trace(go.Scatter(
                        x=closed['ExitTime'],
                        y=closed['ExitPrice'],
                        mode='markers',
                        name=f'{name} SELL',
                        marker=dict(
                            symbol='triangle-down', size=11, color=exit_colors,
                            line=dict(width=1, color='white'),
                        ),
                        text=[f"SELL ${p:.2f} ({r:+.1f}%)<br>PnL ${pnl:,.0f}"
                              for p, r, pnl in zip(closed['ExitPrice'],
                                                   closed['ReturnPct'],
                                                   closed['PnL'])],
                        hovertemplate='%{text}<extra></extra>',
                        legendgroup=name,
                        showlegend=False,
                    ), row=1, col=1)

                    # Connecting lines (entry -> exit)
                    for _, trade in closed.iterrows():
                        line_color = color if trade['PnL'] > 0 else '#ff1744'
                        fig.add_trace(go.Scatter(
                            x=[trade['EntryTime'], trade['ExitTime']],
                            y=[trade['EntryPrice'], trade['ExitPrice']],
                            mode='lines',
                            line=dict(color=line_color, width=1, dash='dot'),
                            showlegend=False,
                            legendgroup=name,
                            hoverinfo='skip',
                        ), row=1, col=1)

    # ── Row 2 (optional): Equity Curves ─────────────────────────────────
    if has_equity:
        eq_row = 2
        for i, (name, equity) in enumerate(equity_by_strategy.items()):
            color = STRATEGY_COLORS[i % len(STRATEGY_COLORS)]
            fig.add_trace(go.Scatter(
                x=equity.index, y=equity.values,
                mode='lines', name=f'{name} Equity',
                line=dict(width=2, color=color),
                legendgroup=name,
                showlegend=False,
            ), row=eq_row, col=1)

        # Add a baseline
        if equity_by_strategy:
            first_eq = list(equity_by_strategy.values())[0]
            fig.add_hline(
                y=first_eq.iloc[0], line_dash='dash',
                line_color='rgba(255,255,255,0.3)',
                annotation_text='Starting capital',
                row=eq_row, col=1,
            )

    # ── Last Row: Volume ─────────────────────────────────────────────────
    vol_row = n_rows
    vol_colors = ['#26a69a' if c >= o else '#ef5350'
                  for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        marker_color=vol_colors, opacity=0.5,
        showlegend=False,
    ), row=vol_row, col=1)

    # ── Layout ───────────────────────────────────────────────────────────
    n_regimes = len(regimes)
    label_counts = {}
    for r in regimes:
        label_counts[r['label']] = label_counts.get(r['label'], 0) + 1
    regime_summary = ", ".join(f"{v} {k}" for k, v in sorted(label_counts.items()))

    fig.update_layout(
        title=dict(
            text=(f"<b>{ticker} Strategy Dashboard</b><br>"
                  f"<span style='font-size:12px;color:#888'>"
                  f"{n_regimes} auto-detected regimes ({regime_summary}) | "
                  f"Data: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
                  f"</span>"),
            font=dict(size=16),
        ),
        template='plotly_dark',
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#16213e',
        height=700 + (200 if has_equity else 0),
        showlegend=True,
        legend=dict(
            orientation='h', y=-0.08,
            font=dict(size=10),
            bgcolor='rgba(0,0,0,0.3)',
        ),
        hovermode='x unified',
        xaxis_rangeslider_visible=False,
        margin=dict(t=100, b=80),
    )

    # Dark grid styling
    for i in range(1, n_rows + 1):
        fig.update_xaxes(
            gridcolor='rgba(255,255,255,0.05)',
            showgrid=True,
            row=i, col=1,
        )
        fig.update_yaxes(
            gridcolor='rgba(255,255,255,0.05)',
            showgrid=True,
            row=i, col=1,
        )

    # Price axis formatting
    fig.update_yaxes(title_text='Price ($)', row=1, col=1)
    if has_equity:
        fig.update_yaxes(title_text='Equity ($)', row=2, col=1)
    fig.update_yaxes(title_text='Volume', row=vol_row, col=1)

    # Save
    fig.write_html(output_path, include_plotlyjs=True)
    print(f"  Chart saved: {output_path}")
    return output_path


def generate_regime_only_chart(df, regimes, ticker="", output_path=None):
    """Quick chart with just price + regime bands (no trades)."""
    return generate_chart(df, regimes, ticker=ticker, output_path=output_path)


if __name__ == "__main__":
    """Quick test: generate chart for any ticker with existing data."""
    import sys
    sys.path.insert(0, '.')
    from utils import load_data
    from regime_detector import detect_regimes

    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"

    df = load_data(ticker, "daily")
    regimes = detect_regimes(df)

    path = generate_chart(df, regimes, ticker=ticker)
    print(f"\n  Open in browser: file://{os.path.abspath(path)}")

    # Try to open in default browser
    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(path)}")
    except Exception:
        pass
