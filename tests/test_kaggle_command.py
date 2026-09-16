from freelance_agent.workers.kaggle import KaggleWorker


def test_kaggle_command_failure_is_explicit() -> None:
    try:
        KaggleWorker._run(["python", "-c", "raise SystemExit(3)"])
    except RuntimeError as exc:
        assert "Kaggle command failed" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")
