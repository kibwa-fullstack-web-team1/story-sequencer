import boto3
import os
import uuid
from botocore.exceptions import ClientError
import logging
from typing import Optional

class S3Service:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.s3_client = None
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'memory-garden-images')
        self.region = os.getenv('AWS_REGION', 'ap-southeast-1')
        
        # AWS 자격 증명 설정
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if aws_access_key_id and aws_secret_access_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=self.region
                )
                self.logger.info(f"S3 client initialized successfully for bucket: {self.bucket_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize S3 client: {e}")
                self.s3_client = None
        else:
            self.logger.warning("AWS 자격 증명이 설정되지 않았습니다. S3 기능을 사용할 수 없습니다.")

    def init_app(self, app):
        """앱 초기화"""
        self.logger.info("S3Service initialized")
        return self

    def upload_image(self, file_content: bytes, file_extension: str) -> Optional[str]:
        """이미지를 S3에 업로드하고 URL을 반환"""
        if not self.s3_client:
            self.logger.error("S3 클라이언트가 초기화되지 않았습니다.")
            return None
        
        try:
            # 고유한 파일명 생성
            file_name = f"story-images/{uuid.uuid4()}.{file_extension}"
            
            # S3에 업로드 (ACL 제거)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_content,
                ContentType=f'image/{file_extension}',
                # ACL='public-read'  # ACL 제거 - 버킷 정책으로 접근 제어
            )
            
            # S3 URL 생성
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_name}"
            self.logger.info(f"이미지 업로드 성공: {s3_url}")
            
            return s3_url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            self.logger.error(f"S3 업로드 실패 - Code: {error_code}, Message: {error_message}")
            
            # ACL 오류인 경우 ACL 없이 재시도
            if error_code == 'AccessControlListNotSupported':
                self.logger.info("ACL not supported, retrying without ACL...")
                try:
                    self.s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=file_name,
                        Body=file_content,
                        ContentType=f'image/{file_extension}'
                    )
                    s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_name}"
                    self.logger.info(f"이미지 업로드 성공 (ACL 없이): {s3_url}")
                    return s3_url
                except Exception as retry_error:
                    self.logger.error(f"Retry upload failed: {retry_error}")
                    return None
            
            return None
        except Exception as e:
            self.logger.error(f"이미지 업로드 중 오류 발생: {e}")
            return None

    def delete_image(self, image_url: str) -> bool:
        """S3에서 이미지 삭제"""
        if not self.s3_client:
            self.logger.error("S3 클라이언트가 초기화되지 않았습니다.")
            return False
        
        try:
            # URL에서 키 추출
            key = image_url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/")[-1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            self.logger.info(f"이미지 삭제 성공: {key}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            self.logger.error(f"S3 삭제 실패 - Code: {error_code}, Message: {error_message}")
            return False
        except Exception as e:
            self.logger.error(f"이미지 삭제 중 오류 발생: {e}")
            return False 