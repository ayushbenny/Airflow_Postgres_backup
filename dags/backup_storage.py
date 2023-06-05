# Import necessary modules
import os
from dotenv import load_dotenv
import boto3
from botocore.client import Config
import requests

# Load environment variables from the .env file in the same directory
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


# Define a class 'S3Boto'
class S3Boto:
    """
    A class used to upload backup files to AWS S3 Bucket using pre-signed URLs

    Attributes:
    backup_file (str): The name of the file to be uploaded

    Methods:
    _boto_conn: Retrieves an S3 client connection from boto3 using environment variables for authentication
    _s3_presigned_url: Generates a presigned URL for uploading the given backup file to an S3 bucket
    upload_to_s3: Uploads the backup file contents to the S3 bucket using the presigned URL
    """

    def __init__(self, backup_file: str):
        """
        Initializes a S3Boto object with the specified backup file name

        Parameters:
        backup_file (str): The name of the file to be uploaded
        """
        self.backup_file = backup_file
        self.boto_conn = self._boto_conn
        self.s3_presigned_url = self._s3_presigned_url

    @property
    def _boto_conn(self) -> "boto3.client":
        """
        Returns a boto3 client connection to AWS S3 using environment variables for authentication

        Returns:
        boto3.client: An S3 client connection with specified credentials and region
        """
        _s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("REGION_NAME"),
            config=Config(signature_version=os.getenv("SIGNATURE_VERSION")),
        )

        return _s3

    @property
    def _s3_presigned_url(self) -> str:
        """
        Generates a presigned URL for uploading the given backup file to an S3 bucket

        Returns:
        str: A presigned URL with a 1 hour expiration time
        """
        conn = self.boto_conn
        presigned_url = conn.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": os.getenv("S3_BUCKET_NAME"),
                "Key": self.backup_file,
            },
            ExpiresIn=3600,
        )
        return presigned_url

    def upload_to_s3(self) -> "requests.Response":
        """
        Uploads the backup file contents to the S3 bucket using the presigned URL

        Returns:
        requests.Response: The response from the PUT request
        """
        pre_signed_url = self.s3_presigned_url
        try:
            with open(self.backup_file, "rb") as file:
                file_contents = file.read()
        except Exception as err:
            return dict(status="Failed", message=str(err))
        response = requests.put(pre_signed_url, data=file_contents)
        return response
