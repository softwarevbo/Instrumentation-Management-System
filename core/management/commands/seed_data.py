"""
Seed Data Management Command - Vainu Bappu Observatory (VBO, Kavalur)
Populates exclusively the 5 requested users:
1. Instrumentation admin (@admin) - Admin
2. Phanindra DVS (@phanindra) - Engineer
3. Rahul Bar (@rahulbar) - Researcher (VBT)
4. Venkatesh S (@venkatesh) - Technical Assistant (JCBT)
5. Surendharnath S (@surendharnath) - Researcher (VBT)

Standard password for all accounts: vbo123pass

Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
import datetime


class Command(BaseCommand):
    help = 'Seeds the database with exact 5 requested VBO technical staff users and observatory dataset.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\nIMS Observatory -- Seeding VBO Kavalur Technical Staff & Data\n'))

        # ─── VBO USERS (EXACTLY 5 USERS MATCHING SCREENSHOT) ─────────────────
        from accounts.models import User

        STANDARD_PASSWORD = 'vbo123pass'

        vbo_users_spec = [
            {
                'username': 'admin',
                'first_name': 'Instrumentation',
                'last_name': 'admin',
                'email': 'admin@iiap.res.in',
                'role': 'admin',
                'department': 'operations',
                'designation': 'Admin',
                'is_staff': True,
                'is_superuser': True,
                'color': '#8b5cf6',
                'telescopes': ['VBT', 'JCBT', 'CZT'],
            },
            {
                'username': 'phanindra',
                'first_name': 'Phanindra',
                'last_name': 'DVS',
                'email': 'phanindra@iiap.res.in',
                'role': 'engineer',
                'department': 'electronics',
                'designation': 'Engineer',
                'is_staff': False,
                'is_superuser': False,
                'color': '#06b6d4',
                'telescopes': ['VBT', 'JCBT', 'CZT'],
            },
            {
                'username': 'rahulbar',
                'first_name': 'Rahul',
                'last_name': 'Bar',
                'email': 'rahul.bar@iiap.res.in',
                'role': 'observer',
                'department': 'software',
                'designation': 'Researcher',
                'is_staff': False,
                'is_superuser': False,
                'color': '#3b82f6',
                'telescopes': ['VBT'],
            },
            {
                'username': 'venkatesh',
                'first_name': 'Venkatesh',
                'last_name': 'S',
                'email': 'venkatesh@iiap.res.in',
                'role': 'observer',
                'department': 'astronomy',
                'designation': 'Technical Assistant – Science Observing & Target Runs',
                'is_staff': False,
                'is_superuser': False,
                'color': '#f59e0b',
                'telescopes': ['JCBT'],
            },
            {
                'username': 'surendharnath',
                'first_name': 'Surendharnath',
                'last_name': 'S',
                'email': 'surendharnath@iiap.res.in',
                'role': 'observer',
                'department': 'optics',
                'designation': 'Researcher',
                'is_staff': False,
                'is_superuser': False,
                'color': '#ec4899',
                'telescopes': ['VBT'],
            },
        ]

        valid_usernames = [u['username'] for u in vbo_users_spec]
        
        # Remove any other accounts completely
        User.objects.exclude(username__in=valid_usernames).delete()

        user_map = {}

        for spec in vbo_users_spec:
            user, created = User.objects.get_or_create(username=spec['username'])
            user.first_name = spec['first_name']
            user.last_name = spec['last_name']
            user.email = spec['email']
            user.role = spec['role']
            user.department = spec['department']
            user.designation = spec['designation']
            user.is_staff = spec['is_staff']
            user.is_superuser = spec['is_superuser']
            user.avatar_color = spec['color']
            user.set_password(STANDARD_PASSWORD)
            user.save()
            user_map[spec['username']] = (user, spec['telescopes'])
            self.stdout.write(self.style.SUCCESS(f"  [OK] User synced: @{spec['username']} ({user.get_full_name()} - {spec['designation']})"))

        admin_user = user_map['admin'][0]
        phanindra_user = user_map['phanindra'][0]
        rahulbar_user = user_map['rahulbar'][0]
        venkatesh_user = user_map['venkatesh'][0]
        surendharnath_user = user_map['surendharnath'][0]

        # ─── VBO TELESCOPES ───────────────────────────────────────────────────
        from telescopes.models import Telescope, TelescopeLog

        Telescope.objects.exclude(code__in=['VBT', 'JCBT', 'CZT']).delete()

        tel_vbt, _ = Telescope.objects.update_or_create(
            code='VBT',
            defaults={
                'name': '2.34m Vainu Bappu Telescope',
                'aperture': 2.34,
                'focal_ratio': 'f/3.25 Prime / f/13 Cassegrain',
                'mount_type': 'fork_eq',
                'location': 'Vainu Bappu Observatory, Kavalur, TN (Lat: 12°34\'N, Lon: 78°50\'E)',
                'status': 'tracking',
                'right_ascension': '10h 44m 57.8s',
                'declination': "+20° 09' 00.1\"",
                'epoch': 'J2000',
                'focus_position': 14.72,
                'dome_status': 'open',
                'primary_mirror_temp': 22.4,
                'ambient_temp': 21.8,
                'humidity': 55.0,
            }
        )

        tel_jcbt, _ = Telescope.objects.update_or_create(
            code='JCBT',
            defaults={
                'name': '1.3m Jagadish Chandra Bhattacharyya Telescope',
                'aperture': 1.30,
                'focal_ratio': 'f/8 Ritchey-Chrétien',
                'mount_type': 'german_eq',
                'location': 'Vainu Bappu Observatory, Kavalur, TN (30\' FoV, 20"/mm scale)',
                'status': 'tracking',
                'right_ascension': '05h 35m 17.3s',
                'declination': "-05° 23' 28.0\"",
                'epoch': 'J2000',
                'focus_position': 9.15,
                'dome_status': 'open',
                'primary_mirror_temp': 23.1,
                'ambient_temp': 22.0,
                'humidity': 58.2,
            }
        )

        tel_czt, _ = Telescope.objects.update_or_create(
            code='CZT',
            defaults={
                'name': '1.02m Carl Zeiss 40-inch Telescope',
                'aperture': 1.02,
                'focal_ratio': 'f/13 Cassegrain / f/30 Coudé',
                'mount_type': 'german_eq',
                'location': 'Vainu Bappu Observatory, Kavalur, TN',
                'status': 'idle',
                'right_ascension': "18h 36m 56.3s",
                'declination': "+38° 47' 01.0\"",
                'epoch': 'J2000',
                'focus_position': 11.35,
                'dome_status': 'closed',
                'primary_mirror_temp': 22.8,
                'ambient_temp': 22.1,
                'humidity': 60.0,
            }
        )

        tel_lookup = {'VBT': tel_vbt, 'JCBT': tel_jcbt, 'CZT': tel_czt}

        # Assign telescopes to users according to screenshot specification
        for username, (u_obj, tel_codes) in user_map.items():
            assigned = [tel_lookup[code] for code in tel_codes if code in tel_lookup]
            u_obj.assigned_telescopes.set(assigned)

        self.stdout.write(self.style.SUCCESS('  [OK] 3 VBO Telescopes registered & assigned'))

        # VBO Telescope Logs
        TelescopeLog.objects.all().delete()
        TelescopeLog.objects.create(
            telescope=tel_vbt, event_type='slew',
            user=admin_user, message="Instrumentation admin initiated VBT slew to Orion Nebula for echelle spectrograph target run."
        )
        TelescopeLog.objects.create(
            telescope=tel_vbt, event_type='dome_open',
            user=phanindra_user, message="Phanindra DVS verified dome shutter open status. VBT dome seeing measured at 1.4 arcsec."
        )
        TelescopeLog.objects.create(
            telescope=tel_jcbt, event_type='slew',
            user=venkatesh_user, message="Venkatesh S aligned JCBT 1.3m on Orion Nebula (M42) for 2Kx4K CCD H-alpha imaging."
        )

        # ─── VBO INSTRUMENTS ──────────────────────────────────────────────────
        from instruments.models import Instrument, InstrumentSensor, FilterWheelConfig

        FilterWheelConfig.objects.all().delete()
        Instrument.objects.exclude(code__in=['VBT-HiRES', 'OMR', 'JCBT-CCD', 'UAGS']).delete()

        inst_hires, _ = Instrument.objects.update_or_create(
            code='VBT-HiRES',
            defaults={
                'name': 'VBT High-Resolution Echelle Spectrograph',
                'instrument_type': 'spectrograph',
                'telescope': tel_vbt,
                'status': 'online',
                'detector_temp': -110.5,
                'setpoint_temp': -115.0,
                'vacuum_pressure': 1.1e-6,
                'cooling_power_percent': 64.0,
                'gain': 0.85,
                'binning': '1x1',
                'readout_speed': '100 kHz (Low Noise UKIRT 4Kx4K CCD)',
                'active_filter': 'Iodine Cell',
            }
        )

        inst_omr, _ = Instrument.objects.update_or_create(
            code='OMR',
            defaults={
                'name': 'Optomechanics Research (OMR) Spectrograph',
                'instrument_type': 'spectrograph',
                'telescope': tel_vbt,
                'status': 'online',
                'detector_temp': -102.0,
                'setpoint_temp': -105.0,
                'vacuum_pressure': 2.4e-6,
                'cooling_power_percent': 71.0,
                'gain': 4.33,
                'binning': '1x1',
                'readout_speed': '250 kHz (Tektronix 1Kx1K CCD)',
                'active_filter': '600 l/mm Grating',
            }
        )

        inst_jcbt_ccd, _ = Instrument.objects.update_or_create(
            code='JCBT-CCD',
            defaults={
                'name': 'JCBT Direct Imaging 2Kx4K CCD Camera',
                'instrument_type': 'ccd_imager',
                'telescope': tel_jcbt,
                'status': 'online',
                'detector_temp': -115.0,
                'setpoint_temp': -120.0,
                'vacuum_pressure': 4.2e-7,
                'cooling_power_percent': 78.0,
                'gain': 1.45,
                'binning': '2x2',
                'readout_speed': '1 MHz (Fast Readout)',
                'active_filter': 'V (550nm)',
            }
        )

        inst_uags, _ = Instrument.objects.update_or_create(
            code='UAGS',
            defaults={
                'name': 'Universal Astronomical Grating Spectrograph',
                'instrument_type': 'spectrograph',
                'telescope': tel_czt,
                'status': 'standby',
                'detector_temp': -95.0,
                'setpoint_temp': -100.0,
                'vacuum_pressure': 8.5e-6,
                'cooling_power_percent': 50.0,
                'gain': 2.10,
                'binning': '1x1',
                'readout_speed': '500 kHz',
                'active_filter': 'ThAr Lamp',
            }
        )

        self.stdout.write(self.style.SUCCESS('  [OK] 4 VBO Instruments seeded (VBT-HiRES, OMR, JCBT-CCD, UAGS)'))

        sensors_vbo = [
            (inst_hires, 'UKIRT 4K CCD Temp', '°C', -110.5, -120.0, -100.0),
            (inst_hires, 'Cryo Vacuum', 'e-6 mbar', 1.1, 0.1, 5.0),
            (inst_hires, 'Iodine Cell Temp', '°C', 50.1, 48.0, 52.0),
            (inst_omr, 'Tek 1K CCD Temp', '°C', -102.0, -110.0, -95.0),
            (inst_omr, 'Grating Angle', 'deg', 14.32, 0.0, 45.0),
            (inst_jcbt_ccd, '2Kx4K CCD Temp', '°C', -115.0, -125.0, -105.0),
            (inst_uags, 'CCD Temp', '°C', -95.0, -105.0, -85.0),
        ]
        for inst, name, unit, val, mn, mx in sensors_vbo:
            InstrumentSensor.objects.get_or_create(
                instrument=inst, sensor_name=name,
                defaults={'unit': unit, 'current_value': val, 'min_warning': mn, 'max_warning': mx}
            )

        # ─── SINGLE DATA FOR CATALOG ──────────────────────────────────────────
        from observations.models import ObservationTarget

        ObservationTarget.objects.all().delete()

        ObservationTarget.objects.create(
            name='Orion Nebula',
            catalog_id='M42 / NGC 1976',
            object_class='nebula',
            right_ascension='05h 35m 17.3s',
            declination="-05° 23' 28\"",
            magnitude=4.00,
            distance_ly=1344.0,
            observation_date=datetime.date(2026, 1, 20),
            recommended_filter='H-alpha (656.3nm)',
            epoch='J2000.0',
            notes='Primary target for VBO 2.34m VBT and 1.3m JCBT nebular spectroscopy and H-alpha imaging.'
        )

        self.stdout.write(self.style.SUCCESS('  [OK] Single Target Catalog entry seeded (Orion Nebula M42)'))

        # ─── SINGLE DATA FOR MAINTENANCE TICKET & CALIBRATION ────────────────
        from maintenance.models import MaintenanceTicket, CalibrationLog

        MaintenanceTicket.objects.all().delete()

        MaintenanceTicket.objects.create(
            title='VBT Prime Focus Carriage Lubrication & Encoder Alignment',
            description='Scheduled PM for VBT 2.34m prime focus assembly and declination drive gears.',
            severity='medium',
            status='in_progress',
            telescope=tel_vbt,
            instrument=inst_hires,
            reported_by=admin_user,
            assigned_engineer=phanindra_user,
        )

        self.stdout.write(self.style.SUCCESS('  [OK] Single Maintenance Ticket registered'))

        CalibrationLog.objects.all().delete()

        CalibrationLog.objects.create(
            instrument=inst_hires,
            calibration_type='wavelength',
            standard_lamp_or_target='ThAr Arc Lamp',
            engineer=phanindra_user,
            status='completed',
            notes='1240 arc lines fitted. RMS residual 0.0018 Å.'
        )

        self.stdout.write(self.style.SUCCESS('  [OK] Single Calibration Log seeded'))

        self.stdout.write(self.style.SUCCESS('\n[DONE] VBO Kavalur Technical Staff & Observatory dataset loaded successfully!\n'))
        self.stdout.write('-' * 70)
        self.stdout.write(self.style.WARNING('VBO Observatory Staff Credentials (EXACT MATCH TO UI SCREENSHOT):'))
        self.stdout.write(f"  STANDARD PASSWORD FOR ALL ACCOUNTS: {STANDARD_PASSWORD}\n")
        self.stdout.write('  1. Admin    -> admin         / vbo123pass  (Instrumentation admin)')
        self.stdout.write('  2. Engineer -> phanindra     / vbo123pass  (Phanindra DVS)')
        self.stdout.write('  3. Observer -> rahulbar      / vbo123pass  (Rahul Bar - VBT)')
        self.stdout.write('  4. Observer -> venkatesh     / vbo123pass  (Venkatesh S - JCBT)')
        self.stdout.write('  5. Observer -> surendharnath / vbo123pass  (Surendharnath S - VBT)')
        self.stdout.write('-' * 70)
