import functools
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Dict

import boto3
from botocore.exceptions import ClientError


class ParrotLogger:
    """A custom logger class that wraps Python's built-in logging functionality.
    This class provides a simplified interface for logging messages with different
    severity levels (info, error, warning, debug) to the console. It automatically
    configures a console handler with a standard formatting pattern.
    Args:
        name (str): The name of the logger instance.
        log_level (int, optional): The minimum logging level. Defaults to logging.INFO.
            Use logging constants like logging.DEBUG, logging.INFO, etc.
    Attributes:
        logger (logging.Logger): The underlying Logger instance from the logging module.
    Example:
        >>> logger = ParrotLogger("my_app")
        >>> logger.info("Application started")
        2023-07-21 10:30:15,123 - my_app - INFO - Application started
    """

    # Remove duplicated logs
    _instances = {}

    def __new__(cls, name):
        if name not in cls._instances:
            instance = super(ParrotLogger, cls).__new__(cls)
            instance.logger = logging.getLogger(name)
            handler_exists = any(
                isinstance(handler, logging.StreamHandler)
                for handler in instance.logger.handlers
            )
            if not handler_exists:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "%(asctime)s - %(request_id)s - %(logger_name)s  - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                instance.logger.addHandler(handler)
            cls._instances[name] = instance
        return cls._instances[name]

    def __init__(
        self,
        name: str,
        log_level=logging.INFO,
        profile_name: str = None,
        request_id: str = None,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        handler_exists = any(
            isinstance(handler, logging.StreamHandler)
            for handler in self.logger.handlers
        )
        if not handler_exists:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(request_id)s - %(logger_name)s  - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, message, logger_name="N/A", req_id="N/A"):
        self.logger.info(
            message, extra={"request_id": req_id, "logger_name": logger_name}
        )

    def error(self, message, logger_name="N/A", req_id="N/A"):
        self.logger.error(
            message, extra={"request_id": req_id, "logger_name": logger_name}
        )

    def warning(self, message, logger_name="N/A", req_id="N/A"):
        self.logger.warning(
            message, extra={"request_id": req_id, "logger_name": logger_name}
        )

    def debug(self, message, logger_name="N/A", req_id="N/A"):
        self.logger.debug(
            message, extra={"request_id": req_id, "logger_name": logger_name}
        )

    time.time()


