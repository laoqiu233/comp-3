import logging
from io import StringIO

import pytest

from comp3.compiler import compile_pipeline
from comp3.machine import main


@pytest.mark.golden_test("golden_tests/*.yml")
def test_golden(golden, caplog, capsys, tmpdir):
    caplog.set_level(logging.DEBUG)

    compiled_prog_buffer = StringIO()
    with open(golden["in_source"], encoding="utf-8") as code_source:
        compile_pipeline(code_source, compiled_prog_buffer)
    compiled_prog = compiled_prog_buffer.getvalue()

    assert golden.out["out_prog"] == compiled_prog

    with open(tmpdir / "tmp_prog.json", "w", encoding="utf-8") as file:
        file.write(compiled_prog)

    main(tmpdir / "tmp_prog.json", golden["in"])

    assert caplog.text == golden.out["out_logs"]
    assert capsys.readouterr().out == golden.out["out"]
