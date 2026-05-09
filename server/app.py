from flask import Flask, request, jsonify
from flask_cors import CORS

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import analyse
from compiler.optimizer import optimize
from compiler.codegen import generate

app = Flask(__name__)
CORS(app)


@app.route("/api/compile", methods=["POST"])
def compile_code():
    body = request.get_json(silent=True) or {}
    source: str = body.get("code", "")

    # ── 1. Lexical analysis ──────────────────────────────────────────────
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    errors = [e.to_dict() for e in lexer.errors]
    token_list = [t.to_dict() for t in tokens if t.type != "EOF"]

    # ── 2. Syntactic analysis + TAC generation ───────────────────────────
    parser = Parser(tokens)
    tac, parse_errors, ast = parser.parse()
    errors.extend(e.to_dict() for e in parse_errors)

    # ── 3. Semantic analysis ─────────────────────────────────────────────
    symbol_table, semantic_errors = analyse(ast)
    semantic_error_dicts = [e.to_dict() for e in semantic_errors]
    errors.extend(semantic_error_dicts)

    # ── 4. Optimization ──────────────────────────────────────────────────
    optimized_tac = optimize(tac)

    # ── 5. Code generation ───────────────────────────────────────────────
    machine_code = generate(optimized_tac)

    return jsonify({
        "tokens": token_list,
        "ast": ast,
        "symbol_table": symbol_table,
        "semantic_errors": semantic_error_dicts,
        "tac": tac,
        "optimized_tac": optimized_tac,
        "machine_code": machine_code,
        "errors": errors,
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
