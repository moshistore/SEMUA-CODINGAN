from flask import Flask, render_template_string, request
import itertools
from sympy import symbols
from sympy.parsing.sympy_parser import parse_expr

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Generator Tabel Kebenaran</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f8; }
        .container { max-width: 700px; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { color: #333; }
        input[type="text"] { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 15px; font-size: 16px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
        th { background-color: #007bff; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .note { background: #e9ecef; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 14px; }
        .error { color: red; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Generator Tabel Kebenaran Logika</h2>
        
        <div class="note">
            <strong>Notasi Operator:</strong><br>
            • AND: <code>&</code> &nbsp;&nbsp; • OR: <code>|</code> &nbsp;&nbsp; • NOT: <code>~</code> &nbsp;&nbsp; • IMPLIES: <code>>></code><br>
            <em>Contoh: <code>(A & B) | ~C</code> atau <code>(P >> Q) & (Q >> P)</code></em>
        </div>

        <form method="POST">
            <input type="text" name="expression" value="{{ expression }}" placeholder="Masukkan ekspresi logika..." required>
            <button type="submit">Proses</button>
        </form>

        {% if error %}
            <p class="error"><strong>Error:</strong> {{ error }}</p>
        {% endif %}

        {% if headers %}
            <h3>Hasil Ekspresi: <code>{{ expression }}</code></h3>
            <table>
                <thead>
                    <tr>
                        {% for h in headers %}
                            <th>{{ h }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                        <tr>
                            {% for cell in row %}
                                <td><strong>{{ cell }}</strong></td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </div>
</body>
</html>
"""

def generate_table_data(expression_str):
    local_dict = {
        'A': symbols('A'), 'B': symbols('B'), 'C': symbols('C'),
        'P': symbols('P'), 'Q': symbols('Q'), 'R': symbols('R')
    }
    
    expr = parse_expr(expression_str, local_dict=local_dict)
    vars_in_expr = sorted(list(expr.free_symbols), key=lambda x: x.name)
    
    if not vars_in_expr:
        return None, None

    headers = [str(v) for v in vars_in_expr] + ["Hasil"]
    num_vars = len(vars_in_expr)
    combinations = list(itertools.product([True, False], repeat=num_vars))

    rows = []
    for combo in combinations:
        val_map = {var: val for var, val in zip(vars_in_expr, combo)}
        result = bool(expr.subs(val_map))
        
        row = ["T" if val else "F" for val in combo]
        row.append("T" if result else "F")
        rows.append(row)
        
    return headers, rows

@app.route("/", methods=["GET", "POST"])
def index():
    headers, rows, error = None, None, None
    expression = ""
    
    if request.method == "POST":
        expression = request.form.get("expression", "")
        try:
            headers, rows = generate_table_data(expression)
        except Exception as e:
            error = f"Gagal memproses ekspresi! Pastikan format input benar."

    return render_template_string(HTML_TEMPLATE, headers=headers, rows=rows, expression=expression, error=error)

if __name__ == "__main__":
    app.run(debug=True, port=5000)