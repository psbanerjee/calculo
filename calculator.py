import sys
import math
import random
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QListWidget, QSplitter, QComboBox, QStackedWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QKeyEvent

class PremiumScientificCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Scientific Calculator")
        self.setMinimumSize(QSize(850, 580))
        self.resize(880, 600)
        
        # State Engine Core Variables
        self.current_expression = "0"
        self.should_reset_current = False
        self.angle_mode = "Deg"  
        self.saved_function = ""  
        self.history_ledger = []  
        self.history_index = -1   
        self.is_shifted = False
        self.shifted_buttons = {}  
        
        self.init_ui()
        self.apply_premium_theme()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(16, 16, 16, 16)
        outer_layout.setSpacing(12)

        header_bar = QHBoxLayout()
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Advanced Scientific Mode", "Standard Basic Mode"])
        self.mode_selector.currentTextChanged.connect(self.switch_mode_view)
        self.mode_selector.setObjectName("ModeSelector")
        header_bar.addWidget(self.mode_selector)
        header_bar.addStretch()
        outer_layout.addLayout(header_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(12)
        
        calc_container = QWidget()
        calc_layout = QVBoxLayout(calc_container)
        calc_layout.setContentsMargins(0, 0, 0, 0)
        calc_layout.setSpacing(12)

        display_panel = QWidget()
        display_panel.setObjectName("DisplayPanel")
        display_panel.setMaximumHeight(130)
        display_inner = QVBoxLayout(display_panel)
        display_inner.setContentsMargins(16, 12, 16, 12)
        display_inner.setSpacing(4)

        top_display_row = QHBoxLayout()
        self.mode_indicator = QLabel("DEG")
        self.mode_indicator.setObjectName("ModeIndicator")
        
        self.formula_display = QLabel("")
        self.formula_display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.formula_display.setObjectName("FormulaDisplay")
        
        top_display_row.addWidget(self.mode_indicator)
        top_display_row.addWidget(self.formula_display)
        
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.display.setObjectName("MainDisplay")

        self.warning_display = QLabel("")
        self.warning_display.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.warning_display.setObjectName("WarningDisplay")
        
        display_inner.addLayout(top_display_row)
        display_inner.addWidget(self.display)
        display_inner.addWidget(self.warning_display)
        calc_layout.addWidget(display_panel)

        self.keypad_stack = QStackedWidget()
        
        # Tooltip Map Definitions
        self.tooltip_map = {
            '↑¹': "Shift: Toggles trigonometric and logarithmic buttons to their inverse functions",
            'x²': "Square: Appends squaring operation to expression",
            'xʸ': "Power: Appends exponentiation power operator (^)",
            'conj': "Complex Conjugate: Appends conjugate evaluation token to expression",
            'x⁻¹': "Reciprocal: Appends inverse fraction operator",
            'C': "Clear: Resets display to 0 and flushes input registers",
            '↑n': "History Back: Navigates backward through calculation log ledger",
            '↓n': "History Forward: Navigates forward through calculation log ledger",
            '÷': "Division Operator", 'mod': "Modulus: Returns integer remainder of division",
            'sin': "Appends Sine operation token",
            'sin⁻¹': "Appends Arcsine operation token",
            'sinh': "Appends Hyperbolic Sine operation token",
            'sinh⁻¹': "Appends Inverse Hyperbolic Sine operation token",
            'logʸ': "Appends custom base logarithm operation token",
            'Arg': "Complex Argument: Appends structural phase angle tracking token",
            '[x]': "Floor Function: Appends truncation token",
            '7': "Digit 7", '8': "Digit 8", '9': "Digit 9", '×': "Multiplication Operator",
            '%': "Percentage Operator",
            'cos': "Appends Cosine operation token",
            'cos⁻¹': "Appends Arcsine operation token",
            'cosh': "Appends Hyperbolic Cosine operation token",
            'cosh⁻¹': "Appends Inverse Hyperbolic Cosine operation token",
            'log': "Appends Common Logarithm base 10 token",
            '10ˣ': "Appends base 10 power token",
            'Re': "Real Component: Appends extraction token",
            '|x|': "Absolute Value: Appends magnitude calculation token",
            '4': "Digit 4", '5': "Digit 5", '6': "Digit 6", '−': "Subtraction Operator",
            '()': "Parentheses grouping bracket sequence controller",
            'tan': "Appends Tangent operation token",
            'tan⁻¹': "Appends Arctangent operation token",
            'tanh': "Appends Hyperbolic Tangent operation token",
            'tanh⁻¹': "Appends Inverse Hyperbolic Tangent operation token",
            'ln': "Appends Natural Logarithm base e token",
            'eˣ': "Appends base e power token",
            'Im': "Imaginary Component: Appends extraction token",
            'x!': "Factorial Operator",
            '1': "Digit 1", '2': "Digit 2", '3': "Digit 3", '+': "Addition Operator",
            'Deg': "Angle System Mode indicator set to Degrees",
            'Rad': "Angle System Mode indicator set to Radians",
            'π': "Pi constant (~3.14159265)", 'e': "Euler's constant (~2.71828182)",
            'i': "Imaginary unit constant identifier (i)",
            'a×b': "Factorize: Breaks down a whole integer into its lowest prime factors",
            '0': "Digit 0", '.': "Decimal separating point",
            'x': "Algebraic input token placeholder variable",
            'f(x)': "Evaluates saved algebra formula against current screen display number",
            '=': "Evaluate sequential expression / Lock template function definition"
        }

        # --- ADVANCED SCIENTIFIC VIEW (5x10) ---
        self.adv_widget = QWidget()
        adv_grid = QGridLayout(self.adv_widget)
        adv_grid.setContentsMargins(0, 0, 0, 0)
        adv_grid.setSpacing(6)
        
        adv_buttons = [
            ('↑¹', 0, 0), ('x²', 0, 1), ('xʸ', 0, 2), ('conj', 0, 3), ('x⁻¹', 0, 4), ('C', 0, 5), ('↑n', 0, 6), ('↓n', 0, 7), ('÷', 0, 8), ('mod', 0, 9),
            ('sin', 1, 0), ('sinh', 1, 1), ('logʸ', 1, 2), ('Arg', 1, 3), ('[x]', 1, 4), ('7', 1, 5), ('8', 1, 6), ('9', 1, 7), ('×', 1, 8), ('%', 1, 9),
            ('cos', 2, 0), ('cosh', 2, 1), ('log', 2, 2), ('Re', 2, 3), ('|x|', 2, 4), ('4', 2, 5), ('5', 2, 6), ('6', 2, 7), ('−', 2, 8), ('()', 2, 9),
            ('tan', 3, 0), ('tanh', 3, 1), ('ln', 3, 2), ('Im', 3, 3), ('x!', 3, 4), ('1', 3, 5), ('2', 3, 6), ('3', 3, 7), ('+', 3, 8), ('=', 3, 9),
            ('Deg', 4, 0), ('π', 4, 1), ('e', 4, 2), ('i', 4, 3), ('a×b', 4, 4), ('0', 4, 5), ('.', 4, 6), ('x', 4, 7), ('f(x)', 4, 8), ('=', 4, 9)
        ]
        
        for text, r, c in adv_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(46)
            self.style_button(btn, text)
            
            if text in self.tooltip_map:
                btn.setToolTip(self.tooltip_map[text])
                
            if text in ['sin', 'sinh', 'cos', 'cosh', 'tan', 'tanh', 'log', 'ln']:
                self.shifted_buttons[text] = btn
                
            btn.clicked.connect(lambda checked, t=text: self.handle_action_route(t))
            if text == '=' and r == 3:
                adv_grid.addWidget(btn, 3, 9, 2, 1)
            elif text == '=' and r == 4:
                continue
            else:
                adv_grid.addWidget(btn, r, c)

        # --- STANDARD BASIC VIEW (5x5) ---
        self.std_widget = QWidget()
        std_grid = QGridLayout(self.std_widget)
        std_grid.setContentsMargins(0, 0, 0, 0)
        std_grid.setSpacing(6)
        
        std_buttons = [
            ('C', 0, 0), ('↑n', 0, 1), ('↓n', 0, 2), ('÷', 0, 3), ('mod', 0, 4),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3), ('%', 1, 4),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('−', 2, 3), ('()', 2, 4),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3), ('=', 3, 4),
            ('0', 4, 0), ('.', 4, 1), ('x', 4, 2), ('f(x)', 4, 3)
        ]
        
        for text, r, c in std_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(46)
            self.style_button(btn, text)
            if text in self.tooltip_map:
                btn.setToolTip(self.tooltip_map[text])
            btn.clicked.connect(lambda checked, t=text: self.handle_action_route(t))
            if text == '=' and r == 3:
                std_grid.addWidget(btn, 3, 4, 2, 1)
            elif text == '=' and r == 4:
                continue
            else:
                std_grid.addWidget(btn, r, c)

        self.keypad_stack.addWidget(self.adv_widget)
        self.keypad_stack.addWidget(self.std_widget)
        calc_layout.addWidget(self.keypad_stack)
        
        self.splitter.addWidget(calc_container)

        history_container = QWidget()
        history_container.setObjectName("HistoryContainer")
        history_layout = QVBoxLayout(history_container)
        history_layout.setContentsMargins(4, 0, 0, 0)
        history_layout.setSpacing(8)
        
        history_header = QLabel("Calculation Audit Trail")
        history_header.setObjectName("HistoryHeader")
        
        self.history_list = QListWidget()
        self.history_list.setObjectName("HistoryList")
        
        clear_hist_btn = QPushButton("Clear Ledger History")
        clear_hist_btn.setObjectName("ClearHistBtn")
        clear_hist_btn.setFixedHeight(34)
        clear_hist_btn.clicked.connect(self.clear_all_history_data)
        
        history_layout.addWidget(history_header)
        history_layout.addWidget(self.history_list)
        history_layout.addWidget(clear_hist_btn)
        
        self.splitter.addWidget(history_container)
        self.splitter.setSizes([580, 230])
        outer_layout.addWidget(self.splitter)

    def style_button(self, btn, text):
        if text.isdigit() or text == '.': btn.setProperty("class", "num-btn")
        elif text in ['÷', '×', '−', '+', 'mod', '%', '()']: btn.setProperty("class", "math-op-btn")
        elif text in ['C']: btn.setProperty("class", "clear-btn")
        elif text == '=': btn.setProperty("class", "equal-btn")
        elif text in ['↑n', '↓n', 'Deg', 'Rad']: btn.setProperty("class", "nav-btn")
        elif text == '↑¹': btn.setProperty("class", "shift-btn-inactive")
        elif text in ['x', 'f(x)']: btn.setProperty("class", "algebra-btn")
        else: btn.setProperty("class", "sci-function-btn")

    def switch_mode_view(self, selected_mode):
        if selected_mode == "Standard Basic Mode":
            self.keypad_stack.setCurrentWidget(self.std_widget)
            self.setMinimumSize(QSize(460, 560))
            self.resize(480, 580)
        else:
            self.keypad_stack.setCurrentWidget(self.adv_widget)
            self.setMinimumSize(QSize(800, 560))
            self.resize(850, 580)

    def apply_premium_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #1E1E1E; color: #F0F0F0; font-family: sans-serif; }
            QComboBox { background-color: #2D2D2D; border: 1px solid #3D3D3D; border-radius: 6px; padding: 6px 14px; color: #FFFFFF; }
            #DisplayPanel { background-color: #161616; border: 1px solid #2B2B2B; border-radius: 8px; }
            #FormulaDisplay { color: #7F7F7F; font-size: 14px; min-height: 20px; }
            #WarningDisplay { color: #FF6B6B; font-size: 13px; font-weight: 500; min-height: 18px; padding-top: 2px; }
            #ModeIndicator {
                color: #3584E4; font-size: 11px; font-weight: bold; background-color: #1F2A3D;
                border: 1px solid #2B3D5C; border-radius: 4px; padding: 2px 6px; max-width: 30px;
            }
            #MainDisplay { color: #FFFFFF; font-size: 34px; font-weight: 600; }
            QPushButton { border: 1px solid #2A2A2A; border-radius: 6px; font-size: 14px; background-color: #2A2A2A; color: #E5E5E5; }
            QPushButton:hover { background-color: #363636; border: 1px solid #444444; }
            QPushButton[class="num-btn"] { background-color: #323232; color: #FFFFFF; font-weight: 600; font-size: 16px; }
            QPushButton[class="num-btn"]:hover { background-color: #3D3D3D; }
            QPushButton[class="math-op-btn"] { background-color: #262626; color: #FFFFFF; font-size: 16px; }
            QPushButton[class="sci-function-btn"] { background-color: #222222; color: #CCCCCC; font-size: 13px; }
            QPushButton[class="nav-btn"] { background-color: #252A34; color: #4A90E2; font-weight: bold; }
            QPushButton[class="nav-btn"]:hover { background-color: #2F3644; }
            QPushButton[class="shift-btn-inactive"] { background-color: #252A34; color: #4A90E2; font-weight: bold; }
            QPushButton[class="shift-btn-inactive"]:hover { background-color: #2F3644; }
            QPushButton[class="shift-btn-active"] { background-color: #3584E4; color: #FFFFFF; font-weight: bold; border: 1px solid #64B5FF; }
            QPushButton[class="algebra-btn"] { background-color: #2E2534; color: #B97CE9; font-weight: bold; }
            QPushButton[class="algebra-btn"]:hover { background-color: #3B2F44; }
            QPushButton[class="clear-btn"] { background-color: #2D2D2D; color: #FF6B6B; font-weight: bold; }
            QPushButton[class="clear-btn"]:hover { background-color: #E05A47; color: #FFFFFF; }
            QPushButton[class="equal-btn"] { background-color: #3584E4; color: #FFFFFF; font-size: 22px; font-weight: bold; border: none; }
            QPushButton[class="equal-btn"]:hover { background-color: #4B96F3; }
            #HistoryHeader { font-size: 12px; font-weight: 600; color: #3584E4; text-transform: uppercase; }
            #HistoryList { background-color: #161616; border: 1px solid #2B2B2B; border-radius: 8px; color: #D0D0D0; font-size: 13px; }
            #ClearHistBtn { background-color: #2A2A2A; border: 1px solid #3A3A3A; border-radius: 6px; color: #A0A0A0; }
            QSplitter::handle { background-color: transparent; }
            QToolTip { background-color: #161616; color: #B3B3B3; font-size: 12px; border: 1px solid #3584E4; border-radius: 4px; padding: 5px 8px; }
        """)

    def handle_action_route(self, char):
        self.warning_display.setText("") # Clear warnings instantly upon typing
        
        normalized_char = char
        if self.is_shifted:
            shift_conversion_map = {
                'sin': 'sin⁻¹', 'sinh': 'sinh⁻¹', 'cos': 'cos⁻¹', 'cosh': 'cosh⁻¹',
                'tan': 'tan⁻¹', 'tanh': 'tanh⁻¹', 'log': '10\u02e3', 'ln': 'e\u02e3'
            }
            if char in shift_conversion_map:
                normalized_char = shift_conversion_map[char]

        if normalized_char in '0123456789.': self.append_token(normalized_char)
        elif normalized_char in ['+', '−', '×', '÷', 'mod']: self.append_token(f" {normalized_char} ")
        elif normalized_char in ['sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh', 'log', 'ln', 
                                 'sin⁻¹', 'cos⁻¹', 'tan⁻¹', 'sinh⁻¹', 'cosh⁻¹', 'tanh⁻¹', 
                                 '10\u02e3', 'e\u02e3', '[x]', '|x|', 'x!', 'x²', 'x⁻¹', 'conj', 'Arg', 'Re', 'Im']:
            self.append_token(f" {normalized_char} ")
        elif normalized_char in ['π', 'e', 'i']: self.append_token(normalized_char)
        elif normalized_char in ['(', ')']: self.append_token(normalized_char)
        elif normalized_char == '()': self.handle_bracket_logic()
        elif normalized_char in ['Deg', 'Rad']: self.toggle_angle_metrics(normalized_char)
        elif normalized_char == 'a×b': self.factorize_integer_input()
        elif normalized_char == 'xʸ': self.append_token(" ^ ")
        elif normalized_char == 'C': self.reset_calculator()
        elif normalized_char == '↑n': self.navigate_history(-1)
        elif normalized_char == '↓n': self.navigate_history(1)
        elif normalized_char == 'x': self.append_token("x")
        elif normalized_char == 'f(x)': self.evaluate_saved_function()
        elif normalized_char == '↑¹': self.toggle_shift_state()
        elif normalized_char == '=': self.resolve_computation()
        
        if self.is_shifted and char != '↑¹':
            self.toggle_shift_state()
            
        self.adjust_font_scaling()

    def append_token(self, token):
        if self.current_expression == "0" and token not in ['.', ' + ', ' − ', ' × ', ' ÷ ', ' mod ']:
            self.current_expression = token
        else:
            self.current_expression += token
        self.display.setText(self.current_expression)

    def handle_bracket_logic(self):
        open_count = self.current_expression.count('(')
        close_count = self.current_expression.count(')')
        token = ')' if open_count > close_count and self.current_expression[-1] not in [' ', '('] else '('
        self.append_token(token)

    def toggle_shift_state(self):
        self.is_shifted = not self.is_shifted
        sender = self.sender()
        if self.is_shifted:
            sender.setProperty("class", "shift-btn-active")
            label_map = {
                'sin': 'sin⁻¹', 'sinh': 'sinh⁻¹', 'cos': 'cos⁻¹', 'cosh': 'cosh⁻¹',
                'tan': 'tan⁻¹', 'tanh': 'tanh⁻¹', 'log': '10\u02e3', 'ln': 'e\u02e3'
            }
        else:
            sender.setProperty("class", "shift-btn-inactive")
            label_map = {
                'sin': 'sin', 'sinh': 'sinh', 'cos': 'cos', 'cosh': 'cosh',
                'tan': 'tan', 'tanh': 'tanh', 'log': 'log', 'ln': 'ln'
            }
        sender.style().unpolish(sender)
        sender.style().polish(sender)
        for base_key, widget in self.shifted_buttons.items():
            new_text = label_map[base_key]
            widget.setText(new_text)
            if new_text in self.tooltip_map:
                widget.setToolTip(self.tooltip_map[new_text])

    def factorize_integer_input(self):
        try:
            if " " in self.current_expression: raise ValueError
            val = int(self.current_expression)
            if val < 2: raise ValueError
            n, original = val, val
            factors = []
            d = 2
            while d * d <= n:
                while (n % d) == 0:
                    factors.append(d)
                    n //= d
                d += 1
            if n > 1: factors.append(n)
            res_str = "×".join(map(str, factors))
            self.add_history_record(f"fact({original})", res_str)
            self.current_expression = res_str
            self.display.setText(res_str)
        except ValueError:
            self.warning_display.setText("Need an integer to factorize")

    def toggle_angle_metrics(self, current_label):
        if self.angle_mode == "Deg":
            self.angle_mode = "Rad"
            self.mode_indicator.setText("RAD")
            self.sender().setText("Rad")
        else:
            self.angle_mode = "Deg"
            self.mode_indicator.setText("DEG")
            self.sender().setText("Deg")

    def evaluate_saved_function(self):
        if not self.saved_function:
            self.warning_display.setText("No function template saved")
            return
        self.current_expression = f" {self.saved_function} "
        self.display.setText(self.current_expression)

    def resolve_computation(self):
        raw_expr = self.current_expression.strip()
        if raw_expr in ["", "0"]: return
        
        # Guard Check: Catch trailing binary operators gracefully to prevent syntax evaluation crashes
        if raw_expr.endswith(('+', '−', '×', '÷', 'mod', '^')):
            self.warning_display.setText("Incomplete expression trailing operator")
            return
        
        if 'x' in raw_expr and 'f(x)' not in raw_expr:
            self.saved_function = raw_expr
            self.formula_display.setText("Saved Template f(x):")
            self.display.setText("f(x) Locked")
            self.current_expression = "0"
            return

        try:
            # Map operators explicitly to Python arithmetic models
            stmt = raw_expr.replace('×', '*').replace('−', '-').replace('÷', '/').replace('mod', '%').replace('^', '**')
            stmt = stmt.replace('π', f"({math.pi})").replace('e', f"({math.e})").replace('i', '1j')
            
            token_ops = ['sin⁻¹', 'cos⁻¹', 'tan⁻¹', 'sinh⁻¹', 'cosh⁻¹', 'tanh⁻¹', 
                         'sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh', 'log', 'ln', 
                         '10\u02e3', 'e\u02e3', r'\[x\]', r'\|x\|', 'x!', 'x²', 'x⁻¹', 'conj', 'Arg', 'Re', 'Im']
            
            for op in token_ops:
                cleaned_op = op.replace('\\', '')
                if cleaned_op in stmt:
                    prefix_pattern = r'\b' + re.escape(cleaned_op) + r'\s*\(([^)]+)\)'
                    def prefix_repl(match):
                        inner_target = match.group(1)
                        return f"self._run_unary('{cleaned_op}', {inner_target})"
                    stmt, counts = re.subn(prefix_pattern, prefix_repl, stmt)
                    
                    if counts == 0:
                        parts = stmt.split(cleaned_op)
                        if len(parts) == 2 and parts[0].strip() != "":
                            target = parts[0].strip()
                            stmt = f"self._run_unary('{cleaned_op}', {target}) {parts[1]}"
            
            raw_ans = eval(stmt)
            
            if isinstance(raw_ans, complex):
                real = 0.0 if abs(raw_ans.real) < 1e-12 else raw_ans.real
                imag = 0.0 if abs(raw_ans.imag) < 1e-12 else raw_ans.imag
                ans_str = f"{real}+{imag}j".replace('+-', '-').replace('+0.0j', '').replace('-0.0j', '')
                if ans_str.endswith(('+', '-')): ans_str = ans_str[:-1]
                if ans_str == "": ans_str = "0"
            else:
                ans_str = str(int(raw_ans) if raw_ans.is_integer() else round(raw_ans, 10))
                
            self.add_history_record(raw_expr, ans_str)
            self.display.setText(ans_str)
            self.current_expression = ans_str
            
        except Exception:
            self.display.setText("Syntax Error")
            self.current_expression = "0"

    def _run_unary(self, op, val):
        is_complex = isinstance(val, complex)
        rad_val = math.radians(val.real) if self.angle_mode == "Deg" and not is_complex else val.real
        
        if op == 'sin': return math.sin(rad_val) if not is_complex else math.sin(val)
        elif op == 'sin⁻¹': return math.degrees(math.asin(val.real)) if self.angle_mode == "Deg" else math.asin(val.real)
        elif op == 'cos': return math.cos(rad_val) if not is_complex else math.cos(val)
        elif op == 'cos⁻¹': return math.degrees(math.acos(val.real)) if self.angle_mode == "Deg" else math.acos(val.real)
        elif op == 'tan': return math.tan(rad_val) if not is_complex else math.tan(val)
        elif op == 'tan⁻¹': return math.degrees(math.atan(val.real)) if self.angle_mode == "Deg" else math.atan(val.real)
        elif op == 'sinh': return math.sinh(val.real)
        elif op == 'sinh⁻¹': return math.asinh(val.real)
        elif op == 'cosh': return math.cosh(val.real)
        elif op == 'cosh⁻¹': return math.acosh(val.real)
        elif op == 'tanh': return math.tanh(val.real)
        elif op == 'tanh⁻¹': return math.atanh(val.real)
        elif op == 'log': return math.log10(val.real)
        elif op == '10\u02e3': return 10 ** val.real
        elif op == 'ln': return math.log(val.real)
        elif op == 'e\u02e3': return math.exp(val.real)
        elif op == '[x]': return int(val.real)
        elif op == '|x|': return abs(val)
        elif op == 'x²': return val ** 2
        elif op == 'x⁻¹': return 1 / val
        elif op == 'conj': return val.conjugate() if is_complex else complex(val).conjugate()
        elif op == 'Arg': return math.atan2(val.imag, val.real)
        elif op == 'Re': return val.real
        elif op == 'Im': return val.imag
        elif op == 'x!': return math.factorial(int(val.real))
        return val

    def add_history_record(self, formula, result):
        self.history_ledger.append((formula, result))
        self.history_list.addItem(f"{formula} = {result}")
        self.history_list.scrollToBottom()
        self.history_index = len(self.history_ledger)

    def navigate_history(self, direction):
        if not self.history_ledger: return
        new_index = self.history_index + direction
        if 0 <= new_index < len(self.history_ledger):
            self.history_index = new_index
            formula, result = self.history_ledger[self.history_index]
            self.formula_display.setText(f"[Log {self.history_index + 1}]")
            self.current_expression = formula
            self.display.setText(formula)
        elif new_index >= len(self.history_ledger):
            self.history_index = len(self.history_ledger)
            self.reset_calculator()

    def clear_all_history_data(self):
        self.history_list.clear()
        self.history_ledger.clear()
        self.history_index = -1

    def reset_calculator(self):
        self.current_expression = "0"
        self.display.setText("0")
        self.formula_display.setText("")
        self.warning_display.setText("")

    def adjust_font_scaling(self):
        length = len(self.display.text())
        size = "16px" if length > 28 else "24px" if length > 16 else "34px"
        self.display.setStyleSheet(f"font-size: {size}; font-weight: 600;")

# --- NATIVE LINUX APPLICATION RUNTIME EXECUTION HUB ---
if __name__ == "__main__":
    # Create a fresh, native operating system desktop execution process
    app = QApplication(sys.argv)
    
    # Initialize your premium calculator widget layer
    premium_calc = PremiumScientificCalculator()
    premium_calc.show()
    
    # Hand control over to the system graphics server event loop context
    sys.exit(app.exec())