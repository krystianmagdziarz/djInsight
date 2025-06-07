# 🖼️ Demo Gallery

Visual showcase of djInsight features and capabilities.

## 📱 Articles List

![Articles List](images/1.png)

**Overview:** Main articles list showing live view counters for each article. Notice how each article displays real-time analytics data including total views and recent activity indicators.

**Features shown:**
- 📊 Live view counters on article cards
- 🎯 Real-time statistics updates  
- 📈 Popular content indicators
- 🎨 Clean, modern UI integration

---

## 📰 Article Analytics Detail

![Article Detail View](images/2.png)

**Overview:** Individual article page demonstrating djInsight's modular template system with comprehensive analytics sidebar.

**Features shown:**
- 📊 **Quick Stats** - Total views, unique visitors, last viewed timestamp
- 🕐 **Live Statistics** - Auto-refreshing counter with 30-second intervals
- 📅 **Time-based Analytics** - Today, week, and month view breakdowns
- 🔧 **Code Examples** - Template tag usage demonstration
- 📱 **Responsive Design** - Mobile-friendly analytics widgets

---

## 📊 Detailed Analytics Demo

![Analytics Components](images/3.png)

**Overview:** Comprehensive demonstration of djInsight's modular template tags and component system.

**Features shown:**
- 🧩 **Individual Statistics Components** - Total views, unique views, last viewed
- ⏰ **Time-based Statistics** - Today, this week, this month counters
- 🔄 **Live Statistics Counter** - Real-time updating display
- 📊 **Complete Analytics Widget** - All-in-one analytics solution
- 🎨 **Flexible Layout** - Mix and match components as needed

---

## 🛒 E-commerce Integration  

![Product Analytics](images/4.png)

**Overview:** Product page showcasing djInsight's cross-content type support with e-commerce specific features.

**Features shown:**
- 🛍️ **Product Analytics** - View tracking for e-commerce items
- 💰 **Popular Product Indicators** - Highlight trending products
- 📊 **Cross-content Analytics** - Articles, products, courses tracked separately
- 🎯 **Content-type Separation** - Prevents ID conflicts between different models
- 🔧 **Custom Display Names** - Tailored presentation for different content types

---

## 📈 Popular Content Overview

![Popular Content](images/5.png)

**Overview:** Dashboard view showing most popular content across different types with comprehensive analytics.

**Features shown:**
- 🏆 **Popular Articles** - Top-performing blog content
- 📊 **Product Analytics** - E-commerce performance tracking  
- 🎓 **Course Statistics** - Educational content metrics
- 📱 **Dashboard Integration** - Overview of site-wide performance
- 🔄 **Real-time Updates** - Live statistics across all content types

---

## 🎨 Key Design Principles

### 📱 **Responsive Design**
All djInsight components are built with mobile-first responsive design, ensuring analytics look great on any device.

### 🎯 **Modular Architecture**  
Individual template tags can be mixed and matched to create custom analytics displays that fit your design.

### ⚡ **Performance-Focused**
Sub-millisecond Redis operations ensure analytics don't slow down your site, with beautiful loading states.

### 🎨 **Framework Agnostic**
Works with Bootstrap, Tailwind, custom CSS, or any frontend framework you're using.

## 🚀 Implementation Examples

### Basic Integration
```html
{% load djInsight_tags %}
{% page_view_tracker obj=article %}
<p>Views: {% total_views_stat obj=article %}</p>
```

### Advanced Dashboard
```html
{% load djInsight_tags %}
<div class="analytics-dashboard">
    {% for item in popular_content %}
        <div class="item-card">
            <h3>{{ item.title }}</h3>
            {% live_stats_counter obj=item refresh_interval=30 %}
        </div>
    {% endfor %}
</div>
```

### E-commerce Integration
```html
{% load djInsight_tags %}
{% page_view_tracker obj=product %}
{% total_views_stat obj=product as views %}
{% if views > 100 %}
    <span class="badge hot">🔥 Popular!</span>
{% endif %}
```

## 🔗 Try It Yourself

1. **📦 Install djInsight** - Follow the [Installation Guide](installation.md)
2. **⚡ Quick Start** - Get running in 5 minutes with [Quick Start](quick-start.md)  
3. **🎨 Customize** - Explore [Template Examples](template-examples.md) for ideas
4. **📊 Advanced** - Check [Analytics Usage](analytics.md) for advanced features 