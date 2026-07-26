from supercode.ui import build_startup_banner


def test_build_startup_banner_contains_ascii_fish_and_command_bar():
    banner = build_startup_banner()

    assert "<><((('>" in banner
    assert "CMD" in banner
    assert "supercode" in banner.lower()
