"""
Management command to populate mock internship posts
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import InternshipPost, EmployerProfile, Skill, Industry, Location
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Populate database with mock internship posts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--posts',
            type=int,
            default=20,
            help='Number of internship posts to create'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_posts = options['posts']
        
        # Get employers
        employers = list(EmployerProfile.objects.all())
        if not employers:
            self.stdout.write(self.style.ERROR('No employers found. Run populate_users first.'))
            return
        
        # Get skills and industries
        skills = list(Skill.objects.all())
        industries = list(Industry.objects.all())
        
        if not skills or not industries:
            self.stdout.write(self.style.ERROR('No skills or industries found. Run populate_users first.'))
            return
        
        self.stdout.write(f'Creating {num_posts} internship posts...')
        
        job_titles = [
            'Software Development Internship',
            'Marketing Internship',
            'Finance Internship',
            'Human Resources Internship',
            'Graphic Design Internship',
            'Data Analysis Internship',
            'Business Administration Internship',
            'IT Support Internship',
            'Sales Internship',
            'Customer Service Internship',
            'Web Development Internship',
            'Mobile App Development Internship',
            'Content Writing Internship',
            'Social Media Management Internship',
            'Project Management Internship',
            'Accounting Internship',
            'Legal Internship',
            'Engineering Internship',
            'Research Internship',
            'Operations Internship',
        ]
        
        for i in range(1, num_posts + 1):
            employer = random.choice(employers)
            
            # Random dates
            start_date = timezone.now().date() + timedelta(days=random.randint(30, 90))
            deadline = start_date - timedelta(days=random.randint(7, 30))
            
            # Create internship
            internship = InternshipPost.objects.create(
                employer=employer,
                title=random.choice(job_titles),
                description=fake.text(max_nb_chars=800),
                requirements=fake.text(max_nb_chars=400),
                responsibilities=fake.text(max_nb_chars=400),
                industry=random.choice(industries),
                location=employer.company_location,
                municipality=employer.municipality,
                province=employer.province,
                duration_months=random.choice([3, 6, 9, 12, 18, 24]),
                stipend=random.choice([None, 2000, 3000, 4000, 5000, 6000, 7500, 10000]),
                start_date=start_date,
                application_deadline=deadline,
                is_active=True,
                is_published=random.choice([True, True, True, False])  # 75% published
            )
            
            # Add required skills (3-7 skills)
            selected_skills = random.sample(skills, random.randint(3, 7))
            internship.skills_required.set(selected_skills)
            
            if i % 5 == 0:
                self.stdout.write(f'Created {i} internship posts...')
        
        self.stdout.write(self.style.SUCCESS(f'\n>> Created {num_posts} internship posts'))
        self.stdout.write(self.style.WARNING('Note: Some posts may be unpublished (drafts)'))

