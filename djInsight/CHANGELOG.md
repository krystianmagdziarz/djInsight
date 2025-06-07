# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-06-07

### Added
- Initial release of djInsight
- Redis-based page view tracking for high performance
- Asynchronous processing with Celery tasks
- PageViewStatisticsMixin for easy integration with Wagtail pages
- Template tags for tracking and displaying statistics:
  - `page_view_tracker` - JavaScript tracking code
  - `page_stats_display` - Live statistics display
  - `page_analytics_widget` - Complete analytics widget
  - `format_view_count` - Number formatting filter
- Django admin interface for viewing logs and summaries
- Management commands for manual processing:
  - `process_pageviews` - Process views from Redis
  - `generate_summaries` - Generate daily summaries
  - `cleanup_pageviews` - Clean up old data
- Comprehensive test suite
- Full documentation and examples
- Support for Django 3.2+ and Wagtail 3.0+
- Support for Python 3.8+

### Features
- **High Performance**: Sub-millisecond page view recording using Redis
- **Real-time Statistics**: Live view counters with auto-refresh
- **Unique Visitor Tracking**: Session-based unique visitor detection
- **Data Aggregation**: Daily summaries for efficient historical queries
- **Automatic Cleanup**: Configurable data retention policies
- **Error Handling**: Robust error handling and logging
- **Scalability**: Designed for high-traffic websites
- **Flexibility**: Configurable settings for all aspects

### Models
- `PageViewStatisticsMixin` - Mixin for adding statistics to pages
- `PageViewLog` - Detailed individual page view logs
- `PageViewSummary` - Daily aggregated statistics

### API Endpoints
- `POST /djInsight/record-view/` - Record page views
- `POST /djInsight/page-stats/` - Get real-time statistics

### Configuration Options
- Redis connection settings
- Processing batch sizes and limits
- Data retention policies
- Tracking enable/disable
- Celery task scheduling

### Dependencies
- Django >= 3.2
- Wagtail >= 3.0
- Redis >= 4.0.0
- Celery >= 5.0.0

## [Unreleased]

### Planned Features
- Chart visualization widgets
- Export functionality for analytics data
- Advanced filtering and reporting
- Integration with Google Analytics
- Performance monitoring dashboard
- A/B testing support
- Geographic tracking (with privacy controls)
- Bot detection and filtering
- Custom event tracking
- REST API for external integrations

---

## Contributing

When contributing to this project, please:

1. Add new features under the `[Unreleased]` section
2. Follow the format: `### Added/Changed/Deprecated/Removed/Fixed/Security`
3. Include a brief description of the change
4. Reference any related issues or pull requests
5. Update the version number when releasing

## Release Process

1. Move items from `[Unreleased]` to a new version section
2. Update version numbers in `setup.py`, `pyproject.toml`, and `__init__.py`
3. Create a git tag for the release
4. Build and upload to PyPI
5. Update documentation 