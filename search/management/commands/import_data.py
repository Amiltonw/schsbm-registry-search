import pandas as pd
from pathlib import Path
from django.core.management.base import BaseCommand
from search.models import NationalRegister

def tidy_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
          .str.strip()
          .str.upper()
          .str.replace(r'\s+', '_', regex=True)
    )
    return df

class Command(BaseCommand):
    help = 'Import National Register data from CSV files'

    def handle(self, *args, **options):
        self.stdout.write('Deleting existing data...')
        NationalRegister.objects.all().delete()

        FILES = {
            2021: 'National Register 2021.csv',
            2025: 'National RegisterMay.csv',
        }

        for yr, path in FILES.items():
            self.stdout.write(f'Importing data from {path}...')
            try:
                tmp = pd.read_csv(Path(path), encoding='latin1', dtype=str)
                tmp['YEAR'] = yr
                tmp = tidy_cols(tmp)

                required = {'FIRST_NAME', 'SURNAME', 'NRN'}
                missing = required - set(tmp.columns)
                if missing:
                    raise KeyError(f"Missing mandatory column(s): {missing}")

                strip_low = lambda s: ' '.join(str(s).lower().split()) if pd.notna(s) else ''
                tmp['FIRST_NORM'] = tmp['FIRST_NAME'].map(strip_low)
                tmp['LAST_NORM']  = tmp['SURNAME'].map(strip_low)

                def _norm_nrn(raw):
                    if pd.isna(raw):
                        return ''
                    s = str(raw).replace('-', '').strip()
                    return s.zfill(10) if s.isdigit() else s
                tmp['NRN_NORM'] = tmp['NRN'].map(_norm_nrn)

                # Convert DATE_OF_BIRTH to datetime objects
                if 'DATE_OF_BIRTH' in tmp.columns:
                    tmp['DATE_OF_BIRTH'] = pd.to_datetime(tmp['DATE_OF_BIRTH'], errors='coerce').dt.date

                for _, row in tmp.iterrows():
                    NationalRegister.objects.create(
                        year=row['YEAR'],
                        first_name=row.get('FIRST_NAME'),
                        surname=row.get('SURNAME'),
                        nrn=row.get('NRN'),
                        date_of_birth=row.get('DATE_OF_BIRTH'),
                        first_norm=row.get('FIRST_NORM'),
                        last_norm=row.get('LAST_NORM'),
                        nrn_norm=row.get('NRN_NORM'),
                    )
            except FileNotFoundError:
                self.stderr.write(self.style.ERROR(f'File not found: {path}'))
                continue

        self.stdout.write(self.style.SUCCESS('Successfully imported all data'))
