import logging
import os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from livekit.agents.telemetry import set_tracer_provider
from src.config.logging_config import logger
from src.config.settings import (
    LK_AGENT_OTEL_AUTH_CODE,
    LK_AGENT_OTEL_ENABLED,
    LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT,
    LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT,
    LK_AGENT_OTEL_EXPORTER_OTLP_METRICS_ENDPOINT,
    LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED,
    LK_AGENT_OTEL_PYTHON_METRICS_AUTO_INSTRUMENTATION_ENABLED,
)
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from livekit.agents.telemetry import set_tracer_provider

# Import metrics SDK components
from opentelemetry.metrics import set_meter_provider
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


def configure_opentelemetry():
    """Configures the OpenTelemetry tracer provider from environment variables."""
    if LK_AGENT_OTEL_ENABLED == "true":
        otel_endpoint = LK_AGENT_OTEL_EXPORTER_OTLP_ENDPOINT
        otel_authcode = LK_AGENT_OTEL_AUTH_CODE

        if not otel_endpoint or not otel_authcode:
            print(
                "OpenTelemetry environment variables are missing. Telemetry will not be enabled."
            )
            return

        # Set up the tracer provider with the OTLP exporter
        otel_exporter = OTLPSpanExporter(
            endpoint=otel_endpoint,
            headers={"Authorization": f"Basic {otel_authcode}"},
        )
        tracer_provider = TracerProvider(
            resource=Resource.create({"service.name": "tutor-voice-agent"})
        )
        # console_exporter = ConsoleSpanExporter()
        tracer_provider.add_span_processor(BatchSpanProcessor(otel_exporter))
        # tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))

        # Register the provider with the LiveKit Agent telemetry system
        set_tracer_provider(tracer_provider)
        logger.info("Open Telemetry configured for agent request")

    # --- Logs Configuration ---
    if LK_AGENT_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED == "true":
        otel_logs_endpoint = LK_AGENT_OTEL_EXPORTER_OTLP_LOGS_ENDPOINT
        otel_authcode = LK_AGENT_OTEL_AUTH_CODE
        if otel_logs_endpoint and otel_authcode:
            logger_provider = LoggerProvider(
                resource=Resource.create({"service.name": "tutor-voice-agent"})
            )
            log_exporter = OTLPLogExporter(
                endpoint=otel_logs_endpoint,
                headers={"Authorization": f"Basic {otel_authcode}"},
            )
            logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(log_exporter)
            )
            set_logger_provider(logger_provider)

            # Attach OTLP handler to the root logger
            logging.getLogger().addHandler(
                LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
            )
            logging.getLogger().addHandler(
                LoggingHandler(level=logging.ERROR, logger_provider=logger_provider)
            )
            logging.info("OpenTelemetry logger provider configured.")
