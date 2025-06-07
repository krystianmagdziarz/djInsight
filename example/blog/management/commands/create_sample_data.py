from django.core.management.base import BaseCommand
from django.utils.text import slugify

from blog.models import Article, Course, Product


class Command(BaseCommand):
    help = "Create sample data for djInsight demo"

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")

        # Create sample articles
        articles_data = [
            {
                "title": "Getting Started with djInsight",
                "content": """djInsight is a powerful Django package for tracking page views and analytics. 
                
This comprehensive guide will walk you through the installation and basic setup of djInsight in your Django project. 

Key features include:
- Real-time view tracking with Redis
- Modular template tags for flexible UI design
- Support for any Django model via mixin inheritance
- Background processing with Celery
- Comprehensive analytics dashboard

Whether you're building a blog, e-commerce site, or any web application, djInsight provides the tools you need to understand your users' behavior and optimize your content strategy.""",
                "author": "djInsight Team",
            },
            {
                "title": "Advanced Analytics with djInsight",
                "content": """Take your analytics to the next level with djInsight's advanced features.

In this article, we'll explore:
- Custom analytics queries
- Time-based statistics
- Popular content detection
- Performance optimization tips
- Integration with external analytics tools

Learn how to leverage djInsight's powerful analytics engine to gain deeper insights into your content performance and user engagement patterns.""",
                "author": "Analytics Expert",
            },
            {
                "title": "Building Responsive Analytics Dashboards",
                "content": """Create beautiful, responsive analytics dashboards using djInsight's modular template tags.

This tutorial covers:
- Designing mobile-friendly analytics displays
- Customizing CSS for your brand
- Creating interactive charts and graphs
- Real-time data updates
- Best practices for UX design

Transform your raw analytics data into compelling visual stories that help you make data-driven decisions.""",
                "author": "UI/UX Designer",
            },
            {
                "title": "Performance Optimization for High-Traffic Sites",
                "content": """Optimize djInsight for high-traffic websites and applications.

Topics covered:
- Redis configuration and clustering
- Celery task optimization
- Database indexing strategies
- Caching best practices
- Monitoring and alerting

Ensure your analytics system can handle millions of page views while maintaining fast response times and accurate data collection.""",
                "author": "DevOps Engineer",
            },
            {
                "title": "Integrating djInsight with Machine Learning",
                "content": """Combine djInsight analytics with machine learning for predictive insights.

Learn about:
- Data export and preprocessing
- Predictive modeling for content performance
- User behavior analysis
- Recommendation systems
- A/B testing frameworks

Discover how to use your analytics data to build intelligent systems that improve user experience and business outcomes.""",
                "author": "Data Scientist",
            },
        ]

        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                title=article_data["title"],
                defaults={
                    "slug": slugify(article_data["title"]),
                    "content": article_data["content"],
                    "author": article_data["author"],
                },
            )
            if created:
                self.stdout.write(f"Created article: {article.title}")

        # Create sample products
        products_data = [
            {
                "name": "djInsight Pro License",
                "price": 99.99,
                "description": "Professional license for djInsight with premium features and support.",
                "category": "Software",
            },
            {
                "name": "Analytics Dashboard Template",
                "price": 49.99,
                "description": "Beautiful, responsive dashboard template designed for djInsight analytics.",
                "category": "Templates",
            },
            {
                "name": "Custom Integration Service",
                "price": 299.99,
                "description": "Professional integration service for complex djInsight setups.",
                "category": "Services",
            },
            {
                "name": "Performance Monitoring Add-on",
                "price": 29.99,
                "description": "Advanced monitoring and alerting for your djInsight installation.",
                "category": "Add-ons",
            },
            {
                "name": "Mobile Analytics SDK",
                "price": 79.99,
                "description": "SDK for tracking mobile app analytics with djInsight backend.",
                "category": "SDK",
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data["name"],
                defaults={
                    "slug": slugify(product_data["name"]),
                    "price": product_data["price"],
                    "description": product_data["description"],
                    "category": product_data["category"],
                },
            )
            if created:
                self.stdout.write(f"Created product: {product.name}")

        # Create sample courses
        courses_data = [
            {
                "title": "Django Analytics Fundamentals",
                "description": "Learn the basics of web analytics and how to implement tracking in Django applications.",
                "instructor": "Sarah Johnson",
                "difficulty": "beginner",
            },
            {
                "title": "Advanced Redis for Analytics",
                "description": "Master Redis for high-performance analytics and real-time data processing.",
                "instructor": "Mike Chen",
                "difficulty": "advanced",
            },
            {
                "title": "Building Analytics Dashboards",
                "description": "Create beautiful, interactive dashboards for your analytics data.",
                "instructor": "Emily Rodriguez",
                "difficulty": "intermediate",
            },
            {
                "title": "Celery for Background Processing",
                "description": "Learn how to use Celery for scalable background task processing.",
                "instructor": "David Kim",
                "difficulty": "intermediate",
            },
            {
                "title": "Data Visualization with Python",
                "description": "Create compelling visualizations from your analytics data using Python.",
                "instructor": "Lisa Wang",
                "difficulty": "beginner",
            },
        ]

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data["title"],
                defaults={
                    "slug": slugify(course_data["title"]),
                    "description": course_data["description"],
                    "instructor": course_data["instructor"],
                    "difficulty": course_data["difficulty"],
                },
            )
            if created:
                self.stdout.write(f"Created course: {course.title}")

        self.stdout.write(self.style.SUCCESS("Successfully created sample data!"))
