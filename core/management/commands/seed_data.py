"""
Seed Data Management Command - Vainu Bappu Observatory (VBO, Kavalur) Only
Populates users exclusively from the VBO Kavalur technical & engineering staff directory (https://www.iiap.res.in/people/technical/#VBOKavalur),
along with VBO telescopes (VBT 2.34m, JCBT 1.3m, CZT 1.02m), VBO instruments (VBT-HiRES, OMR, JCBT-CCD, UAGS),
target catalog with observation dates and optical filters, science queue items, maintenance tickets, and calibration logs.

Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
import datetime


class Command(BaseCommand):
    help = 'Seeds the database with authentic Vainu Bappu Observatory (VBO Kavalur) technical staff and observatory data.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\nIMS Observatory -- Seeding VBO Kavalur Technical Staff & Data\n'))

        # ─── VBO KAVALUR TECHNICAL STAFF USERS ────────────────────────────────
        from accounts.models import User

        # Authentic VBO Kavalur Technical Staff List
        vbo_staff_data = [
            {
                'username': 'anbazhagan',
                'first_name': 'Anbazhagan',
                'last_name': 'P',
                'email': 'anbu@iiap.res.in',
                'role': 'admin',
                'department': 'operations',
                'designation': 'Engineer E & Engineer-in-Charge (VBO Kavalur)',
                'is_staff': True,
                'is_superuser': True,
                'color': '#8b5cf6',
                'demo_alias': 'admin',  # also update default admin
            },
            {
                'username': 'ramachandran',
                'first_name': 'Ramachandran',
                'last_name': 'A',
                'email': 'ramachandran@iiap.res.in',
                'role': 'engineer',
                'department': 'electronics',
                'designation': 'Engineer D – Telescope Control & CCD Systems',
                'is_staff': False,
                'is_superuser': False,
                'color': '#06b6d4',
                'demo_alias': 'engineer1',
            },
            {
                'username': 'sathyanarayanan',
                'first_name': 'Sathyanarayanan',
                'last_name': 'S',
                'email': 'sathya@iiap.res.in',
                'role': 'engineer',
                'department': 'electronics',
                'designation': 'Technical Assistant – Servo Systems & Detector Electronics',
                'is_staff': False,
                'is_superuser': False,
                'color': '#14b8a6',
                'demo_alias': 'engineer2',
            },
            {
                'username': 'rahulbar',
                'first_name': 'Rahul',
                'last_name': 'Bar',
                'email': 'rahul.bar@iiap.res.in',
                'role': 'engineer',
                'department': 'software',
                'designation': 'Lead Technical Officer – VBO Operations & Telemetry',
                'is_staff': False,
                'is_superuser': False,
                'color': '#3b82f6',
                'demo_alias': 'observer2',
            },
            {
                'username': 'surendharnath',
                'first_name': 'Surendharnath',
                'last_name': 'S',
                'email': 'surendharnath@iiap.res.in',
                'role': 'engineer',
                'department': 'optics',
                'designation': 'Technical Officer – VBO Instrumentation & Alignments',
                'is_staff': False,
                'is_superuser': False,
                'color': '#ec4899',
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
                'demo_alias': 'observer1',
            },
            {
                'username': 'naveenkumar',
                'first_name': 'Naveen Kumar',
                'last_name': 'R',
                'email': 'naveenkumar@iiap.res.in',
                'role': 'engineer',
                'department': 'optics',
                'designation': 'Mechanic B – Telescope & Dome Mechanical Systems',
                'is_staff': False,
                'is_superuser': False,
                'color': '#10b981',
            },
        ]

        user_objects = {}

        for staff in vbo_staff_data:
            user, created = User.objects.get_or_create(username=staff['username'])
            user.first_name = staff['first_name']
            user.last_name = staff['last_name']
            user.email = staff['email']
            user.role = staff['role']
            user.department = staff['department']
            user.designation = staff['designation']
            user.is_staff = staff['is_staff']
            user.is_superuser = staff['is_superuser']
            user.avatar_color = staff['color']
            user.set_password('vbo123pass')
            user.save()
            user_objects[staff['username']] = user

            # Create demo alias accounts (admin, engineer1, observer1, etc.) for convenient login
            if 'demo_alias' in staff:
                alias_user, _ = User.objects.get_or_create(username=staff['demo_alias'])
                alias_user.first_name = staff['first_name']
                alias_user.last_name = staff['last_name']
                alias_user.email = staff['email']
                alias_user.role = staff['role']
                alias_user.department = staff['department']
                alias_user.designation = f"{staff['designation']} (Demo Login)"
                alias_user.is_staff = staff['is_staff']
                alias_user.is_superuser = staff['is_superuser']
                alias_user.avatar_color = staff['color']
                if staff['demo_alias'] == 'admin':
                    alias_user.set_password('adminpass123')
                elif 'engineer' in staff['demo_alias']:
                    alias_user.set_password('engineerpass123')
                else:
                    alias_user.set_password('observerpass123')
                alias_user.save()
                user_objects[staff['demo_alias']] = alias_user

            self.stdout.write(self.style.SUCCESS(f"  [OK] VBO Staff user synced: {staff['username']} ({staff['designation']})"))

        admin_user = user_objects.get('anbazhagan') or user_objects.get('admin')
        engineer1 = user_objects.get('ramachandran') or user_objects.get('engineer1')
        engineer2 = user_objects.get('sathyanarayanan') or user_objects.get('engineer2')
        observer1 = user_objects.get('venkatesh') or user_objects.get('observer1')
        observer2 = user_objects.get('rahulbar') or user_objects.get('observer2')

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

        self.stdout.write(self.style.SUCCESS('  [OK] 3 VBO Telescopes registered (VBT 2.34m, JCBT 1.3m, CZT 1.02m)'))

        # Assign authorized telescopes to Observer staff
        venkatesh = user_objects.get('venkatesh')
        if venkatesh:
            venkatesh.assigned_telescopes.set([tel_vbt, tel_jcbt])
        obs1_alias = user_objects.get('observer1')
        if obs1_alias:
            obs1_alias.assigned_telescopes.set([tel_vbt, tel_jcbt])

        rahulbar = user_objects.get('rahulbar')
        if rahulbar:
            rahulbar.assigned_telescopes.set([tel_jcbt, tel_czt])
        obs2_alias = user_objects.get('observer2')
        if obs2_alias:
            obs2_alias.assigned_telescopes.set([tel_jcbt, tel_czt])

        # VBO Telescope Logs
        TelescopeLog.objects.get_or_create(
            telescope=tel_vbt, event_type='slew',
            defaults={'user': admin_user, 'message': "Anbazhagan P initiated VBT slew to Tau Bootis for high-resolution echelle spectroscopic monitoring."}
        )
        TelescopeLog.objects.get_or_create(
            telescope=tel_vbt, event_type='dome_open',
            defaults={'user': engineer1, 'message': "Ramachandran A verified dome shutter open status. VBT dome seeing measured at 1.4 arcsec."}
        )
        TelescopeLog.objects.get_or_create(
            telescope=tel_jcbt, event_type='slew',
            defaults={'user': observer1, 'message': "Venkatesh S aligned JCBT 1.3m on Orion Nebula (M42) for 2Kx4K CCD H-alpha imaging."}
        )

        # ─── VBO INSTRUMENTS ──────────────────────────────────────────────────
        from instruments.models import Instrument, InstrumentSensor, FilterWheelConfig

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

        # VBO Instrument Sensors
        sensors_vbo = [
            (inst_hires, 'UKIRT 4K CCD Temp', '°C', -110.5, -120.0, -100.0),
            (inst_hires, 'Cryo Vacuum', 'e-6 mbar', 1.1, 0.1, 5.0),
            (inst_hires, 'Iodine Cell Temp', '°C', 50.1, 48.0, 52.0),
            (inst_omr, 'Tek 1K CCD Temp', '°C', -102.0, -110.0, -95.0),
            (inst_omr, 'Grating Angle', 'deg', 14.32, 0.0, 45.0),
            (inst_jcbt_ccd, '2Kx4K CCD Temp', '°C', -115.0, -125.0, -105.0),
            (inst_jcbt_ccd, 'Filter Wheel Pos', 'slot', 2.0, 1.0, 6.0),
            (inst_uags, 'CCD Temp', '°C', -95.0, -105.0, -85.0),
        ]
        for inst, name, unit, val, mn, mx in sensors_vbo:
            InstrumentSensor.objects.get_or_create(
                instrument=inst, sensor_name=name,
                defaults={'unit': unit, 'current_value': val, 'min_warning': mn, 'max_warning': mx}
            )

        # VBO Filter Wheels
        filters_hires = [
            (1, 'Iodine Cell', 530.0, 100.0),
            (2, 'ThAr Lamp', 500.0, 400.0),
            (3, 'Flat Lamp', 550.0, 300.0),
            (4, 'Clear / Open', 550.0, 0.0),
        ]
        for slot, name, wave, bw in filters_hires:
            FilterWheelConfig.objects.get_or_create(instrument=inst_hires, slot_number=slot, defaults={'filter_name': name, 'central_wavelength': wave, 'bandwidth': bw})

        filters_jcbt = [
            (1, 'U (Bessel)', 365.0, 68.0),
            (2, 'B (Bessel)', 440.0, 98.0),
            (3, 'V (Bessel)', 550.0, 89.0),
            (4, 'R (Bessel)', 641.0, 150.0),
            (5, 'I (Bessel)', 798.0, 154.0),
            (6, 'H-alpha (656.3nm)', 656.3, 5.0),
            (7, 'OIII (500.7nm)', 500.7, 5.0),
        ]
        for slot, name, wave, bw in filters_jcbt:
            FilterWheelConfig.objects.get_or_create(instrument=inst_jcbt_ccd, slot_number=slot, defaults={'filter_name': name, 'central_wavelength': wave, 'bandwidth': bw})

        self.stdout.write(self.style.SUCCESS('  [OK] VBO Sensors and Filter Wheel slots configured'))

        # ─── VBO TARGET CATALOG WITH DATES & FILTERS ──────────────────────────
        from observations.models import ObservationTarget

        targets_vbo_data = [
            ('Andromeda Galaxy', 'M31 / NGC 224', 'galaxy', '00h 42m 44.3s', "+41° 16' 09\"", 3.44, 2537000.0, datetime.date(2026, 1, 14), 'B (440nm)', 'J2000.0'),
            ('Orion Nebula', 'M42 / NGC 1976', 'nebula', '05h 35m 17.3s', "-05° 23' 28\"", 4.00, 1344.0, datetime.date(2026, 1, 20), 'H-alpha (656.3nm)', 'J2000.0'),
            ('Tau Bootis', 'HD 120136', 'exoplanet', '13h 47m 15.7s', "+17° 27' 25\"", 4.50, 51.0, datetime.date(2026, 2, 5), 'Iodine Cell', 'J2000.0'),
            ('Vega', 'HD 172167', 'star', '18h 36m 56.3s', "+38° 47' 01\"", 0.03, 25.04, datetime.date(2026, 2, 18), 'V (550nm)', 'J2000.0'),
            ('Crab Nebula', 'M1 / NGC 1952', 'nebula', '05h 34m 31.9s', "+22° 00' 52\"", 8.40, 6523.0, datetime.date(2026, 3, 1), 'OIII (500.7nm)', 'J2000.0'),
            ('47 Tucanae', 'NGC 104', 'star', '00h 24m 05.4s', "-72° 04' 53\"", 4.09, 16700.0, datetime.date(2026, 3, 12), 'R (641nm)', 'J2000.0'),
            ('V404 Cygni', 'GS 2023+338', 'star', '20h 24m 03.8s', "+33° 52' 02\"", 11.80, 7800.0, datetime.date(2026, 4, 2), 'I (798nm)', 'J2000.0'),
            ('Betelgeuse', 'Alpha Orionis', 'star', '05h 55m 10.3s', "+07° 24' 25\"", 0.50, 642.5, datetime.date(2026, 4, 15), 'V (550nm)', 'J2000.0'),
            ('Supernova Remnant 1987A', 'SN 1987A', 'nebula', '05h 35m 28.0s', "-69° 16' 11\"", 14.20, 168000.0, datetime.date(2026, 5, 10), 'H-alpha (656.3nm)', 'J2000.0'),
            ('Pulsar PSR B1919+21', 'CP 1919', 'quasar', '19h 21m 44.8s', "+21° 53' 02\"", 16.50, 3260.0, datetime.date(2026, 6, 1), 'ThAr Lamp', 'J2000.0'),
        ]

        targets_dict = {}
        for name, cat, cls, ra, dec, mag, dist, obs_date, filt, ep in targets_vbo_data:
            t, _ = ObservationTarget.objects.update_or_create(
                name=name,
                defaults={
                    'catalog_id': cat,
                    'object_class': cls,
                    'right_ascension': ra,
                    'declination': dec,
                    'magnitude': mag,
                    'distance_ly': dist,
                    'observation_date': obs_date,
                    'recommended_filter': filt,
                    'epoch': ep,
                }
            )
            targets_dict[name] = t

        self.stdout.write(self.style.SUCCESS(f'  [OK] {len(targets_dict)} VBO Target catalog entries seeded with dates & filters'))

        self.stdout.write(self.style.SUCCESS(f'  [OK] {len(targets_dict)} VBO Target catalog entries seeded with dates & filters'))

        # ─── MAINTENANCE TICKETS & CALIBRATIONS ───────────────────────────────
        from maintenance.models import MaintenanceTicket, CalibrationLog

        MaintenanceTicket.objects.get_or_create(
            title='VBT Prime Focus Carriage Lubrication & Encoder Alignment',
            defaults={
                'description': 'Scheduled PM for VBT 2.34m prime focus assembly and declination drive gears.',
                'severity': 'medium',
                'status': 'in_progress',
                'telescope': tel_vbt,
                'instrument': inst_hires,
                'reported_by': admin_user,
                'assigned_engineer': engineer2,
            }
        )

        MaintenanceTicket.objects.get_or_create(
            title='JCBT CCD Dewar Vacuum Evacuation',
            defaults={
                'description': 'Cryo dewar pressure reading 4.2e-7 mbar. Vacuum pump cycle scheduled to achieve <1.0e-7 mbar.',
                'severity': 'low',
                'status': 'open',
                'telescope': tel_jcbt,
                'instrument': inst_jcbt_ccd,
                'reported_by': engineer1,
                'assigned_engineer': engineer1,
            }
        )

        self.stdout.write(self.style.SUCCESS('  [OK] Maintenance tickets registered'))

        # Calibration Logs
        CalibrationLog.objects.get_or_create(
            instrument=inst_hires, calibration_type='wavelength',
            defaults={'standard_lamp_or_target': 'ThAr Arc Lamp', 'engineer': engineer1, 'status': 'completed', 'notes': '1240 arc lines fitted. RMS residual 0.0018 Å.'}
        )
        CalibrationLog.objects.get_or_create(
            instrument=inst_jcbt_ccd, calibration_type='flat',
            defaults={'standard_lamp_or_target': 'Twilight Sky Flat', 'engineer': engineer2, 'status': 'completed', 'notes': 'Uniformity >99.7% across 2Kx4K CCD sensor.'}
        )

        self.stdout.write(self.style.SUCCESS('  [OK] Calibration logs seeded'))

        self.stdout.write(self.style.SUCCESS('\n[DONE] VBO Kavalur Technical Staff & Observatory dataset loaded successfully!\n'))
        self.stdout.write('-' * 70)
        self.stdout.write(self.style.WARNING('VBO Kavalur Staff Credentials:'))
        for staff in vbo_staff_data:
            self.stdout.write(f"  {staff['role'].capitalize():<8} -> {staff['username']:<16} / vbo123pass  ({staff['first_name']} {staff['last_name']} - {staff['designation']})")
        self.stdout.write('-' * 70)
        self.stdout.write(self.style.WARNING('Demo Shortcut Logins:'))
        self.stdout.write('  Admin    -> admin         / adminpass123   (Anbazhagan P - Engineer-in-Charge)')
        self.stdout.write('  Engineer -> engineer1     / engineerpass123(Ramachandran A - Engineer D)')
        self.stdout.write('  Observer -> observer1     / observerpass123(Venkatesh S - Technical Asst)')
        self.stdout.write('-' * 70)
