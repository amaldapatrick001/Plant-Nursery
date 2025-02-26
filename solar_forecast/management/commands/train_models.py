from django.core.management.base import BaseCommand
from solar_forecast.train_model import train_and_save_models

class Command(BaseCommand):
    help = 'Train the hybrid solar radiation prediction models (CNN + CatBoost)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting model training...')
        try:
            train_and_save_models()
            self.stdout.write(self.style.SUCCESS('Successfully trained models!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error training models: {str(e)}')) 