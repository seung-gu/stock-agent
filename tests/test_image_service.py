#!/usr/bin/env python3
"""이미지 서비스 유닛 테스트"""

import unittest
from unittest.mock import patch, MagicMock
from src.services.image_service import find_local_images, upload_images_to_cloudflare


class TestImageService(unittest.TestCase):
    """이미지 서비스 함수 테스트"""
    
    @patch('src.services.image_service.os.path.exists')
    def test_find_local_images(self, mock_exists):
        """로컬 이미지 찾기 함수 테스트"""
        # Mock 설정: 파일이 존재한다고 가정
        mock_exists.return_value = True
        
        test_content = """
        # 테스트 리포트
        ![차트1](sandbox:/tmp/test1.png)
        ![차트2](sandbox:/tmp/test2.png)
        테스트 완료!
        """
        processed_content, image_files, image_map = find_local_images(test_content)
        
        self.assertIn("테스트 완료!", processed_content)
        self.assertIn("{{IMAGE_PLACEHOLDER:/tmp/test1.png}}", processed_content)
        self.assertIn("{{IMAGE_PLACEHOLDER:/tmp/test2.png}}", processed_content)
        self.assertNotIn("![차트1]", processed_content)
        self.assertNotIn("![차트2]", processed_content)
        self.assertEqual(len(image_files), 2)
        self.assertEqual(len(image_map), 2)
        print("✅ find_local_images 테스트 통과")
    
    @patch('src.services.image_service.os.path.exists')
    def test_find_local_images_with_links(self, mock_exists):
        """링크 형태 이미지 찾기 테스트"""
        mock_exists.return_value = True
        
        test_content = """
        [이미지 링크](sandbox:/tmp/test3.png)
        """
        processed_content, image_files, image_map = find_local_images(test_content)
        
        self.assertIn("{{IMAGE_PLACEHOLDER:/tmp/test3.png}}", processed_content)
        self.assertEqual(len(image_files), 1)
        self.assertEqual(image_map["/tmp/test3.png"], "이미지 링크")
        print("✅ find_local_images (링크) 테스트 통과")
    
    @patch('boto3.client')
    @patch('PIL.Image.open')
    def test_upload_images_to_cloudflare(self, mock_image_open, mock_boto3):
        """R2 이미지 업로드 함수 테스트"""
        # Mock 설정
        mock_img = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        test_files = ["/tmp/test1.png", "/tmp/test2.png"]
        result = upload_images_to_cloudflare(test_files)
        
        self.assertIsInstance(result, dict)
        print("✅ upload_images_to_cloudflare 테스트 통과")
    
    @patch('src.services.image_service.os.path.exists')
    def test_find_local_images_empty(self, mock_exists):
        """이미지가 없는 경우 테스트"""
        mock_exists.return_value = False
        
        test_content = """
        # 텍스트만 있는 리포트
        이미지가 없습니다.
        """
        processed_content, image_files, image_map = find_local_images(test_content)
        
        self.assertEqual(len(image_files), 0)
        self.assertEqual(len(image_map), 0)
        self.assertIn("이미지가 없습니다", processed_content)
        print("✅ find_local_images (빈 케이스) 테스트 통과")


if __name__ == "__main__":
    unittest.main(verbosity=2)

