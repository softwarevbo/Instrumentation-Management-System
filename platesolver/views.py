from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import numpy as np

from telescopes.models import Telescope, TelescopeLog
from .solver_engine import PlateSolverEngine
from .models import PlateSolveRun


@login_required
def index_view(request):
    engine = PlateSolverEngine()
    engine.load_catalog()
    catalog_stars = engine.get_catalog_list()

    telescopes = request.user.get_accessible_telescopes()
    selected_telescope = telescopes.first()

    initial_ra_deg = 0.0
    initial_dec_deg = 0.0

    if selected_telescope:
        try:
            # Parse RA/DEC if possible or use current telescope fields
            initial_ra_deg = round(np.random.uniform(10, 200), 3)
            initial_dec_deg = round(np.random.uniform(-40, 60), 3)
        except Exception:
            pass

    history_runs = PlateSolveRun.objects.select_related('telescope', 'user').all()[:10]

    return render(request, 'platesolver/index.html', {
        'catalog_stars': catalog_stars,
        'telescopes': telescopes,
        'selected_telescope': selected_telescope,
        'initial_ra_deg': initial_ra_deg,
        'initial_dec_deg': initial_dec_deg,
        'history_runs': history_runs,
    })


@login_required
def api_get_field_view(request):
    ra_deg = float(request.GET.get('ra', 0.0))
    dec_deg = float(request.GET.get('dec', 0.0))
    fov_deg = float(request.GET.get('fov', 20.0))

    engine = PlateSolverEngine()
    ra_rad = np.deg2rad(ra_deg)
    dec_rad = np.deg2rad(dec_deg)

    stars = engine.get_stars_in_field(ra_rad, dec_rad, fov_deg)
    return JsonResponse({
        'status': 'success',
        'center_ra_deg': ra_deg,
        'center_dec_deg': dec_deg,
        'center_ra_rad': round(ra_rad, 5),
        'center_dec_rad': round(dec_rad, 5),
        'fov_deg': fov_deg,
        'star_count': len(stars),
        'stars': stars,
    })


@login_required
def api_solve_field_view(request):
    if request.method == 'POST':
        ra_deg = float(request.POST.get('ra', 0.0))
        dec_deg = float(request.POST.get('dec', 0.0))
        fov_deg = float(request.POST.get('fov', 20.0))
        add_noise = request.POST.get('noise') == 'true'
        telescope_id = request.POST.get('telescope_id')

        engine = PlateSolverEngine()
        result = engine.solve_plate(ra_deg, dec_deg, fov_deg, add_noise)

        # Log PlateSolveRun record
        tel_obj = None
        if telescope_id:
            tel_obj = Telescope.objects.filter(pk=telescope_id).first()

        run = PlateSolveRun.objects.create(
            telescope=tel_obj,
            user=request.user,
            target_ra_deg=ra_deg,
            target_dec_deg=dec_deg,
            fov_deg=fov_deg,
            solved_ra_deg=result['solved_ra_deg'],
            solved_dec_deg=result['solved_dec_deg'],
            pixel_scale_arcsec=result['pixel_scale_arcsec'],
            rotation_angle_deg=result['rotation_angle_deg'],
            matched_stars_count=result['matched_stars_count'],
            solution_time_sec=result['solution_time_sec'],
            ra_error_arcmin=result['ra_error_arcmin'],
            dec_error_arcmin=result['dec_error_arcmin'],
            status=PlateSolveRun.STATUS_SUCCESS,
        )

        result['run_id'] = run.pk
        return JsonResponse(result)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@login_required
def api_sync_telescope_view(request):
    if request.method == 'POST':
        telescope_id = request.POST.get('telescope_id')
        solved_ra = request.POST.get('solved_ra')
        solved_dec = request.POST.get('solved_dec')

        if not telescope_id:
            return JsonResponse({'status': 'error', 'message': 'No telescope selected.'}, status=400)

        telescope = get_object_or_404(Telescope, pk=telescope_id)
        if not request.user.can_access_telescope(telescope):
            return JsonResponse({'status': 'error', 'message': 'Access Denied for this telescope.'}, status=403)

        telescope.right_ascension = solved_ra
        telescope.declination = solved_dec
        telescope.status = Telescope.STATUS_TRACKING
        telescope.save()

        TelescopeLog.objects.create(
            telescope=telescope,
            user=request.user,
            event_type='slew',
            message=f"Plate Solver Sync: Telescope pointing synced to solved WCS center RA: {solved_ra}, DEC: {solved_dec}."
        )

        return JsonResponse({
            'status': 'success',
            'message': f"Telescope {telescope.code} pointing successfully synced to {solved_ra}, {solved_dec}!"
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=400)
