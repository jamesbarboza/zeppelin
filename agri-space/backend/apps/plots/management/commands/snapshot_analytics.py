from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from apps.plots.models import AnalyticsSnapshot, CropTag, Plot, WeatherCache
from apps.users.models import User


class Command(BaseCommand):
    help = 'Create a daily analytics snapshot'

    def handle(self, *args, **options):
        today = timezone.now().date()
        week_ago = timezone.now() - timedelta(days=7)

        top_tags = (
            CropTag.objects.annotate(plot_count=Count('plot'))
            .order_by('-plot_count')[:10]
            .values('name', 'plot_count')
        )

        reco_count = WeatherCache.objects.filter(
            fetched_at__date=today,
            forecast_json__reco_date=today.isoformat(),
        ).count()

        snapshot, created = AnalyticsSnapshot.objects.update_or_create(
            date=today,
            defaults={
                'total_users': User.objects.count(),
                'active_users_7d': User.objects.filter(last_login__gte=week_ago).count(),
                'total_plots': Plot.objects.count(),
                'recommendations_generated': reco_count,
                'top_crop_tags_json': list(top_tags),
            },
        )
        self.stdout.write(self.style.SUCCESS(f'Snapshot {"created" if created else "updated"} for {today}'))
