from rest_framework.routers import DefaultRouter
from .views import SoundCategoryViewSet

router = DefaultRouter()
router.register(r'categories', SoundCategoryViewSet)

urlpatterns = router.urls
