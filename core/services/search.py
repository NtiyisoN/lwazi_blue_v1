"""
Search Service for Lwazi Blue
Provides advanced search functionality for internships and interns
"""

from django.db.models import Q, Count
from ..models import InternshipPost, InternProfile


class SearchService:
    """Service for searching internships and interns"""
    
    @staticmethod
    def search_internships(query='', filters=None):
        """
        Search internships with full-text search and filters
        
        Args:
            query: Text to search in title, description, company
            filters: Dict with keys:
                - skills: List of skill IDs
                - industry: Industry ID
                - province: Province name
                - municipality: Municipality name
                - stipend_min: Minimum stipend
                - stipend_max: Maximum stipend
                - duration_min: Minimum duration
                - duration_max: Maximum duration
                - start_date_from: Start date from
                - start_date_to: Start date to
        
        Returns:
            QuerySet of InternshipPost
        """
        # Start with active, published internships
        internships = InternshipPost.objects.filter(
            is_active=True,
            is_published=True
        ).select_related('employer', 'employer__user', 'industry').prefetch_related('skills_required')
        
        # Text search
        if query:
            internships = internships.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(requirements__icontains=query) |
                Q(responsibilities__icontains=query) |
                Q(employer__company_name__icontains=query)
            )
        
        # Apply filters
        if filters:
            # Skills filter
            skills = filters.get('skills')
            if skills:
                for skill_id in skills:
                    internships = internships.filter(skills_required__id=skill_id)
            
            # Industry filter
            industry = filters.get('industry')
            if industry:
                internships = internships.filter(industry_id=industry)
            
            # Province filter
            province = filters.get('province')
            if province:
                internships = internships.filter(province=province)
            
            # Municipality filter
            municipality = filters.get('municipality')
            if municipality:
                internships = internships.filter(municipality__icontains=municipality)
            
            # Stipend filters
            stipend_min = filters.get('stipend_min')
            if stipend_min:
                internships = internships.filter(
                    Q(stipend__gte=stipend_min) | Q(stipend__isnull=True)
                )
            
            stipend_max = filters.get('stipend_max')
            if stipend_max:
                internships = internships.filter(stipend__lte=stipend_max)
            
            # Duration filters
            duration_min = filters.get('duration_min')
            if duration_min:
                internships = internships.filter(duration_months__gte=duration_min)
            
            duration_max = filters.get('duration_max')
            if duration_max:
                internships = internships.filter(duration_months__lte=duration_max)
            
            # Date range filters
            start_date_from = filters.get('start_date_from')
            if start_date_from:
                internships = internships.filter(start_date__gte=start_date_from)
            
            start_date_to = filters.get('start_date_to')
            if start_date_to:
                internships = internships.filter(start_date__lte=start_date_to)
        
        return internships.distinct()
    
    @staticmethod
    def search_interns(query='', filters=None):
        """
        Search intern profiles with full-text search and filters
        
        Args:
            query: Text to search in name, bio, username
            filters: Dict with keys:
                - skills: List of skill IDs
                - industries: List of industry IDs
                - province: Province name
                - municipality: Municipality name
                - has_experience: Boolean
                - has_education: Boolean
                - qualification_level: String
        
        Returns:
            QuerySet of InternProfile
        """
        # Get all confirmed intern profiles
        interns = InternProfile.objects.filter(
            user__email_confirmed=True
        ).select_related('user').prefetch_related(
            'skills', 'industries', 'education_set', 'work_experience_set'
        )
        
        # Text search
        if query:
            interns = interns.filter(
                Q(full_name__icontains=query) |
                Q(user__username__icontains=query) |
                Q(user__email__icontains=query) |
                Q(bio__icontains=query) |
                Q(phone__icontains=query)
            )
        
        # Apply filters
        if filters:
            # Skills filter
            skills = filters.get('skills')
            if skills:
                for skill_id in skills:
                    interns = interns.filter(skills__id=skill_id)
            
            # Industries filter
            industries = filters.get('industries')
            if industries:
                for industry_id in industries:
                    interns = interns.filter(industries__id=industry_id)
            
            # Province filter
            province = filters.get('province')
            if province:
                interns = interns.filter(current_province=province)
            
            # Municipality filter
            municipality = filters.get('municipality')
            if municipality:
                interns = interns.filter(current_municipality__icontains=municipality)
            
            # Has experience filter
            has_experience = filters.get('has_experience')
            if has_experience:
                interns = interns.annotate(
                    exp_count=Count('work_experience_set')
                ).filter(exp_count__gt=0)
            
            # Has education filter
            has_education = filters.get('has_education')
            if has_education:
                interns = interns.annotate(
                    edu_count=Count('education_set')
                ).filter(edu_count__gt=0)
        
        return interns.distinct()

