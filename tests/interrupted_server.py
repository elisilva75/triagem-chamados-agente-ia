"""Factory exclusiva de teste: encerra o próprio processo após a aquisição persistida."""

import os

from app.main import create_app


def create_interrupted_app():
    app = create_app()

    class InterruptedProvider:
        def respond(self, *args, **kwargs):
            # Nunca usado pela factory de produção. Exercita perda real do processo.
            os._exit(17)

    app.state.provider = InterruptedProvider()
    return app
