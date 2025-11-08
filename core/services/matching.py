"""
Matching Algorithm Services for Lwazi Blue
Matches interns with internships and vice versa based on configurable weights
"""

from django.conf import settings
from django.db.models import Q, Count, Case, When, IntegerField, Value
from ..models import InternshipPost, InternProfile


class InternshipMatchingService:
    """
    Service to match internships with intern profiles
    Used when interns browse opportunities without specific filters
    """
    
    def __init__(self):
        # Get weights from settings or use defaults
        self.weights = getattr(settings, 'MATCHING_WEIGHTS', {
            'skills': 0.40,
            'industry': 0.25,
            'location': 0.20,
            'qualification': 0.15,
        })
    
    def get_matched_internships(self, intern_profile, limit=20):
        """
        Get internships matched to an intern profile
        Returns a list of (internship, score) tuples ordered by score
        """
        # Start with active, published internships
        internships = InternshipPost.objects.filter(
            is_active=True,
            is_published=True
        ).select_related('employer', 'employer__user', 'industry').prefetch_related('skills_required')
        
        # Calculate match scores
        matched_internships = []
        for internship in internships:
            score = self.calculate_match_score(internship, intern_profile)
            matched_internships.append((internship, score))
        
        # Sort by score (highest first)
        matched_internships.sort(key=lambda x: x[1], reverse=True)
        
        # Return top matches
        return matched_internships[:limit]
    
    def calculate_match_score(self, internship, intern_profile):
        """
        Calculate match score between an internship and intern profile
        Returns a score from 0-100
        """
        total_score = 0.0
        
        # 1. Skills Match (40% weight)
        skills_score = self._calculate_skills_match(internship, intern_profile)
        total_score += skills_score * self.weights['skills']
        
        # 2. Industry Match (25% weight)
        industry_score = self._calculate_industry_match(internship, intern_profile)
        total_score += industry_score * self.weights['industry']
        
        # 3. Location Match (20% weight)
        location_score = self._calculate_location_match(internship, intern_profile)
        total_score += location_score * self.weights['location']
        
        # 4. Qualification/Experience Match (15% weight)
        qualification_score = self._calculate_qualification_match(internship, intern_profile)
        total_score += qualification_score * self.weights['qualification']
        
        return round(total_score, 2)
    
    def _calculate_skills_match(self, internship, intern_profile):
        """Calculate skills match percentage (0-100)"""
        required_skills = set(internship.skills_required.values_list('id', flat=True))
        intern_skills = set(intern_profile.skills.values_list('id', flat=True))
        
        if not required_skills:
            return 50  # Neutral score if no skills required
        
        # Calculate overlap
        matching_skills = required_skills.intersection(intern_skills)
        match_percentage = (len(matching_skills) / len(required_skills)) * 100
        
        return match_percentage
    
    def _calculate_industry_match(self, internship, intern_profile):
        """Calculate industry match percentage (0-100)"""
        if not internship.industry:
            return 50  # Neutral score if no industry specified
        
        intern_industries = intern_profile.industries.values_list('id', flat=True)
        
        if internship.industry.id in intern_industries:
            return 100  # Perfect match
        else:
            return 0  # No match
    
    def _calculate_location_match(self, internship, intern_profile):
        """Calculate location match percentage (0-100)"""
        # Check if internship location matches current or preferred locations
        
        # Check current location
        if (internship.municipality.lower() == intern_profile.current_municipality.lower() and
            internship.province.lower() == intern_profile.current_province.lower()):
            return 100  # Perfect match - current location
        
        # Check preferred locations
        preferred_locations = intern_profile.preferred_locations.all()
        for location in preferred_locations:
            if (location.municipality.lower() == internship.municipality.lower() and
                location.province.lower() == internship.province.lower()):
                return 80  # Good match - preferred location
        
        # Check province only
        if internship.province.lower() == intern_profile.current_province.lower():
            return 40  # Partial match - same province
        
        # Check preferred provinces
        for location in preferred_locations:
            if location.province.lower() == internship.province.lower():
                return 30  # Partial match - preferred province
        
        return 0  # No match
    
    def _calculate_qualification_match(self, internship, intern_profile):
        """Calculate qualification/experience match (0-100)"""
        score = 0
        
        # Check if intern has education records
        education_count = intern_profile.education_set.count()
        if education_count > 0:
            score += 50  # Has education
            
            # Bonus for multiple qualifications
            if education_count > 1:
                score += 20
        
        # Check if intern has work experience
        experience_count = intern_profile.work_experience_set.count()
        if experience_count > 0:
            score += 30  # Has experience
        
        return min(score, 100)  # Cap at 100


