from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import NationalRegister
from datetime import date, datetime
import pandas as pd
from pathlib import Path
from django.contrib import messages
from django.db.models import Count
from django.db import IntegrityError

@login_required
@never_cache
def dashboard(request):
    if request.user.is_superuser:
        return redirect('data_load')
    else:
        return redirect('search_names')

@login_required
@never_cache
def data_load(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('dashboard')

    record_counts = NationalRegister.objects.values('year').annotate(count=Count('year')).order_by('year')
    preview_data = request.session.get('csv_preview_data', None)
    return render(request, 'search/data_load.html', {'record_counts': record_counts, 'preview_data': preview_data})

@login_required
@never_cache
def import_data_view(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('dashboard')

    if request.method == 'POST':
        if 'preview_csv' in request.POST and 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'This is not a CSV file.')
                return redirect('data_load')

            try:
                df = pd.read_csv(csv_file.temporary_file_path(), encoding='latin1', dtype=str)
                df.columns = (
                    df.columns
                      .str.strip()
                      .str.upper()
                      .str.replace(r'\s+', '_', regex=True)
                )

                # Fill missing YEAR with current year for preview
                current_year = datetime.now().year
                if 'YEAR' not in df.columns:
                    df['YEAR'] = current_year
                else:
                    df['YEAR'] = df['YEAR'].fillna(str(current_year))

                # Convert DOB for preview and full data
                if 'DOB' in df.columns:
                    df['DOB'] = pd.to_datetime(df['DOB'], format='%m/%d/%Y', errors='coerce').dt.date

                # Store full data in session
                full_records = df.to_dict(orient='records')
                # Convert date objects to string for JSON serialization for full data
                for record in full_records:
                    if isinstance(record.get('DOB'), date):
                        record['DOB'] = record['DOB'].isoformat()
                request.session['full_csv_data'] = full_records

                # Store preview data in session (first 50 rows)
                preview_records = df.head(50).to_dict(orient='records')
                # Convert date objects to string for JSON serialization for preview data
                for record in preview_records:
                    if isinstance(record.get('DOB'), date):
                        record['DOB'] = record['DOB'].isoformat()
                request.session['csv_preview_data'] = preview_records
                messages.info(request, "CSV file preview generated. Review and click 'Load Data' to import.")

            except Exception as e:
                messages.error(request, f"An error occurred during preview: {e}")

        elif 'load_confirmed' in request.POST and request.session.get('full_csv_data'):
            full_records = request.session.get('full_csv_data')
            del request.session['full_csv_data'] # Clear full data after confirmation
            if 'csv_preview_data' in request.session:
                del request.session['csv_preview_data'] # Clear preview data as well

            imported_count = 0
            skipped_count = 0
            errors = []

            objects_to_create = []
            existing_nrn_year_pairs = set(NationalRegister.objects.values_list('nrn', 'year'))

            for row_data in full_records:
                nrn = row_data.get('NRN')
                year = row_data.get('YEAR')

                if not nrn or not year:
                    errors.append(f"Skipped record due to missing NRN or Year: {row_data}")
                    skipped_count += 1
                    continue

                # Check for existing record with same NRN and Year in the database
                if (nrn, int(year)) in existing_nrn_year_pairs:
                    errors.append(f"Skipped duplicate record (NRN: {nrn}, Year: {year}): {row_data}")
                    skipped_count += 1
                    continue
                
                # Convert DOB back to date object if it was serialized as string
                dob_str = row_data.get('DOB')
                dob_obj = None
                if dob_str:
                    try:
                        dob_obj = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    except ValueError:
                        pass # Handle cases where DOB might be invalid or not in expected format

                objects_to_create.append(NationalRegister(
                    nrn=row_data.get('NRN'),
                    surname=row_data.get('SURNAME'),
                    first_name=row_data.get('FIRST_NAME'),
                    middle_name=row_data.get('MIDDLE_NAMES'),
                    sex=row_data.get('SEX'),
                    date_of_birth=dob_obj,
                    address_line_1=row_data.get('ADDRESS_LINE_1'),
                    address_line_2=row_data.get('ADDRESS_LINE_2'),
                    address_line_3=row_data.get('ADDRESS_LINE_3'),
                    town=row_data.get('TOWN'),
                    parish=row_data.get('PARISH'),
                    postcode=row_data.get('POSTCODE'),
                    telephone_number=row_data.get('TELEPHONE_NUMBER'),
                    first_norm=str(row_data.get('FIRST_NAME', '')).lower(),
                    last_norm=str(row_data.get('SURNAME', '')).lower(),
                    nrn_norm=str(row_data.get('NRN', '')).replace('-', ''),
                    year=row_data.get('YEAR')
                ))
            
            try:
                created_objects = NationalRegister.objects.bulk_create(objects_to_create, ignore_conflicts=True)
                imported_count = len(created_objects)
                skipped_count += (len(objects_to_create) - imported_count) # Count records skipped by ignore_conflicts
            except Exception as e:
                errors.append(f"An error occurred during bulk import: {e}")
                skipped_count += len(objects_to_create) # All records failed if bulk_create fails
            
            messages.success(request, f"Successfully imported {imported_count} records. Skipped {skipped_count} records.")
            for error_msg in errors:
                messages.warning(request, error_msg)
            
            messages.success(request, f"Successfully imported {imported_count} records. Skipped {skipped_count} records.")
            for error_msg in errors:
                messages.warning(request, error_msg)

        else:
            messages.error(request, "Invalid request or no CSV file uploaded for preview.")

        return redirect('data_load')
    else:
        return redirect('data_load')

def search_names(request):
    first_fragment = request.GET.get('first_fragment', '')
    last_fragment = request.GET.get('last_fragment', '')
    results = None
    truncated = False

    if first_fragment or last_fragment:
        query = NationalRegister.objects.all()
        if first_fragment:
            query = query.filter(first_norm__icontains=first_fragment.lower().strip())
        if last_fragment:
            query = query.filter(last_norm__icontains=last_fragment.lower().strip())
        
        total_results = query.count()
        if total_results > 500:
            truncated = True
            results = query.order_by('nrn_norm')[:500]
        else:
            results = query.order_by('nrn_norm')

    return render(request, 'search/search_results.html', {
        'results': results,
        'first_fragment': first_fragment,
        'last_fragment': last_fragment,
        'truncated': truncated,
    })

@never_cache
def search_nrn(request):
    nrn_fragment = request.GET.get('nrn_fragment', '')
    results = None
    truncated = False

    if nrn_fragment:
        frag = nrn_fragment.replace('-', '').strip()
        query = NationalRegister.objects.filter(nrn_norm__icontains=frag)
        
        total_results = query.count()
        if total_results > 500:
            truncated = True
            results = query.order_by('nrn_norm')[:500]
        else:
            results = query.order_by('nrn_norm')

    return render(request, 'search/search_results.html', {
        'results': results,
        'nrn_fragment': nrn_fragment,
        'truncated': truncated,
    })
