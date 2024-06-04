from django.urls import path, include
from rest_framework.routers import DefaultRouter
from Users.views import (
    UserViewSet,
    PasswordChangeView,
    UserDetailView,
    UserUpdateView,
    ProfessorAvailabilityViewSet,
    ProfessorViewSet,
    ProfessorSearchSuggestionView,
    ProfessorPostListView,
    NormalUserPostListView,
    FollowToggleView,
    FollowingListView,
    FollowerListView,
    PasswordResetRequestView,
    PasswordResetView,
    activate,
)
from Posts.views import (
    PostViewSet, 
    FollowedUsersPostsViewSet, 
    PostSearchSuggestionView, 
    ArticleSearchSuggestionView, 
    PostImageUploadView,
    ToggleLikePostView,
)
from Events.views import EventViewSet, EventRegisterUsersView, EventSearchSuggestionView, OrganizerEventsView, EventImageUploadView
from Bookings.views import BookingViewSet, UserBookingsViewSet
from Videos.views import VideoViewSet
from .api import WsUserTokenObtainPairView, WsUserTokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'events', EventViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'availabilities', ProfessorAvailabilityViewSet)
router.register(r'professors', ProfessorViewSet, basename='professor')
router.register(r'videos', VideoViewSet)

urlpatterns = [
    path('login/', WsUserTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', WsUserTokenRefreshView.as_view(), name='token_refresh'),
    path('events/registered-users/', EventRegisterUsersView.as_view(), name='event-registered-users'),
    path('users/<int:user_id>/organized-events/', OrganizerEventsView.as_view(), name='organized-events'),
    path('users/update-profile/', UserUpdateView.as_view(), name='user-update-profile'),
    path('posts/following/', FollowedUsersPostsViewSet.as_view({'get': 'list'}), name='followed-users-posts'), 
    path('bookings/my/', UserBookingsViewSet.as_view({'get': 'list'}), name='user-bookings'),
    path('professors/search-suggestions/', ProfessorSearchSuggestionView.as_view(), name='professor-search-suggestions'), # This is the search suggestion view
    path('posts/search-suggestions/', PostSearchSuggestionView.as_view(), name='post-search-suggestions'),
    path('articles/search-suggestions/', ArticleSearchSuggestionView.as_view(), name='article-search-suggestions'),
    path('events/search-suggestions/', EventSearchSuggestionView.as_view(), name='event-search-suggestions'),
    path('users/update/', UserUpdateView.as_view(), name='user-update'),
    path('users/change-password/', PasswordChangeView.as_view(), name='password-change'),
    path('posts/professors/', ProfessorPostListView.as_view(), name='professor-posts'),
    path('posts/userpost/', NormalUserPostListView.as_view(), name='professor-posts'),
    path('users/follow/', FollowToggleView.as_view(), name='follow-toggle'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/me/following/', FollowingListView.as_view(), name='following-list'),
    path('users/me/followers/', FollowerListView.as_view(), name='follower-list'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', PasswordResetView.as_view(), name='password_reset'),
    path('events/upload-image/', EventImageUploadView.as_view(), name='event-upload-image'),
    path('posts/upload-image/', PostImageUploadView.as_view(), name='post-image-upload'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),  
    path('posts/<int:pk>/toggle-like/', ToggleLikePostView.as_view(), name='toggle-like-post'),
    path('', include(router.urls)),
]
