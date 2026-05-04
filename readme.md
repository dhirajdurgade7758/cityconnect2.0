# CityConnect

CityConnect is an AI-powered civic engagement platform that helps citizens report civic issues, complete eco-friendly tasks, and earn rewards through a transparent EcoCoin system. It combines AI verification, live location tracking, vouchers, and department dashboards to support faster issue resolution and stronger community participation.

## What it does

* Citizens can report civic issues with an image, description, and location.
* AI helps verify reports and eco-task submissions.
* Users earn EcoCoins for valid contributions and can redeem them in the store.
* Department admins can review, assign, and resolve issues from role-based dashboards.
* The system includes maps, analytics, badges, leaderboard rankings, and voucher-based redemption.

## Core Features

### User Experience

* Profile dashboard with reports, tasks, EcoCoins, badges, and redemptions.
* Issue feed with like, comment, save, and share actions.
* Eco task submission and validation.
* Saved posts with an HTMX-powered UI.
* EcoCoin store with voucher PDF generation.

### Department Admin Panels

* Department-specific issue dashboards.
* Live location maps for reported issues.
* Status updates from Pending to In Progress to Resolved.
* Resolution history and admin actions.

### Gamification

* EcoCoins for reports, tasks, likes, and comments.
* Badges for contribution milestones.
* Leaderboard for top contributors.

## EcoCoin Store

Store categories include shop offers, donor gifts, event tickets, and eco rewards. Users redeem offers, receive a voucher, and claim the reward at a physical location.

## Tech Stack

### Backend

* Django 5.x
* PostgreSQL / SQLite
* OpenAI API for image and text verification
* HTMX for interactive updates

### Frontend

* Django Templates
* Bootstrap 5
* Bootstrap Icons / FontAwesome
* JS + AJAX + HTMX

### Other Integrations

* PDF voucher generation
* Live location fetch
* AI-based coin allocation

## Project Structure

```
cityconnect/
│── cityconnect/         # Main project settings
│── core/                # User profiles, dashboard, feed, auth
│── issues/              # Issue reporting & AI verification & civic task submission
│── store/               # EcoCoin store, redemptions
│── admin_panel/         # Department dashboards
│── templates/           # HTML templates
│── static/              # CSS, JS, assets
```

## System Workflow

1. User reports an issue or completes a task.
2. AI verifies the submission.
3. EcoCoins are awarded based on authenticity and engagement.
4. Department admins review and resolve issues.
5. Users redeem rewards in the store.
6. A voucher is generated for physical claim.

## Impact

* Citizens are encouraged to report and act.
* AI helps reduce fake or low-quality submissions.
* Gamification motivates civic participation.
* Departments get real-time actionable insights.
* Local businesses and donors can engage with the community.

## Future Enhancements

* Mobile app support
* Push notifications
* Advanced duplicate report detection
* Shopkeeper and donor self-service panel
* City analytics dashboard

## Conclusion

CityConnect is a scalable smart city solution that bridges citizens, government, and local businesses using AI and gamification to make cities cleaner, greener, and more efficient.
---
