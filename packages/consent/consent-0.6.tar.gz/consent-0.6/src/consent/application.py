import dm.application
from dm.ioc import RequiredFeature
import consent.builder

class Application(dm.application.Application):
    "Provides single entry point for clients."

    builderClass = consent.builder.ApplicationBuilder
