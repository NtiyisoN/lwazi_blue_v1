"""
Management command to populate mock blog posts
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from blog.models import BlogPost, BlogCategory, BlogTag
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Populate database with mock blog posts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--posts',
            type=int,
            default=10,
            help='Number of blog posts to create'
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_posts = options['posts']
        
        # Get or create admin user for blog posts
        admin_user = CustomUser.objects.filter(user_type='admin').first()
        if not admin_user:
            # Create admin user if doesn't exist
            admin_user = CustomUser.objects.create_user(
                username='blogger',
                email='blogger@lwazi-blue.co.za',
                password='password123',
                user_type='admin',
                email_confirmed=True,
                email_confirmed_at=timezone.now()
            )
            self.stdout.write('Created admin user for blog posts')
        
        # Create categories
        categories_data = [
            'Career Tips', 'Industry Insights', 'Success Stories',
            'Job Search', 'Interview Tips', 'Professional Development',
            'Company Culture', 'Technology', 'News'
        ]
        
        categories = []
        for cat_name in categories_data:
            category, created = BlogCategory.objects.get_or_create(name=cat_name)
            categories.append(category)
        
        self.stdout.write(f'Created {len(categories)} blog categories')
        
        # Create tags
        tags_data = [
            'Internships', 'Graduates', 'Employers', 'Career',
            'Skills', 'Education', 'South Africa', 'Technology',
            'Business', 'Tips', 'Advice', 'Success'
        ]
        
        tags = []
        for tag_name in tags_data:
            tag, created = BlogTag.objects.get_or_create(name=tag_name)
            tags.append(tag)
        
        self.stdout.write(f'Created {len(tags)} blog tags')
        
        # Create blog posts
        self.stdout.write(f'\nCreating {num_posts} blog posts...')
        
        blog_titles = [
            'How to Write a Winning Internship Application',
            'Top 10 Skills Employers Look for in 2025',
            'Success Story: From Intern to Full-Time Employee',
            'Preparing for Your First Interview',
            'The Importance of Networking for Graduates',
            'How to Make the Most of Your Internship',
            'Building Your Professional Profile',
            'Understanding South African Job Market Trends',
            'Tips for Remote Internship Success',
            'How to Stand Out as a Graduate',
            'The Future of Work in South Africa',
            'Developing In-Demand Tech Skills',
            'Balancing Internship and Studies',
            'Making a Great First Impression',
            'Career Planning for Recent Graduates',
        ]
        
        created_count = 0
        for i in range(1, num_posts + 1):
            # Random publish date in the past
            published_at = timezone.now() - timedelta(days=random.randint(1, 90))
            
            # Generate unique title with timestamp to avoid slug conflicts
            base_title = blog_titles[i-1] if i <= len(blog_titles) else fake.sentence(nb_words=8).rstrip('.')
            title = f'{base_title} - {timezone.now().strftime("%Y%m%d%H%M%S")}-{i}'
            
            post = BlogPost.objects.create(
                author=admin_user,
                title=title,
                content=fake.text(max_nb_chars=2000),
                excerpt=fake.text(max_nb_chars=200),
                category=random.choice(categories),
                is_published=random.choice([True, True, True, False]),  # 75% published
                published_at=published_at if random.choice([True, True, True, False]) else None,
                views_count=random.randint(0, 500)
            )
            
            # Add tags (2-4 tags)
            selected_tags = random.sample(tags, random.randint(2, 4))
            post.tags.set(selected_tags)
            
            created_count += 1
            
            if created_count % 3 == 0:
                self.stdout.write(f'Created {created_count} blog posts...')
        
        self.stdout.write(self.style.SUCCESS(f'\n>> Created {created_count} blog posts'))
        self.stdout.write(self.style.WARNING('Note: Some posts may be unpublished (drafts)'))

