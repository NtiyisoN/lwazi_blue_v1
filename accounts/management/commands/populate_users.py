"""
Management command to populate mock users (interns and employers)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from core.models import (
    InternProfile, EmployerProfile, 
    Skill, Industry, Location,
    Education, WorkExperience
)
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Populate database with mock users (interns and employers)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interns',
            type=int,
            default=50,
            help='Number of interns to create'
        )
        parser.add_argument(
            '--employers',
            type=int,
            default=10,
            help='Number of employers to create'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_interns = options['interns']
        num_employers = options['employers']
        
        self.stdout.write('Creating supporting data...')
        
        # Create Skills
        skills_data = [
            'Python', 'Django', 'JavaScript', 'React', 'Vue.js', 'Angular',
            'HTML/CSS', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB',
            'Git', 'Docker', 'AWS', 'Azure', 'Linux',
            'Java', 'C#', 'PHP', 'Ruby', 'Node.js',
            'Project Management', 'Communication', 'Teamwork', 'Problem Solving',
            'Data Analysis', 'Excel', 'Power BI', 'Tableau',
            'Marketing', 'Social Media', 'Content Writing', 'SEO',
            'Graphic Design', 'Photoshop', 'Illustrator', 'Figma',
            'Accounting', 'Finance', 'Bookkeeping', 'Auditing'
        ]
        
        skills = []
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skills.append(skill)
        
        self.stdout.write(f'Created {len(skills)} skills')
        
        # Create Industries
        industries_data = [
            'Information Technology', 'Software Development', 'Finance', 'Banking',
            'Healthcare', 'Education', 'Marketing', 'Advertising',
            'Retail', 'E-commerce', 'Manufacturing', 'Construction',
            'Telecommunications', 'Media', 'Entertainment', 'Hospitality',
            'Real Estate', 'Legal Services', 'Consulting', 'Non-Profit'
        ]
        
        industries = []
        for industry_name in industries_data:
            industry, created = Industry.objects.get_or_create(name=industry_name)
            industries.append(industry)
        
        self.stdout.write(f'Created {len(industries)} industries')
        
        # Create Locations (South African municipalities)
        locations_data = [
            ('Johannesburg', 'Gauteng'),
            ('Pretoria', 'Gauteng'),
            ('Sandton', 'Gauteng'),
            ('Cape Town', 'Western Cape'),
            ('Stellenbosch', 'Western Cape'),
            ('Durban', 'KwaZulu-Natal'),
            ('Pietermaritzburg', 'KwaZulu-Natal'),
            ('Port Elizabeth', 'Eastern Cape'),
            ('Bloemfontein', 'Free State'),
            ('Polokwane', 'Limpopo'),
            ('Nelspruit', 'Mpumalanga'),
            ('Kimberley', 'Northern Cape'),
            ('Mahikeng', 'North West'),
        ]
        
        locations = []
        for municipality, province in locations_data:
            location, created = Location.objects.get_or_create(
                municipality=municipality,
                province=province
            )
            locations.append(location)
        
        self.stdout.write(f'Created {len(locations)} locations')
        
        # Create Interns
        self.stdout.write(f'\nCreating {num_interns} interns...')
        
        for i in range(1, num_interns + 1):
            username = f'intern{i}'
            
            # Skip if user already exists
            if CustomUser.objects.filter(username=username).exists():
                continue
            
            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=f'intern{i}@example.com',
                password='password123',
                user_type='intern',
                email_confirmed=True,
                email_confirmed_at=timezone.now()
            )
            
            # Create profile
            location = random.choice(locations)
            profile = InternProfile.objects.create(
                user=user,
                full_name=fake.name(),
                phone=fake.phone_number()[:20],
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=30),
                bio=fake.text(max_nb_chars=300),
                current_location=fake.address()[:200],
                current_municipality=location.municipality,
                current_province=location.province
            )
            
            # Add skills (random 5-10 skills)
            selected_skills = random.sample(skills, random.randint(5, 10))
            profile.skills.set(selected_skills)
            
            # Add industries (random 1-3 industries)
            selected_industries = random.sample(industries, random.randint(1, 3))
            profile.industries.set(selected_industries)
            
            # Add preferred locations (random 1-3)
            selected_locations = random.sample(locations, random.randint(1, 3))
            profile.preferred_locations.set(selected_locations)
            
            # Add education (1-2 records)
            for _ in range(random.randint(1, 2)):
                Education.objects.create(
                    intern=profile,
                    institution=fake.company() + ' University',
                    qualification=random.choice(['Bachelor of Science', 'Bachelor of Arts', 'Diploma', 'National Diploma']),
                    field_of_study=random.choice(['Computer Science', 'Business', 'Engineering', 'Marketing', 'Accounting']),
                    start_date=fake.date_between(start_date='-5y', end_date='-2y'),
                    end_date=fake.date_between(start_date='-2y', end_date='-1y'),
                    is_current=False,
                    grade=random.choice(['Distinction', 'Pass', 'Cum Laude'])
                )
            
            # Add work experience (0-2 records)
            for _ in range(random.randint(0, 2)):
                exp_skills = random.sample(selected_skills, random.randint(2, 4))
                experience = WorkExperience.objects.create(
                    intern=profile,
                    company=fake.company(),
                    position=fake.job(),
                    start_date=fake.date_between(start_date='-3y', end_date='-1y'),
                    end_date=fake.date_between(start_date='-1y', end_date='today') if random.choice([True, False]) else None,
                    is_current=random.choice([True, False]),
                    description=fake.text(max_nb_chars=200)
                )
                experience.skills_used.set(exp_skills)
            
            if i % 10 == 0:
                self.stdout.write(f'Created {i} interns...')
        
        self.stdout.write(self.style.SUCCESS(f'>> Created {num_interns} interns'))
        
        # Create Employers
        self.stdout.write(f'\nCreating {num_employers} employers...')
        
        for i in range(1, num_employers + 1):
            username = f'employer{i}'
            
            # Skip if user already exists
            if CustomUser.objects.filter(username=username).exists():
                continue
            
            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=f'employer{i}@example.com',
                password='password123',
                user_type='employer',
                email_confirmed=True,
                email_confirmed_at=timezone.now()
            )
            
            # Create profile
            location = random.choice(locations)
            profile = EmployerProfile.objects.create(
                user=user,
                company_name=fake.company(),
                company_description=fake.text(max_nb_chars=500),
                company_website=fake.url(),
                contact_person=fake.name(),
                phone=fake.phone_number()[:20],
                company_location=fake.address()[:200],
                municipality=location.municipality,
                province=location.province
            )
            
            # Add industries (random 1-3)
            selected_industries = random.sample(industries, random.randint(1, 3))
            profile.industries.set(selected_industries)
        
        self.stdout.write(self.style.SUCCESS(f'>> Created {num_employers} employers'))
        
        self.stdout.write(self.style.SUCCESS('\n>> All users created successfully!'))
        self.stdout.write(self.style.WARNING('\nDefault password for all users: password123'))

