#!/usr/bin/env python3

import ast
import contextlib
import io
import json
import sys
import traceback


class PyRepl:
    def __init__(self):
        self.locals = {}

    def _make_error(self, message) -> dict:
        return {
            "error": str(message),
        }

    def _py_exception(self, e) -> dict:
        return {"pyerror": "".join(traceback.format_exception(type(e), e, e.__traceback__))}

    def _eval(self, code):
        try:
            a = ast.parse(code)
        except SyntaxError as e:
            return self._py_exception(e)
        has_ret = False
        if len(a.body) >= 1 and isinstance(a.body[-1], ast.Expr):
            a.body[-1] = ast.parse(f"_ret = {ast.unparse(a.body[-1])}")
            has_ret = True
            code = ast.unparse(a)

        with (
            contextlib.redirect_stdout(io.StringIO()) as stdout_stream,
            contextlib.redirect_stderr(io.StringIO()) as stderr_stream,
        ):
            try:
                exec(code, self.locals)
            except Exception as e:
                return self._py_exception(e)

        stdout = stdout_stream.getvalue()
        stderr = stderr_stream.getvalue()

        ret = self.locals["_ret"] if has_ret else None

        return {
            "ret": repr(ret) if ret is not None else None,
            "stdout": stdout,
            "stderr": stderr,
        }

    def line_json(self, cmd):
        if cmd.get("ping") is not None:
            return {"pong": 17}
        elif cmd.get("eval") is not None:
            code = cmd.get("eval")
            return self._eval(code)
        else:
            return self._make_error("unknown command")

    def line(self, line: str) -> str:
        cmd = json.loads(line)
        ret = self.line_json(cmd)
        return json.dumps(ret)


def run_loop(stdin, stdout):
    repl = PyRepl()
    while True:
        line = stdin.readline()
        if not line:
            break
        line = line.strip()
        ret = repl.line(line)
        stdout.write(f"{ret}\n")
        stdout.flush()


if __name__ == "__main__":
    run_loop(sys.stdin, sys.stdout)
