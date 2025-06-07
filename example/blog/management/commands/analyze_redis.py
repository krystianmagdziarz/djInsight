import json
from collections import defaultdict

import redis
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Analyze djInsight Redis keys and show breakdown by model"

    def handle(self, *args, **options):
        try:
            redis_client = redis.Redis(host="localhost", port=6379, db=0)
            redis_client.ping()
        except:
            self.stdout.write(self.style.ERROR("Redis connection failed"))
            return

        self.stdout.write(self.style.SUCCESS("=== djInsight Redis Analysis ==="))

        # Get all djInsight keys
        all_keys = redis_client.keys("djinsight:*")

        counters = defaultdict(int)
        unique_counters = defaultdict(int)
        content_types = defaultdict(list)

        for key in all_keys:
            key_str = key.decode("utf-8")

            # Analyze counter keys
            if ":counter:" in key_str:
                if "unique_counter" not in key_str:
                    parts = key_str.split(":")
                    if len(parts) >= 3:
                        if len(parts) == 3:  # Old format: djinsight:counter:5
                            page_id = parts[2]
                            count = int(redis_client.get(key) or 0)
                            counters[f"unknown:{page_id}"] = count
                        elif (
                            len(parts) == 4
                        ):  # New format: djinsight:counter:blog.article:5
                            content_type, page_id = parts[2], parts[3]
                            count = int(redis_client.get(key) or 0)
                            counters[f"{content_type}:{page_id}"] = count

            # Analyze unique counter keys
            elif ":unique_counter:" in key_str:
                parts = key_str.split(":")
                if len(parts) >= 3:
                    if len(parts) == 3:  # Old format
                        page_id = parts[2]
                        count = int(redis_client.get(key) or 0)
                        unique_counters[f"unknown:{page_id}"] = count
                    elif len(parts) == 4:  # New format
                        content_type, page_id = parts[2], parts[3]
                        count = int(redis_client.get(key) or 0)
                        unique_counters[f"{content_type}:{page_id}"] = count

            # Analyze UUID keys (contain full data)
            elif len(key_str.split(":")) == 2 and "-" in key_str.split(":")[1]:
                try:
                    data = json.loads(redis_client.get(key).decode("utf-8"))
                    content_type = data.get("content_type")
                    page_id = data.get("page_id")
                    if content_type and page_id:
                        content_types[content_type].append(page_id)
                except:
                    pass

        # Display results
        self.stdout.write("\n📊 **View Counters:**")
        for key, count in sorted(counters.items()):
            content_type, page_id = key.split(":")
            self.stdout.write(f"  {content_type} ID {page_id}: {count} views")

        self.stdout.write("\n👥 **Unique View Counters:**")
        for key, count in sorted(unique_counters.items()):
            content_type, page_id = key.split(":")
            self.stdout.write(f"  {content_type} ID {page_id}: {count} unique views")

        self.stdout.write("\n🏷️  **Content Types Found:**")
        for content_type, page_ids in sorted(content_types.items()):
            unique_pages = set(page_ids)
            self.stdout.write(
                f"  {content_type}: {len(page_ids)} views on {len(unique_pages)} pages"
            )
            for page_id in sorted(unique_pages):
                # Try to get object name
                try:
                    if content_type == "blog.article":
                        from blog.models import Article

                        obj = Article.objects.get(id=page_id)
                        name = obj.title
                    elif content_type == "blog.product":
                        from blog.models import Product

                        obj = Product.objects.get(id=page_id)
                        name = obj.name
                    elif content_type == "blog.course":
                        from blog.models import Course

                        obj = Course.objects.get(id=page_id)
                        name = obj.title
                    else:
                        name = "Unknown"
                    self.stdout.write(f"    - ID {page_id}: {name}")
                except:
                    self.stdout.write(f"    - ID {page_id}: (not found in DB)")

        self.stdout.write("\n📈 **Summary:**")
        self.stdout.write(f"  Total Redis keys: {len(all_keys)}")
        self.stdout.write(f"  Content types: {len(content_types)}")
        self.stdout.write(f"  Pages with views: {len(counters)}")
