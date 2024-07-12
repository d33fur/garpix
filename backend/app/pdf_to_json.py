"""
 Copyright 2024 Adobe
 All Rights Reserved.

 NOTICE: Adobe permits you to use, modify, and distribute this file in
 accordance with the terms of the Adobe license agreement accompanying it.
"""

import logging
import os
import sys
import zipfile
import json
from datetime import datetime

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


class ExtractTextInfoFromPDF:
    def __init__(self, file_name):
        self.json_data = None
      
        try:
            file = open('./' + file_name, 'rb')
            input_stream = file.read()
            file.close()

            credentials = ServicePrincipalCredentials(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET
            )

            pdf_services = PDFServices(credentials=credentials)

            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)

            extract_pdf_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TEXT],
            )

            extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

            location = pdf_services.submit(extract_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

            result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            output_file_path = self.create_output_file_path()
            with open(output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())
                
            self.extract_zip_file(output_file_path, "./docs")
            self.read_json_data("./docs/structuredData.json")
                
            

        except ServiceApiException as service_api_exception:
            self.handle_exception("ServiceApiException",
                                  service_api_exception.message,
                                  service_api_exception.status_code)

        except ServiceUsageException as service_usage_exception:
            self.handle_exception("ServiceUsageException",
                                  service_usage_exception.message,
                                  service_usage_exception.status_code)

        except SdkException as sdk_exception:
            self.handle_exception("SdkException",
                                  sdk_exception.message,
                                  None)

    @staticmethod
    def create_output_file_path() -> str:
        now = datetime.now()
        # time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        time_stamp = "1"
        return f"extract_{time_stamp}.zip"
  
    @staticmethod
    def extract_zip_file(zip_path: str, extract_to: str) -> None:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
      
    def read_json_data(self, json_file_path: str) -> None:
        with open(json_file_path, 'r') as json_file:
            self.json_data = json.load(json_file)
            
    def get_json_data(self) -> dict:
        return self.json_data

    @staticmethod
    def handle_exception(exception_type, exception_message, status_code) -> None:
        logging.info(exception_type)
        if status_code is not None:
            logging.info(status_code)
        logging.info(exception_message)


# if __name__ == "__main__":
#     ExtractTextInfoFromPDF()
