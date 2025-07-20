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
    help = 'Load National Register 2025 data from a specific CSV file'

    def handle(self, *args, **options):
        self.stdout.write('Deleting existing NationalRegister data...')
        NationalRegister.objects.all().delete()

        # Define the specific CSV file path
        # Assuming NationalRegister2025.csv is directly in the 'search' app directory
        csv_file_path = Path(__file__).resolve().parent.parent.parent / 'NationalRegister2025.csv'

        self.stdout.write(f'Importing data from {csv_file_path}...')
        try:
            tmp = pd.read_csv(csv_file_path, encoding='latin1', dtype=str)
            tmp['YEAR'] = 2025 # Assuming this file is specifically for 2025 data
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
                    return s.zfill(10)
            tmp['NRN_NORM'] = tmp['NRN'].map(_norm_nrn)

            # Convert DATE_OF_BIRTH to datetime objects
            # Strictly expecting dd/mm/yyyy format, will raise error if not
            if 'DOB' in tmp.columns: # Assuming the column name in CSV is 'DOB'
                tmp['DATE_OF_BIRTH'] = pd.to_datetime(tmp['DOB'], format='%d/%m/%Y').dt.date
            else:
                self.stderr.write(self.style.WARNING("DOB column not found in CSV. Skipping date of birth import."))
                tmp['DATE_OF_BIRTH'] = None # Ensure column exists even if not in CSV

            # Map CSV columns to model fields
            self.stdout.write("Starting data import...")
            total_records = len(tmp)
            for i, row in tmp.iterrows():
                    NationalRegister.objects.update_or_create(
                        nrn=row.get('NRN'),
                        year=row['YEAR'],
                        defaults={
                            'first_name': row.get('FIRST_NAME'),
                            'middle_name': row.get('MIDDLE_NAMES'),
                            'surname': row.get('SURNAME'),
                            'sex': row.get('SEX'),
                            'date_of_birth': row.get('DATE_OF_BIRTH'),
                            'address_line_2': row.get('ADDRESS_LINE_2'),
                            'address_line_3': row.get('ADDRESS_LINE_3'),
                            'parish': row.get('PARISH'),
                            'first_norm': row.get('FIRST_NORM'),
                            'last_norm': row.get('LAST_NORM'),
                            'nrn_norm': row.get('NRN_NORM'),
                        }
                    )
                    if (i + 1) % 100 == 0:
                        self.stdout.write(f"Processed {i + 1}/{total_records} records.")
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {total_records} records from NationalRegister2025.csv'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'File not found: {csv_file_path}'))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f'Error processing CSV: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
