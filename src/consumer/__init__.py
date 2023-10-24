import uvicorn


def start_dev():
    """
    Helper function for running with `poetry run dev`.
    """
    uvicorn.run(
        "provisioning.main:app",
        log_config="logging.yaml",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )
