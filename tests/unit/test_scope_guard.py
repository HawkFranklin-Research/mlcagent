from types import SimpleNamespace as NS

from mlca.engine.scope_guard import layer_one


def test_layer_one_allows_slash_in_words_and_checks_real_paths(tmp_path):
    allowed_file = tmp_path / "allowed.csv"
    allowed_file.touch()
    event = NS(custom_scope=NS(deny_patterns=[]))
    state = NS(test_unlocked=False)
    allowed_paths = [allowed_file]

    # Words with slashes must not be treated as filesystem paths
    assert layer_one("use training/validation rows", event, state, allowed_paths) is None
    assert layer_one("and/or evaluate sensitivity/specificity", event, state, allowed_paths) is None

    # Actual undeclared paths must still be caught
    assert (
        layer_one("read /etc/passwd please", event, state, allowed_paths)
        == "Instruction names an undeclared path"
    )
    assert (
        layer_one("load ./secret.csv", event, state, allowed_paths)
        == "Instruction names an undeclared path"
    )
    assert (
        layer_one('look at "/var/log/syslog"', event, state, allowed_paths)
        == "Instruction names an undeclared path"
    )

    # Declared path passes
    assert layer_one(f"read {allowed_file} please", event, state, allowed_paths) is None
