#########
Changelog
#########

Version 2.2.0
=============
- Prometheus metrics
- Fixing issues with threading => main thread is now looping forever
- FastAPI and uvicorn used to provide Prometheus endpoint

Version 2.1.0
=============
- Including Status report functionality via mqtt

Version 2.0.3
=============
- Issue works for better stability
- Documentation improvement
- Refactoring

Version 2.0.2
=============
- Include sensor update example for axistests

Version 2.0.1
=============
- Include warning about template usage
- Fix os environment setting with monkeypatch in conftest.py of the template

Version 2.0.0
=============
- Major update from threading to asyncio concurrency

Version 1.2
===========
- Provide async_not_ready function for testing purposes
- Migrate to pytest framework

Version 1.1
===========

- Update messaging to new json specification allowing body usage and provide setup for signature creation

Version 1.0
===========

- Move to pyscaffold