def async_timed(logger):
    """Decorador para medir el tiempo de ejecución de funciones asíncronas"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            function_name = func.__name__
            logger.info(f"Iniciando {function_name}")
            try:
                result = await func(*args, **kwargs)
                end_time = time.perf_counter()
                total_time = end_time - start_time
                logger.info(
                    f"Función {function_name} completada en {total_time:.2f} segundos"
                )
                return result
            except Exception as e:
                end_time = time.perf_counter()
                total_time = end_time - start_time
                logger.error(
                    f"Función {function_name} falló después de {total_time:.2f} segundos: {str(e)}"
                )
                raise

        return wrapper

    return decorator


class ParrotError:
    def __init__(self):
        pass

    def format_error(
        self, error=None, function_name: str = "", error_message: str = "", reason_redirect: str = ""
    ) -> Dict:
        """Devuelve una respuesta de error estandarizada."""
        # Check if error is an actual Exception object
        if isinstance(error, Exception):
            # Handle proper Exception objects
            tb = traceback.extract_tb(error.__traceback__)
            error_line = tb[-1].lineno if tb else "N/A"
            error_file = tb[-1].filename if tb else "N/A"
            return {
                "error": True,
                "error_technical_message": str(error),
                "error_message": "disculpe, no hemos podido realizar la gestión, vamos a transferir la llamada con un gestor.",
                "error_type": type(error).__name__,
                "error_function": function_name,
                "error_line": error_line,
                "error_file": error_file,
            }
        elif (
            error is not None
        ):  # Handle non-Exception values (like integers or strings)
            return {
                "error": True,
                "error_technical_message": str(error),
                "error_message": "disculpe, no hemos podido realizar la gestión, vamos a transferir la llamada con un gestor.",
                "error_type": type(error).__name__,
                "error_function": function_name,
            }
        else:  # Handle None case
            return {
                "error": True,
                "error_message": error_message or "Error desconocido",
                "error_type": "CustomError",
                "error_function": function_name,
                "reason_redirect": reason_redirect
            }


class KinesisProccess:
    def __init__(self, logger, profile_name: str = None):
        self.logger = logger
        self.profile_name = profile_name
        self.session = (
            boto3.Session(profile_name=self.profile_name)
            if self.profile_name
            else boto3.Session()
        )
        self.req_id = "N/A"
        self.name = "Kinesis Firehose"
        self.client_firehose = self.session.client("firehose", region_name="eu-west-1")

    def send_dict_to_kfh(self, json_logs, buffer):
        """
        Send Custom Dimension Dict to Kinesis Firehose
        Args:
            json_logs
        """
        try:
            self.client_firehose.put_record(
                DeliveryStreamName=buffer, Record={"Data": json_logs}
            )
            self.logger.info(
                f"Put record in stream {buffer} ",
                req_id=self.req_id,
                logger_name=self.name,
            )
        except ClientError:
            self.logger.error(
                f"Couldn't put record in stream {buffer}",
                req_id=self.req_id,
                logger_name=self.name,
            )
            raise

    def save_model_info_to_firehose(self, output_json, buffer):
        """
        Saves the body request and response in S3 bucket.
        :param output_json: response body
        """
        if buffer is None:
            self.logger.info(
                "No output saved in Firehose", req_id=self.req_id, logger_name=self.name
            )
            return
        today = datetime.now()
        event_time = today.strftime("%Y/%m/%d %H:%M:%S.%f")
        output_json["datetime"] = event_time
        json_logs = json.dumps(output_json)
        self.logger.info(json_logs, req_id=self.req_id, logger_name=self.name)
        self.send_dict_to_kfh(json_logs, buffer)

    def process_kinesis_json(self, output_json, information_api, control_group):
        base_schema = {
            "callId": "",
            "open_claim": 0,
            "is_redirect": 0,
            "reason_redirect": "",
            "second_time": 0,
            "interruptions_barge_in": 0,
            "control_group": 0,
            "claim_information": {
                "policyId": "",
                "claimTypeCode": "",
                "effectiveDate": "",
                "claimOcurrenceAddress": {
                    "zipCode": "",
                    "townDesc": "",
                    "provinceCode": "",
                },
                "claimCaller": {"relationshipCode": ""},
                "correspondence": {
                    "address": {"zipCode": "", "townDesc": "", "provinceCode": ""},
                },
                "report": "",
                "claimDamagesSpecific": {
                    "damage": {"damageCode": "", "damageDesc": ""},
                    "brandCode": "",
                    "modelName": "",
                    "years": "",
                    "warranty": "",
                },
            },
            "datetime": "",
        }

        # Update base schema with output_json values
        try:
            output_json["control_group"] = control_group
            base_schema.update(output_json)
            output_json = base_schema

            output_json["callId"] = output_json.get("callId", "")
            output_json["open_claim"] = (
                information_api.patrimoniales_service.claim_opened
            )
            output_json["is_redirect"] = information_api.flag_redirect_agent.get(
                "flag", 0
            )
            output_json["reason_redirect"] = information_api.flag_redirect_agent.get(
                "reason", None
            )

            # output_json["claim_information"] = (
            #     information_api.patrimoniales_service.process_output_json(
            #         information_api.validated_args,
            #         information_api.patrimoniales_service.informacion_api,
            #     )
            #     if not information_api.patrimoniales_service.claim_information
            #     else information_api.patrimoniales_service.claim_information
            # )
            # TYPE CHECK 3: Check if claim_information exists
            if not hasattr(information_api.patrimoniales_service, "claim_information"):
                self.logger.error(
                    "patrimoniales_service has no claim_information attribute",
                    req_id=self.req_id,
                    logger_name=self.name,
                )
                output_json["claim_information"] = {}
            # TYPE CHECK 4: Check if validated_args and informacion_api exist
            elif not information_api.patrimoniales_service.claim_information:
                if not hasattr(information_api, "validated_args"):
                    self.logger.error(
                        "information_api has no validated_args attribute",
                        req_id=self.req_id,
                        logger_name=self.name,
                    )
                    output_json["claim_information"] = {}
                elif not hasattr(
                    information_api.patrimoniales_service, "informacion_api"
                ):
                    self.logger.error(
                        "patrimoniales_service has no informacion_api attribute",
                        req_id=self.req_id,
                        logger_name=self.name,
                    )
                    output_json["claim_information"] = {}
                else:
                    # Everything is valid, proceed with original logic
                    output_json["claim_information"] = (
                        information_api.patrimoniales_service.process_output_json(
                            information_api.validated_args,
                            information_api.patrimoniales_service.informacion_api,
                        )
                    )
            else:
                output_json["claim_information"] = (
                    information_api.patrimoniales_service.claim_information
                )

            # Eliminar el campo adressName dentro de claimOcurrenceAddress
            if "claimOcurrenceAddress" in output_json["claim_information"]:
                output_json["claim_information"]["claimOcurrenceAddress"].pop(
                    "addressName", None
                )

            # Eliminar el campo contactName dentro de claimCaller
            if "claimCaller" in output_json["claim_information"]:
                output_json["claim_information"]["claimCaller"].pop("contactName", None)
                output_json["claim_information"]["claimCaller"].pop(
                    "contactMethod", None
                )

            # Asegurarse de que correspondence tenga solo zipCode, townDesc y provinceCode
            if "correspondence" in output_json["claim_information"]:
                correspondence = output_json["claim_information"]["correspondence"]
                correspondence["address"] = {
                    "zipCode": correspondence.get("address", {}).get("zipCode", ""),
                    "townDesc": correspondence.get("address", {}).get("townDesc", ""),
                    "provinceCode": correspondence.get("address", {}).get(
                        "provinceCode", ""
                    ),
                }
                correspondence.pop("name", None)
                correspondence.pop("contactMethod", None)
                output_json["claim_information"]["correspondence"] = correspondence

            self.logger.info(
                "Saved output and input json.",
                req_id=self.req_id,
                logger_name=self.name,
            )

            return output_json
        except Exception as e:
            self.logger.error(f"Error: {e}", req_id=self.req_id, logger_name=self.name)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.error(
                f"{exc_type} en {fname} línea {exc_tb.tb_lineno}",
                req_id=self.req_id,
                logger_name=self.name,
            )
            raise
