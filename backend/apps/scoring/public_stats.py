from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.knowledge_base.models import KbChunk
from apps.scoring.models import Penilaian


class PublicStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total_penilaian = Penilaian.objects.filter(
            processing_status="success"
        ).count()

        total_chunk = KbChunk.objects.count()

        return Response({
            "total_penilaian": total_penilaian,
            "total_chunk": total_chunk,
        })