class InternMatchingService:
    """
    Service to match interns with employer requirements
    Used when employers browse candidates without specific filters
    """
    
    def __init__(self):
        # Get weights from settings or use defaults
        self.weights = getattr(settings, 'MATCHING_WEIGHTS', {
            'skills': 0.40,
            'industry': 0.25,
            'location': 0.20,
            'qualification': 0.15,
        })
    
    def get_matched_interns(self, employer_profile, limit=20):
        """
        Get interns matched to an employer profile
        Returns a list of (intern_profile, score) tuples ordered by score
        """
        # Get all intern profiles with related data
        interns = InternProfile.objects.select_related('user').prefetch_related(
            'skills', 'industries', 'preferred_locations', 
            'education_set', 'work_experience_set'
        ).filter(
            user__email_confirmed=True  # Only show confirmed users
        )
        
        # Calculate match scores
        matched_interns = []
        for intern in interns:
            score = self.calculate_match_score(intern, employer_profile)
            matched_interns.append((intern, score))
        
        # Sort by score (highest first)
        matched_interns.sort(key=lambda x: x[1], reverse=True)
        
        # Return top matches
        return matched_interns[:limit]
    
    def calculate_match_score(self, intern_profile, employer_profile):
        """
        Calculate match score between intern profile and employer
        Returns a score from 0-100
        """
        total_score = 0.0
        
        # 1. Skills Match (40% weight)
        skills_score = self._calculate_skills_match(intern_profile, employer_profile)
        total_score += skills_score * self.weights['skills']
        
        # 2. Industry Match (25% weight)
        industry_score = self._calculate_industry_match(intern_profile, employer_profile)
        total_score += industry_score * self.weights['industry']
        
        # 3. Location Match (20% weight)
        location_score = self._calculate_location_match(intern_profile, employer_profile)
        total_score += location_score * self.weights['location']
        
        # 4. Experience Level Match (15% weight)
        experience_score = self._calculate_experience_match(intern_profile)
        total_score += experience_score * self.weights['qualification']
        
        return round(total_score, 2)
    
    def _calculate_skills_match(self, intern_profile, employer_profile):
        """Calculate skills match percentage (0-100)"""
        intern_skills = set(intern_profile.skills.values_list('id', flat=True))
        
        # Get skills from employer's industry or posted internships
        employer_industries = set(employer_profile.industries.values_list('id', flat=True))
        intern_industries = set(intern_profile.industries.values_list('id', flat=True))
        
        if not intern_skills:
            return 0  # No skills listed
        
        # Check if intern has skills matching employer's industry needs
        # For now, we'll check if they have any skills at all
        if intern_skills:
            # More skills = higher score (up to 100)
            skill_count = len(intern_skills)
            base_score = min((skill_count / 10) * 100, 100)  # 10+ skills = 100%
            return base_score
        
        return 0
    
    def _calculate_industry_match(self, intern_profile, employer_profile):
        """Calculate industry match percentage (0-100)"""
        intern_industries = set(intern_profile.industries.values_list('id', flat=True))
        employer_industries = set(employer_profile.industries.values_list('id', flat=True))
        
        if not intern_industries or not employer_industries:
            return 50  # Neutral if no industries specified
        
        # Calculate overlap
        matching_industries = intern_industries.intersection(employer_industries)
        
        if matching_industries:
            # Perfect match if any overlap
            match_percentage = (len(matching_industries) / len(employer_industries)) * 100
            return min(match_percentage, 100)
        
        return 0
    
    def _calculate_location_match(self, intern_profile, employer_profile):
        """Calculate location match percentage (0-100)"""
        # Check if intern's current or preferred location matches employer location
        
        # Check current location
        if (intern_profile.current_municipality.lower() == employer_profile.municipality.lower() and
            intern_profile.current_province.lower() == employer_profile.province.lower()):
            return 100  # Perfect match - current location
        
        # Check preferred locations
        preferred_locations = intern_profile.preferred_locations.all()
        for location in preferred_locations:
            if (location.municipality.lower() == employer_profile.municipality.lower() and
                location.province.lower() == employer_profile.province.lower()):
                return 80  # Good match - preferred location
        
        # Check province only
        if intern_profile.current_province.lower() == employer_profile.province.lower():
            return 40  # Partial match - same province
        
        # Check preferred provinces
        for location in preferred_locations:
            if location.province.lower() == employer_profile.province.lower():
                return 30  # Partial match - preferred province
        
        return 0  # No match
    
    def _calculate_experience_match(self, intern_profile):
        """Calculate experience level score (0-100)"""
        score = 0
        
        # Education score (up to 50 points)
        education_count = intern_profile.education_set.count()
        if education_count > 0:
            score += 30  # Has education
            if education_count > 1:
                score += 20  # Multiple qualifications
        
        # Work experience score (up to 50 points)
        experience_count = intern_profile.work_experience_set.count()
        if experience_count > 0:
            score += 30  # Has experience
            if experience_count > 1:
                score += 20  # Multiple experiences
        
        return min(score, 100)  # Cap at 100

