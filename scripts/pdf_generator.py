#!/usr/bin/env python3
"""
pdf_generator.py - IMPROVED VERSION

PDF report generator for IG Trading Bot.
Generates professional financial reports with tables, charts, and summaries.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

# Try to import FPDF, install if needed
try:
    from fpdf import FPDF
except ImportError:
    raise ImportError(
        "fpdf library is required. Install with: pip install fpdf2\n"
        "Note: Install fpdf2 (newer version), not fpdf (old version)"
    )


class PDFGenerator(FPDF):
    """
    Professional PDF report generator for trading analysis.
    
    Features:
    - Professional headers/footers
    - Dynamic tables with flexible column widths
    - Error handling for missing data
    - Multiple report types (weekly, backtest, portfolio)
    """

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize PDF generator.
        
        Args:
            output_dir: Directory to save PDF files
        """
        super().__init__()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Try to add Unicode fonts
        self.font_name = 'Helvetica'
        self._setup_fonts()

    def _setup_fonts(self):
        """Setup fonts with Unicode support"""
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.add_font('Unicode', '', font_path, uni=True)
                    self.add_font('Unicode', 'B', font_path.replace('.ttf', '-Bold.ttf'), uni=True)
                    self.font_name = 'Unicode'
                    print(f"Using font: {font_path}")
                    return
                except:
                    continue
        
        print("Warning: Unicode font not found. Using Helvetica (limited emoji support)")

    def header(self):
        """Custom header for each page"""
        self.set_font(self.font_name, 'B', 12)
        self.cell(0, 10, 'IG Trading Bot - Financial Report', 0, 1, 'C')
        self.ln(2)

    def footer(self):
        """Custom footer with page numbers"""
        self.set_y(-15)
        self.set_font(self.font_name, '', 8)
        self.set_text_color(128)
        footer_text = f'Page {self.page_no()} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        self.cell(0, 10, footer_text, 0, 0, 'C')

    def _create_title_section(self, title: str, date: str):
        """Create report title section"""
        self.set_font(self.font_name, 'B', 16)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 12, title, 0, 1, 'C', True)
        self.set_font(self.font_name, '', 10)
        self.cell(0, 8, f'Report Date: {date}', 0, 1, 'C')
        self.ln(8)

    def _calculate_column_widths(self, headers: List[str], 
                                 data: List[List[str]], 
                                 available_width: float = 190) -> List[float]:
        """
        Calculate optimal column widths based on content.
        
        Args:
            headers: Column headers
            data: Table data
            available_width: Total available width
            
        Returns:
            List of column widths
        """
        if not headers or not data:
            return [available_width]
        
        num_cols = len(headers)
        
        # Calculate max length for each column
        col_max_lengths = []
        for i in range(num_cols):
            header_len = len(str(headers[i]))
            data_lens = [len(str(row[i])) for row in data if i < len(row)]
            max_len = max([header_len] + data_lens)
            col_max_lengths.append(max_len)
        
        # Calculate widths proportional to content length
        total_chars = sum(col_max_lengths)
        if total_chars == 0:
            return [available_width / num_cols] * num_cols
        
        widths = [
            (length / total_chars) * available_width 
            for length in col_max_lengths
        ]
        
        # Ensure minimum width
        min_width = 20
        widths = [max(w, min_width) for w in widths]
        
        return widths

    def _add_table(self, headers: List[str], 
                   data: List[List[Any]], 
                   col_widths: Optional[List[float]] = None):
        """
        Add a formatted table with error handling.
        
        Args:
            headers: Column headers
            data: Table data (rows)
            col_widths: Optional fixed column widths
        """
        # Validate data
        if not headers:
            self.cell(0, 10, "No data available", 0, 1, 'C')
            return
        
        # Ensure data rows match header count
        num_cols = len(headers)
        validated_data = []
        for row in data:
            if len(row) < num_cols:
                # Pad with empty strings
                row = list(row) + [''] * (num_cols - len(row))
            elif len(row) > num_cols:
                # Truncate
                row = row[:num_cols]
            validated_data.append(row)
        
        # Calculate widths
        if col_widths is None:
            col_widths = self._calculate_column_widths(headers, validated_data)
        
        # Header row
        self.set_font(self.font_name, 'B', 10)
        self.set_fill_color(52, 73, 94)  # Dark blue
        self.set_text_color(255, 255, 255)
        
        for i, header in enumerate(headers):
            width = col_widths[i] if i < len(col_widths) else col_widths[-1]
            self.cell(width, 10, str(header), 1, 0, 'C', True)
        self.ln()
        
        # Data rows with alternating colors
        self.set_font(self.font_name, '', 10)
        self.set_text_color(0, 0, 0)
        
        for idx, row in enumerate(validated_data):
            # Alternating row colors
            if idx % 2 == 0:
                self.set_fill_color(245, 245, 245)  # Light gray
            else:
                self.set_fill_color(255, 255, 255)  # White
            
            for i, item in enumerate(row):
                width = col_widths[i] if i < len(col_widths) else col_widths[-1]
                self.cell(width, 10, str(item), 1, 0, 'C', True)
            self.ln()
        
        self.ln(5)

    def _safe_get(self, data: Dict, key: str, default: Any = 'N/A') -> Any:
        """Safely get value from dictionary"""
        try:
            value = data.get(key, default)
            return value if value is not None else default
        except:
            return default

    def create_weekly_report(self, analysis_data: Dict, date: str) -> str:
        """
        Create weekly market analysis PDF report.
        
        Args:
            analysis_data: Dictionary with analysis results
            date: Report date string
            
        Returns:
            Path to generated PDF file
        """
        try:
            filename = f"{self.output_dir}/weekly_report_{date}.pdf"
            
            self.add_page()
            self._create_title_section(f"Weekly Market Analysis - {date}", date)
            
            # Market Summary Section
            self.set_font(self.font_name, 'B', 12)
            self.cell(0, 10, "Market Summary", 0, 1)
            self.set_font(self.font_name, '', 10)
            
            summary = self._safe_get(analysis_data, 'summary', 'No summary available')
            self.multi_cell(0, 6, str(summary))
            self.ln(5)
            
            # ETF Data Table
            etf_data = self._safe_get(analysis_data, 'etf_data', {})
            if etf_data:
                self.set_font(self.font_name, 'B', 12)
                self.cell(0, 10, "ETF Performance", 0, 1)
                
                headers = ['Ticker', 'Price', 'Trend', 'RSI', 'Recommendation']
                table_data = []
                
                for ticker, info in etf_data.items():
                    if isinstance(info, dict):
                        row = [
                            ticker,
                            f"${self._safe_get(info, 'price', 'N/A')}",
                            self._safe_get(info, 'trend', 'N/A'),
                            self._safe_get(info, 'rsi', 'N/A'),
                            self._safe_get(info, 'recommendation', 'HOLD')
                        ]
                        table_data.append(row)
                
                if table_data:
                    self._add_table(headers, table_data)
            
            # Risk Metrics Section
            risk_data = self._safe_get(analysis_data, 'risk_metrics', {})
            if risk_data:
                self.set_font(self.font_name, 'B', 12)
                self.cell(0, 10, "Risk Metrics", 0, 1)
                
                headers = ['Metric', 'Value']
                table_data = [
                    ['Volatility', f"{self._safe_get(risk_data, 'volatility', 'N/A')}%"],
                    ['Sharpe Ratio', self._safe_get(risk_data, 'sharpe_ratio', 'N/A')],
                    ['Max Drawdown', f"{self._safe_get(risk_data, 'max_drawdown', 'N/A')}%"],
                ]
                self._add_table(headers, table_data)
            
            # Recommendations
            self.set_font(self.font_name, 'B', 12)
            self.cell(0, 10, "Recommendations", 0, 1)
            self.set_font(self.font_name, '', 10)
            
            recommendations = self._safe_get(analysis_data, 'recommendations', [])
            if recommendations:
                for rec in recommendations:
                    self.cell(0, 6, f"- {rec}", 0, 1)
            else:
                self.cell(0, 6, "No specific recommendations at this time.", 0, 1)
            
            self.output(filename)
            print(f"Weekly report saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error creating weekly report: {e}")
            raise

    def create_backtest_report(self, backtest_results: Dict) -> str:
        """
        Create backtest results PDF report.
        
        Args:
            backtest_results: Dictionary with backtest results
            
        Returns:
            Path to generated PDF file
        """
        try:
            date = datetime.now().strftime("%Y%m%d")
            filename = f"{self.output_dir}/backtest_report_{date}.pdf"
            
            self.add_page()
            self._create_title_section("Backtest Results", date)
            
            # Metadata
            metadata = self._safe_get(backtest_results, 'metadata', {})
            self.set_font(self.font_name, 'B', 12)
            self.cell(0, 10, "Test Parameters", 0, 1)
            self.set_font(self.font_name, '', 10)
            
            params = [
                f"ETFs: {', '.join(self._safe_get(metadata, 'etf_list', []))}",
                f"Period: {self._safe_get(metadata, 'start_date', 'N/A')} to {self._safe_get(metadata, 'end_date', 'N/A')}",
                f"Generated: {self._safe_get(metadata, 'generated_at', 'N/A')[:10]}"
            ]
            for param in params:
                self.cell(0, 6, param, 0, 1)
            self.ln(5)
            
            # DCA Results
            dca = self._safe_get(backtest_results, 'results', {}).get('dca', {})
            if dca:
                self.set_font(self.font_name, 'B', 12)
                self.cell(0, 10, "DCA Strategy Results", 0, 1)
                
                headers = ['Metric', 'Value']
                data = [
                    ['Total Invested', f"${self._safe_get(dca, 'total_invested', 0):,.2f}"],
                    ['Final Value', f"${self._safe_get(dca, 'final_value', 0):,.2f}"],
                    ['Profit/Loss', f"${self._safe_get(dca, 'profit_loss', 0):,.2f}"],
                    ['ROI', f"{self._safe_get(dca, 'roi_percent', 0):.2f}%"],
                    ['Number of Months', self._safe_get(dca, 'num_months', 'N/A')],
                ]
                self._add_table(headers, data)
            
            # Lump Sum Results
            lump = self._safe_get(backtest_results, 'results', {}).get('lump_sum', {})
            if lump:
                self.set_font(self.font_name, 'B', 12)
                self.cell(0, 10, "Lump Sum Strategy Results", 0, 1)
                
                headers = ['Metric', 'Value']
                data = [
                    ['Initial Investment', f"${self._safe_get(lump, 'total_amount', 0):,.2f}"],
                    ['Final Value', f"${self._safe_get(lump, 'final_value', 0):,.2f}"],
                    ['Profit/Loss', f"${self._safe_get(lump, 'profit_loss', 0):,.2f}"],
                    ['ROI', f"{self._safe_get(lump, 'roi_percent', 0):.2f}%"],
                ]
                self._add_table(headers, data)
            
            # Comparison
            comparison = self._safe_get(backtest_results, 'results', {}).get('comparison', {})
            if comparison:
                self.set_font(self.font_name, 'B', 12)
                self.cell(0, 10, "Strategy Comparison", 0, 1)
                self.set_font(self.font_name, '', 10)
                
                winner = self._safe_get(comparison, 'winner', 'N/A')
                diff = self._safe_get(comparison, 'value_difference', 0)
                
                self.cell(0, 8, f"Winner: {winner}", 0, 1)
                self.cell(0, 8, f"Value Difference: ${diff:,.2f}", 0, 1)
            
            self.output(filename)
            print(f"Backtest report saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error creating backtest report: {e}")
            raise

    def create_portfolio_report(self, portfolio_data: Dict) -> str:
        """
        Create portfolio summary PDF report.
        
        Args:
            portfolio_data: Dictionary with portfolio information
            
        Returns:
            Path to generated PDF file
        """
        try:
            date = datetime.now().strftime("%Y%m%d")
            filename = f"{self.output_dir}/portfolio_report_{date}.pdf"
            
            self.add_page()
            self._create_title_section("Portfolio Summary", date)
            
            # Portfolio Overview
            self.set_font(self.font_name, 'B', 12)
            self.cell(0, 10, "Portfolio Overview", 0, 1)
            
            total_value = self._safe_get(portfolio_data, 'total_value', 0)
            total_cost = self._safe_get(portfolio_data, 'total_cost', 0)
            
            headers = ['Metric', 'Value']
            data = [
                ['Total Value', f"${total_value:,.2f}"],
                ['Total Cost', f"${total_cost:,.2f}"],
                ['Unrealized P/L', f"${total_value - total_cost:,.2f}"],
                ['Number of Positions', len(self._safe_get(portfolio_data, 'positions', {}))],
            ]
            self._add_table(headers, data)
            
            # Individual Positions
            positions = self._safe_get(portfolio_data, 'positions', {})
            if positions:
                self.set_font(self.font_name, 'B', 12)
                self.cell(0, 10, "Current Positions", 0, 1)
                
                headers = ['Ticker', 'Units', 'Avg Cost', 'Current Price', 'P/L %']
                data = []
                
                for ticker, pos in positions.items():
                    if isinstance(pos, dict):
                        row = [
                            ticker,
                            f"{self._safe_get(pos, 'units', 0):.2f}",
                            f"${self._safe_get(pos, 'avg_cost', 0):.2f}",
                            f"${self._safe_get(pos, 'current_price', 0):.2f}",
                            f"{self._safe_get(pos, 'pl_percent', 0):.2f}%"
                        ]
                        data.append(row)
                
                if data:
                    self._add_table(headers, data)
            
            self.output(filename)
            print(f"Portfolio report saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error creating portfolio report: {e}")
            raise


# --- Example Usage ---
if __name__ == "__main__":
    # Example: Create a weekly report
    generator = PDFGenerator(output_dir="reports")
    
    sample_data = {
        "summary": "Market shows mixed signals with tech leading.",
        "etf_data": {
            "SPY": {"price": 450.20, "trend": "BULLISH", "rsi": 65, "recommendation": "HOLD"},
            "QQQ": {"price": 380.50, "trend": "BULLISH", "rsi": 70, "recommendation": "REDUCE"},
        },
        "risk_metrics": {
            "volatility": 15.5,
            "sharpe_ratio": 1.2,
            "max_drawdown": -8.3
        },
        "recommendations": [
            "Reduce QQQ exposure due to high RSI",
            "Maintain SPY position"
        ]
    }
    
    try:
        pdf_path = generator.create_weekly_report(sample_data, "2024-01-15")
        print(f"Example report created: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")
