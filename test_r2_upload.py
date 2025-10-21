# test_r2_upload.py
import os
import boto3
from PIL import Image
import io
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(override=True)

def test_r2_upload():
    """Cloudflare R2에 이미지 업로드 테스트"""
    print("=" * 80)
    print("🧪 Cloudflare R2 이미지 업로드 테스트 시작...")
    print("=" * 80)
    
    try:
        # 환경변수 확인
        access_key = os.getenv('R2_ACCESS_KEY_ID')
        secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
        bucket_name = os.getenv('R2_BUCKET_NAME')
        
        account_id = os.getenv('R2_ACCOUNT_ID')
        
        if not all([access_key, secret_key, bucket_name, account_id]):
            print("❌ 환경변수 설정 오류:")
            print(f"   R2_ACCESS_KEY_ID: {'✅' if access_key else '❌'}")
            print(f"   R2_SECRET_ACCESS_KEY: {'✅' if secret_key else '❌'}")
            print(f"   R2_BUCKET_NAME: {'✅' if bucket_name else '❌'}")
            print(f"   R2_ACCOUNT_ID: {'✅' if account_id else '❌'}")
            return
        
        # 테스트 이미지 생성
        print("📸 테스트 이미지 생성 중...")
        img = Image.new('RGB', (200, 150), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=80)
        buffer.seek(0)
        
        # R2 클라이언트 설정 (boto3 사용)
        r2_client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'
        )
        
        # R2에 업로드
        import time
        timestamp = int(time.time())
        object_key = f"test/chart_test_{timestamp}.jpg"
        print(f"☁️ R2 업로드 중... (버킷: {bucket_name})")
        
        r2_client.upload_fileobj(
            buffer,
            bucket_name,
            object_key,
            ExtraArgs={'ContentType': 'image/jpeg'}
        )
        
        # 공개 URL 생성
        public_url = f"https://{bucket_name}.r2.dev/{object_key}"
        print(f"✅ R2 업로드 성공!")
        print(f"   파일: {object_key}")
        print(f"   URL: {public_url}")
        
        # URL 접근 테스트
        import requests
        print("🔗 URL 접근 테스트 중...")
        test_response = requests.get(public_url)
        if test_response.status_code == 200:
            print("✅ URL 접근 성공!")
        else:
            print(f"❌ URL 접근 실패: {test_response.status_code}")
        
    except ClientError as e:
        print(f"❌ R2 클라이언트 오류: {e}")
    except Exception as e:
        print(f"❌ 업로드 실패: {e}")
    
    print("=" * 80)
    print("✅ R2 테스트 완료!")
    print("=" * 80)

if __name__ == "__main__":
    test_r2_upload()