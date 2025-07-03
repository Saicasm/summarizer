from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.tasky import process_query
from django.db import connection
from redis import Redis
from celery import Celery
import requests
from django.conf import settings

class QueryView(APIView):
    def post(self, request):
        query_text = request.data.get('query')
        use_web_search = request.data.get('use_web_search', False)
        if not query_text:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        task = process_query.delay(query_text, use_web_search)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
    
class HealthCheckView(APIView):
    def get(self, request):
        health_status = {
            "status": "healthy",
            "components": {
                "database": {"status": "healthy", "error": None},
                "redis": {"status": "healthy", "error": None},
                "celery": {"status": "healthy", "error": None},
                "openai_api": {"status": "healthy", "error": None},
                "tavily_api": {"status": "healthy", "error": None},
            }
        }
        print("test")
        # Check PostgreSQL
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}

        # Check Redis
        try:
            redis_client = Redis.from_url(settings.CELERY_BROKER_URL)
            redis_client.ping()
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["redis"] = {"status": "unhealthy", "error": str(e)}

        # Check Celery
        try:
            app = Celery('config', broker=settings.CELERY_BROKER_URL)
            stats = app.control.inspect().stats()
            if not stats:
                health_status["status"] = "unhealthy"
                health_status["components"]["celery"] = {"status": "unhealthy", "error": "No active Celery workers"}
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["celery"] = {"status": "unhealthy", "error": str(e)}

        # Check OpenAI API
        try:
            response = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}, timeout=5)
            if response.status_code != 200:
                health_status["status"] = "unhealthy"
                health_status["components"]["openai_api"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["openai_api"] = {"status": "unhealthy", "error": str(e)}

        # Check Tavily API
        try:
            response = requests.post("https://api.tavily.com/search", json={"query": "test", "api_key": settings.TAVILY_API_KEY}, timeout=5)
            if response.status_code != 200:
                health_status["status"] = "unhealthy"
                health_status["components"]["tavily_api"] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["tavily_api"] = {"status": "unhealthy", "error": str(e)}

        return Response(health_status, status=status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE)   
